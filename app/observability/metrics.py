from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

asr_partial_latency_ms = Histogram("asr_partial_latency_ms", "Partial latency", buckets=(50, 100, 200, 400, 800))
asr_final_latency_ms = Histogram("asr_final_latency_ms", "Final latency", buckets=(100, 200, 400, 800, 1600))
refine_latency_ms = Histogram("refine_latency_ms", "Hybrid refine latency", buckets=(100, 200, 400, 800, 1600))
endpoint_errors_total = Counter("endpoint_errors_total", "Endpoint errors")
sessions_active = Gauge("sessions_active", "Active sessions")
