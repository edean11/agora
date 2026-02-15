"""Pydantic models for the Agora API."""

from pydantic import BaseModel


# Persona models
class PersonaSummary(BaseModel):
    """Summary view of a persona for list endpoints."""

    id: str
    name: str
    age: int
    background_brief: str  # First 100 chars of background


class BigFiveTrait(BaseModel):
    """Big Five personality trait representation."""

    level: str  # Low/Medium/High
    description: str


class MoralFoundation(BaseModel):
    """Moral Foundation Theory score."""

    name: str
    score: int  # 1-10


class PersonaFull(BaseModel):
    """Complete persona with all psychological traits."""

    id: str
    name: str
    age: int
    background: str
    # Big Five
    openness: BigFiveTrait
    conscientiousness: BigFiveTrait
    extraversion: BigFiveTrait
    agreeableness: BigFiveTrait
    neuroticism: BigFiveTrait
    # True Colors
    true_colors_primary: str
    true_colors_primary_description: str
    true_colors_secondary: str
    true_colors_secondary_description: str
    # Moral Foundations (6 scores)
    care: int
    fairness: int
    loyalty: int
    authority: int
    sanctity: int
    liberty: int
    # Cognitive Style
    reasoning: str
    reasoning_description: str
    thinking_mode: str
    thinking_mode_description: str
    argument_style: str
    argument_style_description: str
    # Communication Style
    pace: str
    pace_description: str
    formality: str
    formality_description: str
    directness: str
    directness_description: str
    emotionality: str
    emotionality_description: str
    # Discussion Tendencies
    conflict_approach: str
    conflict_approach_description: str
    consensus: str
    consensus_description: str
    focus: str
    focus_description: str
    strengths: str
    blind_spots: str
    trigger_points: str


class PersonaCreateRequest(BaseModel):
    """Request to create a persona manually."""

    name: str
    age: int
    background: str
    # Big Five
    openness: BigFiveTrait
    conscientiousness: BigFiveTrait
    extraversion: BigFiveTrait
    agreeableness: BigFiveTrait
    neuroticism: BigFiveTrait
    # True Colors
    true_colors_primary: str
    true_colors_primary_description: str
    true_colors_secondary: str
    true_colors_secondary_description: str
    # Moral Foundations (6 scores)
    care: int
    fairness: int
    loyalty: int
    authority: int
    sanctity: int
    liberty: int
    # Cognitive Style
    reasoning: str
    reasoning_description: str
    thinking_mode: str
    thinking_mode_description: str
    argument_style: str
    argument_style_description: str
    # Communication Style
    pace: str
    pace_description: str
    formality: str
    formality_description: str
    directness: str
    directness_description: str
    emotionality: str
    emotionality_description: str
    # Discussion Tendencies
    conflict_approach: str
    conflict_approach_description: str
    consensus: str
    consensus_description: str
    focus: str
    focus_description: str
    strengths: str
    blind_spots: str
    trigger_points: str


class PersonaGenerateRequest(BaseModel):
    """Request to generate random personas."""

    count: int = 1


class PersonaFromPersonRequest(BaseModel):
    """Request to create a persona from a historical/famous person."""

    name: str
    selected_index: int | None = None  # For disambiguation follow-up


class PersonaDisambiguation(BaseModel):
    """Response for disambiguating persona creation."""

    ambiguous: bool
    candidates: list[dict]  # [{index: int, name: str, description: str}]
    persona: PersonaFull | None = None  # Set if unambiguous


# Discussion models
class TranscriptEntry(BaseModel):
    """Single entry in a discussion transcript."""

    timestamp: str
    speaker: str
    content: str


class DiscussionSummary(BaseModel):
    """Summary view of a discussion for list endpoints."""

    id: str
    topic: str
    created: str
    status: str
    participant_count: int
    message_count: int


class DiscussionFull(BaseModel):
    """Complete discussion with full transcript."""

    id: str
    topic: str
    created: str
    status: str
    participants: list[str]
    transcript: list[TranscriptEntry]


class DiscussionCreateRequest(BaseModel):
    """Request to create a new discussion."""

    topic: str
    agent_ids: list[str] | None = None  # None = all agents
    rounds: int = 5


class StatusUpdateRequest(BaseModel):
    """Request to update discussion status."""

    status: str  # "active", "paused", "completed"


# Agent/Memory models
class MemoryEntry(BaseModel):
    """Single memory entry in an agent's memory stream."""

    id: str
    timestamp: str
    type: str  # observation, own_statement, reflection, user_interaction
    importance: int
    content: str


class ReflectionEntry(BaseModel):
    """Single reflection entry for an agent."""

    timestamp: str
    question: str
    evidence_ids: list[str]
    insight: str


class AskRequest(BaseModel):
    """Request to ask an agent a question."""

    question: str


class AskResponse(BaseModel):
    """Response from asking an agent a question."""

    agent_name: str
    agent_id: str
    response: str


# WebSocket event model
class WSEvent(BaseModel):
    """WebSocket event for real-time updates."""

    type: str
    data: dict
