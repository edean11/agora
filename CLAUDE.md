# CLAUDE.md

## Project Overview

Agora is a set of Claude Code skills that run AI-powered roundtable discussions and population simulations. Personas with psychologically grounded profiles (Big Five, True Colors, Moral Foundations) debate topics posed by the user. Population simulations predict how diverse demographic segments would respond to scenarios. Each persona and segment is a Claude Code subagent.

## Structure

```
agora/
├── .claude-plugin/
│   ├── plugin.json         # Plugin manifest (name: "agora")
│   └── marketplace.json    # Marketplace manifest for distribution
├── install.sh              # Manual install (alternative to plugin install)
├── skills/
│   ├── discuss/            # /agora:discuss — main discussion orchestrator
│   │   ├── SKILL.md
│   │   └── starters/      # 5 bundled starter personas
│   ├── simulate/           # /agora:simulate — population simulation orchestrator
│   │   ├── SKILL.md
│   │   └── starters/      # Bundled starter populations
│   ├── population/         # /agora:population — manage population segment profiles
│   ├── ask/                # /agora:ask — direct Q&A with a persona
│   ├── list/               # /agora:list — browse personas, discussions, populations, simulations
│   └── reflect/            # /agora:reflect — agent reflection & synthesis
├── agents/
│   ├── agora-persona.md    # Reusable persona subagent definition
│   └── aaru-segment.md     # Population segment subagent definition
└── CLAUDE.md
```

## Data Directory

All runtime data lives in `~/.agora/` (or `$AGORA_HOME`):
- `agents/` — persona markdown files
- `discussions/` — transcripts and metadata
- `memory/` — agent memory streams and reflections
- `populations/` — saved population segment profiles
- `simulations/` — simulation reports and metadata

## Installation

**Plugin install (recommended):**
```
/plugin marketplace add <github-user>/agora
/plugin install agora
```

**Manual install:**
```bash
git clone <repo-url> && cd agora && ./install.sh
```

## Usage

```
/agora:discuss "topic"                          # New discussion, auto-select personas
/agora:discuss "topic" socrates ada-lovelace    # New discussion, specific personas
/agora:discuss continue <discussion-id>         # Resume a discussion
/agora:simulate "scenario" "population desc"    # Run a population simulation
/agora:simulate "scenario" --population <id>    # Simulate with a saved population
/agora:population create "US adults age 18-65"  # Create a reusable population
/agora:population list                          # List saved populations
/agora:population view <id>                     # View population segments
/agora:list personas                            # List available personas
/agora:list discussions                         # List past discussions
/agora:list populations                         # List saved populations
/agora:list simulations                         # List past simulations
/agora:ask socrates "What is virtue?"           # Direct Q&A
/agora:reflect socrates                         # Trigger agent reflection
```
