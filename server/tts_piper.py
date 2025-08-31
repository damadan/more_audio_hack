"""Text-to-speech utilities using Piper models."""

from __future__ import annotations

from pathlib import Path

import logging
import numpy as np

try:  # pragma: no cover - environment may not have onnxruntime
    import onnxruntime as ort
except Exception:  # pragma: no cover
    ort = None  # type: ignore

try:  # pragma: no cover - environment may not have piper_phonemizer
    from piper_phonemizer import piper_phonemize
except Exception:  # pragma: no cover
    piper_phonemize = None  # type: ignore


log = logging.getLogger(__name__)


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

    def __init__(
        self,
        model_path: str,
        speaker_json: str,
        model_sample_rate: int | None = None,
    ) -> None:
        self.model_path = model_path
        self.speaker_json = speaker_json
        self.model_sample_rate = model_sample_rate or self.sample_rate

        if not Path(model_path).is_file():
            raise FileNotFoundError(f"Piper model not found: {model_path}")

        if ort is None:  # pragma: no cover - handled via mocks in tests
            raise RuntimeError("onnxruntime is required for PiperTTS")

        self.session = ort.InferenceSession(model_path)
        log.info("Piper model loaded: %s", model_path)

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """Synthesize text into float32 audio and sample rate.

        Parameters
        ----------
        text: str
            Text to synthesize.

        Returns
        -------
        tuple[np.ndarray, int]
            Generated audio in ``float32`` format and its sample rate.
        """
        if piper_phonemize is None:  # pragma: no cover - handled via mocks in tests
            raise RuntimeError("piper_phonemizer is required for phonemization")

        log.debug("synthesize text length=%d", len(text))
        phonemes = piper_phonemize(text, self.speaker_json)
        audio = self.session.run(None, {"input": phonemes})[0]
        audio = np.asarray(audio, dtype=np.float32)
        audio = np.clip(audio, -1.0, 1.0)

        log.debug("synthesize produced %d samples", len(audio))
        return audio, self.model_sample_rate
