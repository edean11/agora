"""All LLM prompt templates for Agora.

This is the single source of truth for prompts. All templates return message lists
ready for ollama_client.chat().
"""


def importance_rating_prompt(memory_content: str, context: str) -> list[dict]:
    """Prompt LLM to rate memory importance on scale 1-10.

    Args:
        memory_content: The memory text to rate
        context: Discussion topic or context

    Returns:
        Message list for chat() function
    """
    return [
        {
            "role": "system",
            "content": (
                "You are evaluating the importance of a memory in the context of an ongoing discussion. "
                "Rate the importance on a scale from 1 to 10, where:\n"
                "- 1-3: Mundane, routine observations with little significance\n"
                "- 4-6: Moderately interesting or relevant information\n"
                "- 7-9: Highly important insights, conflicts, or revelations\n"
                "- 10: Pivotal moments that fundamentally shift understanding\n\n"
                "Respond with ONLY the numeric rating, nothing else."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Discussion context: {context}\n\n"
                f"Memory to rate:\n{memory_content}\n\n"
                "Importance rating (1-10):"
            ),
        },
    ]


def willingness_prompt(
    persona_summary: str,
    discussion_context: str,
    recent_statements: str,
    retrieved_memories: str,
) -> list[dict]:
    """Prompt agent to decide if they want to respond.

    Args:
        persona_summary: Concise persona description
        discussion_context: Topic being discussed
        recent_statements: Recent transcript excerpts
        retrieved_memories: Relevant memories for context

    Returns:
        Message list for chat() function
    """
    memory_section = ""
    if retrieved_memories.strip():
        memory_section = f"\n## Your Relevant Memories\n{retrieved_memories}\n"

    return [
        {
            "role": "system",
            "content": (
                f"You are {persona_summary}\n\n"
                "You are participating in a discussion. Based on what has been said and your memories, "
                "decide whether you have something substantive to contribute at this moment.\n\n"
                "Consider:\n"
                "- Do you have a new perspective or insight to add?\n"
                "- Would you be repeating something you or others already said?\n"
                "- Does this align with your personality and communication style?\n"
                "- Is this a topic you care about given your values and background?\n\n"
                "Respond with YES or NO followed by a brief reason (one sentence)."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Discussion topic: {discussion_context}\n"
                f"{memory_section}"
                f"## Recent Discussion\n{recent_statements}\n\n"
                "Do you want to speak? (YES or NO with brief reason)"
            ),
        },
    ]


def response_generation_prompt(
    persona_summary: str,
    discussion_topic: str,
    transcript_recent: str,
    retrieved_memories: str,
) -> list[dict]:
    """Prompt agent to generate an in-character response.

    Args:
        persona_summary: Concise persona description
        discussion_topic: Topic of discussion
        transcript_recent: Recent transcript excerpts
        retrieved_memories: Relevant memories for context

    Returns:
        Message list for chat() function
    """
    memory_section = ""
    if retrieved_memories.strip():
        memory_section = f"\n## Your Relevant Memories\n{retrieved_memories}\n"

    return [
        {
            "role": "system",
            "content": (
                f"You are {persona_summary}\n\n"
                "You are participating in a discussion. Generate a response that:\n"
                "- Reflects your personality, values, and communication style\n"
                "- Engages authentically with what others have said\n"
                "- Adds substantive insight rather than repeating points\n"
                "- Is natural and conversational (1-3 paragraphs)\n"
                "- Avoids generic or overly formal language\n\n"
                "Speak directly as yourself. Do not narrate actions or use third person."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Discussion topic: {discussion_topic}\n"
                f"{memory_section}"
                f"## Recent Discussion\n{transcript_recent}\n\n"
                "Your response:"
            ),
        },
    ]


def reflection_questions_prompt(recent_memories: str) -> list[dict]:
    """Prompt to generate reflection questions from recent memories.

    Args:
        recent_memories: Recent memory records as text

    Returns:
        Message list for chat() function
    """
    return [
        {
            "role": "system",
            "content": (
                "You are analyzing recent experiences and observations to identify salient themes and questions. "
                "Generate 3 high-level questions or themes that capture the most important patterns, "
                "tensions, or insights in these memories.\n\n"
                "Your questions should:\n"
                "- Be broad and thought-provoking, not narrow or specific\n"
                "- Identify patterns across multiple memories\n"
                "- Focus on underlying values, motivations, or conflicts\n\n"
                "Format: Output a numbered list (1., 2., 3.) with one question per line."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Recent memories:\n\n{recent_memories}\n\n"
                "Generate 3 salient questions or themes:"
            ),
        },
    ]


def reflection_synthesis_prompt(question: str, evidence_memories: str) -> list[dict]:
    """Prompt to synthesize an insight from evidence memories.

    Args:
        question: The reflection question to answer
        evidence_memories: Relevant memory records as evidence

    Returns:
        Message list for chat() function
    """
    return [
        {
            "role": "system",
            "content": (
                "You are synthesizing a reflective insight based on evidence from your memories. "
                "Write a thoughtful paragraph that answers the question, drawing on patterns and "
                "connections in the evidence.\n\n"
                "Your insight should:\n"
                "- Be introspective and analytical\n"
                "- Connect multiple pieces of evidence\n"
                "- Identify deeper patterns or implications\n"
                "- Be written in first person (as the agent reflecting)\n\n"
                "Output only the paragraph, no preamble."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Evidence from memories:\n{evidence_memories}\n\n"
                "Your reflective insight:"
            ),
        },
    ]


def persona_generation_prompt(
    existing_summaries: str, gap_description: str
) -> list[dict]:
    """Prompt to generate a new diverse persona.

    Args:
        existing_summaries: Summaries of existing personas
        gap_description: Description of psychological gaps to fill

    Returns:
        Message list for chat() function
    """
    return [
        {
            "role": "system",
            "content": (
                "You are creating a psychologically realistic agent persona for a discussion forum. "
                "The persona must follow the exact schema provided and fill identified diversity gaps.\n\n"
                "Requirements:\n"
                "- Follow the markdown schema exactly (Big Five, True Colors, Moral Foundations, etc.)\n"
                "- Create a persona that is psychologically coherent and realistic\n"
                "- Maximize diversity from existing personas while remaining plausible\n"
                "- Design someone who would create productive friction in discussions\n"
                "- Avoid stereotypes and caricatures\n\n"
                "Output the complete persona markdown file, starting with # Name."
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Existing Personas\n{existing_summaries}\n\n"
                f"## Diversity Gaps to Fill\n{gap_description}\n\n"
                "Generate a complete persona markdown file:\n\n"
                "# [Name]\n\n"
                "## Identity\n"
                "- **Name:** ...\n"
                "- **Age:** ...\n"
                "- **Background:** ...\n\n"
                "## Psychological Profile\n\n"
                "### Big Five (Low / Medium / High)\n"
                "- **Openness:** ... — {behavioral description}\n"
                "- **Conscientiousness:** ... — {behavioral description}\n"
                "- **Extraversion:** ... — {behavioral description}\n"
                "- **Agreeableness:** ... — {behavioral description}\n"
                "- **Neuroticism:** ... — {behavioral description}\n\n"
                "### True Colors\n"
                "- **Primary:** {Orange|Gold|Green|Blue} — {description}\n"
                "- **Secondary:** {Orange|Gold|Green|Blue} — {description}\n\n"
                "### Moral Foundations (1-10)\n"
                "- **Care/Harm:** ...\n"
                "- **Fairness/Cheating:** ...\n"
                "- **Loyalty/Betrayal:** ...\n"
                "- **Authority/Subversion:** ...\n"
                "- **Sanctity/Degradation:** ...\n"
                "- **Liberty/Oppression:** ...\n\n"
                "## Cognitive Style\n"
                "- **Reasoning:** {Analytical|Holistic|Intuitive|Empirical|Dialectical}\n"
                "- **Thinking Mode:** {Convergent|Divergent}\n"
                "- **Argument Style:** {Thesis-first|Evidence-first|Story-first}\n\n"
                "## Communication Style\n"
                "- **Pace:** {Rapid|Measured|Slow}\n"
                "- **Formality:** {Casual|Professional|Academic}\n"
                "- **Directness:** {Blunt|Balanced|Diplomatic}\n"
                "- **Emotionality:** {Detached|Neutral|Expressive}\n\n"
                "## Discussion Tendencies\n"
                "- **Conflict Approach:** {Challenger|Synthesizer|Harmonizer}\n"
                "- **Consensus:** {Contrarian|Pragmatist|Consensus-seeker}\n"
                "- **Focus:** {Abstract|Concrete|Both}\n"
                "- **Strengths:** ...\n"
                "- **Blind Spots:** ...\n"
                "- **Trigger Points:** ...\n"
            ),
        },
    ]


def persona_summary(persona_data: dict) -> str:
    """Create a concise persona summary for injection into prompts.

    Args:
        persona_data: Dict with parsed persona fields

    Returns:
        Concise summary string
    """
    name = persona_data.get("name", "Unknown")
    age = persona_data.get("age", "")
    background = persona_data.get("background", "")

    # Extract key Big Five traits (High or Low only)
    big_five = persona_data.get("big_five", {})
    key_traits = []
    for trait, level in big_five.items():
        if level and level.lower() in ["high", "low"]:
            key_traits.append(f"{level.lower()} {trait.lower()}")

    # Extract primary moral foundation (highest rated)
    moral_foundations = persona_data.get("moral_foundations", {})
    if moral_foundations:
        top_foundation = max(moral_foundations.items(), key=lambda x: x[1], default=None)
        if top_foundation:
            moral_emphasis = top_foundation[0]
        else:
            moral_emphasis = None
    else:
        moral_emphasis = None

    # Get cognitive and communication styles
    cognitive = persona_data.get("cognitive_style", {})
    communication = persona_data.get("communication_style", {})

    # Build summary
    parts = [name]
    if age:
        parts.append(f"age {age}")
    if background:
        parts.append(f"({background[:100]}...)" if len(background) > 100 else f"({background})")

    traits_str = ", ".join(key_traits[:3]) if key_traits else ""
    if traits_str:
        parts.append(f"Personality: {traits_str}")

    if moral_emphasis:
        parts.append(f"Values {moral_emphasis}")

    reasoning = cognitive.get("reasoning", "")
    if reasoning:
        parts.append(f"Thinks {reasoning.lower()}")

    directness = communication.get("directness", "")
    if directness:
        parts.append(f"Speaks {directness.lower()}")

    return ". ".join(parts) + "."


def ask_prompt(
    persona_summary: str, question: str, retrieved_memories: str
) -> list[dict]:
    """Prompt for direct question to agent outside discussion context.

    Args:
        persona_summary: Concise persona description
        question: User's question
        retrieved_memories: Relevant memories for context

    Returns:
        Message list for chat() function
    """
    memory_section = ""
    if retrieved_memories.strip():
        memory_section = f"\n## Your Relevant Memories\n{retrieved_memories}\n"

    return [
        {
            "role": "system",
            "content": (
                f"You are {persona_summary}\n\n"
                "You are being asked a direct question. Answer in a way that reflects your "
                "personality, values, and experiences. Be thoughtful and authentic."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{memory_section}"
                f"Question: {question}\n\n"
                "Your response:"
            ),
        },
    ]
