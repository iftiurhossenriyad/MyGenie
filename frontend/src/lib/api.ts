import axios, { AxiosError } from 'axios';

export const AUTH_EXPIRED_EVENT = 'mygenie:auth-expired';

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mygenie_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('mygenie_token');
      localStorage.removeItem('mygenie_user');
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    }
    return Promise.reject(error);
  }
);

export default api;