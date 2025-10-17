import { ContentItem } from './content';

export interface Newsletter {
  id: string;
  workspace_id: string;
  title: string;
  subject_line: string;
  content_html: string;
  content_text?: string;
  items: ContentItem[];
  status: 'draft' | 'sent' | 'scheduled';
  scheduled_at?: string;
  sent_at?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface GenerateNewsletterRequest {
  workspace_id: string;
  title: string;
  max_items?: number;
  days_back?: number;
  sources?: string[];
  tone?: string;
  language?: string;
  temperature?: number;
  model?: string;
  use_openrouter?: boolean;
}

export interface UpdateNewsletterRequest {
  title?: string;
  subject_line?: string;
  content_html?: string;
  items?: ContentItem[];
}
