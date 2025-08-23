# Локальный запуск

## Python окружение
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Конфигурация `.env`
```bash
cp .env.example .env
# при необходимости задайте VLLM_BASE_URL, ATS_MODE и др.
```

## Запуск vLLM (REAL режим)
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct --host 0.0.0.0 --port 8000
curl http://localhost:8000/v1/models
```

## Запуск сервиса
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
curl http://localhost:8080/healthz
```

## Smoke тесты
- MOCK: `python scripts/smoke_e2e.py` (использует mock при отсутствии vLLM).
- REAL: установите `VLLM_BASE_URL=http://localhost:8000` и `ATS_MODE=real`+`MOCK_ATS_URL`, затем выполните `python scripts/smoke_e2e.py`.

## TTS веса
- При наличии весов XTTS‑v2 или Silero они используются автоматически.
- При отсутствии весов `synthesize` возвращает синусоидальный звук (TODO: скрипт bootstrap).
