from __future__ import annotations

from collections import deque
from typing import Deque

import numpy as np


class RingBuffer16k:
    """Ring buffer for 16 kHz PCM16 audio samples.

    The buffer stores signed 16-bit integers and provides convenient methods
    to push raw PCM16 bytes, obtain a sliding window of samples and advance
    the window. If the requested window is larger than the amount of data
    available in the buffer, the result is padded with zeros at the
    beginning.
    """

    def __init__(self, max_samples: int = 16000 * 2) -> None:
        """Create a ring buffer.

        Parameters
        ----------
        max_samples:
            Maximum number of samples to keep in the buffer. Defaults to
            two seconds of audio at 16 kHz.
        """
        self.max_samples = max_samples
        self._buf: Deque[int] = deque(maxlen=max_samples)

    def push_pcm16(self, data: bytes) -> None:
        """Append raw PCM16 bytes to the buffer."""
        if not data:
            return
        samples = np.frombuffer(data, dtype=np.int16)
        self._buf.extend(int(s) for s in samples)

    def window(self, samples: int) -> np.ndarray:
        """Return the newest ``samples`` samples as a NumPy array.

        If there are fewer samples available, the array is left-padded with
        zeros to reach the requested length.
        """
        if samples <= 0:
            return np.zeros(0, dtype=np.int16)

        arr = np.fromiter(self._buf, dtype=np.int16)
        if arr.size >= samples:
            return arr[-samples:]

        pad = samples - arr.size
        return np.concatenate((np.zeros(pad, dtype=np.int16), arr))

    def step(self, samples: int) -> None:
        """Advance the buffer by removing ``samples`` samples from the left."""
        for _ in range(min(samples, len(self._buf))):
            self._buf.popleft()
