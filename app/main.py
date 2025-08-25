from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from .api.server import router
from .observability.logging import setup_logging

setup_logging()

app = FastAPI()
app.include_router(router)
app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
