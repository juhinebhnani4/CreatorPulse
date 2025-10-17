"""
Trend Detection Service

Detects emerging trends from content using topic clustering, velocity analysis,
and cross-source validation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from datetime import datetime, timedelta
from uuid import UUID
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from backend.models.trend import (
    TrendCreate,
    TrendResponse,
    TrendHistoryResponse,
    TrendAnalysisSummary,
    DetectTrendsResponse
)
from backend.models.content import ContentItemResponse
from src.ai_newsletter.database.supabase_client import SupabaseManager


class TrendDetectionService:
    """Service for detecting and analyzing trends from content."""

    def __init__(self, min_confidence: float = 0.6):
        self.db = SupabaseManager()
        self.min_confidence = min_confidence
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3),  # unigrams, bigrams, trigrams
            min_df=2  # word must appear in at least 2 documents
        )

    async def detect_trends(
        self,
        workspace_id: UUID,
        days_back: int = 1,
        max_trends: int = 5,
        min_confidence: Optional[float] = None,
        sources: Optional[List[str]] = None
    ) -> Tuple[List[TrendResponse], Dict[str, Any]]:
        """
        Detect trends from recent content.

        Args:
            workspace_id: Workspace ID
            days_back: Number of days to analyze
            max_trends: Maximum trends to return
            min_confidence: Minimum confidence threshold
            sources: Filter by specific sources

        Returns:
            Tuple of (trends, analysis_summary)
        """
        if min_confidence is None:
            min_confidence = self.min_confidence

        # Get recent content
        cutoff_date = datetime.now() - timedelta(days=days_back)
        current_items = self._get_recent_content(
            str(workspace_id),
            cutoff_date,
            sources
        )

        if len(current_items) < 5:
            return [], {
                "content_items_analyzed": len(current_items),
                "topics_found": 0,
                "trends_detected": 0,
                "confidence_threshold": min_confidence,
                "time_range_days": days_back,
                "message": "Insufficient content for trend detection (minimum 5 items required)"
            }

        # Get historical content for velocity calculation
        historical_cutoff = cutoff_date - timedelta(days=days_back)
        historical_items = self._get_recent_content(
            str(workspace_id),
            historical_cutoff,
            sources,
            end_date=cutoff_date
        )

        # Stage 1: Extract topics
        topics = self._extract_topics(current_items)

        # Stage 2: Calculate velocity
        topics_with_velocity = self._calculate_velocity(
            topics,
            current_items,
            historical_items
        )

        # Stage 3: Cross-source validation
        validated_topics = self._validate_cross_source(topics_with_velocity)

        # Stage 4: Score and rank
        scored_trends = self._score_trends(validated_topics)

        # Stage 5: Generate explanations
        trends_data = self._generate_explanations(scored_trends, workspace_id)

        # Filter by confidence
        filtered_trends = [
            t for t in trends_data
            if t.strength_score >= min_confidence
        ][:max_trends]

        # Save trends to database
        saved_trends = []
        for trend_data in filtered_trends:
            try:
                saved_trend = self.db.create_trend(trend_data.model_dump(mode='json'))
                saved_trends.append(TrendResponse(**saved_trend))
            except Exception as e:
                print(f"Error saving trend: {e}")
                continue

        # Build analysis summary
        summary = {
            "content_items_analyzed": len(current_items),
            "topics_found": len(topics),
            "trends_detected": len(saved_trends),
            "confidence_threshold": min_confidence,
            "time_range_days": days_back,
            "sources_analyzed": sources or "all",
            "historical_items_count": len(historical_items)
        }

        return saved_trends, summary

    def _get_recent_content(
        self,
        workspace_id: str,
        start_date: datetime,
        sources: Optional[List[str]] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get recent content items from database."""
        # Build query filters
        filters = {
            "workspace_id": workspace_id,
            "created_at_gte": start_date.isoformat()
        }

        if end_date:
            filters["created_at_lt"] = end_date.isoformat()

        if sources:
            filters["source_in"] = sources

        # Fetch from database
        try:
            items = self.db.list_content_items(
                workspace_id,
                limit=1000,  # Analyze up to 1000 items
                **filters
            )
            return items
        except Exception as e:
            print(f"Error fetching content: {e}")
            return []

    def _extract_topics(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract topics using TF-IDF + K-means clustering.

        Args:
            items: Content items

        Returns:
            List of topic dictionaries
        """
        if len(items) < 5:
            return []

        # Combine title + summary for analysis
        texts = []
        for item in items:
            text = item.get('title', '')
            if item.get('summary'):
                text += " " + item['summary']
            texts.append(text)

        try:
            # TF-IDF vectorization
            tfidf_matrix = self.vectorizer.fit_transform(texts)

            # K-means clustering (5-10 clusters depending on data size)
            n_clusters = min(10, max(3, len(items) // 10))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)

            # Extract topic keywords for each cluster
            topics = []
            feature_names = self.vectorizer.get_feature_names_out()

            for cluster_id in range(n_clusters):
                cluster_items = [items[i] for i in range(len(items)) if clusters[i] == cluster_id]

                if len(cluster_items) < 2:
                    continue

                # Get top keywords for this cluster
                cluster_center = kmeans.cluster_centers_[cluster_id]
                top_indices = cluster_center.argsort()[-10:][::-1]
                keywords = [feature_names[i] for i in top_indices]

                # Main topic is the top keyword
                topic_name = keywords[0].replace('_', ' ').title()

                topics.append({
                    'topic': topic_name,
                    'keywords': keywords[:5],
                    'items': cluster_items,
                    'cluster_id': cluster_id
                })

            return topics

        except Exception as e:
            print(f"Error in topic extraction: {e}")
            return []

    def _calculate_velocity(
        self,
        topics: List[Dict[str, Any]],
        current_items: List[Dict[str, Any]],
        historical_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate mention velocity (spike detection).

        Args:
            topics: Extracted topics
            current_items: Current period items
            historical_items: Historical period items

        Returns:
            Topics with velocity added
        """
        for topic in topics:
            keywords = topic['keywords']

            # Count mentions in current window
            current_mentions = len([
                item for item in current_items
                if any(
                    kw.lower() in item.get('title', '').lower()
                    for kw in keywords
                )
            ])

            # Count mentions in historical window
            historical_mentions = len([
                item for item in historical_items
                if any(
                    kw.lower() in item.get('title', '').lower()
                    for kw in keywords
                )
            ]) if historical_items else 0

            # Calculate velocity (percentage increase)
            if historical_mentions > 0:
                velocity = ((current_mentions - historical_mentions) / historical_mentions) * 100
            elif current_mentions > 0:
                velocity = 100.0  # New topic
            else:
                velocity = 0.0

            topic['mention_count'] = current_mentions
            topic['velocity'] = velocity

        return topics

    def _validate_cross_source(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter topics that appear in multiple sources.

        Args:
            topics: Topics to validate

        Returns:
            Validated topics
        """
        validated = []

        for topic in topics:
            sources = set(item.get('source', 'unknown') for item in topic['items'])

            # Require at least 2 different sources for validation
            if len(sources) >= 2:
                topic['sources'] = list(sources)
                topic['source_count'] = len(sources)
                validated.append(topic)

        return validated

    def _score_trends(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score trends based on multiple factors.

        Args:
            topics: Topics to score

        Returns:
            Scored topics sorted by strength
        """
        for topic in topics:
            score = 0.0

            # Factor 1: Mention count (30% weight)
            mention_score = min(topic['mention_count'] / 20, 1.0)
            score += mention_score * 0.3

            # Factor 2: Velocity (40% weight)
            velocity_score = min(topic.get('velocity', 0) / 100.0, 1.0)
            score += velocity_score * 0.4

            # Factor 3: Source diversity (30% weight)
            source_score = min(topic['source_count'] / 4, 1.0)
            score += source_score * 0.3

            topic['strength_score'] = score

            # Confidence level
            if score >= 0.75:
                topic['confidence_level'] = 'high'
            elif score >= 0.5:
                topic['confidence_level'] = 'medium'
            else:
                topic['confidence_level'] = 'low'

        # Sort by score
        topics.sort(key=lambda x: x['strength_score'], reverse=True)

        return topics

    def _generate_explanations(
        self,
        topics: List[Dict[str, Any]],
        workspace_id: UUID
    ) -> List[TrendCreate]:
        """
        Generate AI explanations for trends.

        Args:
            topics: Scored topics
            workspace_id: Workspace ID

        Returns:
            List of TrendCreate objects
        """
        trends = []

        for topic_data in topics:
            # Create simple explanation (could enhance with AI later)
            item_count = len(topic_data['items'])
            sources_str = ", ".join(topic_data['sources'][:3])
            velocity = topic_data.get('velocity', 0)

            if velocity > 50:
                velocity_text = "showing rapid growth"
            elif velocity > 20:
                velocity_text = "gaining momentum"
            else:
                velocity_text = "steadily discussed"

            explanation = (
                f"This topic is trending with {item_count} mentions across "
                f"{sources_str}. It's {velocity_text} with a "
                f"{topic_data.get('velocity', 0):.0f}% increase in mentions."
            )

            # Get content item IDs
            key_item_ids = [
                UUID(item['id']) for item in topic_data['items'][:5]
                if item.get('id')
            ]

            # Get timestamps
            item_times = [
                datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                for item in topic_data['items']
                if item.get('created_at')
            ]

            first_seen = min(item_times) if item_times else datetime.now()
            peak_time = max(item_times) if item_times else datetime.now()

            # Create trend object
            trend = TrendCreate(
                workspace_id=workspace_id,
                topic=topic_data['topic'],
                keywords=topic_data['keywords'],
                strength_score=round(topic_data['strength_score'], 3),
                mention_count=topic_data['mention_count'],
                velocity=round(topic_data.get('velocity', 0), 2),
                sources=topic_data['sources'],
                source_count=topic_data['source_count'],
                key_content_item_ids=key_item_ids,
                first_seen=first_seen,
                peak_time=peak_time,
                explanation=explanation,
                related_topics=[],  # Could enhance with topic similarity
                confidence_level=topic_data['confidence_level'],
                is_active=True
            )

            trends.append(trend)

        return trends

    async def get_active_trends(
        self,
        workspace_id: UUID,
        limit: int = 5
    ) -> List[TrendResponse]:
        """
        Get active trends for workspace.

        Args:
            workspace_id: Workspace ID
            limit: Maximum trends to return

        Returns:
            List of active trends
        """
        trends_data = self.db.get_active_trends(str(workspace_id), limit)
        return [TrendResponse(**t) for t in trends_data]

    async def get_trend_history(
        self,
        workspace_id: UUID,
        days_back: int = 30
    ) -> TrendHistoryResponse:
        """
        Get trend history for workspace.

        Args:
            workspace_id: Workspace ID
            days_back: Number of days to look back

        Returns:
            Trend history
        """
        history_data = self.db.get_trend_history(str(workspace_id), days_back)

        return TrendHistoryResponse(
            workspace_id=workspace_id,
            history=history_data,
            days_back=days_back,
            count=len(history_data)
        )

    async def get_trend_summary(
        self,
        workspace_id: UUID,
        days_back: int = 7
    ) -> TrendAnalysisSummary:
        """
        Get summary of trends for workspace.

        Args:
            workspace_id: Workspace ID
            days_back: Analysis period

        Returns:
            Trend analysis summary
        """
        # Get all trends from period
        cutoff = datetime.now() - timedelta(days=days_back)
        all_trends = self.db.list_trends(
            str(workspace_id),
            start_date=cutoff
        )

        # Calculate statistics
        total_trends = len(all_trends)
        active_trends = len([t for t in all_trends if t.get('is_active', False)])

        # Top sources
        all_sources = []
        for trend in all_trends:
            all_sources.extend(trend.get('sources', []))

        source_counts = Counter(all_sources)
        top_sources = [
            {"source": source, "count": count}
            for source, count in source_counts.most_common(5)
        ]

        # Average strength
        avg_strength = (
            sum(t.get('strength_score', 0) for t in all_trends) / total_trends
            if total_trends > 0 else 0.0
        )

        # Get content count
        total_content = len(self._get_recent_content(
            str(workspace_id),
            cutoff
        ))

        return TrendAnalysisSummary(
            workspace_id=workspace_id,
            total_trends=total_trends,
            active_trends=active_trends,
            top_sources=top_sources,
            avg_strength_score=round(avg_strength, 2),
            total_content_analyzed=total_content,
            analysis_period_days=days_back
        )

    async def deactivate_old_trends(
        self,
        workspace_id: UUID,
        days_old: int = 7
    ) -> int:
        """
        Mark old trends as inactive.

        Args:
            workspace_id: Workspace ID
            days_old: Age threshold in days

        Returns:
            Number of trends deactivated
        """
        cutoff = datetime.now() - timedelta(days=days_old)
        return self.db.deactivate_old_trends(str(workspace_id), cutoff)
