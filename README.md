# AI Interview Assistant

Минимально жизнеспособный прототип сервиса, помогающего проводить и
оценивать технические интервью.  Реализованы ключевые API-эндпоинты и
несколько лёгких моделей, что позволяет запускать систему локально или в
docker.

## Требования
- Python 3.10+
- FFmpeg для синтеза речи
- GPU (необязательно)

## Установка
```bash
pip install -r requirements.txt
```

## Переменные окружения
Создайте файл `.env` и заполните значения:
```
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL=Qwen/Qwen2.5-14B-Instruct
VLLM_API_KEY=dummy
RIVA_HOST=localhost:50051   # или пусто для заглушки
USE_XTTS=1
SILERO_VOICE=aidar
HR_EMB_BACKEND=BGE_M3   # CONSULTANTBERT|TAROT|BGE_M3
MOCK_ATS_URL=http://localhost:9999/ats
```

## Запуск локального vLLM
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct --max-model-len 8192
```

## Docker Compose
Пример `docker-compose.yaml` уже включён в репозиторий.  Он поднимает
сервис `app` на порту `8080` и монтирует каталог `data/` вместе с томом
для FAISS-индекса.

Запуск:
```bash
docker compose up -d
```

## Makefile команды
- `make run` – старт сервиса на `http://0.0.0.0:8080`
- `make test` – запустить тесты
- `python scripts/smoke_e2e.py` – сквозной прогон API

## Эндпоинты
- `GET /healthz` – проверка работоспособности
- `POST /ie/extract` – извлечение сущностей из транскрипта
- `POST /match/coverage` – покрытие JD индикаторами
- `POST /rubric/score` – оценка по рубрике
- `POST /score/final` – финальный скоринг
- `POST /report` – HTML отчёт

Пример запроса:
```bash
curl -X POST http://localhost:8080/ie/extract \
  -H 'Content-Type: application/json' \
  -d '{"transcript":"Мы используем Docker"}'
```

## Тестовые данные
- `data/jd_ml_engineer.json` – пример JD
- `data/transcripts/ru_sample.jsonl` – фрагменты диалога

## Smoke тест
После запуска сервиса можно выполнить:
```bash
python scripts/smoke_e2e.py
```
Он последовательно вызывает основные эндпоинты и печатает итоговый
скоринг.
