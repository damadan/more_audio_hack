from __future__ import annotations

"""Automatic speech recognition utilities using faster-whisper."""

import numpy as np
from faster_whisper import WhisperModel


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
        segments, _ = self.model.transcribe(
            audio,
            language=lang,
            beam_size=1,
            vad_filter=True,
        )
        return "".join(segment.text for segment in segments)
