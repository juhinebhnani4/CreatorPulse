export interface DeliveryRequest {
  newsletter_id: string;
  workspace_id: string;
  test_email?: string;
}

export interface Delivery {
  id: string;
  newsletter_id: string;
  workspace_id: string;
  total_subscribers: number;
  sent_count: number;
  failed_count: number;
  status: 'pending' | 'sending' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  errors: string[];
  created_at: string;
}

export interface DeliveryListResponse {
  deliveries: Delivery[];
  count: number;
  workspace_id: string;
}

export interface SendNewsletterResponse {
  status: string;
  newsletter_id: string;
  workspace_id: string;
  test_mode: boolean;
  message: string;
  total_subscribers?: number;
  sent_count?: number;
  failed_count?: number;
  errors?: string[];
}
