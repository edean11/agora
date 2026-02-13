"""Discussion orchestrator for Agora.

Manages discussion creation, turn-taking, transcript persistence, and agent participation.
"""

from agora.agent import Agent, load_agents
from agora.config import DISCUSSIONS_DIR
from agora.utils import (
    append_to_file,
    format_timestamp,
    generate_id,
    now_iso,
    parse_markdown_field,
    read_markdown_file,
    slugify,
    write_markdown_file,
)


class Discussion:
    """Orchestrates a multi-agent discussion with transcript persistence.

    Attributes:
        topic: The discussion topic
        agents: List of participating Agent objects
        discussion_id: Unique discussion identifier
        discussion_dir: Path to discussion directory
        transcript: In-memory list of transcript entries
        round_number: Current round number
        consecutive_silence: Rounds where no agent spoke
    """

    def __init__(
        self,
        topic: str,
        agents: list[Agent],
        discussion_id: str | None = None
    ):
        """Initialize a Discussion.

        Args:
            topic: The discussion topic
            agents: List of participating Agent objects
            discussion_id: Optional discussion ID (generated if None)
        """
        self.topic = topic
        self.agents = agents

        # Generate discussion_id if not provided
        if discussion_id is None:
            slug = slugify(topic)
            unique_suffix = generate_id()
            self.discussion_id = f"{slug}-{unique_suffix}"
        else:
            self.discussion_id = discussion_id

        self.discussion_dir = DISCUSSIONS_DIR / self.discussion_id
        self.transcript: list[dict] = []
        self.round_number = 0
        self.consecutive_silence = 0

    def create(self) -> None:
        """Create a new discussion on disk.

        Creates the discussion directory, writes meta.md with metadata,
        and initializes an empty transcript.md file.
        """
        # Create discussion directory
        self.discussion_dir.mkdir(parents=True, exist_ok=True)

        # Write meta.md
        timestamp = now_iso()
        participant_names = ", ".join(agent.name for agent in self.agents)

        meta_content = f"""# {self.topic}

- **ID:** {self.discussion_id}
- **Created:** {timestamp}
- **Participants:** {participant_names}
- **Status:** active
"""
        meta_path = self.discussion_dir / "meta.md"
        write_markdown_file(meta_path, meta_content)

        # Initialize empty transcript.md
        transcript_content = f"""# Discussion: {self.topic}

"""
        transcript_path = self.discussion_dir / "transcript.md"
        write_markdown_file(transcript_path, transcript_content)

    @classmethod
    def load(cls, discussion_id: str) -> "Discussion":
        """Load an existing discussion from disk.

        Args:
            discussion_id: ID of the discussion to load

        Returns:
            Discussion instance with restored state

        Raises:
            FileNotFoundError: If discussion doesn't exist
        """
        discussion_dir = DISCUSSIONS_DIR / discussion_id
        meta_path = discussion_dir / "meta.md"

        if not meta_path.exists():
            raise FileNotFoundError(f"Discussion not found: {discussion_id}")

        # Read and parse meta.md
        meta_content = read_markdown_file(meta_path)

        # Extract topic from first line (# Topic)
        topic = ""
        for line in meta_content.split('\n'):
            if line.startswith('#'):
                topic = line.lstrip('#').strip()
                break

        # Parse metadata fields
        participants_str = parse_markdown_field(meta_content, "Participants")
        participant_names = [name.strip() for name in participants_str.split(',')]

        # Load agents (convert names to IDs by slugifying)
        agent_ids = [slugify(name) for name in participant_names]
        agents = load_agents(agent_ids)

        # Create Discussion instance
        discussion = cls(topic=topic, agents=agents, discussion_id=discussion_id)

        # Read and parse transcript.md
        transcript_path = discussion_dir / "transcript.md"
        transcript_content = read_markdown_file(transcript_path)

        # Parse transcript entries
        # Format: **[14:30] Speaker:**
        # Content
        lines = transcript_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Look for entry header: **[HH:MM] Speaker:**
            if line.startswith('**[') and '] ' in line and line.endswith(':**'):
                # Extract timestamp and speaker
                # Format: **[14:30] Speaker:**
                timestamp_end = line.index(']')
                timestamp = line[3:timestamp_end]  # Skip '**[' prefix
                speaker_part = line[timestamp_end+2:-3]  # Skip '] ' prefix and ':**' suffix
                speaker = speaker_part.strip()

                # Collect content lines until next entry or empty line
                content_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # Stop if we hit another entry or an empty separator
                    if next_line.strip().startswith('**[') or (not next_line.strip() and i + 1 < len(lines) and lines[i + 1].strip().startswith('**[')):
                        break
                    content_lines.append(next_line)
                    i += 1

                content = '\n'.join(content_lines).strip()

                # Add to transcript
                discussion.transcript.append({
                    "timestamp": timestamp,
                    "speaker": speaker,
                    "content": content
                })
            else:
                i += 1

        return discussion

    def add_message(self, speaker: str, content: str) -> None:
        """Add a message to the discussion transcript.

        Appends to in-memory transcript, persists to transcript.md,
        and triggers agent observations.

        Args:
            speaker: Name of the speaker (agent name or "User")
            content: The message content
        """
        # Get current timestamp
        timestamp_iso = now_iso()
        timestamp_display = format_timestamp(timestamp_iso)

        # Add to in-memory transcript
        self.transcript.append({
            "timestamp": timestamp_display,
            "speaker": speaker,
            "content": content
        })

        # Format transcript entry
        transcript_entry = f"""
**{timestamp_display} {speaker}:**
{content}
"""

        # Append to transcript.md
        transcript_path = self.discussion_dir / "transcript.md"
        append_to_file(transcript_path, transcript_entry)

        # Trigger agent observations
        if speaker == "User":
            # All agents observe user interactions
            for agent in self.agents:
                agent.observe(
                    content=content,
                    discussion_id=self.discussion_id,
                    speaker=speaker,
                    memory_type="user_interaction"
                )
        else:
            # Other agents observe this agent's statement
            for agent in self.agents:
                if agent.name != speaker:
                    agent.observe(
                        content=content,
                        discussion_id=self.discussion_id,
                        speaker=speaker,
                        memory_type="observation"
                    )

    def get_recent_transcript(self, n: int = 10) -> str:
        """Get formatted string of recent transcript entries.

        Args:
            n: Number of recent entries to include (default: 10)

        Returns:
            Formatted transcript string for LLM prompt injection
        """
        # Get last n entries
        recent = self.transcript[-n:] if len(self.transcript) > n else self.transcript

        if not recent:
            return ""

        # Format each entry
        lines = []
        for entry in recent:
            lines.append(f"{entry['timestamp']} {entry['speaker']}:")
            lines.append(entry['content'])
            lines.append("")  # Empty line between entries

        return '\n'.join(lines).strip()


def list_discussions() -> list[dict]:
    """List all discussions in the discussions directory.

    Returns:
        List of discussion summary dicts with keys: id, topic, created, status
        Sorted by creation date (newest first)
    """
    if not DISCUSSIONS_DIR.exists():
        return []

    discussions = []

    # Glob for directories containing meta.md
    for discussion_dir in DISCUSSIONS_DIR.iterdir():
        if not discussion_dir.is_dir():
            continue

        meta_path = discussion_dir / "meta.md"
        if not meta_path.exists():
            continue

        # Parse meta.md
        meta_content = read_markdown_file(meta_path)

        # Extract fields
        # Topic from first heading
        topic = ""
        for line in meta_content.split('\n'):
            if line.startswith('#'):
                topic = line.lstrip('#').strip()
                break

        discussion_id = parse_markdown_field(meta_content, "ID")
        created = parse_markdown_field(meta_content, "Created")
        status = parse_markdown_field(meta_content, "Status")

        discussions.append({
            "id": discussion_id,
            "topic": topic,
            "created": created,
            "status": status
        })

    # Sort by creation date (newest first)
    discussions.sort(key=lambda d: d["created"], reverse=True)

    return discussions
