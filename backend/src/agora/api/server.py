"""FastAPI server for the Agora API."""

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agora.api.routes.agents import router as agents_router
from agora.api.routes.discussions import router as discussions_router
from agora.api.routes.personas import router as personas_router
from agora.api.routes.ws import router as ws_router
from agora.config import AGENTS_DIR, DISCUSSIONS_DIR, MEMORY_DIR, OLLAMA_BASE_URL
from agora.ollama_client import OllamaConnectionError

app = FastAPI(
    title="Agora API",
    version="0.1.0",
    description="API for the Agora AI Discussion Forum",
)

# Include routers
app.include_router(personas_router)
app.include_router(discussions_router)
app.include_router(agents_router)
app.include_router(ws_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(FileNotFoundError)
async def not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
    """Handle FileNotFoundError with 404 response."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(OllamaConnectionError)
async def ollama_error_handler(request: Request, exc: OllamaConnectionError) -> JSONResponse:
    """Handle OllamaConnectionError with 503 response."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Ollama is not available. Please ensure Ollama is running on localhost:11434."},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError with 400 response."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.on_event("startup")
async def startup() -> None:
    """Ensure data directories exist on startup."""
    for d in [AGENTS_DIR, DISCUSSIONS_DIR, MEMORY_DIR]:
        d.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
async def health_check() -> dict[str, str | bool]:
    """
    Health check endpoint.

    Returns status and Ollama connectivity check.
    """
    # Check Ollama connectivity
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/version", timeout=5.0)
            ollama_ok = resp.status_code == 200
    except Exception:
        ollama_ok = False
    return {"status": "ok", "ollama": ollama_ok}


def main() -> None:
    """Run the Agora API server."""
    uvicorn.run("agora.api.server:app", host="0.0.0.0", port=8000, reload=True)
