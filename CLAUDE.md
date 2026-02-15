# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agora is a local discussion forum powered by AI agents, inspired by the "Generative Agents" paper (Park et al., UIST '23). AI agents with psychologically grounded personas participate in roundtable discussions on user-posed topics. The user is a first-class participant. Everything runs locally via Ollama with markdown file storage and minimal dependencies.

The system currently has:
- **CLI** — Fully functional command-line interface for discussions and persona management
- **Web UI (In Progress)** — React-based frontend UI components built, API integration pending

Both interfaces will share the same data layer (markdown files in `data/`).

## Project Structure

```
agora/
├── backend/          # Python backend (CLI + FastAPI API)
│   ├── src/agora/   # Core implementation
│   └── pyproject.toml
├── frontend/        # React/TypeScript web frontend
│   ├── src/
│   └── package.json
├── data/            # Shared markdown storage
│   ├── agents/      # Agent persona definitions
│   ├── discussions/ # Discussion transcripts
│   └── memory/      # Agent memory streams
└── CLAUDE.md        # This file
```

## Commands

### Backend

```bash
cd backend
uv sync                        # Install dependencies

# CLI commands
uv run agora --help
uv run agora discuss "topic here"
uv run agora persona list
uv run agora continue <discussion-id>
uv run python -m agora         # Run as module

# API server (coming soon)
# uv run agora-api             # Start API server on :8000

# Quality checks (all must pass clean with 0 errors)
uv run ruff check src/agora/
uv run ruff format --check src/agora/
uv run mypy src/agora/
```

### Frontend

```bash
cd frontend
npm install                    # Install dependencies
npm run dev                    # Dev server on :5173
npm run build                  # Production build
npm run preview                # Preview production build
```

### Running the Full Stack (Coming Soon)

The web frontend is built but not yet connected to a backend API. Currently, the CLI is the primary interface.

```bash
# For now: Use the CLI
cd backend && uv run agora discuss "your topic"

# Future: Full stack
# Terminal 1: Backend API
# cd backend && uv run agora-api
#
# Terminal 2: Frontend dev server
# cd frontend && npm run dev
#
# Open http://localhost:5173
```

### Required external setup

```bash
ollama pull qwen2.5:32b-instruct
ollama pull nomic-embed-text
```

Ollama must be running on `localhost:11434`.

## Architecture

The system implements a cognitive architecture with three pillars: **memory streams**, **retrieval scoring**, and **reflection**.

### Backend Module Responsibilities (`backend/src/agora/`)

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

### Frontend Architecture (`frontend/src/`)

Frontend UI components are built and ready for backend integration:

- **`pages/`** — React components for each route (Home, Discussion, Agents, etc.)
- **`components/`** — Reusable UI components (AgentCard, MessageBubble, etc.)
- **`api/`** — API client functions (ready for backend integration)
- **`types/`** — TypeScript type definitions
- **`App.tsx`** — Main app component with routing
- **`main.tsx`** — React entry point

### Data Storage

All state is markdown files under `data/`:
- **`data/agents/{id}.md`** — Persona definitions
- **`data/discussions/{id}/meta.md` + `transcript.md`** — Discussion metadata and transcripts
- **`data/memory/{agent_id}/stream.md` + `reflections.md`** — Agent memory streams and reflection outputs

### Key Design Decisions

- **No database** — markdown files only, parsed with utilities in `utils.py`. Both CLI and web UI share the same `data/` directory.
- **Heuristic importance scoring** — uses keyword/pattern matching instead of LLM calls for speed.
- **Minimal backend dependencies** — only `httpx` and `fastapi`; no torch, langchain, or vector DB.
- **Models**: `qwen2.5:32b-instruct` for chat, `nomic-embed-text` (768-dim) for embeddings.
- **Performance**: ~15-25 LLM calls per round with 4 agents, ~45-125 seconds per round.
- **API Design** — RESTful endpoints with FastAPI, CORS enabled for local development.
- **Frontend Stack** — React 18 with TypeScript, Vite for build tooling, React Router for navigation.
