"""Discussion REST API endpoints."""

import shutil

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from agora.agent import load_agents
from agora.api.models import (
    DiscussionCreateRequest,
    DiscussionFull,
    DiscussionSummary,
    StatusUpdateRequest,
    TranscriptEntry,
)
from agora.config import DISCUSSIONS_DIR
from agora.discussion import Discussion, list_discussions
from agora.utils import parse_markdown_field, read_markdown_file

router = APIRouter(prefix="/api/discussions", tags=["discussions"])


def _get_discussion_summary(discussion_dict: dict) -> DiscussionSummary:
    """Convert discussion dict to DiscussionSummary with participant and message counts.

    Args:
        discussion_dict: Dict with keys: id, topic, created, status

    Returns:
        DiscussionSummary with additional counts
    """
    discussion_id = discussion_dict["id"]
    discussion_dir = DISCUSSIONS_DIR / discussion_id

    # Read meta.md for participant count
    meta_path = discussion_dir / "meta.md"
    meta_content = read_markdown_file(meta_path)
    participants_str = parse_markdown_field(meta_content, "Participants")
    participant_count = len([p.strip() for p in participants_str.split(",") if p.strip()])

    # Read transcript.md to count messages
    transcript_path = discussion_dir / "transcript.md"
    transcript_content = read_markdown_file(transcript_path)
    # Count lines starting with **[
    message_count = sum(1 for line in transcript_content.split("\n") if line.strip().startswith("**["))

    return DiscussionSummary(
        id=discussion_dict["id"],
        topic=discussion_dict["topic"],
        created=discussion_dict["created"],
        status=discussion_dict["status"],
        participant_count=participant_count,
        message_count=message_count,
    )


@router.get("", response_model=list[DiscussionSummary])
async def list_all_discussions() -> list[DiscussionSummary]:
    """List all discussions with participant and message counts.

    Returns:
        List of discussion summaries (newest first)
    """
    discussions = list_discussions()
    return [_get_discussion_summary(d) for d in discussions]


@router.get("/{discussion_id}", response_model=DiscussionFull)
async def get_discussion(discussion_id: str) -> DiscussionFull:
    """Get full discussion with transcript.

    Args:
        discussion_id: Discussion ID

    Returns:
        Full discussion details with complete transcript

    Raises:
        HTTPException: 404 if discussion not found
    """
    try:
        # Load the discussion using quiet mode for API
        discussion = Discussion.load(discussion_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Discussion '{discussion_id}' not found"
        ) from e

    # Read meta.md for created and status
    meta_path = discussion.discussion_dir / "meta.md"
    meta_content = read_markdown_file(meta_path)
    created = parse_markdown_field(meta_content, "Created")
    status_value = parse_markdown_field(meta_content, "Status")

    # Extract participant names
    participants = [agent.name for agent in discussion.agents]

    # Convert transcript to TranscriptEntry models
    transcript = [
        TranscriptEntry(timestamp=entry["timestamp"], speaker=entry["speaker"], content=entry["content"])
        for entry in discussion.transcript
    ]

    return DiscussionFull(
        id=discussion.discussion_id,
        topic=discussion.topic,
        created=created,
        status=status_value,
        participants=participants,
        transcript=transcript,
    )


@router.post("", response_model=DiscussionSummary, status_code=status.HTTP_201_CREATED)
async def create_discussion(req: DiscussionCreateRequest) -> DiscussionSummary:
    """Create a new discussion.

    Args:
        req: Discussion creation request with topic, agent_ids, and rounds

    Returns:
        Created discussion summary

    Raises:
        HTTPException: 400 if invalid agent IDs
    """
    try:
        # Load agents with quiet mode for API
        agents = load_agents(req.agent_ids, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid agent ID: {e}") from e

    # Create discussion
    discussion = Discussion(req.topic, agents)
    discussion.create()

    # Add initial topic as user message
    discussion.add_user_message(req.topic)

    # Read meta.md to get created timestamp and status
    meta_path = discussion.discussion_dir / "meta.md"
    meta_content = read_markdown_file(meta_path)
    created = parse_markdown_field(meta_content, "Created")
    status_value = parse_markdown_field(meta_content, "Status")

    # Return summary
    return DiscussionSummary(
        id=discussion.discussion_id,
        topic=discussion.topic,
        created=created,
        status=status_value,
        participant_count=len(agents),
        message_count=1,  # Only the initial user message
    )


@router.patch("/{discussion_id}/status", response_model=DiscussionSummary)
async def update_discussion_status(discussion_id: str, req: StatusUpdateRequest) -> DiscussionSummary:
    """Update discussion status.

    Args:
        discussion_id: Discussion ID
        req: Status update request

    Returns:
        Updated discussion summary

    Raises:
        HTTPException: 404 if discussion not found
    """
    try:
        # Load discussion with quiet mode for API
        discussion = Discussion.load(discussion_id, quiet=True)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Discussion '{discussion_id}' not found"
        ) from e

    # Update status
    discussion.update_status(req.status)

    # Read meta.md for updated data
    meta_path = discussion.discussion_dir / "meta.md"
    meta_content = read_markdown_file(meta_path)
    created = parse_markdown_field(meta_content, "Created")
    status_value = parse_markdown_field(meta_content, "Status")
    participants_str = parse_markdown_field(meta_content, "Participants")
    participant_count = len([p.strip() for p in participants_str.split(",") if p.strip()])

    # Count messages in transcript
    message_count = len(discussion.transcript)

    return DiscussionSummary(
        id=discussion.discussion_id,
        topic=discussion.topic,
        created=created,
        status=status_value,
        participant_count=participant_count,
        message_count=message_count,
    )


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(discussion_id: str) -> Response:
    """Delete a discussion.

    Args:
        discussion_id: Discussion ID to delete

    Returns:
        204 No Content

    Raises:
        HTTPException: 404 if discussion not found
    """
    discussion_dir = DISCUSSIONS_DIR / discussion_id
    if not discussion_dir.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Discussion '{discussion_id}' not found")

    # Delete the entire discussion directory
    shutil.rmtree(discussion_dir)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
