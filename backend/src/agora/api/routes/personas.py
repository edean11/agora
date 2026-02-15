"""Persona REST API endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from agora.api.models import (
    PersonaCreateRequest,
    PersonaDisambiguation,
    PersonaFromPersonRequest,
    PersonaFull,
    PersonaGenerateRequest,
    PersonaSummary,
)
from agora.config import AGENTS_DIR
from agora.ollama_client import chat
from agora.persona import (
    Persona,
    generate_persona,
    list_personas,
    load_persona,
    save_persona,
)
from agora.prompts import persona_disambiguation_prompt, persona_from_person_prompt
from agora.utils import slugify

router = APIRouter(prefix="/api/personas", tags=["personas"])


def _persona_to_summary(persona: Persona) -> PersonaSummary:
    """Convert Persona dataclass to PersonaSummary API model.

    Args:
        persona: Persona dataclass

    Returns:
        PersonaSummary API model
    """
    background_brief = persona.background[:100] if len(persona.background) > 100 else persona.background
    return PersonaSummary(
        id=persona.id,
        name=persona.name,
        age=persona.age,
        background_brief=background_brief,
    )


def _persona_to_full(persona: Persona) -> PersonaFull:
    """Convert Persona dataclass to PersonaFull API model.

    Args:
        persona: Persona dataclass

    Returns:
        PersonaFull API model
    """
    from agora.api.models import BigFiveTrait

    return PersonaFull(
        id=persona.id,
        name=persona.name,
        age=persona.age,
        background=persona.background,
        # Big Five
        openness=BigFiveTrait(
            level=persona.big_five.get("openness", "Medium"),
            description=persona.big_five_descriptions.get("openness", ""),
        ),
        conscientiousness=BigFiveTrait(
            level=persona.big_five.get("conscientiousness", "Medium"),
            description=persona.big_five_descriptions.get("conscientiousness", ""),
        ),
        extraversion=BigFiveTrait(
            level=persona.big_five.get("extraversion", "Medium"),
            description=persona.big_five_descriptions.get("extraversion", ""),
        ),
        agreeableness=BigFiveTrait(
            level=persona.big_five.get("agreeableness", "Medium"),
            description=persona.big_five_descriptions.get("agreeableness", ""),
        ),
        neuroticism=BigFiveTrait(
            level=persona.big_five.get("neuroticism", "Medium"),
            description=persona.big_five_descriptions.get("neuroticism", ""),
        ),
        # True Colors
        true_colors_primary=persona.true_colors_primary,
        true_colors_primary_description=persona.true_colors_primary_desc,
        true_colors_secondary=persona.true_colors_secondary,
        true_colors_secondary_description=persona.true_colors_secondary_desc,
        # Moral Foundations
        care=persona.moral_foundations.get("care", 5),
        fairness=persona.moral_foundations.get("fairness", 5),
        loyalty=persona.moral_foundations.get("loyalty", 5),
        authority=persona.moral_foundations.get("authority", 5),
        sanctity=persona.moral_foundations.get("sanctity", 5),
        liberty=persona.moral_foundations.get("liberty", 5),
        # Cognitive Style
        reasoning=persona.cognitive_reasoning,
        reasoning_description="",  # Not stored separately in Persona
        thinking_mode=persona.cognitive_thinking_mode,
        thinking_mode_description="",  # Not stored separately
        argument_style=persona.cognitive_argument_style,
        argument_style_description="",  # Not stored separately
        # Communication Style
        pace=persona.communication_pace,
        pace_description="",  # Not stored separately
        formality=persona.communication_formality,
        formality_description="",  # Not stored separately
        directness=persona.communication_directness,
        directness_description="",  # Not stored separately
        emotionality=persona.communication_emotionality,
        emotionality_description="",  # Not stored separately
        # Discussion Tendencies
        conflict_approach=persona.conflict_approach,
        conflict_approach_description="",  # Not stored separately
        consensus=persona.consensus,
        consensus_description="",  # Not stored separately
        focus=persona.focus,
        focus_description="",  # Not stored separately
        strengths=persona.strengths,
        blind_spots=persona.blind_spots,
        trigger_points=persona.trigger_points,
    )


def _request_to_persona(req: PersonaCreateRequest) -> Persona:
    """Convert PersonaCreateRequest to Persona dataclass.

    Args:
        req: PersonaCreateRequest API model

    Returns:
        Persona dataclass
    """
    agent_id = slugify(req.name)
    return Persona(
        id=agent_id,
        name=req.name,
        age=req.age,
        background=req.background,
        big_five={
            "openness": req.openness.level,
            "conscientiousness": req.conscientiousness.level,
            "extraversion": req.extraversion.level,
            "agreeableness": req.agreeableness.level,
            "neuroticism": req.neuroticism.level,
        },
        big_five_descriptions={
            "openness": req.openness.description,
            "conscientiousness": req.conscientiousness.description,
            "extraversion": req.extraversion.description,
            "agreeableness": req.agreeableness.description,
            "neuroticism": req.neuroticism.description,
        },
        true_colors_primary=req.true_colors_primary,
        true_colors_secondary=req.true_colors_secondary,
        true_colors_primary_desc=req.true_colors_primary_description,
        true_colors_secondary_desc=req.true_colors_secondary_description,
        moral_foundations={
            "care": req.care,
            "fairness": req.fairness,
            "loyalty": req.loyalty,
            "authority": req.authority,
            "sanctity": req.sanctity,
            "liberty": req.liberty,
        },
        cognitive_reasoning=req.reasoning,
        cognitive_thinking_mode=req.thinking_mode,
        cognitive_argument_style=req.argument_style,
        communication_pace=req.pace,
        communication_formality=req.formality,
        communication_directness=req.directness,
        communication_emotionality=req.emotionality,
        conflict_approach=req.conflict_approach,
        consensus=req.consensus,
        focus=req.focus,
        strengths=req.strengths,
        blind_spots=req.blind_spots,
        trigger_points=req.trigger_points,
    )


@router.get("", response_model=list[PersonaSummary])
async def list_all_personas() -> list[PersonaSummary]:
    """List all personas.

    Returns:
        List of persona summaries
    """
    personas = list_personas()
    return [_persona_to_summary(p) for p in personas]


@router.get("/{persona_id}", response_model=PersonaFull)
async def get_persona(persona_id: str) -> PersonaFull:
    """Get full persona detail.

    Args:
        persona_id: Persona ID

    Returns:
        Full persona details

    Raises:
        HTTPException: 404 if persona not found
    """
    try:
        persona = load_persona(persona_id)
        return _persona_to_full(persona)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Persona '{persona_id}' not found") from e


@router.post("", response_model=PersonaFull, status_code=status.HTTP_201_CREATED)
async def create_persona(req: PersonaCreateRequest) -> PersonaFull:
    """Create persona from form data.

    Args:
        req: Persona creation request

    Returns:
        Created persona details

    Raises:
        HTTPException: 400 if persona already exists
    """
    persona = _request_to_persona(req)

    # Check if already exists
    path = AGENTS_DIR / f"{persona.id}.md"
    if path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Persona '{persona.id}' already exists")

    save_persona(persona)
    return _persona_to_full(persona)


@router.post("/generate", response_model=list[PersonaSummary])
async def generate_random_personas(req: PersonaGenerateRequest) -> list[PersonaSummary]:
    """Auto-generate diverse personas.

    Args:
        req: Generation request with count

    Returns:
        List of generated persona summaries
    """

    def _generate() -> list[Persona]:
        return generate_persona(req.count)

    # Run LLM calls in thread pool to avoid blocking
    generated = await asyncio.to_thread(_generate)
    return [_persona_to_summary(p) for p in generated]


@router.post("/from-person", response_model=PersonaDisambiguation)
async def create_from_person(req: PersonaFromPersonRequest) -> PersonaDisambiguation:
    """Create persona from historical/famous person.

    Two-step flow:
    1. First call (selected_index=None): Disambiguates name.
       - If unambiguous: creates persona and returns it in persona field
       - If ambiguous: returns candidates list
    2. Follow-up call (selected_index set): Creates persona from selected candidate

    Args:
        req: Request with person name and optional selected_index

    Returns:
        Disambiguation response with candidates or created persona

    Raises:
        HTTPException: 400 if invalid selection or persona already exists
    """
    from agora.persona import _parse_disambiguation_response, _parse_persona_from_markdown
    from agora.utils import parse_markdown_field, parse_markdown_sections

    # If this is a disambiguation follow-up, use stored state
    # For now, we'll require the full flow in a single call by re-disambiguating
    # This is a simplification - a production version would cache disambiguation results

    def _disambiguate() -> tuple[bool, str | list[tuple[int, str, str]]]:
        messages = persona_disambiguation_prompt(req.name)
        response = chat(messages, temperature=0.3)
        return _parse_disambiguation_response(response)

    is_ambiguous, result = await asyncio.to_thread(_disambiguate)

    # If selected_index is provided, we're in step 2
    if req.selected_index is not None:
        if not is_ambiguous:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name is unambiguous, selected_index should not be provided",
            )

        assert isinstance(result, list)
        selected = [c for c in result if c[0] == req.selected_index]
        if not selected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid selected_index: {req.selected_index}"
            )

        _, sel_name, sel_desc = selected[0]
        person_description = f"{sel_name} ({sel_desc})"
    else:
        # Step 1: First call
        if is_ambiguous:
            assert isinstance(result, list)
            # Return candidates for user to choose
            candidates = [{"index": num, "name": name, "description": desc} for num, name, desc in result]
            return PersonaDisambiguation(ambiguous=True, candidates=candidates, persona=None)
        else:
            assert isinstance(result, str)
            person_description = result

    # Generate persona from person_description
    def _generate_persona() -> str:
        messages = persona_from_person_prompt(person_description)
        return chat(messages, temperature=0.7)

    response = await asyncio.to_thread(_generate_persona)

    # Extract name and create ID
    first_line = response.split("\n")[0].strip()
    if first_line.startswith("#"):
        persona_name = first_line.lstrip("#").strip()
    else:
        sections = parse_markdown_sections(response)
        identity = sections.get("Identity", "")
        persona_name = parse_markdown_field(identity, "Name")

    agent_id = slugify(persona_name) if persona_name else slugify(req.name)

    # Check for collision
    path = AGENTS_DIR / f"{agent_id}.md"
    if path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Persona '{agent_id}' already exists. Remove it first or use a different name.",
        )

    # Parse and save
    persona = _parse_persona_from_markdown(response, agent_id)
    save_persona(persona)

    return PersonaDisambiguation(ambiguous=False, candidates=[], persona=_persona_to_full(persona))


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(persona_id: str) -> Response:
    """Delete a persona.

    Args:
        persona_id: Persona ID to delete

    Returns:
        204 No Content

    Raises:
        HTTPException: 404 if persona not found
    """
    path = AGENTS_DIR / f"{persona_id}.md"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Persona '{persona_id}' not found")

    path.unlink()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
