import { apiClient } from './client';
import { AuthResponse, LoginRequest, RegisterRequest, User } from '@/types/user';
import { ApiResponse } from '@/types/api';

export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    console.log('[authApi] Attempting login for:', credentials.email);
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', credentials);
    console.log('[authApi] Login response:', response);

    if (response.success && response.data) {
      // Backend returns 'token' not 'access_token'
      apiClient.saveAuthToken(response.data.token);
      console.log('[authApi] Token saved successfully');
      return response.data;
    }
    throw new Error(response.error?.message || response.error || 'Login failed');
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    console.log('[authApi] Attempting registration for:', data.email);
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/signup', data);
    console.log('[authApi] Registration response:', response);

    if (response.success && response.data) {
      // Backend returns 'token' not 'access_token'
      apiClient.saveAuthToken(response.data.token);
      console.log('[authApi] Token saved successfully');
      return response.data;
    }
    throw new Error(response.error?.message || response.error || 'Registration failed');
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } finally {
      apiClient.clearAuthToken();
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get user');
  },

  isAuthenticated(): boolean {
    return apiClient.isAuthenticated();
  },
};
