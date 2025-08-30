"""Voice Activity Detection utilities using webrtcvad."""

from __future__ import annotations

import numpy as np
import webrtcvad

_vad = webrtcvad.Vad(2)


def active_mask(int16_pcm: np.ndarray, sr: int = 16000, frame_ms: int = 20) -> np.ndarray:
    """Return boolean array of speech activity for each frame.

    Parameters
    ----------
    int16_pcm: np.ndarray
        1-D numpy array of int16 PCM samples.
    sr: int
        Sample rate of the audio, defaults to 16 kHz.
    frame_ms: int
        Frame size in milliseconds, defaults to 20 ms.

    Returns
    -------
    np.ndarray
        Boolean array with length equal to number of frames, where True
        indicates presence of speech in the corresponding frame.
    """
    frame_len = int(sr * frame_ms / 1000)
    n_frames = len(int16_pcm) // frame_len
    mask = np.zeros(n_frames, dtype=bool)

    for i in range(n_frames):
        frame = int16_pcm[i * frame_len:(i + 1) * frame_len]
        mask[i] = _vad.is_speech(frame.tobytes(), sr)

    return mask


def trim_silence_head_tail(pcm: np.ndarray, sr: int = 16000, frame_ms: int = 20) -> np.ndarray:
    """Trim leading and trailing silence from PCM audio."""
    mask = active_mask(pcm, sr=sr, frame_ms=frame_ms)
    if not mask.any():
        return pcm[:0]

    frame_len = int(sr * frame_ms / 1000)
    start_frame = mask.argmax()
    end_frame = len(mask) - mask[::-1].argmax()
    return pcm[start_frame * frame_len:end_frame * frame_len]


def is_speech_present(pcm: np.ndarray, sr: int = 16000, frame_ms: int = 20) -> bool:
    """Return True if any speech detected in the PCM audio."""
    return bool(active_mask(pcm, sr=sr, frame_ms=frame_ms).any())
