/**
 * Style Profile Types
 *
 * Types for writing style training and management.
 * Matches backend models in backend/models/style_profile.py
 */

export interface StyleProfile {
  // Core attributes
  workspace_id: string;

  // Voice characteristics
  tone: string; // "conversational" | "authoritative" | "humorous" | "professional"
  formality_level: number; // 0.0 (casual) to 1.0 (formal)

  // Sentence patterns
  avg_sentence_length: number;
  sentence_length_variety: number;
  question_frequency: number;

  // Vocabulary preferences
  vocabulary_level: string; // "simple" | "intermediate" | "advanced"
  favorite_phrases: string[];
  avoided_words: string[];

  // Structural preferences
  typical_intro_style: string; // "question" | "statement" | "anecdote" | "statistic"
  section_count: number;
  uses_emojis: boolean;
  emoji_frequency: number;

  // Examples
  example_intros: string[];
  example_transitions: string[];
  example_conclusions: string[];

  // Metadata
  trained_on_count: number;
  confidence_score?: number;
  created_at: string;
  updated_at: string;
}

export interface TrainStyleRequest {
  workspace_id: string;
  samples: string[]; // Array of newsletter text samples
  retrain?: boolean; // Whether to overwrite existing profile
}

export interface TrainStyleResponse {
  success: boolean;
  message: string;
  profile: StyleProfile;
  analysis_summary: {
    samples_analyzed: number;
    avg_sample_length: number;
    detected_tone: string;
    detected_formality: number;
    detected_patterns: string[];
  };
}

export interface StyleProfileResponse extends StyleProfile {
  id: string;
}

export interface StyleProfileUpdate {
  tone?: string;
  formality_level?: number;
  avg_sentence_length?: number;
  sentence_length_variety?: number;
  question_frequency?: number;
  vocabulary_level?: string;
  favorite_phrases?: string[];
  avoided_words?: string[];
  typical_intro_style?: string;
  section_count?: number;
  uses_emojis?: boolean;
  emoji_frequency?: number;
  example_intros?: string[];
  example_transitions?: string[];
  example_conclusions?: string[];
}

export interface StyleProfileSummary {
  has_profile: boolean;
  workspace_id: string;
  tone?: string;
  formality_level?: number;
  trained_on_count?: number;
  last_updated?: string;
  confidence_score?: number;
}

export interface GeneratePromptRequest {
  workspace_id: string;
}

export interface GeneratePromptResponse {
  has_profile: boolean;
  prompt: string;
  profile_summary?: StyleProfileSummary;
}

// UI-specific types
export interface StyleAnalysis {
  characteristic: string;
  value: string | number;
  description: string;
  icon?: string;
}

export interface StyleTrainingProgress {
  stage: 'uploading' | 'analyzing' | 'extracting' | 'validating' | 'complete' | 'error';
  progress: number; // 0-100
  message: string;
}
