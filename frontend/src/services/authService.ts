import { axiosClient } from '../api/axiosClient';

export const authService = {
  logout: async () => {
    try {
      // 1. In the future: Call backend to invalidate token
      // await axiosClient.post('/auth/logout'); 
      
      // 2. Clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } catch (error) {
      console.error('Logout failed', error);
      // logout even if server call fails
    }
  }
};