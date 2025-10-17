export interface Workspace {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceConfig {
  workspace_id: string;
  sources: SourceConfig[];
  newsletter_settings: NewsletterSettings;
  email_settings: EmailSettings;
  scheduler_settings: SchedulerSettings;
}

export interface SourceConfig {
  type: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog';
  enabled: boolean;
  config: Record<string, any>;
}

export interface NewsletterSettings {
  tone?: string;
  language?: string;
  max_items?: number;
  template?: string;
}

export interface EmailSettings {
  provider?: 'smtp' | 'sendgrid';
  smtp_server?: string;
  smtp_port?: number;
  smtp_username?: string;
  from_email?: string;
  from_name?: string;
}

export interface SchedulerSettings {
  enabled: boolean;
  frequency?: string;
  time?: string;
  timezone?: string;
}
