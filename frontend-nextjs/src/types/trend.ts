/**
 * Trend Detection Types
 *
 * Types for trend detection and analysis.
 * Matches backend models in backend/models/trend.py
 */

export type ConfidenceLevel = 'low' | 'medium' | 'high';

export interface Trend {
  id: string;
  workspace_id: string;

  // Core attributes
  topic: string;
  keywords: string[];

  // Strength indicators
  strength_score: number; // 0.0 to 1.0
  mention_count: number;
  velocity: number; // Mentions per hour or percentage increase

  // Sources
  sources: string[];
  source_count: number;

  // Evidence
  key_content_item_ids: string[];
  first_seen?: string;
  peak_time?: string;

  // Context
  explanation?: string;
  related_topics: string[];
  confidence_level: ConfidenceLevel;
  is_active: boolean;

  // Metadata
  detected_at: string;
  created_at: string;
  updated_at: string;
}

export interface TrendCreate {
  workspace_id: string;
  topic: string;
  keywords: string[];
  strength_score: number;
  mention_count: number;
  velocity: number;
  sources: string[];
  source_count: number;
  key_content_item_ids: string[];
  first_seen?: string;
  peak_time?: string;
  explanation?: string;
  related_topics?: string[];
  confidence_level?: ConfidenceLevel;
}

export interface TrendUpdate {
  strength_score?: number;
  mention_count?: number;
  velocity?: number;
  sources?: string[];
  source_count?: number;
  key_content_item_ids?: string[];
  peak_time?: string;
  explanation?: string;
  related_topics?: string[];
  confidence_level?: ConfidenceLevel;
  is_active?: boolean;
}

export interface TrendResponse extends Trend {
  // Includes all Trend fields
}

export interface TrendListResponse {
  trends: TrendResponse[];
  count: number;
  workspace_id: string;
}

export interface DetectTrendsRequest {
  workspace_id: string;
  days_back?: number; // Default: 7, Max: 30
  max_trends?: number; // Default: 5, Max: 20
  min_confidence?: number; // Default: 0.6
  sources?: string[]; // Optional: filter by sources
}

export interface DetectTrendsResponse {
  success: boolean;
  message: string;
  trends: TrendResponse[];
  analysis_summary: TrendAnalysisSummary;
}

export interface TrendAnalysisSummary {
  content_items_analyzed: number;
  date_range: {
    start: string;
    end: string;
  };
  sources_analyzed: string[];
  trends_detected: number;
  avg_confidence: number;
  top_keywords: string[];
  detection_method: string; // "TF-IDF + K-means clustering"
}

export interface TrendHistoryResponse {
  workspace_id: string;
  trends_by_date: Array<{
    date: string;
    trends: Array<{
      topic: string;
      strength_score: number;
      mention_count: number;
    }>;
  }>;
  date_range: {
    start: string;
    end: string;
  };
}

export interface TrendSummaryResponse {
  workspace_id: string;
  total_trends_detected: number;
  active_trends: number;
  inactive_trends: number;
  avg_strength_score: number;
  top_sources_by_trends: Array<{
    source: string;
    trend_count: number;
  }>;
  trending_keywords: string[];
  date_range: {
    start: string;
    end: string;
  };
}

// UI-specific types
export interface TrendCard {
  trend: TrendResponse;
  displayStrength: string; // "🔥 Strong" | "📈 Growing" | "📊 Emerging"
  strengthColor: string; // Tailwind color class
  strengthIcon: string;
}

export interface TrendFilter {
  confidence_level?: ConfidenceLevel;
  min_strength?: number;
  sources?: string[];
  is_active?: boolean;
}

export interface TrendStats {
  totalTrends: number;
  activeTrends: number;
  avgStrength: number;
  topKeywords: string[];
}

export interface TrendVisualizationData {
  labels: string[]; // Dates
  datasets: Array<{
    label: string; // Trend topic
    data: number[]; // Strength scores over time
    borderColor: string;
    backgroundColor: string;
  }>;
}
