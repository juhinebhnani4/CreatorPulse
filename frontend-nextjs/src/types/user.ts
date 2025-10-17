export interface User {
  user_id: string;
  email: string;
  username: string;
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  username: string;
  token: string;
  expires_at: string;
}
