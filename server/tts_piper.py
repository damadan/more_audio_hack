from __future__ import annotations

"""Text-to-speech utilities using Piper models."""

from pathlib import Path

import numpy as np

try:  # pragma: no cover - environment may not have onnxruntime
    import onnxruntime as ort
except Exception:  # pragma: no cover
    ort = None  # type: ignore

try:  # pragma: no cover - environment may not have piper_phonemizer
    from piper_phonemizer import piper_phonemize
except Exception:  # pragma: no cover
    piper_phonemize = None  # type: ignore


class PiperTTS:
    """Simple wrapper around a Piper ONNX model.

    Parameters
    ----------
    model_path: str
        Path to the Piper ONNX model.
    speaker_json: str
        Path to speaker configuration used for phonemization.
    """

    sample_rate = 16_000

    def __init__(self, model_path: str, speaker_json: str) -> None:
        self.model_path = model_path
        self.speaker_json = speaker_json

        if not Path(model_path).is_file():
            raise FileNotFoundError(f"Piper model not found: {model_path}")

        if ort is None:  # pragma: no cover - handled via mocks in tests
            raise RuntimeError("onnxruntime is required for PiperTTS")

        self.session = ort.InferenceSession(model_path)

    def synthesize(self, text: str) -> bytes:
        """Synthesize text into 16 kHz PCM16 audio.

        Parameters
        ----------
        text: str
            Text to synthesize.

        Returns
        -------
        bytes
            Raw PCM16 audio bytes at 16 kHz.
        """
        if piper_phonemize is None:  # pragma: no cover - handled via mocks in tests
            raise RuntimeError("piper_phonemizer is required for phonemization")

        phonemes = piper_phonemize(text, self.speaker_json)
        audio = self.session.run(None, {"input": phonemes})[0]
        audio = np.asarray(audio, dtype=np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        pcm = (audio * 32767).astype(np.int16)
        return pcm.tobytes()
