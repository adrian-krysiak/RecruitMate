import { axiosClient } from "../api/axiosClient";
import {
  type LoginRequest,
  type LoginResponse,
  type RegisterRequest,
  type RegisterResponse,
  type User,
  type UpdateProfileRequest,
  type StoredUser,
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
    } catch {
      // Continue with local logout even if backend call fails
    }

    // 2. Clear ALL user data (auth + scanner session data)
    StorageService.clearAllUserData();
  },

  refreshToken: async (): Promise<string> => {
    const refreshToken = StorageService.getString(STORAGE_KEYS.REFRESH_TOKEN);
    if (!refreshToken) throw new Error("No refresh token available");

    try {
      const response = await axiosClient.post<{ access: string; refresh: string }>(
        API_ENDPOINTS.AUTH.REFRESH,
        { refresh: refreshToken }
      );

      const { access, refresh } = response.data;
      StorageService.setString(STORAGE_KEYS.TOKEN, access);
      StorageService.setString(STORAGE_KEYS.REFRESH_TOKEN, refresh);

      return access;
    } catch (error) {
      StorageService.clearAuthData();
      throw error;
    }
  },

  getStoredUser: (): StoredUser | null => {
    return StorageService.getItem<StoredUser>(STORAGE_KEYS.USER);
  },

  getStoredToken: () => {
    return StorageService.getString(STORAGE_KEYS.TOKEN);
  },

  getUserProfile: async (): Promise<User> => {
    const response = await axiosClient.get<User>(
      API_ENDPOINTS.AUTH.DASHBOARD
    );
    return response.data;
  },

  updateUserProfile: async (data: UpdateProfileRequest): Promise<User> => {
    const response = await axiosClient.patch<User>(
      API_ENDPOINTS.AUTH.DASHBOARD,
      data
    );
    StorageService.setItem(STORAGE_KEYS.USER, response.data);
    return response.data;
  },

  deleteAccount: async (): Promise<void> => {
    await axiosClient.delete(API_ENDPOINTS.AUTH.DASHBOARD);
    StorageService.clearAuthData();
  },
};
