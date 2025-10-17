export interface Subscriber {
  id: string;
  workspace_id: string;
  email: string;
  name?: string;
  status: 'active' | 'unsubscribed' | 'bounced';
  source?: string;
  subscribed_at: string;
  unsubscribed_at?: string;
  last_sent_at?: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SubscriberStats {
  workspace_id: string;
  total_subscribers: number;
  active_subscribers: number;
  unsubscribed: number;
  bounced: number;
}

export interface CreateSubscriberRequest {
  workspace_id: string;
  email: string;
  name?: string;
  source?: string;
  metadata?: Record<string, any>;
}

export interface BulkCreateSubscribersRequest {
  workspace_id: string;
  subscribers: Array<{
    email: string;
    name?: string;
    metadata?: Record<string, any>;
  }>;
}

export interface UpdateSubscriberRequest {
  name?: string;
  status?: 'active' | 'unsubscribed' | 'bounced';
  metadata?: Record<string, any>;
}

export interface SubscriberListResponse {
  subscribers: Subscriber[];
  count: number;
  workspace_id: string;
}

export interface BulkCreateResponse {
  created_count: number;
  failed_count: number;
  created: Subscriber[];
  failed: Array<{
    email: string;
    error: string;
  }>;
}
