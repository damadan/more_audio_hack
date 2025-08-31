from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Protocol

import numpy as np

from rt_echo.server.buffer import RingBuffer16k
from .stabilizer import Stabilizer
from .tts import ensure_pcm16_16k


class TTS(Protocol):
    """Protocol describing minimal text-to-speech interface."""

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """Synthesize ``text`` into float32 audio and its sample rate."""
        ...


if TYPE_CHECKING:  # pragma: no cover - used only for type hints
    from .asr import AsrEngine


class EchoSession:
    """Realtime speech-to-speech echo session.

    The session accumulates incoming PCM16 audio in a :class:`RingBuffer16k`,
    periodically runs ASR to obtain text, stabilizes the hypothesis and
    speaks back newly stabilized text using provided TTS engine.
    """

    def __init__(self, config, asr: "AsrEngine", tts: TTS) -> None:
        self.config = config
        self.asr = asr
        self.tts = tts

        max_samples = int(config.asr_sr * config.window_sec)
        self.ring = RingBuffer16k(max_samples)
        self.stabilizer = Stabilizer()
        self.window_samples = max_samples
        self.step_samples = int(config.asr_sr * config.step_sec)
        self.step_sec = config.step_sec
        self.log = logging.getLogger(__name__)

    def push(self, data: bytes) -> None:
        """Append raw PCM16 bytes to the internal ring buffer."""
        self.log.debug("push %d bytes", len(data))
        self.ring.push_pcm16(data)

    async def tick(self, ws) -> None:
        """Process audio in a loop and stream synthesized speech.

        Every ``config.step_sec`` seconds the newest ``config.window_sec`` window of audio is
        transcribed. Newly stabilized text is synthesized to speech and sent
        over the provided websocket ``ws``.
        """

        try:
            while True:
                await asyncio.sleep(self.step_sec)
                self.log.debug("tick start")

                window = self.ring.window(self.window_samples)
                audio = window.astype(np.float32) / 32768.0

                start_asr = time.perf_counter()
                hyp = self.asr.transcribe_window(audio)
                mic_to_asr = time.perf_counter() - start_asr
                self.log.debug("ASR hypothesis: %s", hyp.strip())
                delta = self.stabilizer.get_delta(hyp)

                if delta:
                    start_tts = time.perf_counter()
                    audio, sr = self.tts.synthesize(delta)
                    pcm = ensure_pcm16_16k(audio, sr)
                    asr_to_tts = time.perf_counter() - start_tts

                    start_play = time.perf_counter()
                    await ws.send(pcm)
                    tts_to_play = time.perf_counter() - start_play

                    self.log.info(
                        "metrics mic→asr=%.3f asr→tts=%.3f tts→play=%.3f",
                        mic_to_asr,
                        asr_to_tts,
                        tts_to_play,
                    )
                else:
                    self.log.info("metrics mic→asr=%.3f", mic_to_asr)

                self.ring.step(self.step_samples)
                self.log.debug("tick end")
        except asyncio.CancelledError:  # pragma: no cover - cancellation flow
            pass
