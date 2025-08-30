import os
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rt_echo.common.audio import float32_to_pcm16, resample
from server.tts_piper import PiperTTS


class DummySession:
    def __init__(self, expected_path: str, audio: np.ndarray):
        self.expected_path = expected_path
        self.audio = audio

    def run(self, *_args, **_kwargs):
        return [self.audio]


def test_synthesize(monkeypatch, tmp_path):
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"")
    speaker_json = tmp_path / "speaker.json"
    speaker_json.write_text("{}")

    audio = np.array([0.0, 0.5, -0.5], dtype=np.float32)

    dummy_session = DummySession(str(model_path), audio)
    monkeypatch.setattr(
        "server.tts_piper.ort",
        SimpleNamespace(InferenceSession=lambda path: dummy_session),
    )
    monkeypatch.setattr(
        "server.tts_piper.piper_phonemize",
        lambda text, speaker: np.array([1, 2, 3], dtype=np.int64),
    )

    tts = PiperTTS(str(model_path), str(speaker_json))
    pcm_bytes = tts.synthesize("hello")

    expected = float32_to_pcm16(audio)
    assert pcm_bytes == expected


def test_missing_model(tmp_path):
    speaker_json = tmp_path / "speaker.json"
    speaker_json.write_text("{}")

    with pytest.raises(FileNotFoundError):
        PiperTTS(str(tmp_path / "missing.onnx"), str(speaker_json))


def test_resample(monkeypatch, tmp_path):
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"")
    speaker_json = tmp_path / "speaker.json"
    speaker_json.write_text("{}")

    audio = np.linspace(-1, 1, 8, dtype=np.float32)

    dummy_session = DummySession(str(model_path), audio)
    monkeypatch.setattr(
        "server.tts_piper.ort",
        SimpleNamespace(InferenceSession=lambda path: dummy_session),
    )
    monkeypatch.setattr(
        "server.tts_piper.piper_phonemize",
        lambda text, speaker: np.array([1, 2, 3], dtype=np.int64),
    )

    tts = PiperTTS(str(model_path), str(speaker_json), model_sample_rate=8_000)
    pcm_bytes = tts.synthesize("hello")

    expected_audio = resample(audio, 8_000, tts.sample_rate)
    expected = float32_to_pcm16(expected_audio)
    assert pcm_bytes == expected
