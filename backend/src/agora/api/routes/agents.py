"""Agent utility REST API endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, status

from agora.agent import Agent
from agora.api.models import AskRequest, AskResponse, MemoryEntry, ReflectionEntry
from agora.memory import MemoryRecord

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _memory_record_to_entry(record: MemoryRecord) -> MemoryEntry:
    """Convert MemoryRecord dataclass to MemoryEntry API model.

    Args:
        record: MemoryRecord dataclass

    Returns:
        MemoryEntry API model
    """
    return MemoryEntry(
        id=record.id,
        timestamp=record.timestamp,
        type=record.type,
        importance=record.importance,
        content=record.content,
    )


def _memory_record_to_reflection_entry(record: MemoryRecord) -> ReflectionEntry:
    """Convert a reflection MemoryRecord to ReflectionEntry API model.

    Args:
        record: MemoryRecord dataclass (must be type="reflection")

    Returns:
        ReflectionEntry API model
    """
    # For reflections, the content is the insight
    # The question needs to be extracted from the reflections.md file
    # For now, we'll use a placeholder question
    # A more complete implementation would parse the reflections.md file
    return ReflectionEntry(
        timestamp=record.timestamp,
        question="",  # Would need to parse from reflections.md
        evidence_ids=record.evidence,
        insight=record.content,
    )


@router.post("/{agent_id}/ask", response_model=AskResponse)
async def ask_agent(agent_id: str, request: AskRequest) -> AskResponse:
    """Ask an agent a direct question.

    Args:
        agent_id: Agent ID
        request: Question to ask

    Returns:
        Agent's response

    Raises:
        HTTPException: 404 if agent not found
    """
    try:
        agent = Agent(agent_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found") from e

    # Run LLM call in thread pool to avoid blocking event loop
    def _ask() -> str:
        return agent.answer_question(request.question)

    response = await asyncio.to_thread(_ask)

    return AskResponse(
        agent_name=agent.name,
        agent_id=agent.id,
        response=response,
    )


@router.get("/{agent_id}/memory", response_model=list[MemoryEntry])
async def get_agent_memory(agent_id: str, last: int = 20) -> list[MemoryEntry]:
    """View agent's recent memory stream.

    Args:
        agent_id: Agent ID
        last: Number of recent memories to retrieve (default: 20)

    Returns:
        List of memory entries

    Raises:
        HTTPException: 404 if agent not found
    """
    try:
        agent = Agent(agent_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found") from e

    # Get recent memories
    memories = agent.memory_stream.get_recent(last)

    # Convert to API models
    return [_memory_record_to_entry(mem) for mem in memories]


@router.post("/{agent_id}/reflect", response_model=list[ReflectionEntry])
async def trigger_agent_reflection(agent_id: str) -> list[ReflectionEntry]:
    """Trigger manual reflection for an agent.

    Args:
        agent_id: Agent ID

    Returns:
        List of new reflection entries

    Raises:
        HTTPException: 404 if agent not found
    """
    try:
        agent = Agent(agent_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found") from e

    # Run reflection in thread pool to avoid blocking event loop
    def _reflect() -> list[MemoryRecord]:
        return agent.trigger_reflection()

    reflection_records = await asyncio.to_thread(_reflect)

    # Convert to API models
    return [_memory_record_to_reflection_entry(rec) for rec in reflection_records]


@router.get("/{agent_id}/reflections", response_model=dict)
async def get_agent_reflections(agent_id: str) -> dict:
    """Get formatted reflection history for an agent.

    Args:
        agent_id: Agent ID

    Returns:
        JSON object with agent info and reflections

    Raises:
        HTTPException: 404 if agent not found
    """
    try:
        agent = Agent(agent_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found") from e

    # Get formatted reflections
    reflections = agent.get_reflections()

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "reflections": reflections,
    }
