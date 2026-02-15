"""WebSocket endpoints for real-time discussion streaming."""

import asyncio
import contextlib
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agora.agent import load_agents
from agora.discussion import Discussion

router = APIRouter()


async def send_json_safe(websocket: WebSocket, data: dict[str, Any]) -> None:
    """Send JSON data to WebSocket with error handling.

    Args:
        websocket: The WebSocket connection
        data: Data to send as JSON
    """
    # Silently ignore send failures (connection may be closed)
    with contextlib.suppress(Exception):
        await websocket.send_json(data)


def create_sync_event_callback(websocket: WebSocket, loop: asyncio.AbstractEventLoop) -> Any:
    """Create a synchronous event callback that bridges to async WebSocket send.

    Args:
        websocket: The WebSocket connection
        loop: The asyncio event loop

    Returns:
        Callback function that can be used as Discussion.on_event
    """

    def sync_on_event(event_type: str, data: dict[str, Any]) -> None:
        """Bridge from sync thread to async event loop.

        Args:
            event_type: Type of event
            data: Event data
        """
        # Schedule the coroutine in the event loop and wait for completion
        future = asyncio.run_coroutine_threadsafe(
            websocket.send_json({"type": event_type, **data}),
            loop,
        )
        # Wait for send to complete (ensures message ordering)
        # Silently ignore send failures
        with contextlib.suppress(Exception):
            future.result(timeout=10)

    return sync_on_event


@router.websocket("/api/discussions/{discussion_id}/ws")
async def discussion_ws(websocket: WebSocket, discussion_id: str) -> None:
    """WebSocket endpoint for connecting to an existing discussion.

    Args:
        websocket: WebSocket connection
        discussion_id: ID of the discussion to connect to
    """
    await websocket.accept()
    discussion = None

    try:
        # Load existing discussion with quiet agents
        discussion = await asyncio.to_thread(Discussion.load, discussion_id, True)

        # Set up event callback bridge (sync callback → async WebSocket send)
        loop = asyncio.get_event_loop()
        discussion.on_event = create_sync_event_callback(websocket, loop)

        # Send connection info
        await websocket.send_json(
            {
                "type": "connected",
                "discussion_id": discussion.discussion_id,
                "topic": discussion.topic,
                "agents": [a.name for a in discussion.agents],
            }
        )

        # Message loop
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg["type"] in ("start", "continue"):
                rounds = msg.get("rounds", 5)
                await asyncio.to_thread(discussion.run_rounds, rounds)
                await send_json_safe(websocket, {"type": "user_prompt"})

                # Check if discussion is finished
                if discussion.is_finished():
                    await send_json_safe(websocket, {"type": "discussion_finished"})

            elif msg["type"] == "user_message":
                content = msg["content"]
                await asyncio.to_thread(discussion.add_user_message, content)
                await asyncio.to_thread(discussion.run_rounds, 5)
                await send_json_safe(websocket, {"type": "user_prompt"})

                # Check if discussion is finished
                if discussion.is_finished():
                    await send_json_safe(websocket, {"type": "discussion_finished"})

            elif msg["type"] == "done":
                await asyncio.to_thread(discussion.update_status, "completed")
                await send_json_safe(websocket, {"type": "discussion_finished"})
                break

    except WebSocketDisconnect:
        # Client disconnected — pause discussion
        if discussion:
            with contextlib.suppress(Exception):
                await asyncio.to_thread(discussion.update_status, "paused")
    except Exception as e:
        # Send error to client
        await send_json_safe(websocket, {"type": "error", "message": str(e)})


@router.websocket("/api/discussions/new/ws")
async def new_discussion_ws(websocket: WebSocket) -> None:
    """WebSocket endpoint for creating a new discussion and starting live.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    discussion = None

    try:
        # Wait for create message
        raw = await websocket.receive_text()
        msg = json.loads(raw)

        if msg["type"] != "create":
            await send_json_safe(websocket, {"type": "error", "message": "Expected 'create' message"})
            return

        topic = msg["topic"]
        agent_ids = msg.get("agent_ids")
        rounds = msg.get("rounds", 5)

        # Create discussion
        agents = await asyncio.to_thread(load_agents, agent_ids, True)  # quiet=True
        discussion = Discussion(topic, agents)
        await asyncio.to_thread(discussion.create)
        await asyncio.to_thread(discussion.add_user_message, topic)

        # Set up event callback (same as above)
        loop = asyncio.get_event_loop()
        discussion.on_event = create_sync_event_callback(websocket, loop)

        # Send connected
        await websocket.send_json(
            {
                "type": "connected",
                "discussion_id": discussion.discussion_id,
                "topic": topic,
                "agents": [a.name for a in agents],
            }
        )

        # Run initial rounds
        await asyncio.to_thread(discussion.run_rounds, rounds)
        await send_json_safe(websocket, {"type": "user_prompt"})

        # Check if discussion is finished after initial rounds
        if discussion.is_finished():
            await send_json_safe(websocket, {"type": "discussion_finished"})

        # Enter message loop (same as existing discussion)
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg["type"] in ("start", "continue"):
                rounds = msg.get("rounds", 5)
                await asyncio.to_thread(discussion.run_rounds, rounds)
                await send_json_safe(websocket, {"type": "user_prompt"})

                # Check if discussion is finished
                if discussion.is_finished():
                    await send_json_safe(websocket, {"type": "discussion_finished"})

            elif msg["type"] == "user_message":
                content = msg["content"]
                await asyncio.to_thread(discussion.add_user_message, content)
                await asyncio.to_thread(discussion.run_rounds, 5)
                await send_json_safe(websocket, {"type": "user_prompt"})

                # Check if discussion is finished
                if discussion.is_finished():
                    await send_json_safe(websocket, {"type": "discussion_finished"})

            elif msg["type"] == "done":
                await asyncio.to_thread(discussion.update_status, "completed")
                await send_json_safe(websocket, {"type": "discussion_finished"})
                break

    except WebSocketDisconnect:
        # Client disconnected — pause discussion
        if discussion:
            with contextlib.suppress(Exception):
                await asyncio.to_thread(discussion.update_status, "paused")
    except Exception as e:
        # Send error to client
        await send_json_safe(websocket, {"type": "error", "message": str(e)})
