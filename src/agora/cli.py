"""CLI interface for Agora discussion forum.

Provides argparse-based commands for managing discussions, agents, and memory.
"""

import argparse
import sys

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


def cmd_not_implemented(args) -> None:
    """Placeholder for commands to be implemented in task 20.

    Args:
        args: Parsed command-line arguments
    """
    print("Not yet implemented.")


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
    discuss_parser.set_defaults(func=cmd_not_implemented)

    # continue
    continue_parser = subparsers.add_parser(
        "continue",
        help="Resume a paused discussion"
    )
    continue_parser.add_argument("discussion_id", help="Discussion ID to resume")
    continue_parser.set_defaults(func=cmd_not_implemented)

    # list
    list_parser = subparsers.add_parser(
        "list",
        help="List all discussions"
    )
    list_parser.set_defaults(func=cmd_not_implemented)

    # ask
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a direct question to an agent"
    )
    ask_parser.add_argument("agent_id", help="Agent ID to ask")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.set_defaults(func=cmd_not_implemented)

    # reflect
    reflect_parser = subparsers.add_parser(
        "reflect",
        help="Manually trigger reflection for an agent"
    )
    reflect_parser.add_argument("agent_id", help="Agent ID to reflect")
    reflect_parser.set_defaults(func=cmd_not_implemented)

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
    memory_parser.set_defaults(func=cmd_not_implemented)

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
