"""
Style Profile Models

Pydantic models for writing style profiles that enable AI to match user's voice.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class StyleProfileBase(BaseModel):
    """Base style profile attributes."""

    tone: str = Field(
        default="professional",
        description="Writing tone (conversational, authoritative, humorous, professional)",
        examples=["conversational", "authoritative", "humorous", "professional"]
    )
    formality_level: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Formality level from 0.0 (casual) to 1.0 (formal)",
        examples=[0.35, 0.65]
    )
    avg_sentence_length: Optional[float] = Field(
        default=15.0,
        description="Average sentence length in words",
        examples=[12.5, 18.3]
    )
    sentence_length_variety: Optional[float] = Field(
        default=5.0,
        description="Sentence length standard deviation",
        examples=[4.2, 6.5]
    )
    question_frequency: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Frequency of questions (0.0 to 1.0)",
        examples=[0.08, 0.15]
    )
    vocabulary_level: str = Field(
        default="intermediate",
        description="Vocabulary sophistication (simple, intermediate, advanced)",
        examples=["simple", "intermediate", "advanced"]
    )
    favorite_phrases: List[str] = Field(
        default_factory=list,
        description="Frequently used phrases",
        examples=[["Here's the thing", "Let's dive in"]]
    )
    avoided_words: List[str] = Field(
        default_factory=list,
        description="Words user avoids",
        examples=[["synergy", "leverage", "utilize"]]
    )
    typical_intro_style: str = Field(
        default="question",
        description="Typical intro style (question, statement, anecdote, statistic)",
        examples=["question", "statement", "anecdote"]
    )
    section_count: int = Field(
        default=4,
        description="Typical number of sections",
        examples=[3, 5]
    )
    uses_emojis: bool = Field(
        default=False,
        description="Whether emojis are used",
        examples=[True, False]
    )
    emoji_frequency: float = Field(
        default=0.00,
        ge=0.0,
        le=1.0,
        description="Emoji frequency (0.0 to 1.0)",
        examples=[0.05, 0.12]
    )
    example_intros: List[str] = Field(
        default_factory=list,
        description="Example intro sentences",
        examples=[["Ever wonder why AI is everywhere?", "Let's talk about trends."]]
    )
    example_transitions: List[str] = Field(
        default_factory=list,
        description="Example transition sentences",
        examples=[["Now here's where it gets interesting", "But there's more"]]
    )
    example_conclusions: List[str] = Field(
        default_factory=list,
        description="Example conclusion sentences",
        examples=[["That's all for today", "Stay curious!"]]
    )

    @field_validator('tone', 'vocabulary_level', 'typical_intro_style')
    @classmethod
    def validate_enum_fields(cls, value: str) -> str:
        """Validate enum-like string fields."""
        return value.lower().strip()


class StyleProfileCreate(StyleProfileBase):
    """Create new style profile - requires workspace_id."""

    workspace_id: UUID = Field(
        description="Workspace ID to associate profile with",
        examples=["3353d8f1-4bec-465c-9518-91ccc35d2898"]
    )
    trained_on_count: int = Field(
        default=0,
        description="Number of sample newsletters analyzed",
        examples=[10, 25]
    )
    training_samples: List[str] = Field(
        default_factory=list,
        description="Sample newsletter texts used for training",
        examples=[["Sample newsletter 1...", "Sample newsletter 2..."]]
    )


class StyleProfileUpdate(BaseModel):
    """Update existing style profile - all fields optional."""

    tone: Optional[str] = Field(None, examples=["conversational"])
    formality_level: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.45])
    avg_sentence_length: Optional[float] = Field(None, examples=[14.2])
    sentence_length_variety: Optional[float] = Field(None, examples=[5.5])
    question_frequency: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.12])
    vocabulary_level: Optional[str] = Field(None, examples=["advanced"])
    favorite_phrases: Optional[List[str]] = Field(None, examples=[["Let's dive in"]])
    avoided_words: Optional[List[str]] = Field(None, examples=[["synergy"]])
    typical_intro_style: Optional[str] = Field(None, examples=["question"])
    section_count: Optional[int] = Field(None, examples=[5])
    uses_emojis: Optional[bool] = Field(None, examples=[True])
    emoji_frequency: Optional[float] = Field(None, ge=0.0, le=1.0, examples=[0.08])
    example_intros: Optional[List[str]] = Field(None)
    example_transitions: Optional[List[str]] = Field(None)
    example_conclusions: Optional[List[str]] = Field(None)
    trained_on_count: Optional[int] = Field(None, examples=[15])


class StyleProfileResponse(StyleProfileBase):
    """Full style profile response including metadata."""

    id: UUID = Field(description="Style profile ID")
    workspace_id: UUID = Field(description="Associated workspace ID")
    trained_on_count: int = Field(description="Number of samples used for training")
    created_at: datetime = Field(description="Profile creation timestamp")
    updated_at: datetime = Field(description="Profile last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "tone": "conversational",
                "formality_level": 0.35,
                "avg_sentence_length": 15.8,
                "sentence_length_variety": 6.2,
                "question_frequency": 0.12,
                "vocabulary_level": "intermediate",
                "favorite_phrases": ["Here's the thing", "Let's dive in"],
                "avoided_words": ["synergy", "leverage"],
                "typical_intro_style": "question",
                "section_count": 4,
                "uses_emojis": True,
                "emoji_frequency": 0.08,
                "example_intros": ["Ever wonder why AI is everywhere?"],
                "example_transitions": ["Now here's where it gets interesting"],
                "example_conclusions": ["That's all for today"],
                "trained_on_count": 23,
                "created_at": "2025-01-20T10:30:00Z",
                "updated_at": "2025-01-20T10:30:00Z"
            }
        }
    }


class StyleProfileSummary(BaseModel):
    """Summary of style profile for workspace."""

    has_profile: bool = Field(description="Whether workspace has a style profile")
    trained_on_count: int = Field(default=0, description="Number of training samples")
    tone: Optional[str] = Field(None, description="Current tone setting")
    formality_level: Optional[float] = Field(None, description="Current formality level")
    uses_emojis: bool = Field(default=False, description="Whether emojis are used")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "has_profile": True,
                "trained_on_count": 23,
                "tone": "conversational",
                "formality_level": 0.35,
                "uses_emojis": True,
                "last_updated": "2025-01-20T10:30:00Z"
            }
        }
    }


class TrainStyleRequest(BaseModel):
    """Request to train style profile from newsletter samples."""

    workspace_id: UUID = Field(description="Workspace ID")
    samples: List[str] = Field(
        min_length=5,
        description="Newsletter text samples (minimum 5, recommended 20+)",
        examples=[
            [
                "Newsletter sample 1: Ever wonder why...",
                "Newsletter sample 2: Here's the thing...",
                "Newsletter sample 3: Let's dive into..."
            ]
        ]
    )
    retrain: bool = Field(
        default=False,
        description="Whether to retrain existing profile or fail if exists",
        examples=[False, True]
    )

    @field_validator('samples')
    @classmethod
    def validate_samples(cls, samples: List[str]) -> List[str]:
        """Validate sample newsletters."""
        if len(samples) < 5:
            raise ValueError("Minimum 5 samples required for training")

        # Filter out empty samples
        filtered = [s.strip() for s in samples if s.strip()]

        if len(filtered) < 5:
            raise ValueError("Minimum 5 non-empty samples required")

        # Warn if samples are too short
        for idx, sample in enumerate(filtered):
            if len(sample.split()) < 50:
                raise ValueError(
                    f"Sample {idx+1} is too short ({len(sample.split())} words). "
                    "Each sample should be at least 50 words."
                )

        return filtered


class TrainStyleResponse(BaseModel):
    """Response after training style profile."""

    success: bool = Field(description="Whether training succeeded")
    message: str = Field(description="Status message")
    profile: StyleProfileResponse = Field(description="Trained style profile")
    analysis_summary: Dict[str, Any] = Field(
        description="Summary of analysis performed",
        examples=[
            {
                "samples_analyzed": 23,
                "total_words": 5420,
                "total_sentences": 342,
                "avg_words_per_sample": 235.7,
                "detected_tone": "conversational",
                "confidence_score": 0.87
            }
        ]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Style profile trained successfully on 23 samples",
                "profile": {
                    "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                    "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                    "tone": "conversational",
                    "formality_level": 0.35,
                    "trained_on_count": 23
                },
                "analysis_summary": {
                    "samples_analyzed": 23,
                    "total_words": 5420,
                    "confidence_score": 0.87
                }
            }
        }
    }


class GeneratePromptRequest(BaseModel):
    """Request to generate style-specific prompt for newsletter generation."""

    workspace_id: UUID = Field(description="Workspace ID with style profile")

    model_config = {
        "json_schema_extra": {
            "example": {
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898"
            }
        }
    }


class GeneratePromptResponse(BaseModel):
    """Response with generated style prompt."""

    has_profile: bool = Field(description="Whether workspace has style profile")
    prompt: str = Field(description="Generated style instruction prompt")
    profile_summary: Optional[StyleProfileSummary] = Field(
        None,
        description="Summary of style profile used"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "has_profile": True,
                "prompt": "Write in this specific style:\n- Tone: conversational (35% formal)\n- Average sentence length: 15.8 words...",
                "profile_summary": {
                    "has_profile": True,
                    "trained_on_count": 23,
                    "tone": "conversational"
                }
            }
        }
    }
