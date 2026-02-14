# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agora is a local CLI discussion forum powered by AI agents, inspired by the "Generative Agents" paper (Park et al., UIST '23). AI agents with psychologically grounded personas participate in roundtable discussions on user-posed topics. The user is a first-class participant. Everything runs locally via Ollama with markdown file storage and a single Python dependency (`httpx`).

## Commands

```bash
# Install dependencies
cd backend && uv sync

# Run the CLI
cd backend && uv run agora --help
cd backend && uv run agora discuss "topic here"
cd backend && uv run agora persona list
cd backend && uv run agora continue <discussion-id>

# Run as module
cd backend && uv run python -m agora

# Run validation tests (no formal test framework; tests are standalone scripts)
uv run python .df/test_task18_simple.py

# Lint, format, and type check (all must pass clean with 0 errors)
uv run ruff check backend/src/agora/
uv run ruff format --check backend/src/agora/
uv run mypy backend/src/agora/
```

### Required external setup

```bash
ollama pull qwen2.5:32b-instruct
ollama pull nomic-embed-text
```

Ollama must be running on `localhost:11434`.

## Architecture

The system implements a cognitive architecture with three pillars: **memory streams**, **retrieval scoring**, and **reflection**.

### Module Responsibilities (`backend/src/agora/`)

- **`cli.py`** — argparse subcommands + interactive discussion loop. Entry point via `agora.cli:main`.
- **`agent.py`** — `Agent` class tying persona + memory + LLM reasoning. Key methods: `observe()`, `decide_to_respond()`, `generate_response()`.
- **`discussion.py`** — Orchestrator: turn-taking (willingness → engagement ordering → generation), real-time transcript persistence, user participation.
- **`memory.py`** — `MemoryStream` with composite retrieval scoring: recency (exponential decay 0.995^n) × importance (heuristic, no LLM) × relevance (cosine similarity on embeddings).
- **`reflection.py`** — Triggered at cumulative importance threshold (50). Generates questions → retrieves evidence → synthesizes insights.
- **`persona.py`** — Load/save/generate personas based on Big Five traits, True Colors, Moral Foundations Theory, cognitive & communication styles.
- **`prompts.py`** — All LLM prompt templates (willingness evaluation, response generation, reflection, persona generation).
- **`ollama_client.py`** — Thin `httpx` wrapper for Ollama `chat()` and `embed()` endpoints.
- **`config.py`** — All constants: paths, model names, tuning parameters.
- **`utils.py`** — Markdown I/O, timestamps, vector math (cosine similarity).

### Data Storage

All state is markdown files under `data/`:
- **`data/agents/{id}.md`** — Persona definitions
- **`data/discussions/{id}/meta.md` + `transcript.md`** — Discussion metadata and transcripts
- **`data/memory/{agent_id}/stream.md` + `reflections.md`** — Agent memory streams and reflection outputs

### Key Design Decisions

- **No database** — markdown files only, parsed with utilities in `utils.py`.
- **Heuristic importance scoring** — uses keyword/pattern matching instead of LLM calls for speed.
- **Single dependency** — only `httpx`; no torch, langchain, or vector DB.
- **Models**: `qwen2.5:32b-instruct` for chat, `nomic-embed-text` (768-dim) for embeddings.
- **Performance**: ~15-25 LLM calls per round with 4 agents, ~45-125 seconds per round.
