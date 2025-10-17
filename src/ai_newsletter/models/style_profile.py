"""
Style profile model for voice and tone analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class StyleProfile:
    """
    Represents a user's writing style profile.

    This is used to train the AI to match the user's tone,
    vocabulary, and structural preferences in generated content.
    """

    # Voice characteristics
    tone: str = "professional"  # e.g., "professional", "casual", "enthusiastic"
    formality_level: float = 0.7  # 0 = very casual, 1 = very formal

    # Sentence patterns
    avg_sentence_length: float = 15.0
    sentence_length_variety: float = 0.5  # 0 = uniform, 1 = highly varied
    question_frequency: float = 0.1  # % of sentences that are questions

    # Vocabulary
    vocabulary_level: str = "intermediate"  # "simple", "intermediate", "advanced"
    favorite_phrases: List[str] = field(default_factory=list)
    avoided_words: List[str] = field(default_factory=list)

    # Structure
    typical_intro_style: str = "statement"  # "question", "statement", "hook"
    section_count: int = 3  # Typical number of sections
    uses_emojis: bool = False
    emoji_frequency: float = 0.0  # Emojis per sentence

    # Examples
    example_intros: List[str] = field(default_factory=list)
    example_transitions: List[str] = field(default_factory=list)
    example_conclusions: List[str] = field(default_factory=list)

    # Metadata
    trained_on_count: int = 0  # Number of examples used for training
    last_updated: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'tone': self.tone,
            'formality_level': self.formality_level,
            'avg_sentence_length': self.avg_sentence_length,
            'sentence_length_variety': self.sentence_length_variety,
            'question_frequency': self.question_frequency,
            'vocabulary_level': self.vocabulary_level,
            'favorite_phrases': self.favorite_phrases,
            'avoided_words': self.avoided_words,
            'typical_intro_style': self.typical_intro_style,
            'section_count': self.section_count,
            'uses_emojis': self.uses_emojis,
            'emoji_frequency': self.emoji_frequency,
            'example_intros': self.example_intros,
            'example_transitions': self.example_transitions,
            'example_conclusions': self.example_conclusions,
            'trained_on_count': self.trained_on_count,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StyleProfile':
        """Create from dictionary."""
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

    def get_style_prompt(self) -> str:
        """Generate a prompt describing this style for AI."""
        return f"""Write in a {self.tone} tone with {self.formality_level:.0%} formality.

Average sentence length: {self.avg_sentence_length:.0f} words.
Vocabulary level: {self.vocabulary_level}.
Introduction style: {self.typical_intro_style}.
{'Use emojis occasionally.' if self.uses_emojis else 'Do not use emojis.'}

{f'Favorite phrases to incorporate: {", ".join(self.favorite_phrases[:5])}' if self.favorite_phrases else ''}
{f'Words to avoid: {", ".join(self.avoided_words[:5])}' if self.avoided_words else ''}
"""
