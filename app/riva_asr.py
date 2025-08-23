"""Riva ASR client wrapper."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from .schemas import ASRChunk, ASRWord


class NotConfigured(RuntimeError):
    """Raised when Riva ASR service is not configured or unavailable."""


@dataclass
class _StreamHolder:
    """Small helper container keeping Riva streaming call state.

    This object holds references to the request/response streams returned by
    the Riva python client.  It is defined merely to keep the attributes typed
    and grouped together.
    """

    requests: Any  # type: ignore[valid-type]
    responses: Any  # type: ignore[valid-type]


class RivaASR:
    """Minimal client for NVIDIA Riva streaming ASR service.

    The implementation relies on the ``riva.client`` python package.  It is not
    an optional dependency of this repository, therefore ``connect`` will raise
    :class:`NotConfigured` if the package is missing or the remote service is
    unreachable.
    """

    def __init__(
        self,
        language_code: str = "ru-RU",
        sample_rate: int = 16_000,
        hotwords: Optional[List[str]] = None,
    ) -> None:
        self.language_code = language_code
        self.sample_rate = sample_rate
        self.hotwords = hotwords or []
        self._client = None  # will hold riva.client.ASRService
        self._stream: Optional[_StreamHolder] = None

    # ------------------------------------------------------------------
    # connection management
    # ------------------------------------------------------------------
    def connect(self, host: str, creds: Optional[str] = None) -> None:
        """Connect to a Riva server.

        Parameters
        ----------
        host:
            Hostname (and port) of the Riva server.
        creds:
            Optional credential token.  When provided a secure connection is
            attempted.
        """
        try:
            import riva.client  # type: ignore

            auth = riva.client.Auth(uri=host, ssl=bool(creds), auth_token=creds)
            self._client = riva.client.ASRService(auth)
        except Exception as exc:  # pragma: no cover - depends on external pkg
            raise NotConfigured("Riva ASR is not configured") from exc

    # ------------------------------------------------------------------
    def start_stream(self, session_id: str) -> None:
        """Start streaming session with the remote ASR service."""
        if not self._client:
            raise NotConfigured("connect() must be called before start_stream()")

        try:
            import riva.client  # type: ignore

            config = riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hertz=self.sample_rate,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
                speech_contexts=[riva.client.SpeechContext(phrases=self.hotwords)],
            )
            streaming_config = riva.client.StreamingRecognitionConfig(
                config=config, interim_results=True, session_id=session_id
            )

            requests, responses = self._client.streaming_response(streaming_config)
            self._stream = _StreamHolder(requests=requests, responses=responses)
        except Exception as exc:  # pragma: no cover - depends on external pkg
            raise NotConfigured("Unable to start Riva streaming session") from exc

    # ------------------------------------------------------------------
    def send_pcm(self, data: bytes) -> None:
        """Send a chunk of raw PCM audio to the active stream."""
        if not self._stream:
            raise NotConfigured("stream is not started")
        try:
            self._stream.requests.write(data)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - external pkg
            raise NotConfigured("Failed to send audio to Riva") from exc

    # ------------------------------------------------------------------
    def recv_hypotheses(self) -> Optional[ASRChunk]:
        """Receive recognition hypotheses from the stream.

        Returns ``None`` when the stream does not yield further hypotheses.
        """
        if not self._stream:
            raise NotConfigured("stream is not started")
        try:
            response = next(self._stream.responses)  # type: ignore[attr-defined]
        except StopIteration:
            return None
        except Exception as exc:  # pragma: no cover - external pkg
            raise NotConfigured("Failed to read from Riva") from exc

        if not getattr(response, "results", None):  # pragma: no cover
            return None

        result = response.results[0]
        alternative = result.alternatives[0]
        words = [
            ASRWord(w.word, w.start_time, w.end_time, w.confidence)
            for w in getattr(alternative, "words", [])
        ]
        t0 = words[0].t0 if words else 0.0
        t1 = words[-1].t1 if words else 0.0
        chunk_type = "final" if getattr(result, "is_final", False) else "partial"
        conf = alternative.confidence if chunk_type == "final" else None

        return ASRChunk(
            type=chunk_type,
            t0=t0,
            t1=t1,
            text=alternative.transcript,
            conf=conf,
            words=words or None,
        )
