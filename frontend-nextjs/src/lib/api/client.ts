/**
 * API Client for CreatorPulse Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string };
  status?: number;  // HTTP status code
}

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

function setAuthToken(token: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
}

function removeAuthToken() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
}

async function request<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers || {}) as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, { ...options, headers });
    const contentType = response.headers.get('content-type');

    if (contentType && !contentType.includes('application/json')) {
      if (!response.ok) throw new APIError('Request failed', response.status);
      return response as unknown as T;
    }

    const data: APIResponse<T> = await response.json();

    if (!response.ok || !data.success) {
      throw new APIError(
        data.error?.message || 'Request failed',
        response.status,
        data.error?.code
      );
    }

    return data.data as T;
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// Handle 401 errors by clearing token and redirecting to login
function handle401() {
  if (typeof window !== 'undefined') {
    removeAuthToken();
    window.location.href = '/login';
  }
}

// Generic API Client for use by specific API modules
export const apiClient = {
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<APIResponse<T>> {
    // Build query string from params if provided
    let url = `${API_BASE_URL}${endpoint}`;
    if (params) {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
      const queryString = queryParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      handle401();
      return { success: false, error: { code: 'UNAUTHORIZED', message: 'Session expired' } };
    }

    return response.json();
  },

  async post<T>(endpoint: string, data: any): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify(data),
      });

      // Handle 401 Unauthorized
      if (response.status === 401) {
        handle401();
        return { success: false, error: { code: 'UNAUTHORIZED', message: 'Session expired' } };
      }

      // Parse JSON response
      const jsonData = await response.json();

      // If response is not OK (4xx, 5xx), return error
      if (!response.ok) {
        // FastAPI error response format: {detail: "error message"}
        const errorMessage = jsonData.detail || jsonData.message || 'Request failed';
        console.error('[API Client] POST Error:', {
          endpoint,
          status: response.status,
          statusText: response.statusText,
          detail: jsonData
        });

        return {
          success: false,
          error: {
            code: `HTTP_${response.status}`,
            message: errorMessage
          },
          status: response.status
        } as any;
      }

      // Success response
      return jsonData;
    } catch (error: any) {
      console.error('[API Client] POST Exception:', {
        endpoint,
        error: error.message
      });

      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error.message || 'Network request failed'
        }
      } as any;
    }
  },

  async put<T>(endpoint: string, data: any): Promise<APIResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify(data),
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      handle401();
      return { success: false, error: { code: 'UNAUTHORIZED', message: 'Session expired' } };
    }

    return response.json();
  },

  async patch<T>(endpoint: string, data: any): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify(data),
      });

      // Handle 401 Unauthorized
      if (response.status === 401) {
        handle401();
        return { success: false, error: { code: 'UNAUTHORIZED', message: 'Session expired' } };
      }

      // Parse JSON response
      const jsonData = await response.json();

      // If response is not OK (4xx, 5xx), return error
      if (!response.ok) {
        const errorMessage = jsonData.detail || jsonData.message || 'Request failed';
        console.error('[API Client] PATCH Error:', {
          endpoint,
          status: response.status,
          statusText: response.statusText,
          detail: jsonData
        });

        return {
          success: false,
          error: {
            code: `HTTP_${response.status}`,
            message: errorMessage
          },
          status: response.status
        } as any;
      }

      // Success response
      return jsonData;
    } catch (error: any) {
      console.error('[API Client] PATCH Exception:', {
        endpoint,
        error: error.message
      });

      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error.message || 'Network request failed'
        }
      } as any;
    }
  },

  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
      handle401();
      return { success: false, error: { code: 'UNAUTHORIZED', message: 'Session expired' } };
    }

    return response.json();
  },

  // Auth token management methods
  saveAuthToken(token: string): void {
    setAuthToken(token);
  },

  clearAuthToken(): void {
    removeAuthToken();
  },

  isAuthenticated(): boolean {
    return !!getAuthToken();
  },
};

// Workspace types
export interface Workspace {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  role?: 'owner' | 'member';
}

export interface WorkspaceConfig {
  sources?: Array<{
    type: 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';
    enabled: boolean;
    config: Record<string, any>;
  }>;
  [key: string]: any;
}

// API methods
export const api = {
  auth: {
    async signup(email: string, username: string, password: string) {
      const data = await request<{ user_id: string; email: string; username: string; token: string }>(
        '/api/v1/auth/signup',
        { method: 'POST', body: JSON.stringify({ email, username, password }) }
      );
      setAuthToken(data.token);
      return data;
    },

    async login(email: string, password: string) {
      const data = await request<{ user_id: string; email: string; username: string; token: string }>(
        '/api/v1/auth/login',
        { method: 'POST', body: JSON.stringify({ email, password }) }
      );
      setAuthToken(data.token);
      return data;
    },

    async me() {
      return request<{ user_id: string; email: string; username: string }>('/api/v1/auth/me');
    },

    async logout() {
      await request('/api/v1/auth/logout', { method: 'POST' });
      removeAuthToken();
    },

    isAuthenticated(): boolean {
      return !!getAuthToken();
    },
  },

  workspaces: {
    async list() {
      return request<Workspace[]>('/api/v1/workspaces');
    },

    async create(name: string, description?: string) {
      return request<Workspace>('/api/v1/workspaces', {
        method: 'POST',
        body: JSON.stringify({ name, description }),
      });
    },

    async get(workspaceId: string) {
      return request<Workspace>(`/api/v1/workspaces/${workspaceId}`);
    },

    async getConfig(workspaceId: string) {
      const response = await request<{ config: WorkspaceConfig }>(`/api/v1/workspaces/${workspaceId}/config`);
      return response.config;
    },

    async saveConfig(workspaceId: string, config: WorkspaceConfig) {
      const response = await request<{ config: WorkspaceConfig }>(`/api/v1/workspaces/${workspaceId}/config`, {
        method: 'PUT',
        body: JSON.stringify({ config }),
      });
      return response.config;
    },
  },

  content: {
    async scrape(workspaceId: string, sources?: string[], limitPerSource?: number) {
      return request<{
        message: string;
        workspace_id: string;
        total_items: number;
        items_by_source: Record<string, number>;
        scraped_at: string;
      }>('/api/v1/content/scrape', {
        method: 'POST',
        body: JSON.stringify({ workspace_id: workspaceId, sources, limit_per_source: limitPerSource }),
      });
    },

    async stats(workspaceId: string) {
      return request<{
        workspace_id: string;
        total_items: number;
        items_by_source: Record<string, number>;
        items_last_24h: number;
        items_last_7d: number;
        latest_scrape: string | null;
      }>(`/api/v1/content/workspaces/${workspaceId}/stats`);
    },
  },
};

export default api;
