"""Automatic speech recognition utilities using faster-whisper."""

from __future__ import annotations

import logging
import numpy as np
from faster_whisper import WhisperModel


log = logging.getLogger(__name__)


class AsrEngine:
    """Thin wrapper around :class:`WhisperModel` for windowed transcription."""

    def __init__(self, config) -> None:
        """Load Whisper model using configuration.

        Parameters
        ----------
        config:
            Application configuration with ASR parameters.
        """
        self.model = WhisperModel(
            config.asr_model,
            device=config.asr_device,
            compute_type=config.asr_compute_type,
        )
        log.info("ASR model loaded: %s", config.asr_model)

    def transcribe_window(self, audio: np.ndarray, lang: str = "ru") -> str:
        """Transcribe a window of PCM audio and return recognized text.

        Parameters
        ----------
        audio: np.ndarray
            Float32 PCM audio samples at expected sample rate.
        lang: str, optional
            Language code for transcription, defaults to ``"ru"``.

        Returns
        -------
        str
            Concatenated text from all transcription segments.
        """
        log.debug("transcribe window size=%d", len(audio))
        segments, _ = self.model.transcribe(
            audio,
            language=lang,
            beam_size=1,
            vad_filter=True,
        )
        text = "".join(segment.text for segment in segments)
        log.debug("transcription result: %s", text.strip())
        return text
