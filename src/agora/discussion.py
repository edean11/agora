"""Discussion orchestrator for Agora.

Manages discussion creation, turn-taking, transcript persistence, and agent participation.
"""

import random
import sys

from agora.agent import Agent, load_agents
from agora.config import DEFAULT_ROUNDS_PER_BATCH, DISCUSSIONS_DIR, MAX_CONSECUTIVE_SILENCE
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

    def __init__(self, topic: str, agents: list[Agent], discussion_id: str | None = None):
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
        for line in meta_content.split("\n"):
            if line.startswith("#"):
                topic = line.lstrip("#").strip()
                break

        # Parse metadata fields
        participants_str = parse_markdown_field(meta_content, "Participants")
        participant_names = [name.strip() for name in participants_str.split(",")]

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
        lines = transcript_content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Look for entry header: **[HH:MM] Speaker:**
            if line.startswith("**[") and "] " in line and line.endswith(":**"):
                # Extract timestamp and speaker
                # Format: **[14:30] Speaker:**
                timestamp_end = line.index("]")
                timestamp = line[3:timestamp_end]  # Skip '**[' prefix
                speaker_part = line[timestamp_end + 2 : -3]  # Skip '] ' prefix and ':**' suffix
                speaker = speaker_part.strip()

                # Collect content lines until next entry or empty line
                content_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    # Stop if we hit another entry or an empty separator
                    if next_line.strip().startswith("**[") or (
                        not next_line.strip() and i + 1 < len(lines) and lines[i + 1].strip().startswith("**[")
                    ):
                        break
                    content_lines.append(next_line)
                    i += 1

                content = "\n".join(content_lines).strip()

                # Add to transcript
                discussion.transcript.append({"timestamp": timestamp, "speaker": speaker, "content": content})
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
        self.transcript.append({"timestamp": timestamp_display, "speaker": speaker, "content": content})

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
                    content=content, discussion_id=self.discussion_id, speaker=speaker, memory_type="user_interaction"
                )
        else:
            # Other agents observe this agent's statement
            for agent in self.agents:
                if agent.name != speaker:
                    agent.observe(
                        content=content, discussion_id=self.discussion_id, speaker=speaker, memory_type="observation"
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
            lines.append(entry["content"])
            lines.append("")  # Empty line between entries

        return "\n".join(lines).strip()

    def run_round(self) -> list[dict]:
        """Execute one complete round of discussion.

        Returns:
            List of messages generated in this round (can be empty if all agents decline)
        """
        messages = []
        recent_transcript = self.get_recent_transcript()

        # Phase 1: Willingness - collect (agent, willing, engagement_score) tuples
        willingness_results = []
        for agent in self.agents:
            willing, engagement_score = agent.decide_to_respond(self.topic, recent_transcript)
            willingness_results.append((agent, willing, engagement_score))

        # Filter to only willing agents
        willing_agents = [(agent, score) for agent, willing, score in willingness_results if willing]

        # Phase 2: Ordering - sort by engagement score descending
        willing_agents.sort(key=lambda x: x[1], reverse=True)

        # Phase 3: Generation - each willing agent generates response in order
        if willing_agents:
            for agent, _engagement_score in willing_agents:
                # Generate response
                response = agent.generate_response(self.topic, recent_transcript, self.discussion_id)

                # Add to transcript and trigger observations
                self.add_message(agent.name, response)

                # Print in real-time
                timestamp = self.transcript[-1]["timestamp"]
                self._print_message(agent.name, response, timestamp)

                # Track message for return
                messages.append({"speaker": agent.name, "content": response})

                # Update recent_transcript for next agent in this round
                recent_transcript = self.get_recent_transcript()

        # Phase 4: Silence tracking
        if not willing_agents:
            self.consecutive_silence += 1
        else:
            self.consecutive_silence = 0

        # Phase 5: Fallback nudge
        if self.consecutive_silence >= MAX_CONSECUTIVE_SILENCE:
            # Pick a random agent
            nudged_agent = random.choice(self.agents)

            # Force generate_response (skip willingness check)
            response = nudged_agent.generate_response(self.topic, recent_transcript, self.discussion_id)

            # Add to transcript and trigger observations
            self.add_message(nudged_agent.name, response)

            # Print in real-time
            timestamp = self.transcript[-1]["timestamp"]
            self._print_message(nudged_agent.name, response, timestamp)

            # Track message for return
            messages.append({"speaker": nudged_agent.name, "content": response})

            # Reset consecutive silence
            self.consecutive_silence = 0

        # Increment round number
        self.round_number += 1

        return messages

    def run_rounds(self, n: int = DEFAULT_ROUNDS_PER_BATCH) -> list[dict]:
        """Run n rounds sequentially.

        Args:
            n: Number of rounds to run (default: DEFAULT_ROUNDS_PER_BATCH)

        Returns:
            Combined list of all messages from all rounds
        """
        all_messages = []

        for _i in range(n):
            # Print round separator
            print(f"\n{'=' * 60}")
            print(f"ROUND {self.round_number + 1}")
            print(f"{'=' * 60}\n")

            # Run the round
            round_messages = self.run_round()
            all_messages.extend(round_messages)

        return all_messages

    def _print_message(self, speaker: str, content: str, timestamp: str) -> None:
        """Format and print a single message to stdout.

        Args:
            speaker: Name of the speaker
            content: The message content
            timestamp: Timestamp of the message
        """
        # Format speaker line (simple format: [HH:MM] Name:)
        speaker_line = f"[{timestamp}] {speaker}:"

        # Print formatted message
        print(speaker_line)
        print(content)
        print()  # Empty line after message
        sys.stdout.flush()  # Ensure real-time display

    def add_user_message(self, content: str) -> None:
        """Record user's message in transcript and display it.

        Args:
            content: The user's message content
        """
        # Record in transcript via add_message
        # add_message already handles agent observations with memory_type="user_interaction"
        self.add_message("User", content)

        # Print the user's message for confirmation
        timestamp = self.transcript[-1]["timestamp"]
        self._print_message("User", content, timestamp)

    def is_finished(self) -> bool:
        """Check if the discussion should be considered finished.

        Returns:
            True if consecutive_silence >= MAX_CONSECUTIVE_SILENCE * 2
            (all agents have declined twice in a row without even a nudge producing conversation)
        """
        return self.consecutive_silence >= MAX_CONSECUTIVE_SILENCE * 2

    def update_status(self, status: str) -> None:
        """Update the status field in meta.md.

        Args:
            status: New status value (e.g., "active", "completed", "paused")
        """
        meta_path = self.discussion_dir / "meta.md"

        # Read current meta.md
        meta_content = read_markdown_file(meta_path)

        # Replace status line
        lines = meta_content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("- **Status:**"):
                new_lines.append(f"- **Status:** {status}")
            else:
                new_lines.append(line)

        # Write back
        new_meta_content = "\n".join(new_lines)
        write_markdown_file(meta_path, new_meta_content)

    def get_summary(self) -> str:
        """Return a formatted summary of the discussion for display.

        Returns:
            Formatted string with topic, participants, rounds, message count, status
        """
        # Count messages in transcript
        message_count = len(self.transcript)

        # Get participant names
        participant_names = ", ".join(agent.name for agent in self.agents)

        # Read status from meta.md
        meta_path = self.discussion_dir / "meta.md"
        meta_content = read_markdown_file(meta_path)
        status = parse_markdown_field(meta_content, "Status")

        # Format summary
        summary = f"""Discussion: {self.topic}
ID: {self.discussion_id}
Participants: {participant_names}
Rounds: {self.round_number}
Messages: {message_count}
Status: {status}"""

        return summary

    def print_header(self) -> None:
        """Print the discussion header."""
        participant_names = ", ".join(agent.name for agent in self.agents)

        # Use simple format that works for any topic length
        print(f"\n=== Agora: {self.topic} ===")
        print(f"Participants: {participant_names}\n")
        sys.stdout.flush()

    def print_user_prompt(self) -> str:
        """Print user prompt and read user input.

        Returns:
            The user's input string

        Handles:
            KeyboardInterrupt gracefully (treats as 'done')
        """
        try:
            print()  # Blank line before prompt for visual separation
            sys.stdout.flush()
            user_input = input("> Your turn (message / 'continue' / 'done'): ")
            return user_input
        except KeyboardInterrupt:
            print()  # Newline after Ctrl+C
            return "done"

    def handle_user_input(self, user_input: str) -> str:
        """Parse user input and take appropriate action.

        Args:
            user_input: The user's input string

        Returns:
            Action type: "continue", "done", or "message"
        """
        # Normalize input
        normalized = user_input.strip().lower()

        # Check for continue
        if normalized in ("continue", ""):
            return "continue"

        # Check for done
        if normalized in ("done", "quit", "exit"):
            self.update_status("completed")
            return "done"

        # Otherwise treat as a message
        self.add_user_message(user_input.strip())
        return "message"


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
        for line in meta_content.split("\n"):
            if line.startswith("#"):
                topic = line.lstrip("#").strip()
                break

        discussion_id = parse_markdown_field(meta_content, "ID")
        created = parse_markdown_field(meta_content, "Created")
        status = parse_markdown_field(meta_content, "Status")

        discussions.append({"id": discussion_id, "topic": topic, "created": created, "status": status})

    # Sort by creation date (newest first)
    discussions.sort(key=lambda d: d["created"], reverse=True)

    return discussions
