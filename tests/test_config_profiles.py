import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from rt_echo.common.config import load_config


def test_fast_profile(monkeypatch):
    monkeypatch.setenv("APP_PROFILE", "fast")
    cfg = load_config()
    assert cfg.asr_model == "small"
    assert cfg.asr_compute_type == "int8"
    assert cfg.window_sec == 0.8
    assert cfg.step_sec == 0.25


def test_quality_profile(monkeypatch):
    monkeypatch.setenv("APP_PROFILE", "quality")
    cfg = load_config()
    assert cfg.asr_model == "large-v3"
    assert cfg.asr_compute_type == "fp16"
