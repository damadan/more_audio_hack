from __future__ import annotations

import asyncio
import json
import logging

import websockets

from .audio_io import MicStreamer
from .player import PcmPlayer


async def run(url: str, mic: MicStreamer, player: PcmPlayer) -> None:
    """Connect to a websocket server and stream audio in both directions.

    Automatically reconnects with exponential backoff (starting at 0.5 s,
    doubling each attempt up to a maximum of 5 s) when the connection drops.
    Audio threads are safely shut down on disconnect or cancellation.

    Parameters
    ----------
    url:
        Websocket server URL.
    mic:
        Microphone streamer providing 20 ms PCM16 blocks.
    player:
        PCM player consuming audio blocks from the server.
    """

    backoff = 0.5
    while True:
        try:
            async with websockets.connect(url) as ws, mic:
                backoff = 0.5  # Reset backoff after successful connection
                player.start()

                async def _sender() -> None:
                    while True:
                        block = await mic.read_block()
                        await ws.send(block)

                async def _receiver() -> None:
                    async for message in ws:
                        if isinstance(message, bytes):
                            player.play(message)
                        else:
                            logging.info(
                                json.dumps({"type": "partial", "text": message})
                            )

                sender_task = asyncio.create_task(_sender())
                receiver_task = asyncio.create_task(_receiver())
                done, pending = await asyncio.wait(
                    {sender_task, receiver_task},
                    return_when=asyncio.FIRST_EXCEPTION,
                )

                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                for task in done:
                    task.result()
                player.stop()

        except asyncio.CancelledError:
            # Propagate cancellation to allow graceful shutdown by context managers
            raise
        except (OSError, websockets.WebSocketException) as exc:
            logging.warning(
                "Connection error: %s. Reconnecting in %.1f s", exc, backoff
            )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 5.0)
