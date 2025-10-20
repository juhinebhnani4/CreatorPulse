/**
 * Feedback & Learning Types
 *
 * Types for feedback collection and learning system.
 * Matches backend models in backend/models/feedback.py
 */

export type FeedbackRating = 'positive' | 'negative' | 'neutral';
export type EngagementType = 'high_score' | 'high_comments' | 'balanced';

// Content Item Feedback
export interface FeedbackItemCreate {
  content_item_id: string;
  rating: FeedbackRating;
  included_in_final: boolean;
  newsletter_id?: string;
  original_summary?: string;
  edited_summary?: string;
  edit_distance?: number;
  feedback_notes?: string;
}

export interface FeedbackItemResponse {
  id: string;
  workspace_id: string;
  user_id: string;
  content_item_id: string;
  newsletter_id?: string;
  rating: FeedbackRating;
  included_in_final: boolean;
  original_summary?: string;
  edited_summary?: string;
  edit_distance: number;
  feedback_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface FeedbackItemListResponse {
  items: FeedbackItemResponse[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// Newsletter Feedback
export interface NewsletterFeedbackCreate {
  newsletter_id: string;
  overall_rating: number; // 1-5 stars
  time_to_finalize_minutes?: number;
  items_added?: number;
  items_removed?: number;
  items_edited?: number;
  notes?: string;
  would_recommend?: boolean;
}

export interface NewsletterFeedbackResponse {
  id: string;
  workspace_id: string;
  user_id: string;
  newsletter_id: string;
  overall_rating: number;
  time_to_finalize_minutes?: number;
  items_added: number;
  items_removed: number;
  items_edited: number;
  notes?: string;
  would_recommend?: boolean;
  created_at: string;
  updated_at: string;
}

export interface NewsletterFeedbackListResponse {
  items: NewsletterFeedbackResponse[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// Source Quality
export interface SourceQualityScore {
  source: string;
  quality_score: number; // 0.0 to 1.0
  total_feedback_count: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  inclusion_rate: number; // Percentage kept in final newsletters
  avg_edit_distance?: number;
  quality_label: 'excellent' | 'good' | 'average' | 'poor';
  last_updated: string;
}

export interface SourceQualityScoreListResponse {
  items: SourceQualityScore[];
  total: number;
}

// Content Preferences
export interface ContentPreferences {
  workspace_id: string;
  preferred_sources: string[];
  avoided_topics: string[];
  preferred_topics: string[];
  min_score_threshold?: number;
  max_score_threshold?: number;
  preferred_content_length?: string; // "short" | "medium" | "long"
  preferred_recency_hours?: number;
  preferred_engagement_type?: EngagementType;
  confidence_level: number; // 0.0 to 1.0
  based_on_feedback_count: number;
  last_updated: string;
}

export interface ContentPreferencesResponse extends ContentPreferences {
  id: string;
  created_at: string;
  updated_at: string;
}

// Analytics
export interface FeedbackAnalyticsSummary {
  workspace_id: string;
  date_range: {
    start: string;
    end: string;
  };

  // Item feedback stats
  total_item_feedback: number;
  positive_item_count: number;
  negative_item_count: number;
  neutral_item_count: number;
  positive_rate: number;
  negative_rate: number;
  inclusion_rate: number;

  // Newsletter feedback stats
  total_newsletter_feedback: number;
  avg_newsletter_rating: number;
  avg_time_to_finalize_minutes?: number;
  avg_items_edited_per_newsletter: number;

  // Source performance
  top_performing_sources: Array<{
    source: string;
    quality_score: number;
    feedback_count: number;
  }>;
  worst_performing_sources: Array<{
    source: string;
    quality_score: number;
    feedback_count: number;
  }>;

  // Learning status
  learning_confidence: number;
  total_feedback_used: number;
  recommendations: string[];
}

// Apply Learning
export interface ApplyLearningRequest {
  content_item_ids: string[];
  apply_source_quality?: boolean;
  apply_preferences?: boolean;
}

export interface ApplyLearningResponse {
  adjusted_items: Array<{
    content_item_id: string;
    original_score: number;
    adjusted_score: number;
    adjustments: string[];
  }>;
  adjustments_made: number;
  quality_scores_applied: Record<string, number>;
  preferences_applied: boolean;
}

// UI-specific types
export interface FeedbackStats {
  totalFeedback: number;
  positiveRate: number;
  learningConfidence: number;
  topSource: {
    name: string;
    score: number;
  };
}

export interface FeedbackFilter {
  content_item_id?: string;
  newsletter_id?: string;
  rating?: FeedbackRating;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}
