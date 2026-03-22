# Agora

AI-powered roundtable discussions and population simulations for Claude Code.

Agora creates discussions between AI personas with psychologically grounded profiles — Big Five personality traits, True Colors temperament, Moral Foundations, cognitive and communication styles. Population simulations predict how diverse demographic segments would respond to real-world scenarios. Each persona and segment is a Claude Code subagent.

## Install

**Plugin install (recommended):**
```
/plugin marketplace add <github-user>/agora
/plugin install agora
```

**Manual install:**
```bash
git clone <repo-url> agora && cd agora && ./install.sh
```

Then in any Claude Code session:

```
/agora:discuss "Is free will an illusion?"
/agora:simulate "If we raised prices 20%" "B2B SaaS customers"
```

## Skills

| Skill | Description |
|-------|-------------|
| `/agora:discuss "topic"` | Start a new roundtable discussion |
| `/agora:discuss "topic" socrates ada-lovelace` | Start with specific personas |
| `/agora:discuss continue <id>` | Resume a past discussion |
| `/agora:simulate "scenario" "population"` | Run a population simulation |
| `/agora:simulate "scenario" --population <id>` | Simulate with a saved population |
| `/agora:population create "description"` | Create a reusable population |
| `/agora:population list` | List saved populations |
| `/agora:population view <id>` | View population segments |
| `/agora:list personas` | List all available personas |
| `/agora:list discussions` | Browse past discussions |
| `/agora:list populations` | List saved populations |
| `/agora:list simulations` | List past simulations |
| `/agora:ask socrates "What is virtue?"` | Ask a persona directly |
| `/agora:reflect socrates` | Trigger reflection on recent memories |

## How It Works

### Discussions

1. **You pick a topic** — `/agora:discuss "Should AI systems have rights?"`
2. **Agora selects personas** — diverse thinkers from different eras and disciplines (or you pick them)
3. **Each persona responds** — spawned as a Claude Code subagent with their full psychological profile
4. **You join in** — type your own thoughts between rounds, or just watch
5. **Memory persists** — personas remember past discussions and build on prior insights

### Simulations

1. **You describe a scenario** — `/agora:simulate "If we raised prices 20%" "B2B SaaS customers"`
2. **Agora generates segments** — diverse demographic cohorts with psychographic profiles
3. **Each segment analyzes** — qualitative reasoning + quantitative estimates (likelihood, sentiment, intensity)
4. **Results aggregate** — weighted metrics, fault lines, and actionable recommendations

## Personas

Agora ships with 5 starter personas:

- **Socrates** — Dialectical questioner, challenger, abstract thinker
- **Ada Lovelace** — Analytical mathematician, empirical, evidence-first
- **Friedrich Nietzsche** — Provocateur, contrarian, blunt and expressive
- **Simone de Beauvoir** — Existentialist, balanced, ethical responsibility
- **Oscar Wilde** — Witty aesthete, diplomatic, story-first

Add more by placing `.md` files in `~/.agora/agents/`.

## Starter Populations

- **US Consumers** — 6 segments spanning income, age, geography, and lifestyle
- **Tech Early Adopters** — 5 segments from developer enthusiasts to pragmatic mainstream

## Data

All data lives in `~/.agora/` (override with `AGORA_HOME` env var):

```
~/.agora/
  agents/        Persona definition files
  discussions/   Transcripts and metadata
  memory/        Agent memory streams and reflections
  populations/   Saved population segment profiles
  simulations/   Simulation reports and metadata
```

## Requirements

- [Claude Code](https://claude.ai/code) installed and authenticated
- That's it. No API keys, no local models, no databases.
