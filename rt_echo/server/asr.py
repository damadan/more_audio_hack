"""Compatibility wrapper adapting :class:`AsrEngine` from ``server.asr``."""

from types import SimpleNamespace

from server.asr import AsrEngine as _AsrEngine


class AsrEngine(_AsrEngine):
    """Adapter that mirrors new constructor signature.

    Parameters
    ----------
    model: str
        Whisper model identifier.
    device: str
        Device to run the model on.
    compute_type: str
        Computation type passed to Faster-Whisper.
    """

    def __init__(self, model: str, device: str, compute_type: str):
        cfg = SimpleNamespace(
            asr_model=model, asr_device=device, asr_compute_type=compute_type
        )
        super().__init__(cfg)


__all__ = ["AsrEngine"]

