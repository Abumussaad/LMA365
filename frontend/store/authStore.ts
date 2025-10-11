import { create } from 'zustand';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL + '/api';

interface User {
  id: string;
  email: string;
  role: string;
  full_name: string;
  phone?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, role: string, phone?: string) => Promise<void>;
  logout: () => Promise<void>;
  loadToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,
  isAuthenticated: false,

  loadToken: async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      const userStr = await AsyncStorage.getItem('user');
      
      if (token && userStr) {
        const user = JSON.parse(userStr);
        set({ token, user, isAuthenticated: true, isLoading: false });
        
        // Set default axios header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      console.error('Error loading token:', error);
      set({ isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      
      await AsyncStorage.setItem('token', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      set({ token: access_token, user, isAuthenticated: true });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  register: async (email: string, password: string, fullName: string, role: string, phone?: string) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        full_name: fullName,
        role,
        phone
      });
      const { access_token, user } = response.data;
      
      await AsyncStorage.setItem('token', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(user));
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      set({ token: access_token, user, isAuthenticated: true });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  },

  logout: async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    set({ token: null, user: null, isAuthenticated: false });
  }
}));