import axios from "axios";
import { API_CONFIG, STORAGE_KEYS, HTTP_STATUS } from "../constants";
import { StorageService } from "../utils/storage";
import {
  RateLimitManager,
  type RateLimitInfo,
} from "../utils/rateLimitManager";

// Rate limit state tracking
export const rateLimitState = {
  current: null as RateLimitInfo | null,
  listeners: new Set<(info: RateLimitInfo | null) => void>(),
};

export function subscribeToRateLimit(
  callback: (info: RateLimitInfo | null) => void
): () => void {
  rateLimitState.listeners.add(callback);
  return () => rateLimitState.listeners.delete(callback);
}

function notifyRateLimitChange(info: RateLimitInfo | null) {
  rateLimitState.current = info;
  rateLimitState.listeners.forEach((listener) => listener(info));
}

export const axiosClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: API_CONFIG.TIMEOUT,
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = StorageService.getString(STORAGE_KEYS.TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosClient.interceptors.response.use(
  (response) => {
    // Clear rate limit on successful response
    const rateLimitInfo = RateLimitManager.extractRateLimitInfo(
      response.headers as Record<string, string | number | undefined>
    );
    if (rateLimitInfo && rateLimitInfo.remaining > 0) {
      notifyRateLimitChange(null);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle Rate Limiting (429)
    if (error.response?.status === 429 && !originalRequest._retryCount) {
      originalRequest._retryCount = 1;

      const rateLimitInfo = RateLimitManager.extractRateLimitInfo(
        error.response.headers as Record<string, string | number | undefined>
      );

      if (rateLimitInfo) {
        notifyRateLimitChange(rateLimitInfo);

        // Wait before retrying
        const delay = RateLimitManager.getBackoffDelay(0);
        await new Promise((resolve) => setTimeout(resolve, delay));

        if (RateLimitManager.shouldRetry(originalRequest._retryCount, 1)) {
          return axiosClient(originalRequest);
        }
      }
    }

    // Auto-Refresh Token Logic
    if (
      error.response?.status === HTTP_STATUS.UNAUTHORIZED &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = StorageService.getString(
          STORAGE_KEYS.REFRESH_TOKEN
        );
        if (!refreshToken) {
          // If there's no refresh token, clear auth and reject original error
          StorageService.clearAuthData();
          return Promise.reject(error);
        }

        const response = await axios.post(
          `${API_CONFIG.BASE_URL}/auth/token/refresh/`,
          {
            refresh: refreshToken,
          }
        );

        const { access_token } = response.data;
        StorageService.setString(STORAGE_KEYS.TOKEN, access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        // Clear auth data but don't redirect - let React handle navigation
        StorageService.clearAuthData();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
