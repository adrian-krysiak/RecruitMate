import { axiosClient } from "../api/axiosClient";
import {
  type LoginRequest,
  type LoginResponse,
  type RegisterRequest,
  type RegisterResponse,
} from "../types/api";
import { API_ENDPOINTS, STORAGE_KEYS } from "../constants";
import { StorageService } from "../utils/storage";

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await axiosClient.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    const { access_token, refresh_token, user } = response.data;

    // Store token and user info
    StorageService.setString(STORAGE_KEYS.TOKEN, access_token);
    if (refresh_token) {
      StorageService.setString(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
    }
    StorageService.setItem(STORAGE_KEYS.USER, user);

    return response.data;
  },

  register: async (payload: RegisterRequest): Promise<RegisterResponse> => {
    const response = await axiosClient.post<RegisterResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      payload
    );

    const { access_token, refresh_token, user } = response.data;

    // Store token and user info to align with login
    StorageService.setString(STORAGE_KEYS.TOKEN, access_token);
    if (refresh_token) {
      StorageService.setString(STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
    }
    StorageService.setItem(STORAGE_KEYS.USER, user);

    return response.data;
  },

  logout: async () => {
    try {
      const refreshToken = StorageService.getString(STORAGE_KEYS.REFRESH_TOKEN);
      
      // 1. Call backend to invalidate token (only if refresh token exists)
      if (refreshToken) {
        await axiosClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
          refresh: refreshToken,
        });
      }
    } catch (error) {
      console.error("Logout backend call failed", error);
      // Continue with local logout even if backend call fails
    }

    // 2. Clear local storage regardless of backend response
    StorageService.clearAuthData();
  },

  refreshToken: async (): Promise<string> => {
    const refreshToken = StorageService.getString(STORAGE_KEYS.REFRESH_TOKEN);
    if (!refreshToken) throw new Error("No refresh token available");

    const response = await axiosClient.post<{ access_token: string }>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh: refreshToken }
    );

    const { access_token } = response.data;
    StorageService.setString(STORAGE_KEYS.TOKEN, access_token);
    return access_token;
  },

  getStoredUser: (): { username: string; email: string; id: string } | null => {
    return StorageService.getItem<{
      username: string;
      email: string;
      id: string;
    }>(STORAGE_KEYS.USER);
  },

  getStoredToken: () => {
    return StorageService.getString(STORAGE_KEYS.TOKEN);
  },
};
