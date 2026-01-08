import axios from "axios";

export const axiosClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
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
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);