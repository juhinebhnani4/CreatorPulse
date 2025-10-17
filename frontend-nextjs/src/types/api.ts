// Base API Response Structure
export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: string | null;
  message?: string;
}

// Pagination
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
