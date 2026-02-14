"""Thin httpx wrapper for Ollama HTTP API.

Provides chat() and embed() functions for LLM inference and text embedding.
"""

import httpx

from agora.config import (
    CHAT_MODEL,
    EMBED_MODEL,
    OLLAMA_BASE_URL,
)


class OllamaConnectionError(Exception):
    """Raised when Ollama connection fails."""

    pass


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """Generate a chat completion via Ollama.

    Args:
        messages: List of message dicts with "role" and "content" keys.
                  role should be "system", "user", or "assistant".
        model: Model name (defaults to CHAT_MODEL from config).
        temperature: Sampling temperature (0.0 to 1.0).

    Returns:
        Generated response text.

    Raises:
        OllamaConnectionError: If Ollama is not running or unreachable.
    """
    endpoint = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model or CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    try:
        response = httpx.post(endpoint, json=payload, timeout=httpx.Timeout(timeout=600.0))
        response.raise_for_status()
        data = response.json()
        return str(data["message"]["content"])
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise OllamaConnectionError(
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. Is Ollama running? Try: ollama serve"
        ) from e
    except httpx.HTTPStatusError as e:
        raise OllamaConnectionError(f"Ollama returned an error: {e.response.status_code} {e.response.text}") from e


def embed(
    text: str | list[str],
    model: str | None = None,
) -> list[list[float]]:
    """Generate embeddings via Ollama.

    Args:
        text: Single string or list of strings to embed.
        model: Model name (defaults to EMBED_MODEL from config).

    Returns:
        List of embedding vectors (each 768-dim for nomic-embed-text).
        If text is a single string, returns a single-element list.

    Raises:
        OllamaConnectionError: If Ollama is not running or unreachable.
    """
    endpoint = f"{OLLAMA_BASE_URL}/api/embed"

    # Wrap single string in a list for the API
    input_list = [text] if isinstance(text, str) else text

    payload = {
        "model": model or EMBED_MODEL,
        "input": input_list,
    }

    try:
        response = httpx.post(endpoint, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return list(data["embeddings"])
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise OllamaConnectionError(
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. Is Ollama running? Try: ollama serve"
        ) from e
    except httpx.HTTPStatusError as e:
        raise OllamaConnectionError(f"Ollama returned an error: {e.response.status_code} {e.response.text}") from e
