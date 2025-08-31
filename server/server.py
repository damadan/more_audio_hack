"""Minimal WebSocket echo server for CPU deployment."""

from __future__ import annotations

import asyncio
import logging
import os

from aiohttp import WSMsgType, web

log = logging.getLogger(__name__)


async def ws_handler(request: web.Request) -> web.StreamResponse:
    """Echo binary messages back to the client."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == WSMsgType.BINARY:
            await ws.send_bytes(msg.data)
    return ws


async def healthz_handler(_request: web.Request) -> web.Response:
    """Return a simple JSON health check."""
    return web.json_response({"status": "ok"})


async def start_server() -> None:
    """Start a simple WebSocket server and log the port."""
    port = int(os.getenv("WS_PORT", "8000"))
    log.info("WS server on :%d", port)
    app = web.Application()
    app.router.add_get("/", ws_handler)
    app.router.add_get("/healthz", healthz_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info("/healthz ready")
    await asyncio.Future()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_server())


if __name__ == "__main__":
    main()
