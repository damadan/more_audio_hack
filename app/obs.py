import time
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus metric definitions
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)

request_latency_seconds = Histogram(
    "request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
)

asr_partial_latency = Histogram(
    "asr_partial_latency",
    "Latency of partial ASR results in seconds",
)

asr_final_latency = Histogram(
    "asr_final_latency",
    "Latency of final ASR results in seconds",
)

llm_latency = Histogram(
    "llm_latency",
    "Latency of LLM responses in seconds",
)

score_overall_hist = Histogram(
    "score_overall_hist",
    "Histogram of overall scores",
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start_time
        endpoint = request.url.path
        request_latency_seconds.labels(endpoint=endpoint).observe(latency)
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()
        return response


def setup_metrics(app: FastAPI) -> None:
    """Attach Prometheus metrics middleware and endpoint."""

    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics")
    async def metrics() -> Response:  # pragma: no cover - simple wrapper
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
