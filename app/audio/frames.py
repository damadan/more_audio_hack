from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class AudioFrame:
    pcm: np.ndarray  # int16, shape (N,)
    sample_rate: int  # 16000
    t0: float  # seconds from session start
    t1: float  # t0 + N / sample_rate
