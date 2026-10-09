/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, type ReactNode } from 'react';
import api from '../lib/api';
import type { User, UserLogin, UserCreate, AuthResponse } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const storedUser = localStorage.getItem('mygenie_user');
    if (!storedUser) return null;
    try {
      return JSON.parse(storedUser) as User;
    } catch {
      localStorage.removeItem('mygenie_user');
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('mygenie_token'));
  const [loading] = useState(false);

  const login = async (credentials: UserLogin) => {
    const response = await api.post<AuthResponse>('/api/v1/auth/login', credentials);
    const { access_token } = response.data;

    localStorage.setItem('mygenie_token', access_token);
    setToken(access_token);

    // Fetch user profile
    const userResponse = await api.get<User>('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    setUser(userResponse.data);
    localStorage.setItem('mygenie_user', JSON.stringify(userResponse.data));
  };

  const register = async (data: UserCreate) => {
    await api.post('/api/v1/auth/register', data);
    // After registration, login automatically
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    localStorage.removeItem('mygenie_token');
    localStorage.removeItem('mygenie_user');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    const response = await api.get<User>('/api/v1/auth/me');
    setUser(response.data);
    localStorage.setItem('mygenie_user', JSON.stringify(response.data));
  };

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}