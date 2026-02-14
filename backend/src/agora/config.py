"""Configuration constants for Agora.

Defines paths, model names, and tuning parameters for the discussion forum.
"""

import os
from pathlib import Path

# Path constants — support monorepo layout with data/ at root
_PACKAGE_DIR = Path(__file__).resolve().parent  # backend/src/agora/
_BACKEND_DIR = _PACKAGE_DIR.parent.parent  # backend/
_MONOREPO_ROOT = _BACKEND_DIR.parent  # project root

DATA_DIR = Path(os.environ.get("AGORA_DATA_DIR", str(_MONOREPO_ROOT / "data")))
AGENTS_DIR = DATA_DIR / "agents"
DISCUSSIONS_DIR = DATA_DIR / "discussions"
MEMORY_DIR = DATA_DIR / "memory"

# Model constants
CHAT_MODEL = "qwen2.5:32b-instruct"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768

# Ollama constants
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = "/api/chat"
OLLAMA_EMBED_ENDPOINT = "/api/embed"

# Memory constants
DECAY_FACTOR = 0.995
DEFAULT_TOP_K = 10
REFLECTION_THRESHOLD = 50
REFLECTION_RECENT_COUNT = 50
REFLECTION_QUESTIONS = 3
REFLECTION_EVIDENCE_PER_QUESTION = 8

# Discussion constants
DEFAULT_ROUNDS_PER_BATCH = 5
MAX_CONSECUTIVE_SILENCE = 2

# Persona generation constants
MIN_DIVERSITY_DISTANCE = 0.35
PERSONA_VECTOR_DIMS = 18
