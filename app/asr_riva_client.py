from __future__ import annotations

import os
from typing import Optional, List

from .schemas import ASRChunk, Word


class RivaASR:
    """Thin wrapper around NVIDIA Riva streaming ASR client."""

    def __init__(self, host: str, creds: Optional[object] = None) -> None:
        try:
            import riva.client  # type: ignore
        except ModuleNotFoundError as e:  # pragma: no cover - optional dependency
            raise NotImplementedError(
                "The 'riva' package is required to use RivaASR"
            ) from e

        self._riva = riva.client  # type: ignore
        self.host = host
        self.creds = creds
        self._client = None
        self._stream = None
        self._streaming_config = None

    # ------------------------------------------------------------------
    def connect(self, host: Optional[str] = None, creds: Optional[object] = None) -> None:
        """Initialise connection to the Riva server."""
        self.host = host or self.host
        self.creds = creds or self.creds

        auth = self._riva.Auth(uri=self.host, ssl_cert=self.creds)
        self._client = self._riva.ASRService(auth)

        hotwords_env = os.getenv("RIVA_HOTWORDS", "")
        phrases: List[str] = [w.strip() for w in hotwords_env.split(",") if w.strip()]
        speech_contexts = (
            [self._riva.SpeechContext(phrases=phrases)] if phrases else []
        )
        cfg = self._riva.RecognitionConfig(
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
            speech_contexts=speech_contexts,
        )
        self._streaming_config = self._riva.StreamingRecognitionConfig(
            config=cfg, interim_results=True
        )

    # ------------------------------------------------------------------
    def start_stream(self, session_id: str) -> None:
        if self._client is None or self._streaming_config is None:
            raise RuntimeError("Client not connected")
        self._stream = self._client.get_streaming_response(
            streaming_config=self._streaming_config, session_id=session_id
        )

    # ------------------------------------------------------------------
    def send_pcm(self, pcm: bytes) -> None:
        if self._stream is None:
            raise RuntimeError("Stream not started")
        self._stream.add_audio(pcm)

    # ------------------------------------------------------------------
    def recv_hypotheses(self) -> ASRChunk:
        if self._stream is None:
            raise RuntimeError("Stream not started")
        resp = next(self._stream)

        is_final = bool(getattr(resp, "final", False))
        text = ""
        conf = None
        words = None
        results = getattr(resp, "results", None)
        if results:
            alt = results[0].alternatives[0]
            text = alt.transcript
            conf = getattr(alt, "confidence", None)
            word_list = getattr(alt, "words", [])
            if word_list:
                words = [
                    Word(
                        w.word,
                        getattr(w, "start_time", 0.0),
                        getattr(w, "end_time", 0.0),
                        getattr(w, "confidence", 0.0),
                    )
                    for w in word_list
                ]
        chunk = ASRChunk(
            type="final" if is_final else "partial",
            t0=0.0,
            t1=0.0,
            text=text,
            conf=conf,
            words=words,
        )
        return chunk


__all__ = ["RivaASR"]
