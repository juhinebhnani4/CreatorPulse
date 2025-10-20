"""
Configuration constants for backend services.

Centralized configuration for magic numbers, thresholds, and limits
across all backend services.
"""

import os
from typing import Optional


class NewsletterConstants:
    """Constants for newsletter generation service."""

    # Trend integration
    MAX_TRENDS_TO_FETCH: int = int(os.getenv("MAX_TRENDS_TO_FETCH", "5"))
    TREND_SCORE_BOOST_MULTIPLIER: float = float(os.getenv("TREND_SCORE_BOOST_MULTIPLIER", "1.3"))  # 30% boost
    CONTENT_FETCH_MULTIPLIER: int = int(os.getenv("CONTENT_FETCH_MULTIPLIER", "2"))  # Fetch 2x max_items

    # Default parameters
    DEFAULT_MAX_ITEMS: int = int(os.getenv("DEFAULT_MAX_ITEMS", "15"))
    DEFAULT_DAYS_BACK: int = int(os.getenv("DEFAULT_DAYS_BACK", "7"))
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_TONE: str = os.getenv("DEFAULT_TONE", "professional")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")

    # Limits
    MAX_NEWSLETTER_LIST_LIMIT: int = int(os.getenv("MAX_NEWSLETTER_LIST_LIMIT", "50"))


class FeedbackConstants:
    """Constants for feedback learning service."""

    # Score adjustments
    PREFERRED_SOURCE_BOOST_MULTIPLIER: float = float(os.getenv("PREFERRED_SOURCE_BOOST", "1.2"))  # 20% boost
    BELOW_THRESHOLD_PENALTY_MULTIPLIER: float = float(os.getenv("BELOW_THRESHOLD_PENALTY", "0.7"))  # 30% penalty

    # Limits
    MAX_FEEDBACK_ITEMS_TO_ANALYZE: int = int(os.getenv("MAX_FEEDBACK_ITEMS", "1000"))


class TrendConstants:
    """Constants for trend detection service."""

    # Detection parameters
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("TREND_MIN_CONFIDENCE", "0.6"))
    MAX_CONTENT_ITEMS_TO_ANALYZE: int = int(os.getenv("TREND_MAX_CONTENT_ITEMS", "1000"))
    MIN_ITEMS_FOR_DETECTION: int = int(os.getenv("TREND_MIN_ITEMS", "5"))

    # TF-IDF parameters
    TFIDF_MAX_FEATURES: int = int(os.getenv("TFIDF_MAX_FEATURES", "100"))
    TFIDF_MIN_DF: int = int(os.getenv("TFIDF_MIN_DF", "2"))
    TFIDF_NGRAM_RANGE: tuple = (1, 3)  # unigrams, bigrams, trigrams

    # Clustering parameters
    MIN_CLUSTER_SIZE: int = int(os.getenv("MIN_CLUSTER_SIZE", "2"))
    MAX_CLUSTERS: int = int(os.getenv("MAX_CLUSTERS", "10"))
    MIN_CLUSTERS: int = int(os.getenv("MIN_CLUSTERS", "3"))

    # Scoring weights
    MENTION_SCORE_WEIGHT: float = 0.3
    VELOCITY_SCORE_WEIGHT: float = 0.4
    SOURCE_DIVERSITY_WEIGHT: float = 0.3

    # Confidence levels
    HIGH_CONFIDENCE_THRESHOLD: float = 0.75
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.5

    # Cross-source validation
    MIN_SOURCES_FOR_VALIDATION: int = int(os.getenv("MIN_SOURCES_FOR_TREND", "2"))


class AnalyticsConstants:
    """Constants for analytics tracking."""

    # HMAC token settings
    DEFAULT_TOKEN_EXPIRY_DAYS: int = int(os.getenv("ANALYTICS_TOKEN_EXPIRY_DAYS", "30"))
    TOKEN_EXPIRY_SECONDS: int = DEFAULT_TOKEN_EXPIRY_DAYS * 86400  # 30 days in seconds


class SchedulerConstants:
    """Constants for scheduler service."""

    # Execution history
    DEFAULT_EXECUTION_HISTORY_LIMIT: int = int(os.getenv("SCHEDULER_HISTORY_LIMIT", "10"))


class ContentConstants:
    """Constants for content service."""

    # Content limits
    MAX_CONTENT_ITEMS_TO_FETCH: int = int(os.getenv("MAX_CONTENT_ITEMS", "10000"))


class HistoricalConstants:
    """Constants for historical data service."""

    # Retention and limits
    DEFAULT_RETENTION_DAYS: int = int(os.getenv("HISTORICAL_RETENTION_DAYS", "7"))
    MAX_HISTORICAL_ITEMS_TO_ANALYZE: int = int(os.getenv("MAX_HISTORICAL_ITEMS", "1000"))
    DEFAULT_HISTORICAL_DAYS_BACK: int = int(os.getenv("HISTORICAL_DAYS_BACK", "1"))


# Convenience class for accessing all constants
class ServiceConstants:
    """Aggregated constants for all services."""

    Newsletter = NewsletterConstants
    Feedback = FeedbackConstants
    Trend = TrendConstants
    Analytics = AnalyticsConstants
    Scheduler = SchedulerConstants
    Content = ContentConstants
    Historical = HistoricalConstants


# Export for easy access
__all__ = [
    'NewsletterConstants',
    'FeedbackConstants',
    'TrendConstants',
    'AnalyticsConstants',
    'SchedulerConstants',
    'ContentConstants',
    'HistoricalConstants',
    'ServiceConstants'
]
