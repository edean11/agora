"""Memory stream system for Agora agents.

Implements MemoryRecord dataclass and MemoryStream class for storing and retrieving
agent memories. All memories are persisted to markdown files in chronological order.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import re

from agora.config import MEMORY_DIR, DECAY_FACTOR, DEFAULT_TOP_K
from agora.ollama_client import embed
from agora.utils import append_to_file, cosine_similarity, generate_id, now_iso, read_markdown_file, write_markdown_file


def heuristic_importance(content: str, context: str = "") -> int:
    """Calculate importance score (1-10) based on text heuristics.

    This is a fast alternative to LLM-based importance scoring. It evaluates
    content based on linguistic markers that correlate with memorable/important
    statements in discussion contexts.

    Args:
        content: The text content to score
        context: Optional context (currently unused, reserved for future use)

    Returns:
        Integer importance score in range [1, 10]
    """
    score = 4.0  # Base score (neutral)

    content_lower = content.lower()
    content_len = len(content)

    # Length bonus: longer content tends to be more substantive
    if content_len > 300:
        score += 2
    elif content_len > 100:
        score += 1

    # Question marks: questions drive discussion
    question_count = content.count('?')
    if question_count > 0:
        score += 1
        if question_count > 2:
            score += 1

    # Exclamation marks: emotional intensity
    if '!' in content:
        score += 1

    # Named entities / proper nouns: capitalized words mid-sentence
    # Look for capitalized words that aren't at the start of sentences
    sentences = re.split(r'[.!?]+', content)
    for sentence in sentences:
        words = sentence.strip().split()
        # Check for capitalized words beyond the first word
        if len(words) > 1:
            for word in words[1:]:
                # Check if word starts with capital and isn't all caps (acronym)
                if word and word[0].isupper() and not word.isupper():
                    score += 1
                    break  # Only add bonus once per sentence

    # Disagreement signals: conflict is memorable
    disagreement_words = [
        'disagree', 'but', 'however', 'wrong', 'contrary',
        'push back', 'challenge', 'oppose', 'refute'
    ]
    if any(word in content_lower for word in disagreement_words):
        score += 1

    # Agreement signals: less memorable but still notable
    agreement_words = ['agree', 'exactly', 'right', 'yes']
    if any(word in content_lower for word in agreement_words):
        score += 0.5

    # Self-reference: personal stakes
    self_reference_phrases = [
        'i think', 'i believe', 'in my experience',
        'i feel', 'my view', 'personally'
    ]
    if any(phrase in content_lower for phrase in self_reference_phrases):
        score += 1

    # Reflection-type content: high value
    reflection_phrases = [
        'realize', 'upon reflection', "i've come to", 'i have come to',
        'changed my mind', 'reconsidered', 'rethinking', 'reconsider'
    ]
    if any(phrase in content_lower for phrase in reflection_phrases):
        score += 4

    # Clamp to [1, 10] and round to nearest integer
    final_score = min(10, max(1, round(score)))

    return final_score


@dataclass
class MemoryRecord:
    """A single memory record in an agent's memory stream.

    Attributes:
        id: Unique identifier for this memory
        timestamp: ISO 8601 timestamp when memory was created
        type: Type of memory (observation/own_statement/reflection/user_interaction)
        discussion_id: ID of the discussion this memory is from
        importance: Importance score (1-10)
        content: The actual memory text
        last_accessed: ISO 8601 timestamp when memory was last retrieved
        evidence: List of memory IDs that support this memory (for reflections)
    """
    id: str
    timestamp: str
    type: str
    discussion_id: str
    importance: int
    content: str
    last_accessed: str
    evidence: list[str]


class MemoryStream:
    """Manages an agent's chronological memory stream.

    Stores memories as MemoryRecord objects and persists them to markdown files.
    Supports adding records, retrieving recent memories, and calculating cumulative
    importance for reflection triggering.
    """

    def __init__(self, agent_id: str):
        """Initialize memory stream for an agent.

        Args:
            agent_id: ID of the agent this memory stream belongs to
        """
        self.agent_id = agent_id
        self.records: list[MemoryRecord] = self._load_from_file()

    def add_record(
        self,
        type: str,
        discussion_id: str,
        importance: int,
        content: str,
        evidence: list[str] | None = None
    ) -> MemoryRecord:
        """Add a new memory record to the stream.

        Args:
            type: Type of memory (observation/own_statement/reflection/user_interaction)
            discussion_id: ID of the discussion this memory is from
            importance: Importance score (1-10)
            content: The actual memory text
            evidence: List of memory IDs supporting this memory (for reflections)

        Returns:
            The newly created MemoryRecord
        """
        timestamp = now_iso()
        record = MemoryRecord(
            id=generate_id(),
            timestamp=timestamp,
            type=type,
            discussion_id=discussion_id,
            importance=importance,
            content=content,
            last_accessed=timestamp,
            evidence=evidence or []
        )
        self.records.append(record)
        self._append_to_file(record)
        return record

    def get_recent(self, n: int = 50) -> list[MemoryRecord]:
        """Get the n most recent memory records.

        Args:
            n: Number of recent records to retrieve

        Returns:
            List of up to n most recent MemoryRecords
        """
        return self.records[-n:]

    def get_by_id(self, memory_id: str) -> MemoryRecord | None:
        """Find a memory record by its ID.

        Args:
            memory_id: ID of the memory to find

        Returns:
            The MemoryRecord if found, None otherwise
        """
        for record in self.records:
            if record.id == memory_id:
                return record
        return None

    def get_cumulative_importance_since_last_reflection(self) -> int:
        """Calculate sum of importance since the last reflection.

        Used to determine when to trigger a new reflection. Sums the importance
        scores of all records added since the most recent reflection-type record.

        Returns:
            Cumulative importance score
        """
        # Find the index of the last reflection
        last_reflection_idx = -1
        for i in range(len(self.records) - 1, -1, -1):
            if self.records[i].type == "reflection":
                last_reflection_idx = i
                break

        # Sum importance from records after last reflection
        cumulative = 0
        for i in range(last_reflection_idx + 1, len(self.records)):
            cumulative += self.records[i].importance

        return cumulative

    def retrieve(self, query: str, k: int = DEFAULT_TOP_K) -> list[MemoryRecord]:
        """Retrieve top-k memory records most relevant to a query.

        Scores records using composite score (recency + importance + relevance).
        Updates last_accessed timestamps on retrieved records and persists changes.

        Args:
            query: Query text to search for
            k: Number of top records to retrieve (default: DEFAULT_TOP_K)

        Returns:
            List of up to k MemoryRecords sorted by descending composite score
        """
        if not self.records:
            return []

        # Embed the query once
        query_embedding = embed(query)[0]

        # Score all records
        scored_records = []
        for record in self.records:
            recency = self._recency_score(record, self.records)
            importance = self._importance_score(record)
            relevance = self._relevance_score(record, query_embedding)
            composite = self._composite_score(recency, importance, relevance)
            scored_records.append((composite, record))

        # Sort by descending score and take top-k
        scored_records.sort(key=lambda x: x[0], reverse=True)
        top_records = [record for _, record in scored_records[:k]]

        # Update last_accessed timestamps
        current_time = now_iso()
        for record in top_records:
            record.last_accessed = current_time

        # Persist updated timestamps
        self._save_all()

        return top_records

    def _recency_score(self, record: MemoryRecord, all_records: list[MemoryRecord]) -> float:
        """Calculate recency score based on how many records were added since last access.

        Args:
            record: The memory record to score
            all_records: All records in the stream (for counting records since last access)

        Returns:
            Recency score in (0, 1], where 1 is most recent
        """
        # Count records added since this record was last accessed
        records_since = 0
        for r in all_records:
            # Compare timestamps: if record was added after our record's last_accessed
            if r.timestamp > record.last_accessed:
                records_since += 1

        # Apply exponential decay: 0.995^n
        score = DECAY_FACTOR ** records_since
        return score

    def _importance_score(self, record: MemoryRecord) -> float:
        """Calculate importance score normalized to [0.1, 1.0].

        Args:
            record: The memory record to score

        Returns:
            Importance score (importance / 10.0)
        """
        return record.importance / 10.0

    def _relevance_score(self, record: MemoryRecord, query_embedding: list[float]) -> float:
        """Calculate relevance score based on semantic similarity to query.

        Args:
            record: The memory record to score
            query_embedding: Pre-computed embedding vector for the query

        Returns:
            Cosine similarity score in [-1, 1] (typically [0, 1] for text)
        """
        # Embed the record's content
        record_embedding = embed(record.content)[0]

        # Compute cosine similarity
        similarity = cosine_similarity(record_embedding, query_embedding)
        return similarity

    def _composite_score(self, recency: float, importance: float, relevance: float) -> float:
        """Combine recency, importance, and relevance into composite score.

        Args:
            recency: Recency score
            importance: Importance score
            relevance: Relevance score

        Returns:
            Composite score (equal weights: 1.0 * recency + 1.0 * importance + 1.0 * relevance)
        """
        return 1.0 * recency + 1.0 * importance + 1.0 * relevance

    def _save_all(self) -> None:
        """Rewrite the entire stream.md file with current records.

        Used after retrieval to persist updated last_accessed timestamps.
        """
        stream_path = MEMORY_DIR / self.agent_id / "stream.md"

        # Build the full file content
        content_parts = []
        for record in self.records:
            evidence_json = json.dumps(record.evidence)
            record_text = f"""---
id: {record.id}
timestamp: {record.timestamp}
type: {record.type}
discussion_id: {record.discussion_id}
importance: {record.importance}
last_accessed: {record.last_accessed}
evidence: {evidence_json}
---

{record.content}

"""
            content_parts.append(record_text)

        # Write entire file
        full_content = ''.join(content_parts)
        write_markdown_file(stream_path, full_content)

    def _load_from_file(self) -> list[MemoryRecord]:
        """Load memory records from the stream.md file.

        Returns:
            List of MemoryRecords parsed from file, or empty list if file doesn't exist
        """
        stream_path = MEMORY_DIR / self.agent_id / "stream.md"
        content = read_markdown_file(stream_path)

        if not content:
            return []

        records = []
        # Split on record boundaries (looking for pattern: \n---\nid:)
        # Each record starts with --- followed by metadata
        record_starts = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if line.strip() == '---' and i + 1 < len(lines) and lines[i + 1].startswith('id:'):
                record_starts.append(i)

        # Process each record
        for idx, start in enumerate(record_starts):
            # Find end of this record (start of next record or end of file)
            if idx + 1 < len(record_starts):
                end = record_starts[idx + 1]
            else:
                end = len(lines)

            # Extract record lines
            record_lines = lines[start:end]

            # Find the second --- which separates metadata from content
            metadata_end = -1
            for i in range(1, len(record_lines)):
                if record_lines[i].strip() == '---':
                    metadata_end = i
                    break

            if metadata_end == -1:
                continue

            # Parse metadata (between first and second ---)
            metadata = {}
            for line in record_lines[1:metadata_end]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Extract content (after second ---)
            content_lines = record_lines[metadata_end + 1:]
            content_text = '\n'.join(content_lines).strip()

            # Parse evidence as JSON list
            evidence_str = metadata.get('evidence', '[]')
            try:
                evidence = json.loads(evidence_str)
            except json.JSONDecodeError:
                evidence = []

            # Create MemoryRecord
            record = MemoryRecord(
                id=metadata.get('id', ''),
                timestamp=metadata.get('timestamp', ''),
                type=metadata.get('type', ''),
                discussion_id=metadata.get('discussion_id', ''),
                importance=int(metadata.get('importance', 1)),
                content=content_text,
                last_accessed=metadata.get('last_accessed', ''),
                evidence=evidence
            )
            records.append(record)

        return records

    def _append_to_file(self, record: MemoryRecord) -> None:
        """Append a memory record to the stream.md file.

        Args:
            record: The MemoryRecord to persist
        """
        stream_path = MEMORY_DIR / self.agent_id / "stream.md"

        # Format evidence as JSON list
        evidence_json = json.dumps(record.evidence)

        # Build the record text
        record_text = f"""---
id: {record.id}
timestamp: {record.timestamp}
type: {record.type}
discussion_id: {record.discussion_id}
importance: {record.importance}
last_accessed: {record.last_accessed}
evidence: {evidence_json}
---

{record.content}

"""

        append_to_file(stream_path, record_text)
