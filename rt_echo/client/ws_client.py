from __future__ import annotations

import asyncio
import json
import logging

import websockets

from .audio_io import MicStreamer
from .player import PcmPlayer


async def run(url: str, mic: MicStreamer, player: PcmPlayer) -> None:
    """Connect to a websocket server and stream audio in both directions.

    Parameters
    ----------
    url:
        Websocket server URL.
    mic:
        Microphone streamer providing 20 ms PCM16 blocks.
    player:
        PCM player consuming audio blocks from the server.
    """

    async with websockets.connect(url) as ws, mic, player:
        async def _sender() -> None:
            while True:
                block = await mic.read_block()
                await ws.send(block)

        async def _receiver() -> None:
            async for message in ws:
                if isinstance(message, bytes):
                    await player.play(message)
                else:
                    logging.info(json.dumps({"type": "partial", "text": message}))

        await asyncio.gather(_sender(), _receiver())
