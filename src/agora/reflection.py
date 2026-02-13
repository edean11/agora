"""Reflection system for Agora agents.

Implements the reflection pipeline from the Generative Agents paper:
1. Check cumulative importance threshold
2. Generate reflection questions from recent memories
3. Retrieve evidence memories for each question
4. Synthesize insights from evidence
5. Store reflections as memory records
"""

from pathlib import Path

from agora.config import (
    REFLECTION_THRESHOLD,
    REFLECTION_RECENT_COUNT,
    REFLECTION_QUESTIONS,
    REFLECTION_EVIDENCE_PER_QUESTION,
    MEMORY_DIR,
)
from agora.memory import MemoryRecord
from agora import ollama_client
from agora.prompts import reflection_questions_prompt, reflection_synthesis_prompt
from agora.utils import append_to_file, now_iso, read_markdown_file


def should_reflect(agent: "Agent") -> bool:
    """Check if agent should trigger reflection based on cumulative importance.

    Args:
        agent: The Agent to check

    Returns:
        True if cumulative importance since last reflection >= REFLECTION_THRESHOLD
    """
    cumulative = agent.memory_stream.get_cumulative_importance_since_last_reflection()
    return cumulative >= REFLECTION_THRESHOLD


def reflect(agent: "Agent") -> list[MemoryRecord]:
    """Execute the full reflection process.

    Generates questions from recent memories, retrieves evidence, synthesizes
    insights, and stores them as reflection-type memory records.

    Args:
        agent: The Agent performing reflection

    Returns:
        List of newly created reflection MemoryRecords
    """
    # Step 1: Get recent memories
    recent_memories = agent.memory_stream.get_recent(REFLECTION_RECENT_COUNT)

    # Step 2: Generate reflection questions
    # Format memories for LLM
    formatted_memories = _format_memories_for_questions(recent_memories)

    # Call LLM to generate questions
    messages = reflection_questions_prompt(formatted_memories)
    questions_response = ollama_client.chat(messages)

    # Parse questions from response
    questions = _parse_questions(questions_response)

    # Step 3-5: For each question, retrieve evidence and synthesize insight
    reflection_records = []

    for question in questions:
        # Step 3: Retrieve evidence memories
        evidence_memories = agent.memory_stream.retrieve(
            question,
            k=REFLECTION_EVIDENCE_PER_QUESTION
        )
        evidence_ids = [mem.id for mem in evidence_memories]

        # Step 4: Synthesize insight
        formatted_evidence = _format_memories_for_synthesis(evidence_memories)
        messages = reflection_synthesis_prompt(question, formatted_evidence)
        insight = ollama_client.chat(messages)

        # Step 5: Store reflection as memory record
        record = agent.memory_stream.add_record(
            type="reflection",
            discussion_id="",  # Cross-discussion
            importance=8,  # Reflections default to 8
            content=insight,
            evidence=evidence_ids
        )
        reflection_records.append(record)

        # Also persist to reflections.md file
        _append_to_reflections_file(
            agent_id=agent.id,
            timestamp=record.timestamp,
            question=question,
            evidence_ids=evidence_ids,
            insight=insight
        )

    return reflection_records


def format_reflections(agent_id: str) -> str:
    """Read and format reflections for display.

    Args:
        agent_id: ID of the agent

    Returns:
        Formatted reflections string for display
    """
    reflections_path = MEMORY_DIR / agent_id / "reflections.md"
    content = read_markdown_file(reflections_path)

    if not content:
        return f"No reflections yet for agent {agent_id}."

    return content


def _format_memories_for_questions(memories: list[MemoryRecord]) -> str:
    """Format memory records for question generation prompt.

    Args:
        memories: List of MemoryRecord objects

    Returns:
        Formatted string with one memory per line
    """
    if not memories:
        return ""

    lines = []
    for memory in memories:
        # Format timestamp (extract date and time)
        timestamp = memory.timestamp[:16].replace('T', ' ')  # "2024-01-15 14:30"

        # Include type prefix for reflections
        if memory.type == "reflection":
            lines.append(f"[{timestamp}] [REFLECTION] {memory.content}")
        else:
            lines.append(f"[{timestamp}] {memory.content}")

    return "\n".join(lines)


def _format_memories_for_synthesis(memories: list[MemoryRecord]) -> str:
    """Format memory records for synthesis prompt.

    Args:
        memories: List of MemoryRecord objects

    Returns:
        Formatted string with memory IDs and content
    """
    if not memories:
        return ""

    lines = []
    for memory in memories:
        # Format timestamp
        timestamp = memory.timestamp[:16].replace('T', ' ')

        # Include memory ID for evidence tracing
        lines.append(f"[{memory.id}] [{timestamp}] {memory.content}")

    return "\n".join(lines)


def _parse_questions(llm_response: str) -> list[str]:
    """Parse numbered questions from LLM response.

    Expects format like:
    1. First question here?
    2. Second question here?
    3. Third question here?

    Args:
        llm_response: Raw LLM response text

    Returns:
        List of parsed question strings (up to REFLECTION_QUESTIONS)
    """
    questions = []
    lines = llm_response.strip().split('\n')

    for line in lines:
        # Strip whitespace
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Remove numbering (e.g., "1.", "2)", "3 -", etc.)
        # Match patterns like: "1.", "1)", "1 -", "1:", etc.
        line = line.lstrip('0123456789').lstrip('.)- :').strip()

        # If we have content, add it
        if line:
            questions.append(line)

        # Stop after we have enough questions
        if len(questions) >= REFLECTION_QUESTIONS:
            break

    return questions


def _append_to_reflections_file(
    agent_id: str,
    timestamp: str,
    question: str,
    evidence_ids: list[str],
    insight: str
) -> None:
    """Append a reflection to the agent's reflections.md file.

    Args:
        agent_id: ID of the agent
        timestamp: ISO timestamp of the reflection
        question: The reflection question
        evidence_ids: List of memory IDs used as evidence
        insight: The synthesized insight paragraph
    """
    reflections_path = MEMORY_DIR / agent_id / "reflections.md"

    # Format evidence IDs as comma-separated list
    evidence_str = ", ".join(evidence_ids)

    # Build reflection entry
    reflection_entry = f"""---
## Reflection: {timestamp}

**Question:** {question}
**Evidence:** {evidence_str}

{insight}

"""

    append_to_file(reflections_path, reflection_entry)
