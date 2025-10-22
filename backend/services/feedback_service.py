"""
Feedback Service for learning from user preferences.

This service handles:
- Recording and managing feedback
- Calculating source quality scores
- Extracting content preferences from patterns
- Adjusting content scoring based on learned preferences
- Providing analytics and recommendations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from collections import defaultdict, Counter

from backend.services.base_service import BaseService
from backend.utils.error_handling import handle_service_errors
from backend.config.constants import FeedbackConstants
from src.ai_newsletter.database.supabase_client import SupabaseManager


class FeedbackService(BaseService):
    """
    Service for managing feedback and learning from user preferences.

    This service implements learning algorithms that:
    1. Track user feedback on content items and newsletters
    2. Calculate source quality scores from feedback patterns
    3. Extract content preferences (preferred sources, topics, etc.)
    4. Adjust content scoring to prioritize high-quality sources
    5. Provide analytics and recommendations
    """

    def __init__(self, db: Optional[SupabaseManager] = None):
        """
        Initialize feedback service.

        Args:
            db: Optional Supabase manager instance
        """
        super().__init__(db)

    # =========================================================================
    # FEEDBACK RECORDING
    # =========================================================================

    def record_item_feedback(
        self,
        workspace_id: str,
        user_id: str,
        content_item_id: str,
        rating: str,
        included_in_final: bool = False,
        newsletter_id: Optional[str] = None,
        original_summary: Optional[str] = None,
        edited_summary: Optional[str] = None,
        feedback_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record feedback on a content item.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            content_item_id: Content item ID
            rating: Feedback rating (positive, negative, neutral)
            included_in_final: Whether item was included in final newsletter
            newsletter_id: Optional newsletter ID
            original_summary: Original summary text
            edited_summary: Edited summary text
            feedback_notes: Optional notes

        Returns:
            Created feedback data
        """
        # Calculate edit distance if both summaries provided
        edit_distance = 0.0
        if original_summary and edited_summary:
            edit_distance = self._calculate_edit_distance(original_summary, edited_summary)

        feedback_data = {
            'workspace_id': workspace_id,
            'user_id': user_id,
            'content_item_id': content_item_id,
            'rating': rating,
            'included_in_final': included_in_final,
            'newsletter_id': newsletter_id,
            'original_summary': original_summary,
            'edited_summary': edited_summary,
            'edit_distance': edit_distance,
            'feedback_notes': feedback_notes
        }

        feedback = self.db.create_feedback_item(feedback_data)

        # Trigger source quality recalculation (async in background)
        # This is handled by database trigger automatically

        return feedback

    def record_newsletter_feedback(
        self,
        workspace_id: str,
        user_id: str,
        newsletter_id: str,
        overall_rating: Optional[int] = None,
        time_to_finalize_minutes: Optional[int] = None,
        items_added: int = 0,
        items_removed: int = 0,
        items_edited: int = 0,
        notes: Optional[str] = None,
        would_recommend: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Record feedback on a newsletter.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            newsletter_id: Newsletter ID
            overall_rating: Rating 1-5
            time_to_finalize_minutes: Time spent finalizing
            items_added: Number of items added
            items_removed: Number of items removed
            items_edited: Number of items edited
            notes: Optional notes
            would_recommend: Whether user would recommend

        Returns:
            Created feedback data
        """
        # Calculate draft acceptance rate
        total_changes = items_added + items_removed + items_edited
        draft_acceptance_rate = max(0.0, 1.0 - (total_changes * 0.1))

        feedback_data = {
            'workspace_id': workspace_id,
            'user_id': user_id,
            'newsletter_id': newsletter_id,
            'overall_rating': overall_rating,
            'time_to_finalize_minutes': time_to_finalize_minutes,
            'items_added': items_added,
            'items_removed': items_removed,
            'items_edited': items_edited,
            'notes': notes,
            'would_recommend': would_recommend,
            'draft_acceptance_rate': draft_acceptance_rate
        }

        feedback = self.db.create_newsletter_feedback(feedback_data)

        return feedback

    # =========================================================================
    # SOURCE QUALITY SCORING
    # =========================================================================

    def get_source_quality_scores(
        self,
        workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get source quality scores for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of source quality scores
        """
        scores = self.db.get_source_quality_scores(workspace_id)

        # Add derived metrics
        for score in scores:
            total = score.get('total_feedback_count', 0)
            if total > 0:
                score['positive_rate'] = score.get('positive_count', 0) / total
                score['negative_rate'] = score.get('negative_count', 0) / total
            else:
                score['positive_rate'] = 0.0
                score['negative_rate'] = 0.0

            # Quality label
            quality = score.get('quality_score', 0.5)
            if quality >= 0.75:
                score['quality_label'] = 'Excellent'
            elif quality >= 0.6:
                score['quality_label'] = 'Good'
            elif quality >= 0.4:
                score['quality_label'] = 'Average'
            else:
                score['quality_label'] = 'Poor'

        return scores

    def recalculate_source_quality(
        self,
        workspace_id: str
    ) -> int:
        """
        Recalculate source quality scores from feedback.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of sources recalculated
        """
        return self.db.recalculate_source_quality(workspace_id)

    # =========================================================================
    # CONTENT PREFERENCES
    # =========================================================================

    def get_content_preferences(
        self,
        workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get content preferences for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Content preferences or None
        """
        preferences = self.db.get_content_preferences(workspace_id)

        if preferences:
            # Add confidence label
            confidence = preferences.get('confidence_level', 0.0)
            if confidence >= 0.8:
                preferences['confidence_label'] = 'High'
            elif confidence >= 0.5:
                preferences['confidence_label'] = 'Medium'
            else:
                preferences['confidence_label'] = 'Low'

            # Check if reliable
            preferences['is_reliable'] = preferences.get('total_feedback_count', 0) >= 10

        return preferences

    def extract_content_preferences(
        self,
        workspace_id: str
    ) -> Optional[str]:
        """
        Extract content preferences from feedback patterns.

        Args:
            workspace_id: Workspace ID

        Returns:
            Preferences ID or None
        """
        return self.db.extract_content_preferences(workspace_id)

    # =========================================================================
    # CONTENT SCORING ADJUSTMENT
    # =========================================================================

    @handle_service_errors(default_return=[], log_errors=True)
    def adjust_content_scoring(
        self,
        workspace_id: str,
        content_items: List[Any],  # Can be ContentItem objects or dicts
        apply_source_quality: bool = True,
        apply_preferences: bool = True
    ) -> List[Dict[str, Any]]:  # Always returns list of dicts
        """
        Adjust content item scores based on learned preferences.

        This method accepts both ContentItem dataclass objects and dictionaries,
        and ALWAYS returns a list of dictionaries with adjusted scores.

        Args:
            workspace_id: Workspace ID
            content_items: List of content items (ContentItem objects or dicts)
            apply_source_quality: Whether to apply source quality scores
            apply_preferences: Whether to apply learned preferences

        Returns:
            List of content items as dictionaries with adjusted scores
            Each dict includes:
            - All original fields
            - 'original_score': The score before adjustments
            - 'adjusted_score': The score after adjustments
            - 'score': The final score (same as adjusted_score)
            - 'adjustments': List of adjustment descriptions
        """
        self.logger.info(f"Adjusting content scoring for workspace {workspace_id}, {len(content_items)} items")
        adjusted_items = []
        adjustments_made = 0
        quality_scores_applied = {}

        # Convert ContentItem objects to dicts if needed
        items_as_dicts = []
        for item in content_items:
            if hasattr(item, 'to_dict'):
                # It's a ContentItem object
                items_as_dicts.append(item.to_dict())
            elif isinstance(item, dict):
                # Already a dict
                items_as_dicts.append(item)
            else:
                # Unknown type - convert to dict manually
                items_as_dicts.append(dict(item))

        # Get source quality scores
        source_scores = {}
        if apply_source_quality:
            scores = self.get_source_quality_scores(workspace_id)
            source_scores = {s['source_name']: s['quality_score'] for s in scores}

        # Get content preferences
        preferences = None
        if apply_preferences:
            preferences = self.get_content_preferences(workspace_id)

        # Adjust each item
        for item in items_as_dicts:
            original_score = item.get('score', 0)
            adjusted_score = original_score
            adjustments = []

            source = item.get('source', '')

            # Apply source quality multiplier
            if apply_source_quality and source in source_scores:
                quality_score = source_scores[source]
                adjusted_score = int(adjusted_score * quality_score)
                adjustments.append(f"source_quality:{quality_score:.2f}")
                quality_scores_applied[source] = quality_score
                adjustments_made += 1

            # Apply preferences boost
            if apply_preferences and preferences:
                preferred_sources = preferences.get('preferred_sources', [])
                if source in preferred_sources:
                    # Boost by configured multiplier for preferred sources
                    adjusted_score = int(adjusted_score * FeedbackConstants.PREFERRED_SOURCE_BOOST_MULTIPLIER)
                    boost_pct = (FeedbackConstants.PREFERRED_SOURCE_BOOST_MULTIPLIER - 1) * 100
                    adjustments.append(f"preferred_source:+{boost_pct:.0f}%")
                    adjustments_made += 1

                # Check score thresholds
                min_threshold = preferences.get('min_score_threshold', 0)
                if original_score < min_threshold:
                    # Reduce score by configured penalty if below minimum preference
                    adjusted_score = int(adjusted_score * FeedbackConstants.BELOW_THRESHOLD_PENALTY_MULTIPLIER)
                    penalty_pct = (1 - FeedbackConstants.BELOW_THRESHOLD_PENALTY_MULTIPLIER) * 100
                    adjustments.append(f"below_threshold:-{penalty_pct:.0f}%")
                    adjustments_made += 1

            # Update item with adjusted score
            item['original_score'] = original_score
            item['adjusted_score'] = adjusted_score
            item['score'] = adjusted_score
            item['adjustments'] = adjustments

            adjusted_items.append(item)

        return adjusted_items

    # =========================================================================
    # ANALYTICS & INSIGHTS
    # =========================================================================

    def get_feedback_analytics(
        self,
        workspace_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive feedback analytics.

        Args:
            workspace_id: Workspace ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Analytics summary with metrics and insights
        """
        # Get raw analytics from database
        analytics = self.db.get_feedback_analytics(workspace_id, start_date, end_date)

        # Calculate derived metrics
        total_feedback = analytics.get('total_feedback_items', 0)
        if total_feedback > 0:
            positive = analytics.get('positive_count', 0)
            negative = analytics.get('negative_count', 0)

            analytics['positive_rate'] = positive / total_feedback
            analytics['negative_rate'] = negative / total_feedback
        else:
            analytics['positive_rate'] = 0.0
            analytics['negative_rate'] = 0.0

        # Add recommendations
        analytics['recommendations'] = self._generate_recommendations(analytics)

        # Get source quality scores
        source_scores = self.get_source_quality_scores(workspace_id)

        # Top and worst sources
        analytics['top_sources'] = source_scores[:5]
        analytics['worst_sources'] = [s for s in source_scores if s['quality_score'] < 0.4][:3]
        analytics['total_sources_tracked'] = len(source_scores)

        # Get preferences confidence
        preferences = self.get_content_preferences(workspace_id)
        if preferences:
            analytics['preferences_confidence'] = preferences.get('confidence_level', 0.0)
        else:
            analytics['preferences_confidence'] = 0.0

        return analytics

    def get_learning_summary(
        self,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get a summary of learning status for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Learning summary with status and metrics
        """
        # Get feedback counts
        feedback_items = self.db.list_feedback_items(workspace_id, limit=1000)
        total_feedback = len(feedback_items)

        # Get source scores
        source_scores = self.get_source_quality_scores(workspace_id)
        sources_with_data = len(source_scores)

        # Get preferences
        preferences = self.get_content_preferences(workspace_id)
        preferences_extracted = preferences is not None
        preferences_confidence = preferences.get('confidence_level', 0.0) if preferences else 0.0

        # Learning status
        if total_feedback == 0:
            learning_status = "No data"
            status_label = "error"
        elif total_feedback < 10:
            learning_status = "Collecting data"
            status_label = "warning"
        elif preferences_confidence < 0.5:
            learning_status = "Learning"
            status_label = "info"
        elif preferences_confidence < 0.8:
            learning_status = "Confident"
            status_label = "success"
        else:
            learning_status = "Highly confident"
            status_label = "success"

        return {
            'total_feedback_items': total_feedback,
            'sources_tracked': sources_with_data,
            'preferences_extracted': preferences_extracted,
            'preferences_confidence': preferences_confidence,
            'learning_status': learning_status,
            'status_label': status_label,
            'recommendations': self._get_learning_recommendations(
                total_feedback,
                sources_with_data,
                preferences_confidence
            )
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _calculate_edit_distance(
        self,
        original: str,
        edited: str
    ) -> float:
        """
        Calculate normalized edit distance between two strings.

        Uses simple character-level Levenshtein distance.

        Args:
            original: Original text
            edited: Edited text

        Returns:
            Distance from 0.0 (identical) to 1.0 (completely different)
        """
        if not original or not edited:
            return 0.0

        # Simple character-level distance
        len1, len2 = len(original), len(edited)

        # Create distance matrix
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize first row and column
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j

        # Fill matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if original[i-1] == edited[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )

        # Normalize by max length
        max_len = max(len1, len2)
        return dp[len1][len2] / max_len if max_len > 0 else 0.0

    def _generate_recommendations(
        self,
        analytics: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on analytics.

        Args:
            analytics: Analytics data

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check feedback volume
        total_feedback = analytics.get('total_feedback_items', 0)
        if total_feedback < 10:
            recommendations.append(
                f"Provide more feedback to improve learning (currently {total_feedback}/10 minimum)"
            )

        # Check negative rate
        negative_rate = analytics.get('negative_rate', 0.0)
        if negative_rate > 0.3:
            recommendations.append(
                f"High negative feedback rate ({negative_rate:.0%}). Consider adjusting content sources."
            )

        # Check inclusion rate
        inclusion_rate = analytics.get('inclusion_rate', 0.0)
        if inclusion_rate < 0.5:
            recommendations.append(
                f"Low inclusion rate ({inclusion_rate:.0%}). Content quality may need improvement."
            )

        # Check time to finalize
        avg_time = analytics.get('avg_time_to_finalize', 0)
        if avg_time and avg_time > 30:
            recommendations.append(
                f"Average time to finalize is {avg_time:.0f} minutes. Consider training writing style."
            )

        # Check newsletter rating
        avg_rating = analytics.get('avg_newsletter_rating', 0)
        if avg_rating and avg_rating < 3:
            recommendations.append(
                f"Low newsletter rating ({avg_rating:.1f}/5). Review content selection and generation."
            )

        # Check source diversity
        top_sources = analytics.get('top_sources', [])
        if len(top_sources) < 3:
            recommendations.append(
                "Add more content sources for better diversity."
            )

        return recommendations

    def _get_learning_recommendations(
        self,
        total_feedback: int,
        sources_tracked: int,
        confidence: float
    ) -> List[str]:
        """
        Get recommendations for improving learning.

        Args:
            total_feedback: Total feedback items
            sources_tracked: Number of sources with data
            confidence: Confidence level

        Returns:
            List of recommendations
        """
        recommendations = []

        if total_feedback < 10:
            recommendations.append(
                "Rate more content items to build a learning baseline (10+ recommended)"
            )

        if total_feedback < 50 and confidence < 0.8:
            recommendations.append(
                "Continue providing feedback to increase confidence in preferences"
            )

        if sources_tracked < 3:
            recommendations.append(
                "Add more content sources to improve learning diversity"
            )

        if confidence >= 0.8:
            recommendations.append(
                "Learning confidence is high. System will optimize content selection automatically."
            )

        return recommendations
