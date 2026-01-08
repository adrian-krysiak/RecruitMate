import { axiosClient } from "../api/axiosClient";
import { type LoginRequest, type LoginResponse } from "../types/api";

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await axiosClient.post<LoginResponse>(
      "/auth/login",
      credentials
    );
    const { access_token, user } = response.data;

    // Store token and user info
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", JSON.stringify(user));

    return response.data;
  },

  logout: async () => {
    try {
      // 1. Call backend to invalidate token
      await axiosClient.post('/auth/logout');

      // 2. Clear local storage
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    } catch (error) {
      console.error("Logout failed", error);
      throw error;
    }
  },

  getStoredUser: () => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  getStoredToken: () => {
    return localStorage.getItem("token");
  },
};
