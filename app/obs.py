from __future__ import annotations

"""Prometheus metrics for the service."""

from prometheus_client import Counter, Histogram

# HTTP layer
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
HTTP_REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency", ["method", "endpoint"]
)

# ASR metrics
ASR_PARTIAL_LATENCY = Histogram(
    "asr_partial_latency_seconds", "ASR partial latency"
)
ASR_FINAL_LATENCY = Histogram(
    "asr_final_latency_seconds", "ASR final latency"
)

# LLM metrics
LLM_LATENCY = Histogram("llm_latency_seconds", "LLM latency")

# Dialog manager metrics
DM_LATENCY = Histogram(
    "dm_latency_seconds", "Dialog manager latency", ["mode"]
)

# TTS metrics
TTS_TTF_SECONDS = Histogram(
    "tts_ttf_seconds", "Time to first audio byte", ["engine", "mode"]
)
TTS_BYTES_TOTAL = Counter(
    "tts_bytes_total", "Total bytes returned by TTS", ["engine", "mode"]
)

# Scoring metrics
SCORE_OVERALL_HIST = Histogram("score_overall_hist", "Final score histogram")

__all__ = [
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_LATENCY",
    "ASR_PARTIAL_LATENCY",
    "ASR_FINAL_LATENCY",
    "LLM_LATENCY",
    "DM_LATENCY",
    "TTS_TTF_SECONDS",
    "TTS_BYTES_TOTAL",
    "SCORE_OVERALL_HIST",
]
