"""Shared utility functions for Agora.

Provides markdown I/O, timestamp formatting, text utilities, and vector math.
"""

import re
import uuid
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to URL-safe slug.

    Lowercases, replaces spaces and special chars with hyphens,
    strips leading/trailing hyphens.

    Args:
        text: Input text to slugify

    Returns:
        URL-safe slug string
    """
    # Lowercase
    slug = text.lower()
    # Replace spaces and non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def now_iso() -> str:
    """Return current timestamp in ISO 8601 format.

    Returns:
        ISO 8601 timestamp string (e.g., "2024-01-15T14:30:00")
    """
    return datetime.now().isoformat(timespec="seconds")


def format_timestamp(iso_str: str) -> str:
    """Format ISO timestamp for display.

    Args:
        iso_str: ISO 8601 timestamp string

    Returns:
        Formatted timestamp for display (e.g., "[14:30]")
    """
    dt = datetime.fromisoformat(iso_str)
    return f"[{dt.strftime('%H:%M')}]"


def parse_markdown_sections(text: str) -> dict[str, str]:
    """Parse markdown into sections keyed by heading text.

    Handles ## and ### level headings. Returns dict mapping heading text
    to content under that heading.

    Args:
        text: Markdown text to parse

    Returns:
        Dict mapping heading text to section content
    """
    sections = {}
    current_heading = None
    current_content: list[str] = []

    for line in text.split("\n"):
        # Check for headings (## or ###)
        match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if match:
            # Save previous section if exists
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_content).strip()
            # Start new section
            current_heading = match.group(2).strip()
            current_content = []
        elif current_heading is not None:
            current_content.append(line)

    # Save final section
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_content).strip()

    return sections


def parse_markdown_field(text: str, field_name: str) -> str:
    """Extract value from a `- **Field:** value` pattern in markdown text.

    Args:
        text: Markdown text to search
        field_name: Name of field to extract

    Returns:
        Field value, or empty string if not found
    """
    pattern = rf"^\s*-\s*\*\*{re.escape(field_name)}:\*\*\s*(.+)$"
    for line in text.split("\n"):
        match = re.match(pattern, line)
        if match:
            return match.group(1).strip()
    return ""


def parse_markdown_list_fields(text: str) -> dict[str, str]:
    """Extract all `- **Key:** Value` patterns from text into a dict.

    Args:
        text: Markdown text to parse

    Returns:
        Dict mapping field names to values
    """
    fields = {}
    pattern = r"^\s*-\s*\*\*([^*]+):\*\*\s*(.+)$"
    for line in text.split("\n"):
        match = re.match(pattern, line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            fields[key] = value
    return fields


def write_markdown_file(path: Path, content: str) -> None:
    """Write content to file, creating parent dirs as needed.

    Args:
        path: Path to file
        content: Content to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_markdown_file(path: Path) -> str:
    """Read file content, return empty string if file doesn't exist.

    Args:
        path: Path to file

    Returns:
        File content, or empty string if file doesn't exist
    """
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_to_file(path: Path, content: str) -> None:
    """Append content to file, creating parent dirs and file if needed.

    Args:
        path: Path to file
        content: Content to append
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Pure Python implementation. Handles zero vectors gracefully.

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine similarity (0.0 if either vector is zero)
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have same length")

    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=True))

    # Compute magnitudes
    mag_a = sum(a * a for a in vec_a) ** 0.5
    mag_b = sum(b * b for b in vec_b) ** 0.5

    # Handle zero vectors
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return float(dot_product / (mag_a * mag_b))


def generate_id() -> str:
    """Generate a short unique ID.

    Returns:
        8-character unique ID from uuid4 hex
    """
    return uuid.uuid4().hex[:8]
