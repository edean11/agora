"""Persona system for Agora.

Loads, saves, and manipulates psychologically grounded agent personas
based on Big Five, True Colors, and Moral Foundations Theory.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from agora.config import AGENTS_DIR, MIN_DIVERSITY_DISTANCE, PERSONA_VECTOR_DIMS
from agora.ollama_client import chat
from agora.prompts import (
    persona_disambiguation_prompt,
    persona_from_person_prompt,
    persona_generation_prompt,
    persona_summary,
)
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
- **Openness:** {persona.big_five.get("openness", "Medium")} — {persona.big_five_descriptions.get("openness", "")}
- **Conscientiousness:** {persona.big_five.get("conscientiousness", "Medium")} — {persona.big_five_descriptions.get("conscientiousness", "")}
- **Extraversion:** {persona.big_five.get("extraversion", "Medium")} — {persona.big_five_descriptions.get("extraversion", "")}
- **Agreeableness:** {persona.big_five.get("agreeableness", "Medium")} — {persona.big_five_descriptions.get("agreeableness", "")}
- **Neuroticism:** {persona.big_five.get("neuroticism", "Medium")} — {persona.big_five_descriptions.get("neuroticism", "")}

### True Colors
- **Primary:** {persona.true_colors_primary} — {persona.true_colors_primary_desc}
- **Secondary:** {persona.true_colors_secondary} — {persona.true_colors_secondary_desc}

### Moral Foundations (1-10)
- **Care/Harm:** {persona.moral_foundations.get("care", 5)}
- **Fairness/Cheating:** {persona.moral_foundations.get("fairness", 5)}
- **Loyalty/Betrayal:** {persona.moral_foundations.get("loyalty", 5)}
- **Authority/Subversion:** {persona.moral_foundations.get("authority", 5)}
- **Sanctity/Degradation:** {persona.moral_foundations.get("sanctity", 5)}
- **Liberty/Oppression:** {persona.moral_foundations.get("liberty", 5)}

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
    squared_diff = sum((a - b) ** 2 for a, b in zip(v1, v2, strict=True))
    distance = squared_diff**0.5

    # Normalize by sqrt(dims) since max distance is sqrt(dims) when all coords differ by 1
    normalized = distance / (PERSONA_VECTOR_DIMS**0.5)

    return float(normalized)


def _find_diversity_gap(personas: list[Persona]) -> str:
    """Identify psychological gaps in existing persona set.

    Analyzes the distribution of existing personas across the 18-dimensional
    psychological space to find underrepresented regions.

    Args:
        personas: List of existing personas

    Returns:
        Natural language description of gaps to fill
    """
    if not personas:
        return (
            "Create a psychologically realistic persona with distinct Big Five traits, "
            "clear moral foundation priorities, and a coherent cognitive/communication style."
        )

    # Vectorize all personas
    vectors = [vectorize_persona(p) for p in personas]

    # Analyze each dimension for clustering
    gaps = []

    # Big Five (dims 0-4)
    big_five_traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
    for i, trait in enumerate(big_five_traits):
        values = [v[i] for v in vectors]
        avg = sum(values) / len(values)
        # Check if clustering high (avg > 0.6) or low (avg < 0.4)
        if avg > 0.6:
            gaps.append(f"Low {trait}")
        elif avg < 0.4:
            gaps.append(f"High {trait}")

    # Moral Foundations (dims 5-10)
    moral_foundations = ["Care", "Fairness", "Loyalty", "Authority", "Sanctity", "Liberty"]
    moral_values = {}
    for i, foundation in enumerate(moral_foundations):
        dim_idx = 5 + i
        values = [v[dim_idx] for v in vectors]
        avg = sum(values) / len(values)
        moral_values[foundation] = avg

    # Find the least represented moral foundation
    if moral_values:
        min_foundation = min(moral_values, key=lambda k: moral_values[k])
        if moral_values[min_foundation] < 0.4:
            gaps.append(f"High {min_foundation}")
        max_foundation = max(moral_values, key=lambda k: moral_values[k])
        if moral_values[max_foundation] > 0.6:
            gaps.append(f"Low {max_foundation}")

    # Cognitive Style (dims 11-13)
    # Check for underrepresented reasoning styles
    reasoning_dim = 11
    reasoning_values = [v[reasoning_dim] for v in vectors]
    reasoning_avg = sum(reasoning_values) / len(reasoning_values)
    if reasoning_avg < 0.3:
        gaps.append("Holistic or Intuitive reasoning")
    elif reasoning_avg > 0.7:
        gaps.append("Analytical or Empirical reasoning")

    # Thinking mode
    thinking_dim = 12
    thinking_values = [v[thinking_dim] for v in vectors]
    thinking_avg = sum(thinking_values) / len(thinking_values)
    if thinking_avg < 0.3:
        gaps.append("Divergent thinking")
    elif thinking_avg > 0.7:
        gaps.append("Convergent thinking")

    # Argument style
    argument_dim = 13
    argument_values = [v[argument_dim] for v in vectors]
    argument_avg = sum(argument_values) / len(argument_values)
    if argument_avg < 0.3:
        gaps.append("Thesis-first argument style")
    elif argument_avg > 0.7:
        gaps.append("Story-first argument style")

    # Communication (dims 14-17)
    pace_dim = 14
    pace_values = [v[pace_dim] for v in vectors]
    pace_avg = sum(pace_values) / len(pace_values)
    if pace_avg < 0.3:
        gaps.append("Rapid communication pace")
    elif pace_avg > 0.7:
        gaps.append("Slow communication pace")

    directness_dim = 16
    directness_values = [v[directness_dim] for v in vectors]
    directness_avg = sum(directness_values) / len(directness_values)
    if directness_avg < 0.3:
        gaps.append("Blunt directness")
    elif directness_avg > 0.7:
        gaps.append("Diplomatic directness")

    if gaps:
        return "We need someone with: " + ", ".join(gaps[:5])  # Limit to top 5 gaps
    else:
        return "Create a persona that maximizes diversity from existing personas."


def _parse_persona_from_markdown(markdown: str, agent_id: str) -> Persona:
    """Parse LLM-generated markdown into a Persona object.

    Args:
        markdown: Markdown text from LLM
        agent_id: ID to assign to the persona

    Returns:
        Parsed Persona object
    """
    sections = parse_markdown_sections(markdown)

    # Parse Identity section
    identity = sections.get("Identity", "")
    name = parse_markdown_field(identity, "Name")
    age_str = parse_markdown_field(identity, "Age")
    age = int(age_str) if age_str and age_str.isdigit() else 0
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


def _generate_candidate(existing: list[Persona], gap_description: str) -> Persona:
    """Generate a candidate persona using LLM.

    Args:
        existing: List of existing personas
        gap_description: Description of psychological gaps to fill

    Returns:
        Generated Persona object
    """
    # Create summaries of existing personas
    existing_summaries = []
    for p in existing:
        persona_dict = {
            "name": p.name,
            "age": p.age,
            "background": p.background,
            "big_five": p.big_five,
            "moral_foundations": p.moral_foundations,
            "cognitive_style": {
                "reasoning": p.cognitive_reasoning,
                "thinking_mode": p.cognitive_thinking_mode,
                "argument_style": p.cognitive_argument_style,
            },
            "communication_style": {
                "pace": p.communication_pace,
                "formality": p.communication_formality,
                "directness": p.communication_directness,
                "emotionality": p.communication_emotionality,
            },
        }
        summary = persona_summary(persona_dict)
        existing_summaries.append(f"- {summary}")

    existing_summaries_text = "\n".join(existing_summaries) if existing_summaries else "None yet"

    # Generate persona via LLM
    messages = persona_generation_prompt(existing_summaries_text, gap_description)
    response = chat(messages, temperature=0.9)

    # Parse response into Persona
    # Extract name from first line (should be # Name)
    first_line = response.split("\n")[0].strip()
    if first_line.startswith("#"):
        name = first_line.lstrip("#").strip()
    else:
        # Fallback: extract from Identity section
        sections = parse_markdown_sections(response)
        identity = sections.get("Identity", "")
        name = parse_markdown_field(identity, "Name")

    agent_id = slugify(name) if name else f"persona-{len(existing) + 1}"

    return _parse_persona_from_markdown(response, agent_id)


def _validate_candidate(candidate: Persona, existing: list[Persona]) -> bool:
    """Validate that a candidate persona meets diversity and plausibility requirements.

    Args:
        candidate: Candidate persona to validate
        existing: List of existing personas

    Returns:
        True if valid, False if should retry
    """
    # Check minimum distance threshold
    for existing_persona in existing:
        distance = persona_distance(candidate, existing_persona)
        if distance < MIN_DIVERSITY_DISTANCE:
            return False

    # Check psychological plausibility constraints
    # Not both high Liberty (>=8) AND high Authority (>=8)
    liberty = candidate.moral_foundations.get("liberty", 5)
    authority = candidate.moral_foundations.get("authority", 5)
    if liberty >= 8 and authority >= 8:
        return False

    # Not both high Agreeableness AND Blunt directness AND Challenger conflict approach
    agreeableness = candidate.big_five.get("agreeableness", "Medium").lower()
    directness = candidate.communication_directness.lower()
    conflict = candidate.conflict_approach.lower()
    return not (agreeableness == "high" and directness == "blunt" and conflict == "challenger")


def generate_persona(count: int = 1) -> list[Persona]:
    """Auto-generate diverse personas with validation.

    For each persona:
    1. Load existing personas
    2. Identify diversity gaps
    3. Generate candidate via LLM
    4. Validate diversity and plausibility
    5. Save if valid, retry if not (max 3 attempts)

    Args:
        count: Number of personas to generate

    Returns:
        List of generated Persona objects
    """
    generated: list[Persona] = []

    for _ in range(count):
        existing = list_personas()
        # Add already-generated personas from this call to the existing list
        existing.extend(generated)

        # Try up to 3 times to generate a valid persona
        for _attempt in range(3):
            gap_description = _find_diversity_gap(existing)
            candidate = _generate_candidate(existing, gap_description)

            if _validate_candidate(candidate, existing):
                save_persona(candidate)
                generated.append(candidate)
                break
            # If validation fails and we have attempts left, retry

    return generated


def interactive_create_persona() -> Persona:
    """Interactively create a persona through CLI prompts.

    Walks through each field of the persona schema, validates inputs,
    and saves the resulting persona.

    Returns:
        Created Persona object
    """
    print("=== Interactive Persona Creation ===\n")

    # Identity
    name = input("Name: ").strip()
    age_str = input("Age: ").strip()
    age = int(age_str) if age_str.isdigit() else 30
    background = input("Background (education, career, life experiences): ").strip()

    # Big Five
    print("\n--- Big Five Traits (Low / Medium / High) ---")
    big_five = {}
    big_five_descriptions = {}
    for trait in ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]:
        level = ""
        while level.lower() not in ["low", "medium", "high"]:
            level = input(f"{trait} (Low/Medium/High): ").strip()
        big_five[trait.lower()] = level.capitalize()
        desc = input(f"  {trait} description: ").strip()
        big_five_descriptions[trait.lower()] = desc

    # True Colors
    print("\n--- True Colors ---")
    true_colors_primary = ""
    while true_colors_primary.lower() not in ["orange", "gold", "green", "blue"]:
        true_colors_primary = input("Primary (Orange/Gold/Green/Blue): ").strip()
    true_colors_primary = true_colors_primary.capitalize()
    true_colors_primary_desc = input("  Primary description: ").strip()

    true_colors_secondary = ""
    while true_colors_secondary.lower() not in ["orange", "gold", "green", "blue"]:
        true_colors_secondary = input("Secondary (Orange/Gold/Green/Blue): ").strip()
    true_colors_secondary = true_colors_secondary.capitalize()
    true_colors_secondary_desc = input("  Secondary description: ").strip()

    # Moral Foundations
    print("\n--- Moral Foundations (1-10) ---")
    moral_foundations = {}
    for key, display_name in [
        ("care", "Care/Harm"),
        ("fairness", "Fairness/Cheating"),
        ("loyalty", "Loyalty/Betrayal"),
        ("authority", "Authority/Subversion"),
        ("sanctity", "Sanctity/Degradation"),
        ("liberty", "Liberty/Oppression"),
    ]:
        value_str = input(f"{display_name}: ").strip()
        value = int(value_str) if value_str.isdigit() and 1 <= int(value_str) <= 10 else 5
        moral_foundations[key] = value

    # Cognitive Style
    print("\n--- Cognitive Style ---")
    cognitive_reasoning = ""
    valid_reasoning = ["analytical", "holistic", "intuitive", "empirical", "dialectical"]
    while cognitive_reasoning.lower() not in valid_reasoning:
        cognitive_reasoning = input("Reasoning (Analytical/Holistic/Intuitive/Empirical/Dialectical): ").strip()
    cognitive_reasoning = cognitive_reasoning.capitalize()

    cognitive_thinking_mode = ""
    while cognitive_thinking_mode.lower() not in ["convergent", "divergent"]:
        cognitive_thinking_mode = input("Thinking Mode (Convergent/Divergent): ").strip()
    cognitive_thinking_mode = cognitive_thinking_mode.capitalize()

    cognitive_argument_style = ""
    valid_argument = ["thesis-first", "evidence-first", "story-first"]
    while cognitive_argument_style.lower() not in valid_argument:
        cognitive_argument_style = input("Argument Style (Thesis-first/Evidence-first/Story-first): ").strip()
    cognitive_argument_style = cognitive_argument_style.capitalize()

    # Communication Style
    print("\n--- Communication Style ---")
    communication_pace = ""
    while communication_pace.lower() not in ["rapid", "measured", "slow"]:
        communication_pace = input("Pace (Rapid/Measured/Slow): ").strip()
    communication_pace = communication_pace.capitalize()

    communication_formality = ""
    while communication_formality.lower() not in ["casual", "professional", "academic"]:
        communication_formality = input("Formality (Casual/Professional/Academic): ").strip()
    communication_formality = communication_formality.capitalize()

    communication_directness = ""
    while communication_directness.lower() not in ["blunt", "balanced", "diplomatic"]:
        communication_directness = input("Directness (Blunt/Balanced/Diplomatic): ").strip()
    communication_directness = communication_directness.capitalize()

    communication_emotionality = ""
    while communication_emotionality.lower() not in ["detached", "neutral", "expressive"]:
        communication_emotionality = input("Emotionality (Detached/Neutral/Expressive): ").strip()
    communication_emotionality = communication_emotionality.capitalize()

    # Discussion Tendencies
    print("\n--- Discussion Tendencies ---")
    conflict_approach = ""
    while conflict_approach.lower() not in ["challenger", "synthesizer", "harmonizer"]:
        conflict_approach = input("Conflict Approach (Challenger/Synthesizer/Harmonizer): ").strip()
    conflict_approach = conflict_approach.capitalize()

    consensus = ""
    while consensus.lower() not in ["contrarian", "pragmatist", "consensus-seeker"]:
        consensus = input("Consensus (Contrarian/Pragmatist/Consensus-seeker): ").strip()
    consensus = consensus.capitalize()

    focus = ""
    while focus.lower() not in ["abstract", "concrete", "both"]:
        focus = input("Focus (Abstract/Concrete/Both): ").strip()
    focus = focus.capitalize()

    strengths = input("Strengths: ").strip()
    blind_spots = input("Blind Spots: ").strip()
    trigger_points = input("Trigger Points: ").strip()

    # Create and save persona
    agent_id = slugify(name)
    persona = Persona(
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

    save_persona(persona)
    print(f"\nPersona '{name}' saved successfully!")
    return persona


def _parse_disambiguation_response(
    response: str,
) -> tuple[bool, str | list[tuple[int, str, str]]]:
    """Parse LLM disambiguation response into structured result.

    Args:
        response: Raw LLM response text

    Returns:
        Tuple of (is_ambiguous, result) where result is either:
        - A person description string (if unambiguous)
        - A list of (number, name, description) tuples (if ambiguous)

    Raises:
        ValueError: If the response cannot be parsed
    """
    text = response.strip()

    if text.startswith("UNAMBIGUOUS:"):
        person_description = text[len("UNAMBIGUOUS:") :].strip()
        return (False, person_description)

    if text.startswith("AMBIGUOUS"):
        candidates: list[tuple[int, str, str]] = []
        for match in re.finditer(r"(\d+)\.\s*(.+?)\s*—\s*(.+)", text):
            num = int(match.group(1))
            name = match.group(2).strip()
            desc = match.group(3).strip()
            candidates.append((num, name, desc))
        if candidates:
            return (True, candidates)

    raise ValueError(f"Could not parse disambiguation response:\n{text}")


def create_persona_from_person(name: str) -> Persona:
    """Create a persona based on a real or historical person.

    Uses LLM to disambiguate the name, then generates a full persona
    profile grounded in the person's known biography and character.

    Args:
        name: Name of the person (e.g. "aristotle", "goethe")

    Returns:
        Created and saved Persona object

    Raises:
        FileExistsError: If a persona with this ID already exists
        ValueError: If disambiguation fails or user cancels selection
    """
    # Step 1: Disambiguate
    messages = persona_disambiguation_prompt(name)
    response = chat(messages, temperature=0.3)
    is_ambiguous, result = _parse_disambiguation_response(response)

    # Step 2: Resolve to a single person description
    if is_ambiguous:
        assert isinstance(result, list)
        print("Multiple people match that name:\n")
        for num, cand_name, desc in result:
            print(f"  {num}. {cand_name} — {desc}")
        print()
        choice = input("Select a number (or 0 to cancel): ").strip()
        if not choice.isdigit() or int(choice) == 0:
            raise ValueError("Selection cancelled.")
        choice_num = int(choice)
        selected = [c for c in result if c[0] == choice_num]
        if not selected:
            raise ValueError(f"Invalid selection: {choice_num}")
        _, sel_name, sel_desc = selected[0]
        person_description = f"{sel_name} ({sel_desc})"
        print(f"\nCreating persona for: {person_description}")
    else:
        assert isinstance(result, str)
        person_description = result
        print(f"Identified: {person_description}")

    # Step 3: Generate persona
    messages = persona_from_person_prompt(person_description)
    response = chat(messages, temperature=0.7)

    # Step 4: Extract name and create ID
    first_line = response.split("\n")[0].strip()
    if first_line.startswith("#"):
        persona_name = first_line.lstrip("#").strip()
    else:
        sections = parse_markdown_sections(response)
        identity = sections.get("Identity", "")
        persona_name = parse_markdown_field(identity, "Name")

    agent_id = slugify(persona_name) if persona_name else slugify(name)

    # Step 5: Check for collision
    path = AGENTS_DIR / f"{agent_id}.md"
    if path.exists():
        raise FileExistsError(f"Persona '{agent_id}' already exists. Remove it first or use a different name.")

    # Step 6: Parse and save
    persona = _parse_persona_from_markdown(response, agent_id)
    save_persona(persona)
    return persona
