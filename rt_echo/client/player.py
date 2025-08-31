from typing import Optional

import numpy as np
import sounddevice as sd


class PcmPlayer:
    def __init__(self, samplerate: int = 16000) -> None:
        self._sr = samplerate
        self._stream: Optional[sd.OutputStream] = None

    def start(self) -> None:
        if self._stream is None:
            self._stream = sd.OutputStream(samplerate=self._sr, channels=1, dtype="int16")
            self._stream.start()

    def play(self, pcm: bytes) -> None:
        assert self._stream is not None
        arr = np.frombuffer(pcm, dtype=np.int16)
        self._stream.write(arr)

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None


__all__ = ["PcmPlayer"]

