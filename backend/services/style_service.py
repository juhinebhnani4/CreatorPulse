"""
Style Analysis Service

Analyzes newsletter samples to extract writing style patterns and generates
style-specific prompts for AI newsletter generation.
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from uuid import UUID
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import textstat
from backend.models.style_profile import (
    StyleProfileCreate,
    StyleProfileResponse,
    StyleProfileUpdate,
    GeneratePromptResponse,
    StyleProfileSummary
)
from backend.services.base_service import BaseService
from backend.utils.error_handling import handle_service_errors
from src.ai_newsletter.database.supabase_client import SupabaseManager


# Download required NLTK data on first import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class StyleAnalysisService(BaseService):
    """Service for analyzing writing style from newsletter samples."""

    def __init__(self, db: Optional[SupabaseManager] = None):
        super().__init__(db)
        self.stopwords = set(stopwords.words('english'))

    def analyze_samples(
        self,
        samples: List[str],
        workspace_id: UUID
    ) -> Tuple[StyleProfileCreate, Dict[str, Any]]:
        """
        Analyze newsletter samples to extract writing style.

        Args:
            samples: List of newsletter text samples
            workspace_id: Workspace to associate profile with

        Returns:
            Tuple of (StyleProfileCreate, analysis_summary)
        """
        # Combine all samples
        combined_text = "\n\n".join(samples)

        # Analyze different aspects
        sentences = self._analyze_sentences(combined_text)
        vocabulary = self._analyze_vocabulary(combined_text)
        tone_info = self._analyze_tone(combined_text)
        structure = self._analyze_structure(samples)
        examples = self._extract_examples(samples)

        # Build style profile
        profile = StyleProfileCreate(
            workspace_id=workspace_id,
            tone=tone_info['tone'],
            formality_level=tone_info['formality'],
            avg_sentence_length=sentences['avg_length'],
            sentence_length_variety=sentences['std_dev'],
            question_frequency=sentences['question_freq'],
            vocabulary_level=vocabulary['level'],
            favorite_phrases=vocabulary['common_phrases'][:10],
            avoided_words=vocabulary['rare_words'][:10],
            typical_intro_style=structure['intro_style'],
            section_count=structure['avg_sections'],
            uses_emojis=structure['uses_emojis'],
            emoji_frequency=structure['emoji_freq'],
            example_intros=examples['intros'][:3],
            example_transitions=examples['transitions'][:3],
            example_conclusions=examples['conclusions'][:3],
            trained_on_count=len(samples),
            training_samples=samples
        )

        # Build analysis summary
        summary = {
            "samples_analyzed": len(samples),
            "total_words": vocabulary['total_words'],
            "total_sentences": sentences['total_count'],
            "avg_words_per_sample": vocabulary['total_words'] / len(samples),
            "detected_tone": tone_info['tone'],
            "confidence_score": tone_info['confidence'],
            "readability_score": vocabulary['readability'],
            "unique_words": vocabulary['unique_words']
        }

        return profile, summary

    def _analyze_sentences(self, text: str) -> Dict[str, Any]:
        """Analyze sentence-level patterns."""
        sentences = sent_tokenize(text)

        if not sentences:
            return {
                'total_count': 0,
                'avg_length': 15.0,
                'std_dev': 5.0,
                'question_freq': 0.0
            }

        # Calculate sentence lengths
        lengths = []
        question_count = 0

        for sent in sentences:
            words = word_tokenize(sent)
            lengths.append(len(words))

            if '?' in sent:
                question_count += 1

        avg_length = sum(lengths) / len(lengths) if lengths else 15.0
        std_dev = (sum((x - avg_length) ** 2 for x in lengths) / len(lengths)) ** 0.5 if len(lengths) > 1 else 5.0
        question_freq = question_count / len(sentences) if sentences else 0.0

        return {
            'total_count': len(sentences),
            'avg_length': round(avg_length, 2),
            'std_dev': round(std_dev, 2),
            'question_freq': round(question_freq, 3)
        }

    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary patterns."""
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum()]

        if not words:
            return {
                'total_words': 0,
                'unique_words': 0,
                'level': 'intermediate',
                'common_phrases': [],
                'rare_words': [],
                'readability': 60.0
            }

        # Calculate metrics
        unique_words = len(set(words))
        lexical_diversity = unique_words / len(words) if words else 0.5

        # Extract common phrases (bigrams and trigrams)
        common_phrases = self._extract_common_phrases(text)

        # Get readability score
        readability = textstat.flesch_reading_ease(text)

        # Determine vocabulary level based on readability
        if readability >= 80:
            level = "simple"
        elif readability >= 60:
            level = "intermediate"
        else:
            level = "advanced"

        # Find avoided words (very rare technical terms)
        word_freq = Counter(words)
        rare_words = [
            word for word, count in word_freq.items()
            if count == 1 and len(word) > 8 and word not in self.stopwords
        ][:10]

        return {
            'total_words': len(words),
            'unique_words': unique_words,
            'lexical_diversity': round(lexical_diversity, 3),
            'level': level,
            'common_phrases': common_phrases,
            'rare_words': rare_words,
            'readability': round(readability, 1)
        }

    def _extract_common_phrases(self, text: str) -> List[str]:
        """Extract frequently used phrases (2-3 word combinations)."""
        # Simple phrase extraction using regex
        phrases = []

        # Look for common phrase patterns
        patterns = [
            r"here'?s? (the|a) \w+",
            r"let'?s? \w+ \w+",
            r"(you|we) (can|could|should|must) \w+",
            r"\w+ \w+ (is|are) \w+",
            r"in (this|the) \w+"
        ]

        text_lower = text.lower()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            phrases.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])

        # Count and return top phrases
        phrase_counts = Counter(phrases)
        return [phrase for phrase, _ in phrase_counts.most_common(10)]

    def _analyze_tone(self, text: str) -> Dict[str, Any]:
        """Detect tone and formality."""
        text_lower = text.lower()

        # Count indicators
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        exclamations = text.count('!')
        emojis = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text))
        personal_pronouns = len(re.findall(r'\b(i|you|we|my|your|our)\b', text_lower))

        # Calculate formality (0.0 = casual, 1.0 = formal)
        words = word_tokenize(text)
        word_count = len(words)

        if word_count == 0:
            return {
                'tone': 'professional',
                'formality': 0.5,
                'confidence': 0.5
            }

        contraction_rate = contractions / word_count if word_count > 0 else 0
        personal_rate = personal_pronouns / word_count if word_count > 0 else 0
        exclamation_rate = exclamations / word_count if word_count > 0 else 0

        # Higher = more formal
        formality = 1.0 - (contraction_rate * 2 + personal_rate + exclamation_rate)
        formality = max(0.0, min(1.0, formality))

        # Determine tone
        if formality < 0.3:
            tone = "conversational"
        elif formality > 0.7:
            tone = "authoritative"
        elif exclamation_rate > 0.01 or emojis > 5:
            tone = "humorous"
        else:
            tone = "professional"

        # Confidence based on text length
        confidence = min(0.95, 0.5 + (word_count / 10000))

        return {
            'tone': tone,
            'formality': round(formality, 2),
            'confidence': round(confidence, 2)
        }

    def _analyze_structure(self, samples: List[str]) -> Dict[str, Any]:
        """Analyze structural patterns."""
        total_sections = 0
        emoji_count = 0
        total_chars = 0

        intro_styles = []

        for sample in samples:
            # Count sections (headers with #, ##, or blank lines)
            sections = len(re.findall(r'\n\n', sample)) + len(re.findall(r'^#{1,3}\s', sample, re.MULTILINE))
            total_sections += max(1, sections)

            # Count emojis
            emoji_count += len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', sample))
            total_chars += len(sample)

            # Detect intro style (first sentence)
            sentences = sent_tokenize(sample)
            if sentences:
                first = sentences[0].strip()
                if first.endswith('?'):
                    intro_styles.append('question')
                elif any(word in first.lower() for word in ['once', 'story', 'imagine']):
                    intro_styles.append('anecdote')
                elif any(char.isdigit() for char in first):
                    intro_styles.append('statistic')
                else:
                    intro_styles.append('statement')

        avg_sections = round(total_sections / len(samples)) if samples else 4
        uses_emojis = emoji_count > 0
        emoji_freq = emoji_count / total_chars if total_chars > 0 else 0.0

        # Most common intro style
        intro_counter = Counter(intro_styles)
        intro_style = intro_counter.most_common(1)[0][0] if intro_counter else 'statement'

        return {
            'avg_sections': avg_sections,
            'uses_emojis': uses_emojis,
            'emoji_freq': round(emoji_freq, 3),
            'intro_style': intro_style
        }

    def _extract_examples(self, samples: List[str]) -> Dict[str, List[str]]:
        """Extract example sentences for few-shot learning."""
        intros = []
        transitions = []
        conclusions = []

        transition_words = ['however', 'moreover', 'furthermore', 'meanwhile', 'now', 'but', 'yet']

        for sample in samples:
            sentences = sent_tokenize(sample)

            if not sentences:
                continue

            # First sentence as intro
            intros.append(sentences[0].strip())

            # Last sentence as conclusion
            conclusions.append(sentences[-1].strip())

            # Find transitions
            for sent in sentences[1:-1]:  # Skip first and last
                sent_lower = sent.lower()
                if any(word in sent_lower.split()[:3] for word in transition_words):
                    transitions.append(sent.strip())

        return {
            'intros': intros[:5],  # Top 5 unique intros
            'transitions': transitions[:5],
            'conclusions': conclusions[:5]
        }

    def generate_style_prompt(self, profile: StyleProfileResponse) -> str:
        """
        Generate style-specific prompt for AI newsletter generation.

        Args:
            profile: Style profile to convert to prompt

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "Write in this specific style:",
            f"- Tone: {profile.tone} ({profile.formality_level:.0%} formal)",
            f"- Average sentence length: {profile.avg_sentence_length} words",
            f"- Question frequency: Include questions {profile.question_frequency:.0%} of the time"
        ]

        if profile.favorite_phrases:
            phrases = ", ".join(f'"{p}"' for p in profile.favorite_phrases[:3])
            prompt_parts.append(f"- Use these characteristic phrases: {phrases}")

        if profile.avoided_words:
            words = ", ".join(profile.avoided_words[:5])
            prompt_parts.append(f"- Avoid these words: {words}")

        prompt_parts.append(f"- Intro style: {profile.typical_intro_style}")

        if profile.uses_emojis:
            prompt_parts.append(f"- Include emojis occasionally (about {profile.emoji_frequency:.0%} of content)")
        else:
            prompt_parts.append("- Do not use emojis")

        # Add examples
        if profile.example_intros:
            prompt_parts.append(f"\nExample intro: \"{profile.example_intros[0]}\"")

        if profile.example_transitions:
            prompt_parts.append(f"Example transition: \"{profile.example_transitions[0]}\"")

        return "\n".join(prompt_parts)

    @handle_service_errors(default_return=None, log_errors=True)
    async def get_style_profile(self, workspace_id: UUID) -> Optional[StyleProfileResponse]:
        """
        Get style profile for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            StyleProfileResponse or None if not found
        """
        self.logger.debug(f"Fetching style profile for workspace {workspace_id}")
        profile_data = self.db.get_style_profile(str(workspace_id))

        if not profile_data:
            self.logger.info(f"No style profile found for workspace {workspace_id}")
            return None

        return StyleProfileResponse(**profile_data)

    async def get_style_summary(self, workspace_id: UUID) -> StyleProfileSummary:
        """
        Get style profile summary for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            StyleProfileSummary
        """
        summary_data = self.db.get_style_profile_summary(str(workspace_id))

        if not summary_data:
            return StyleProfileSummary(has_profile=False)

        return StyleProfileSummary(**summary_data)

    @handle_service_errors(raise_on_error=True, log_errors=True)
    async def create_or_update_profile(
        self,
        workspace_id: UUID,
        profile_data: StyleProfileCreate,
        retrain: bool = False
    ) -> StyleProfileResponse:
        """
        Create or update style profile.

        Args:
            workspace_id: Workspace ID
            profile_data: Style profile data
            retrain: Whether to overwrite existing profile

        Returns:
            StyleProfileResponse

        Raises:
            ValueError: If profile exists and retrain=False
        """
        self.logger.info(f"Creating/updating style profile for workspace {workspace_id}, retrain={retrain}")

        # Check if profile exists
        existing = await self.get_style_profile(workspace_id)

        if existing and not retrain:
            raise ValueError("Style profile already exists. Set retrain=True to overwrite.")

        if existing:
            # Update existing
            self.logger.info(f"Updating existing style profile for workspace {workspace_id}")
            result = self.db.update_style_profile(
                str(workspace_id),
                profile_data.model_dump(exclude={'workspace_id', 'training_samples'})
            )
        else:
            # Create new
            self.logger.info(f"Creating new style profile for workspace {workspace_id}")
            result = self.db.create_style_profile(profile_data.model_dump(mode='json'))

        return StyleProfileResponse(**result)

    async def delete_profile(self, workspace_id: UUID) -> bool:
        """
        Delete style profile for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted
        """
        return self.db.delete_style_profile(str(workspace_id))
