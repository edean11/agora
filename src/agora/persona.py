"""Persona system for Agora.

Loads, saves, and manipulates psychologically grounded agent personas
based on Big Five, True Colors, and Moral Foundations Theory.
"""

from dataclasses import dataclass
from pathlib import Path

from agora.config import AGENTS_DIR, PERSONA_VECTOR_DIMS
from agora.utils import (
    parse_markdown_field,
    parse_markdown_list_fields,
    parse_markdown_sections,
    read_markdown_file,
    slugify,
    write_markdown_file,
)


@dataclass
class Persona:
    """Psychologically grounded agent persona.

    Attributes:
        id: Slug derived from name
        name: Agent's name
        age: Agent's age
        background: Education, career, life experiences
        big_five: Big Five traits (Low/Medium/High)
        big_five_descriptions: Behavioral descriptions for each trait
        true_colors_primary: Primary True Color (Orange/Gold/Green/Blue)
        true_colors_secondary: Secondary True Color
        true_colors_primary_desc: Description of primary color
        true_colors_secondary_desc: Description of secondary color
        moral_foundations: Moral Foundations scores (1-10)
        cognitive_reasoning: Reasoning style
        cognitive_thinking_mode: Thinking mode
        cognitive_argument_style: Argument style
        communication_pace: Communication pace
        communication_formality: Formality level
        communication_directness: Directness level
        communication_emotionality: Emotionality level
        conflict_approach: How they handle conflict
        consensus: Attitude toward consensus
        focus: Cognitive focus
        strengths: Strengths in discussion
        blind_spots: Blind spots
        trigger_points: What triggers strong reactions
    """

    id: str
    name: str
    age: int
    background: str
    big_five: dict[str, str]
    big_five_descriptions: dict[str, str]
    true_colors_primary: str
    true_colors_secondary: str
    true_colors_primary_desc: str
    true_colors_secondary_desc: str
    moral_foundations: dict[str, int]
    cognitive_reasoning: str
    cognitive_thinking_mode: str
    cognitive_argument_style: str
    communication_pace: str
    communication_formality: str
    communication_directness: str
    communication_emotionality: str
    conflict_approach: str
    consensus: str
    focus: str
    strengths: str
    blind_spots: str
    trigger_points: str


def load_persona(agent_id: str) -> Persona:
    """Load a persona from markdown file.

    Args:
        agent_id: Agent ID (filename without .md extension)

    Returns:
        Parsed Persona object

    Raises:
        FileNotFoundError: If persona file doesn't exist
    """
    path = AGENTS_DIR / f"{agent_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Persona not found: {agent_id}")

    content = read_markdown_file(path)
    sections = parse_markdown_sections(content)

    # Parse Identity section
    identity = sections.get("Identity", "")
    name = parse_markdown_field(identity, "Name")
    age_str = parse_markdown_field(identity, "Age")
    age = int(age_str) if age_str else 0
    background = parse_markdown_field(identity, "Background")

    # Parse Big Five
    big_five_section = sections.get("Big Five (Low / Medium / High)", "")
    big_five = {}
    big_five_descriptions = {}
    for trait in ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]:
        full_value = parse_markdown_field(big_five_section, trait)
        # Format: "High — description text"
        if " — " in full_value:
            level, desc = full_value.split(" — ", 1)
            big_five[trait.lower()] = level.strip()
            big_five_descriptions[trait.lower()] = desc.strip()
        else:
            big_five[trait.lower()] = full_value.strip()
            big_five_descriptions[trait.lower()] = ""

    # Parse True Colors
    true_colors_section = sections.get("True Colors", "")
    primary_full = parse_markdown_field(true_colors_section, "Primary")
    secondary_full = parse_markdown_field(true_colors_section, "Secondary")

    # Format: "Blue — description"
    if " — " in primary_full:
        true_colors_primary, true_colors_primary_desc = primary_full.split(" — ", 1)
        true_colors_primary = true_colors_primary.strip()
        true_colors_primary_desc = true_colors_primary_desc.strip()
    else:
        true_colors_primary = primary_full.strip()
        true_colors_primary_desc = ""

    if " — " in secondary_full:
        true_colors_secondary, true_colors_secondary_desc = secondary_full.split(" — ", 1)
        true_colors_secondary = true_colors_secondary.strip()
        true_colors_secondary_desc = true_colors_secondary_desc.strip()
    else:
        true_colors_secondary = secondary_full.strip()
        true_colors_secondary_desc = ""

    # Parse Moral Foundations
    moral_section = sections.get("Moral Foundations (1-10)", "")
    moral_fields = parse_markdown_list_fields(moral_section)
    moral_foundations = {}
    for key, display_name in [
        ("care", "Care/Harm"),
        ("fairness", "Fairness/Cheating"),
        ("loyalty", "Loyalty/Betrayal"),
        ("authority", "Authority/Subversion"),
        ("sanctity", "Sanctity/Degradation"),
        ("liberty", "Liberty/Oppression"),
    ]:
        value_str = moral_fields.get(display_name, "5")
        moral_foundations[key] = int(value_str) if value_str.isdigit() else 5

    # Parse Cognitive Style
    cognitive_section = sections.get("Cognitive Style", "")
    cognitive_reasoning = parse_markdown_field(cognitive_section, "Reasoning")
    cognitive_thinking_mode = parse_markdown_field(cognitive_section, "Thinking Mode")
    cognitive_argument_style = parse_markdown_field(cognitive_section, "Argument Style")

    # Parse Communication Style
    communication_section = sections.get("Communication Style", "")
    communication_pace = parse_markdown_field(communication_section, "Pace")
    communication_formality = parse_markdown_field(communication_section, "Formality")
    communication_directness = parse_markdown_field(communication_section, "Directness")
    communication_emotionality = parse_markdown_field(communication_section, "Emotionality")

    # Parse Discussion Tendencies
    discussion_section = sections.get("Discussion Tendencies", "")
    conflict_approach = parse_markdown_field(discussion_section, "Conflict Approach")
    consensus = parse_markdown_field(discussion_section, "Consensus")
    focus = parse_markdown_field(discussion_section, "Focus")
    strengths = parse_markdown_field(discussion_section, "Strengths")
    blind_spots = parse_markdown_field(discussion_section, "Blind Spots")
    trigger_points = parse_markdown_field(discussion_section, "Trigger Points")

    return Persona(
        id=agent_id,
        name=name,
        age=age,
        background=background,
        big_five=big_five,
        big_five_descriptions=big_five_descriptions,
        true_colors_primary=true_colors_primary,
        true_colors_secondary=true_colors_secondary,
        true_colors_primary_desc=true_colors_primary_desc,
        true_colors_secondary_desc=true_colors_secondary_desc,
        moral_foundations=moral_foundations,
        cognitive_reasoning=cognitive_reasoning,
        cognitive_thinking_mode=cognitive_thinking_mode,
        cognitive_argument_style=cognitive_argument_style,
        communication_pace=communication_pace,
        communication_formality=communication_formality,
        communication_directness=communication_directness,
        communication_emotionality=communication_emotionality,
        conflict_approach=conflict_approach,
        consensus=consensus,
        focus=focus,
        strengths=strengths,
        blind_spots=blind_spots,
        trigger_points=trigger_points,
    )


def save_persona(persona: Persona) -> Path:
    """Save a persona to markdown file.

    Args:
        persona: Persona to save

    Returns:
        Path to saved file
    """
    # Build markdown content following PLAN.md schema
    content = f"""# {persona.name}

## Identity
- **Name:** {persona.name}
- **Age:** {persona.age}
- **Background:** {persona.background}

## Psychological Profile

### Big Five (Low / Medium / High)
- **Openness:** {persona.big_five.get('openness', 'Medium')} — {persona.big_five_descriptions.get('openness', '')}
- **Conscientiousness:** {persona.big_five.get('conscientiousness', 'Medium')} — {persona.big_five_descriptions.get('conscientiousness', '')}
- **Extraversion:** {persona.big_five.get('extraversion', 'Medium')} — {persona.big_five_descriptions.get('extraversion', '')}
- **Agreeableness:** {persona.big_five.get('agreeableness', 'Medium')} — {persona.big_five_descriptions.get('agreeableness', '')}
- **Neuroticism:** {persona.big_five.get('neuroticism', 'Medium')} — {persona.big_five_descriptions.get('neuroticism', '')}

### True Colors
- **Primary:** {persona.true_colors_primary} — {persona.true_colors_primary_desc}
- **Secondary:** {persona.true_colors_secondary} — {persona.true_colors_secondary_desc}

### Moral Foundations (1-10)
- **Care/Harm:** {persona.moral_foundations.get('care', 5)}
- **Fairness/Cheating:** {persona.moral_foundations.get('fairness', 5)}
- **Loyalty/Betrayal:** {persona.moral_foundations.get('loyalty', 5)}
- **Authority/Subversion:** {persona.moral_foundations.get('authority', 5)}
- **Sanctity/Degradation:** {persona.moral_foundations.get('sanctity', 5)}
- **Liberty/Oppression:** {persona.moral_foundations.get('liberty', 5)}

## Cognitive Style
- **Reasoning:** {persona.cognitive_reasoning}
- **Thinking Mode:** {persona.cognitive_thinking_mode}
- **Argument Style:** {persona.cognitive_argument_style}

## Communication Style
- **Pace:** {persona.communication_pace}
- **Formality:** {persona.communication_formality}
- **Directness:** {persona.communication_directness}
- **Emotionality:** {persona.communication_emotionality}

## Discussion Tendencies
- **Conflict Approach:** {persona.conflict_approach}
- **Consensus:** {persona.consensus}
- **Focus:** {persona.focus}
- **Strengths:** {persona.strengths}
- **Blind Spots:** {persona.blind_spots}
- **Trigger Points:** {persona.trigger_points}
"""

    path = AGENTS_DIR / f"{persona.id}.md"
    write_markdown_file(path, content)
    return path


def list_personas() -> list[Persona]:
    """List all personas in the agents directory.

    Returns:
        List of all Persona objects, sorted by name
    """
    if not AGENTS_DIR.exists():
        return []

    personas = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        agent_id = path.stem
        try:
            persona = load_persona(agent_id)
            personas.append(persona)
        except Exception:
            # Skip malformed files
            continue

    return sorted(personas, key=lambda p: p.name)


def vectorize_persona(persona: Persona) -> list[float]:
    """Convert persona to 18-dimensional vector.

    Dimensions:
    - Big Five (5 dims): Low=0.0, Medium=0.5, High=1.0
    - Moral Foundations (6 dims): value/10.0
    - Cognitive Style (3 dims): mapped to [0, 1]
    - Communication (4 dims): mapped to [0, 1]

    Args:
        persona: Persona to vectorize

    Returns:
        18-dimensional vector with all values in [0, 1]
    """
    vector = []

    # Big Five (5 dims)
    big_five_mapping = {"low": 0.0, "medium": 0.5, "high": 1.0}
    for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
        level = persona.big_five.get(trait, "Medium").lower()
        vector.append(big_five_mapping.get(level, 0.5))

    # Moral Foundations (6 dims)
    for foundation in ["care", "fairness", "loyalty", "authority", "sanctity", "liberty"]:
        value = persona.moral_foundations.get(foundation, 5)
        vector.append(value / 10.0)

    # Cognitive Style (3 dims)
    reasoning_mapping = {
        "analytical": 0.0,
        "empirical": 0.25,
        "dialectical": 0.5,
        "holistic": 0.75,
        "intuitive": 1.0,
    }
    vector.append(reasoning_mapping.get(persona.cognitive_reasoning.lower(), 0.5))

    thinking_mode_mapping = {"convergent": 0.0, "divergent": 1.0}
    vector.append(thinking_mode_mapping.get(persona.cognitive_thinking_mode.lower(), 0.5))

    argument_style_mapping = {
        "thesis-first": 0.0,
        "evidence-first": 0.5,
        "story-first": 1.0,
    }
    vector.append(argument_style_mapping.get(persona.cognitive_argument_style.lower(), 0.5))

    # Communication (4 dims)
    pace_mapping = {"slow": 0.0, "measured": 0.5, "rapid": 1.0}
    vector.append(pace_mapping.get(persona.communication_pace.lower(), 0.5))

    formality_mapping = {"casual": 0.0, "professional": 0.5, "academic": 1.0}
    vector.append(formality_mapping.get(persona.communication_formality.lower(), 0.5))

    directness_mapping = {"diplomatic": 0.0, "balanced": 0.5, "blunt": 1.0}
    vector.append(directness_mapping.get(persona.communication_directness.lower(), 0.5))

    emotionality_mapping = {"detached": 0.0, "neutral": 0.5, "expressive": 1.0}
    vector.append(emotionality_mapping.get(persona.communication_emotionality.lower(), 0.5))

    return vector


def persona_distance(p1: Persona, p2: Persona) -> float:
    """Compute normalized Euclidean distance between two personas.

    Distance is normalized by sqrt(PERSONA_VECTOR_DIMS) to be in [0, 1].

    Args:
        p1: First persona
        p2: Second persona

    Returns:
        Normalized distance in [0, 1]
    """
    v1 = vectorize_persona(p1)
    v2 = vectorize_persona(p2)

    # Euclidean distance
    squared_diff = sum((a - b) ** 2 for a, b in zip(v1, v2))
    distance = squared_diff ** 0.5

    # Normalize by sqrt(dims) since max distance is sqrt(dims) when all coords differ by 1
    normalized = distance / (PERSONA_VECTOR_DIMS ** 0.5)

    return normalized
