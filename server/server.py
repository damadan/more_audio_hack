"""Minimal WebSocket echo server for CPU deployment."""

from __future__ import annotations

import asyncio
import logging
import os

import websockets

log = logging.getLogger(__name__)


async def handler(ws: websockets.WebSocketServerProtocol) -> None:
    """Echo binary messages back to the client."""
    async for message in ws:
        if isinstance(message, bytes):
            await ws.send(message)


async def start_server() -> None:
    """Start a simple WebSocket server and log the port."""
    port = int(os.getenv("WS_PORT", "8000"))
    log.info("WS server on :%d", port)
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_server())


if __name__ == "__main__":
    main()
