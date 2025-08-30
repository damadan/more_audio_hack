.PHONY: run-server run-client lint typecheck test

run-server:
	python -m server.server

run-client:
	python - <<'PY'
import asyncio
from rt_echo.client import MicStreamer, PcmPlayer
from rt_echo.client.ws_client import run
asyncio.run(run("ws://localhost:8000", MicStreamer(), PcmPlayer()))
PY

lint:
	ruff check .

typecheck:
	mypy server tests --ignore-missing-imports

test:
	pytest
