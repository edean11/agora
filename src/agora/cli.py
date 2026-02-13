"""CLI interface for Agora discussion forum.

Provides argparse-based commands for managing discussions, agents, and memory.
"""

import argparse
import sys

from agora.agent import Agent, load_agents
from agora.config import DEFAULT_ROUNDS_PER_BATCH
from agora.discussion import Discussion, list_discussions
from agora.ollama_client import OllamaConnectionError
from agora.persona import generate_persona, interactive_create_persona, list_personas


def cmd_persona_list(args) -> None:
    """List all available personas.

    Args:
        args: Parsed command-line arguments
    """
    personas = list_personas()

    if not personas:
        print("No personas found.")
        print("Create one with: agora persona add")
        print("Or generate one with: agora persona generate")
        return

    print("Agents:")
    for persona in personas:
        # Extract a brief description from background (first sentence or first 60 chars)
        background_brief = persona.background.split('.')[0][:60]
        if len(persona.background) > 60 and '.' not in persona.background[:60]:
            background_brief += "..."

        print(f"  {persona.id:12s}  {persona.name} ({background_brief}, Age {persona.age})")


def cmd_persona_add(args) -> None:
    """Interactively create a new persona.

    Args:
        args: Parsed command-line arguments
    """
    try:
        persona = interactive_create_persona()
        print(f"\nCreated persona: {persona.name} ({persona.id})")
    except KeyboardInterrupt:
        print("\n\nPersona creation cancelled.")
        sys.exit(1)


def cmd_persona_generate(args) -> None:
    """Generate persona(s) automatically with diversity validation.

    Args:
        args: Parsed command-line arguments
    """
    try:
        personas = generate_persona(count=args.n)

        if not personas:
            print(f"Failed to generate {args.n} persona(s) after multiple attempts.")
            print("Try again or create manually with: agora persona add")
            return

        for persona in personas:
            # Brief description from background
            background_brief = persona.background.split('.')[0][:80]
            if len(persona.background.split('.')[0]) > 80:
                background_brief += "..."

            print(f"Generated: {persona.name} — {background_brief}")

    except OllamaConnectionError as e:
        print(f"Error: {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        print("\nAnd that the required models are installed:")
        print("  ollama pull qwen2.5:32b-instruct")
        print("  ollama pull nomic-embed-text")
        sys.exit(1)


def cmd_discuss(args) -> None:
    """Start a new discussion.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Load agents
        if args.agents:
            agents = load_agents(args.agents)
        else:
            agents = load_agents()

        if not agents:
            print("No agents found.")
            print("Create one with: agora persona add")
            print("Or generate one with: agora persona generate")
            return

        # Create discussion
        discussion = Discussion(topic=args.topic, agents=agents)
        discussion.create()

        # Print discussion header
        discussion.print_header()

        # Add initial user topic as message
        discussion.add_user_message(args.topic)

        # Run initial rounds
        discussion.run_rounds(args.rounds or DEFAULT_ROUNDS_PER_BATCH)

        # Enter interactive loop (placeholder - implemented in task 21)
        _interactive_loop(discussion)

    except OllamaConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? Try: ollama serve")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDiscussion interrupted.")
        sys.exit(0)


def cmd_continue(args) -> None:
    """Resume a paused discussion.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Load discussion
        discussion = Discussion.load(args.discussion_id)

        # Print discussion header
        discussion.print_header()

        # Print last few transcript entries for context
        recent_transcript = discussion.get_recent_transcript(n=5)
        if recent_transcript:
            print("Recent conversation:")
            print("-" * 60)
            print(recent_transcript)
            print("-" * 60)
            print()

        # Enter interactive loop
        _interactive_loop(discussion)

    except FileNotFoundError:
        print(f"Error: Discussion '{args.discussion_id}' not found")
        sys.exit(1)
    except OllamaConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? Try: ollama serve")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDiscussion interrupted.")
        sys.exit(0)


def cmd_list(args) -> None:
    """List all discussions.

    Args:
        args: Parsed command-line arguments
    """
    discussions = list_discussions()

    if not discussions:
        print("No discussions found.")
        print("Start one with: agora discuss \"your topic\"")
        return

    print("Discussions:")
    for disc in discussions:
        # Load the discussion to get more details
        try:
            loaded_disc = Discussion.load(disc["id"])
            num_agents = len(loaded_disc.agents)
            num_messages = len(loaded_disc.transcript)
            status = disc["status"]

            print(f"  {disc['id']:25s}  {disc['topic']:30s}  {num_agents} agents  {num_messages} messages  {status}")
        except FileNotFoundError:
            # If discussion can't be loaded, just show basic info
            print(f"  {disc['id']:25s}  {disc['topic']:30s}  {disc['status']}")


def cmd_ask(args) -> None:
    """Ask a direct question to an agent.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Create agent
        agent = Agent(args.agent_id)

        # Get response
        response = agent.answer_question(args.question)

        # Print formatted response
        print(f"\n{agent.name}:")
        print(response)
        print()

    except FileNotFoundError:
        print(f"Error: Agent '{args.agent_id}' not found")
        sys.exit(1)
    except OllamaConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? Try: ollama serve")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)


def cmd_memory(args) -> None:
    """View an agent's recent memories.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Load agent to get name
        agent = Agent(args.agent_id)

        # Get recent memories
        recent_memories = agent.memory_stream.get_recent(args.last or 20)

        if not recent_memories:
            print(f"No memories found for {agent.name}.")
            return

        # Print formatted memory list
        print(f"\nRecent memories for {agent.name}:")
        for memory in recent_memories:
            # Format timestamp (ISO format: "2024-01-15T14:30:00")
            timestamp = memory.timestamp[:16].replace('T', ' ')

            # Truncate content to 80 characters
            content_truncated = memory.content[:80]
            if len(memory.content) > 80:
                content_truncated += "..."

            print(f"  [{timestamp}] ({memory.type}, importance: {memory.importance}) {content_truncated}")
        print()

    except FileNotFoundError:
        print(f"Error: Agent '{args.agent_id}' not found")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)


def cmd_reflect(args) -> None:
    """Manually trigger reflection for an agent.

    Args:
        args: Parsed command-line arguments
    """
    try:
        # Create agent
        agent = Agent(args.agent_id)

        # Get recent memories count
        recent_count = len(agent.memory_stream.get_recent(50))

        if recent_count == 0:
            print(f"No memories to reflect on for {agent.name}.")
            return

        print(f"\nTriggering reflection for {agent.name}...")

        # Trigger reflection
        new_reflections = agent.trigger_reflection()

        # Print each generated insight
        if new_reflections:
            print(f"\nGenerated {len(new_reflections)} new insights:")
            for reflection in new_reflections:
                print(f"  • {reflection.content}")
            print()
        else:
            print("No new reflections generated.")

    except FileNotFoundError:
        print(f"Error: Agent '{args.agent_id}' not found")
        sys.exit(1)
    except OllamaConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? Try: ollama serve")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)


def _interactive_loop(discussion: Discussion) -> None:
    """Interactive discussion loop (placeholder for task 21).

    Args:
        discussion: Discussion instance
    """
    # Placeholder - this will be implemented in task 21
    # For now, just provide a simple loop
    while True:
        user_input = discussion.print_user_prompt()
        action = discussion.handle_user_input(user_input)

        if action == "done":
            print("Discussion completed.")
            break
        elif action == "continue":
            # Run more rounds
            discussion.run_rounds(DEFAULT_ROUNDS_PER_BATCH)
        elif action == "message":
            # User added a message, run one more round
            discussion.run_rounds(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="agora",
        description="Local AI discussion forum powered by generative agents"
    )

    # Create subparsers for top-level commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # === Persona command (with sub-subcommands) ===
    persona_parser = subparsers.add_parser(
        "persona",
        help="Manage agent personas"
    )
    persona_subparsers = persona_parser.add_subparsers(
        dest="persona_command",
        help="Persona operations"
    )

    # persona list
    persona_list_parser = persona_subparsers.add_parser(
        "list",
        help="List all available personas"
    )
    persona_list_parser.set_defaults(func=cmd_persona_list)

    # persona add
    persona_add_parser = persona_subparsers.add_parser(
        "add",
        help="Interactively create a new persona"
    )
    persona_add_parser.set_defaults(func=cmd_persona_add)

    # persona generate
    persona_generate_parser = persona_subparsers.add_parser(
        "generate",
        help="Auto-generate diverse persona(s)"
    )
    persona_generate_parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of personas to generate (default: 1)"
    )
    persona_generate_parser.set_defaults(func=cmd_persona_generate)

    # === Placeholder commands (task 20) ===

    # discuss
    discuss_parser = subparsers.add_parser(
        "discuss",
        help="Start a new discussion"
    )
    discuss_parser.add_argument("topic", help="Discussion topic")
    discuss_parser.add_argument(
        "--agents",
        nargs="+",
        help="Specific agent IDs to include (default: all)"
    )
    discuss_parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Number of auto-rounds before user prompt (default: 5)"
    )
    discuss_parser.set_defaults(func=cmd_discuss)

    # continue
    continue_parser = subparsers.add_parser(
        "continue",
        help="Resume a paused discussion"
    )
    continue_parser.add_argument("discussion_id", help="Discussion ID to resume")
    continue_parser.set_defaults(func=cmd_continue)

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List all discussions"
    )
    list_parser.set_defaults(func=cmd_list)

    # ask
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a direct question to an agent"
    )
    ask_parser.add_argument("agent_id", help="Agent ID to ask")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.set_defaults(func=cmd_ask)

    # reflect
    reflect_parser = subparsers.add_parser(
        "reflect",
        help="Manually trigger reflection for an agent"
    )
    reflect_parser.add_argument("agent_id", help="Agent ID to reflect")
    reflect_parser.set_defaults(func=cmd_reflect)

    # memory
    memory_parser = subparsers.add_parser(
        "memory",
        help="View an agent's recent memories"
    )
    memory_parser.add_argument("agent_id", help="Agent ID")
    memory_parser.add_argument(
        "--last",
        type=int,
        default=20,
        help="Number of recent memories to show (default: 20)"
    )
    memory_parser.set_defaults(func=cmd_memory)

    # Parse arguments
    args = parser.parse_args()

    # If no command given, print help
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Special handling for persona subcommand without sub-subcommand
    if args.command == "persona" and not hasattr(args, 'func'):
        persona_parser.print_help()
        sys.exit(0)

    # Execute the appropriate handler function
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
