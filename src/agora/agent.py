"""Agent class tying persona + memory + LLM for Agora.

Agents have psychologically grounded personas, maintain memory streams,
and participate in discussions via observation and response generation.
"""

from agora.config import DEFAULT_TOP_K, REFLECTION_THRESHOLD
from agora.memory import MemoryRecord, MemoryStream, heuristic_importance
from agora.persona import Persona, list_personas, load_persona
from agora.prompts import persona_summary


class Agent:
    """An AI agent with persona, memory, and reasoning capabilities.

    Attributes:
        persona: Psychologically grounded Persona object
        memory_stream: MemoryStream for storing and retrieving memories
        persona_summary_text: Pre-generated persona summary for LLM prompts
        _reflection_needed: Flag indicating if reflection threshold has been met
    """

    def __init__(self, agent_id: str):
        """Initialize an Agent by loading persona and memory.

        Args:
            agent_id: ID of the agent (persona filename without .md extension)
        """
        # Load persona
        self.persona = load_persona(agent_id)

        # Create/load memory stream
        self.memory_stream = MemoryStream(agent_id)

        # Generate persona summary for LLM prompts
        persona_dict = {
            "name": self.persona.name,
            "age": self.persona.age,
            "background": self.persona.background,
            "big_five": self.persona.big_five,
            "moral_foundations": self.persona.moral_foundations,
            "cognitive_style": {
                "reasoning": self.persona.cognitive_reasoning,
                "thinking_mode": self.persona.cognitive_thinking_mode,
                "argument_style": self.persona.cognitive_argument_style,
            },
            "communication_style": {
                "pace": self.persona.communication_pace,
                "formality": self.persona.communication_formality,
                "directness": self.persona.communication_directness,
                "emotionality": self.persona.communication_emotionality,
            },
        }
        self.persona_summary_text = persona_summary(persona_dict)

        # Reflection flag (checked by reflection.py and discussion.py)
        self._reflection_needed = False

    def observe(
        self,
        content: str,
        discussion_id: str,
        speaker: str,
        memory_type: str = "observation"
    ) -> MemoryRecord:
        """Record what someone else said or a user interaction.

        Formats content with speaker attribution, rates importance heuristically,
        adds to memory stream, and checks reflection trigger.

        Args:
            content: The statement or interaction text
            discussion_id: ID of the discussion this observation is from
            speaker: Name of the speaker (e.g., "Ada", "User")
            memory_type: Type of memory (default: "observation")

        Returns:
            The created MemoryRecord
        """
        # Format with speaker attribution
        formatted_content = f"{speaker}: {content}"

        # Rate importance heuristically
        importance = heuristic_importance(content)

        # Add to memory stream
        record = self.memory_stream.add_record(
            type=memory_type,
            discussion_id=discussion_id,
            importance=importance,
            content=formatted_content
        )

        # Check reflection trigger
        cumulative_importance = self.memory_stream.get_cumulative_importance_since_last_reflection()
        if cumulative_importance >= REFLECTION_THRESHOLD:
            self._reflection_needed = True

        return record

    def observe_own_statement(self, content: str, discussion_id: str) -> MemoryRecord:
        """Record agent's own statement.

        Own statements are always assigned importance 5 (moderately important).

        Args:
            content: The agent's statement
            discussion_id: ID of the discussion

        Returns:
            The created MemoryRecord
        """
        # Own statements have fixed importance of 5
        importance = 5

        # Add to memory stream
        record = self.memory_stream.add_record(
            type="own_statement",
            discussion_id=discussion_id,
            importance=importance,
            content=content
        )

        # Check reflection trigger
        cumulative_importance = self.memory_stream.get_cumulative_importance_since_last_reflection()
        if cumulative_importance >= REFLECTION_THRESHOLD:
            self._reflection_needed = True

        return record

    def get_relevant_memories(self, query: str, k: int = DEFAULT_TOP_K) -> list[MemoryRecord]:
        """Retrieve top-k memories most relevant to a query.

        Wrapper around memory_stream.retrieve() for convenience.

        Args:
            query: Query text to search for
            k: Number of top memories to retrieve (default: DEFAULT_TOP_K)

        Returns:
            List of up to k most relevant MemoryRecords
        """
        return self.memory_stream.retrieve(query, k)

    @property
    def name(self) -> str:
        """Get the agent's name.

        Returns:
            Agent's name from persona
        """
        return self.persona.name

    @property
    def id(self) -> str:
        """Get the agent's ID.

        Returns:
            Agent's ID from persona
        """
        return self.persona.id


def load_agents(agent_ids: list[str] | None = None) -> list[Agent]:
    """Load Agent objects for specified or all personas.

    Args:
        agent_ids: List of agent IDs to load, or None to load all

    Returns:
        List of Agent objects
    """
    if agent_ids is None:
        # Load all personas
        personas = list_personas()
        return [Agent(persona.id) for persona in personas]
    else:
        # Load specified personas
        return [Agent(agent_id) for agent_id in agent_ids]
