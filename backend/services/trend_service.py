"""
Trend Detection Service

Detects emerging trends from content using topic clustering, velocity analysis,
and cross-source validation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from uuid import UUID
import numpy as np
import spacy
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
from backend.services.base_service import BaseService
from backend.utils.error_handling import handle_service_errors
from backend.config.constants import TrendConstants
from src.ai_newsletter.database.supabase_client import SupabaseManager


class TrendDetectionService(BaseService):
    """Service for detecting and analyzing trends from content."""

    def __init__(self, db: Optional[SupabaseManager] = None, min_confidence: float = None):
        super().__init__(db)
        self.min_confidence = min_confidence or TrendConstants.MIN_CONFIDENCE_THRESHOLD
        self.vectorizer = TfidfVectorizer(
            max_features=TrendConstants.TFIDF_MAX_FEATURES,
            stop_words='english',
            ngram_range=TrendConstants.TFIDF_NGRAM_RANGE,
            min_df=TrendConstants.TFIDF_MIN_DF
        )

        # Load spaCy for named entity recognition
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

    @handle_service_errors(default_return=([], {}), log_errors=True)
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

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if max_trends <= 0:
            raise ValueError("max_trends must be positive")

        if days_back <= 0 or days_back > 365:
            raise ValueError("days_back must be between 1 and 365")

        # Validate workspace_id UUID
        try:
            UUID(str(workspace_id))
        except ValueError as e:
            raise ValueError(f"Invalid workspace_id UUID: {e}")

        self.logger.info(f"Detecting trends for workspace {workspace_id}, days_back={days_back}")
        if min_confidence is None:
            min_confidence = self.min_confidence

        # Validate min_confidence after default assignment
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(f"min_confidence must be between 0.0 and 1.0, got {min_confidence}")

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

        # Get historical content for velocity calculation (30-day baseline)
        historical_cutoff = cutoff_date - timedelta(days=30)  # CHANGED: 30 days for better baseline
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

        # Stage 3.5: Merge similar topics (NEW)
        merged_topics = self._merge_similar_topics(validated_topics)

        # Stage 4: Score and rank
        scored_trends = self._score_trends(merged_topics)

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
        # Fetch from database using correct parameter names
        try:
            items = self.db.list_content_items(
                workspace_id=workspace_id,
                start_date=start_date,      # Pass datetime directly (not ISO string)
                end_date=end_date,           # Pass datetime directly (not ISO string)
                sources=sources,             # Pass list directly
                limit=1000                   # Analyze up to 1000 items
            )
            return items
        except Exception as e:
            self.logger.error(f"Error fetching content: {e}")
            return []

    def _extract_topics(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract topics using TF-IDF + K-means clustering + NER.

        Improvements:
        1. Named entity recognition for proper nouns
        2. N-gram based topic naming (prefer bigrams/trigrams)
        3. Recency boost for items in last 24 hours

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

            # K-means clustering
            n_clusters = min(10, max(3, len(items) // 10))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)

            # Extract topic keywords for each cluster
            topics = []
            feature_names = self.vectorizer.get_feature_names_out()

            for cluster_id in range(n_clusters):
                cluster_items = [items[i] for i in range(len(items)) if clusters[i] == cluster_id]
                cluster_texts = [texts[i] for i in range(len(items)) if clusters[i] == cluster_id]

                if len(cluster_items) < 2:
                    continue

                # Get top keywords for this cluster
                cluster_center = kmeans.cluster_centers_[cluster_id]
                top_indices = cluster_center.argsort()[-10:][::-1]
                keywords = [feature_names[i] for i in top_indices]

                # NEW: Extract named entities if spaCy available
                topic_name = self._extract_topic_name(cluster_texts, keywords)

                # NEW: Calculate recency boost
                recency_boost = self._calculate_recency_boost(cluster_items)

                topics.append({
                    'topic': topic_name,
                    'keywords': keywords[:5],
                    'items': cluster_items,
                    'cluster_id': cluster_id,
                    'recency_boost': recency_boost  # NEW
                })

            return topics

        except Exception as e:
            self.logger.error(f"Error in topic extraction: {e}")
            return []

    def _extract_topic_name(self, cluster_texts: List[str], keywords: List[str]) -> str:
        """
        Extract meaningful topic name using NER and n-grams.

        Priority:
        1. Named entities (ChatGPT, Atlas, etc.)
        2. Longest common n-gram from keywords
        3. Fallback to top keyword

        Args:
            cluster_texts: List of text strings from the cluster
            keywords: List of TF-IDF keywords for the cluster

        Returns:
            Topic name string
        """
        # VALIDATION: Handle empty keywords (edge case that causes crashes)
        if not keywords:
            self.logger.warning("Empty keywords list provided to _extract_topic_name, returning 'Unknown Topic'")
            return "Unknown Topic"

        if not self.nlp:
            # Fallback: Use longest n-gram from keywords
            ngrams = [kw for kw in keywords if ' ' in kw]
            if ngrams:
                return ngrams[0].replace('_', ' ').title()
            # Safe to access keywords[0] now (validated above)
            return keywords[0].replace('_', ' ').title()

        # Extract named entities from cluster texts
        entities = defaultdict(int)
        month_suffixes = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for text in cluster_texts:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['PRODUCT', 'ORG', 'EVENT', 'WORK_OF_ART']:
                    entity_text = ent.text.strip()

                    # Filter out poor entity names:
                    # 1. Too short (< 3 chars)
                    if len(entity_text) < 3:
                        continue

                    # 2. All uppercase acronyms (< 5 chars) - likely noise
                    if entity_text.isupper() and len(entity_text) < 5:
                        continue

                    # 3. Month-ending entities (CompanyJan, Company Oct, Company-Oct, etc.)
                    entity_lower = entity_text.lower()
                    skip_month = False
                    for month in month_suffixes:
                        month_lower = month.lower()
                        if (entity_lower.endswith(month_lower) or
                            entity_lower.endswith(f' {month_lower}') or
                            entity_lower.endswith(f'-{month_lower}') or
                            f'{month_lower} ' in entity_lower):  # "Oct 2025" patterns
                            skip_month = True
                            break

                    if skip_month:
                        continue

                    entities[entity_text] += 1

        # Boost entities that appear in top keywords (relevance weighting)
        # This ensures we pick entities related to the cluster's main topic
        if entities and keywords:
            for entity_text in list(entities.keys()):
                entity_lower = entity_text.lower()

                # Boost if entity matches or is substring of top 3 keywords
                for i, keyword in enumerate(keywords[:3]):
                    keyword_lower = keyword.lower()

                    # Exact match or entity is part of keyword
                    if entity_lower == keyword_lower or entity_lower in keyword_lower:
                        # Higher boost for top keywords (3x for #1, 2x for #2, 1.5x for #3)
                        boost = 3.0 - (i * 0.5)
                        entities[entity_text] = int(entities[entity_text] * boost)
                        break

                    # Keyword is part of entity (e.g., "chat" in "ChatGPT")
                    if keyword_lower in entity_lower and len(keyword_lower) >= 3:
                        boost = 2.0 - (i * 0.3)
                        entities[entity_text] = int(entities[entity_text] * boost)
                        break

        # Return most relevant named entity (now weighted by keyword relevance)
        if entities:
            top_entity = max(entities.items(), key=lambda x: x[1])[0]

            # Fix common casing issues
            casing_fixes = {
                'chatgpt': 'ChatGPT',
                'openai': 'OpenAI',
                'gpt': 'GPT',
                'api': 'API',
                'youtube': 'YouTube',
                'microsoft': 'Microsoft',
                'google': 'Google',
                'apple': 'Apple',
                'amazon': 'Amazon',
                'meta': 'Meta',
                'tesla': 'Tesla',
                'nvidia': 'NVIDIA',
                'amd': 'AMD',
            }

            entity_key = top_entity.lower()
            if entity_key in casing_fixes:
                top_entity = casing_fixes[entity_key]

            # Reject generic single words (fall back to n-grams instead)
            generic_words = {'ai', 'tech', 'new', 'latest', 'best', 'top', 'guide', 'review', 'news'}
            if top_entity.lower() in generic_words:
                # Fall through to n-gram fallback below
                pass
            else:
                return top_entity

        # Fallback to n-grams
        ngrams = [kw for kw in keywords if ' ' in kw]
        if ngrams:
            # Prefer longer n-grams
            longest_ngram = max(ngrams, key=lambda x: len(x.split()))
            return longest_ngram.replace('_', ' ').title()

        # Final fallback
        return keywords[0].replace('_', ' ').title()

    def _calculate_recency_boost(self, cluster_items: List[Dict[str, Any]]) -> float:
        """
        Calculate recency boost for topics mentioned in last 24 hours.

        Args:
            cluster_items: List of content items in the cluster

        Returns:
            Float between 0.0 and 0.3 (max 30% boost)
        """
        now = datetime.now()
        recent_threshold = now - timedelta(hours=24)

        recent_count = 0
        for item in cluster_items:
            created_at = item.get('created_at')
            if created_at:
                try:
                    item_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if item_time >= recent_threshold:
                        recent_count += 1
                except:
                    pass

        # Calculate boost: 0-30% based on percentage of recent items
        if len(cluster_items) == 0:
            return 0.0

        recent_percentage = recent_count / len(cluster_items)
        return min(recent_percentage * 0.3, 0.3)  # Cap at 30%

    def _merge_similar_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge topics with >50% keyword overlap.

        Example: "Ai" and "Chatgpt" both have keywords ["atlas", "opened"]
        → Merge into single topic "ChatGPT Atlas"

        Args:
            topics: List of topic dictionaries

        Returns:
            Deduplicated list of topics
        """
        if len(topics) <= 1:
            return topics

        merged = []
        used = set()

        for i, topic1 in enumerate(topics):
            if i in used:
                continue

            kw1 = set(topic1['keywords'])
            merged_topic = topic1.copy()

            # Find similar topics to merge
            for j, topic2 in enumerate(topics[i+1:], start=i+1):
                if j in used:
                    continue

                # Fallback 1: Merge topics with exact same name (case-insensitive)
                if topic1['topic'].lower().strip() == topic2['topic'].lower().strip():
                    self.logger.debug(
                        f"Merging topics by name: '{topic1['topic']}' + '{topic2['topic']}' (exact name match)"
                    )

                    kw2 = set(topic2['keywords'])

                    # Merge topic2 into topic1
                    merged_topic['items'].extend(topic2['items'])
                    merged_topic['keywords'] = list(set(topic1['keywords']) | kw2)[:5]
                    merged_topic['mention_count'] += topic2['mention_count']
                    merged_topic['sources'] = list(set(merged_topic['sources'] + topic2['sources']))
                    merged_topic['source_count'] = len(merged_topic['sources'])

                    # Use topic name from higher velocity topic
                    if topic2.get('velocity', 0) > topic1.get('velocity', 0):
                        merged_topic['topic'] = topic2['topic']

                    used.add(j)
                    continue  # Skip keyword overlap check

                # Fallback 2: Merge topics with high keyword overlap
                kw2 = set(topic2['keywords'])
                overlap = len(kw1 & kw2) / len(kw1 | kw2)  # Jaccard similarity
                shared_keywords = kw1 & kw2

                # Use configurable thresholds from constants
                if (overlap >= TrendConstants.TOPIC_MERGE_SIMILARITY_THRESHOLD and
                    len(shared_keywords) >= TrendConstants.TOPIC_MERGE_MIN_KEYWORD_OVERLAP):
                    # Log merge decision for debugging
                    self.logger.debug(
                        f"Merging topics by keywords: '{topic1['topic']}' + '{topic2['topic']}' "
                        f"(overlap={overlap:.2f}, shared_kw={len(shared_keywords)}, threshold={TrendConstants.TOPIC_MERGE_SIMILARITY_THRESHOLD})"
                    )

                    # Merge topic2 into topic1
                    merged_topic['items'].extend(topic2['items'])
                    merged_topic['keywords'] = list(kw1 | kw2)[:5]  # Union of keywords
                    merged_topic['mention_count'] += topic2['mention_count']
                    merged_topic['sources'] = list(set(merged_topic['sources'] + topic2['sources']))
                    merged_topic['source_count'] = len(merged_topic['sources'])

                    # Use topic name from higher velocity topic
                    if topic2.get('velocity', 0) > topic1.get('velocity', 0):
                        merged_topic['topic'] = topic2['topic']

                    used.add(j)

            merged.append(merged_topic)
            used.add(i)

        return merged

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

        Weights:
        - Velocity: 60% (spikes matter most)
        - Mentions: 20% (volume matters less)
        - Sources: 20% (diversity still important)
        + Recency boost: up to 30% extra

        Args:
            topics: Topics to score

        Returns:
            Scored topics sorted by strength
        """
        for topic in topics:
            score = 0.0

            # Factor 1: Mention count (20% weight) - REDUCED
            mention_score = min(topic['mention_count'] / 20, 1.0)
            score += mention_score * TrendConstants.MENTION_SCORE_WEIGHT  # 0.2

            # Factor 2: Velocity (60% weight) - INCREASED
            velocity_score = min(topic.get('velocity', 0) / 100.0, 1.0)
            score += velocity_score * TrendConstants.VELOCITY_SCORE_WEIGHT  # 0.6

            # Factor 3: Source diversity (20% weight) - REDUCED
            source_score = min(topic['source_count'] / 4, 1.0)
            score += source_score * TrendConstants.SOURCE_DIVERSITY_WEIGHT  # 0.2

            # Factor 4: Recency boost (up to 30% extra) - NEW
            recency_boost = topic.get('recency_boost', 0.0)
            score += recency_boost

            # Cap total score at 1.0
            score = min(score, 1.0)

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

    @handle_service_errors(default_return=[], log_errors=True)
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
        self.logger.debug(f"Fetching active trends for workspace {workspace_id}, limit={limit}")
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
