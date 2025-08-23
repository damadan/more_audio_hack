# AI Interview Assistant

AI Interview Assistant проводит техническое собеседование и автоматически
оценяет ответы кандидата. Сервис принимает аудиопоток, расшифровывает речь,
управляет диалогом через LLM, извлекает навыки и проекты, сопоставляет их с
вакансией, выставляет оценки по рубрике и возвращает итоговый отчёт.

## Архитектура на пальцах

```mermaid
graph LR
    A[Клиент / WebRTC] -->|PCM 16 kHz| B(ASR / Riva)
    B --> C(Dialog Manager / Qwen)
    C --> D(TTS)
    C --> E(IE & Matching)
    E --> F(Rubric / Qwen)
    F --> G(Final Scoring / CatBoost)
    G --> H(Report)
```

## Быстрый старт

### 1) MOCK‑режим (без vLLM)

1. Подготовьте окружение и запустите сервис:
   ```bash
   cp .env.example .env  # укажите APP_PORT и WS_BASE_URL при необходимости
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```
2. Прогоните smoke‑тест (он автоматически добавит `?mock=1` для рубрики):
   ```bash
   python scripts/smoke_e2e.py
   ```

### 2) REAL‑режим (с vLLM)

1. Запустите vLLM с моделью Qwen‑2.5‑14B‑Instruct:
   ```bash
   python -m vllm.entrypoints.openai.api_server \
       --model Qwen/Qwen2.5-14B-Instruct --host 0.0.0.0 --port 8000
   ```
2. Запустите сервис (`make run` или `docker compose up -d`).
3. Выполните тот же `python scripts/smoke_e2e.py` — тест пойдёт в REAL‑режиме.

Пример запроса к `/interview/start`:

```bash
curl -s -X POST http://localhost:8080/interview/start
# {"session_id": "...", "ws_url": "ws://localhost:8080/stream/..."}
```

`ws_url` берётся из `WS_BASE_URL` или собирается из заголовков
`X-Forwarded-Proto/Host` при работе за прокси.

## Smoke‑тест

Скрипт `scripts/smoke_e2e.py` вызывает `/ie/extract → /match/coverage →
/rubric/score → /score/final → /report` и печатает:

```
overall: 0.73
decision: move
report length: 12345
```

## Ссылки на документацию

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API.md](docs/API.md)
- [docs/SCHEMAS.md](docs/SCHEMAS.md)
- [docs/SETUP_LOCAL.md](docs/SETUP_LOCAL.md)
- [docs/SETUP_DOCKER.md](docs/SETUP_DOCKER.md)
- [docs/ENV_VARS.md](docs/ENV_VARS.md)
- Остальные документы см. в каталоге `docs/`.

## Troubleshooting

- Проверьте, что запущен vLLM и доступен `VLLM_BASE_URL`.
- Отсутствие зависимостей приводит к ошибкам при запуске тестов — установите
  пакеты из `requirements.txt`.
- Для работы TTS необходимы веса XTTS‑v2 или Silero; при их отсутствии будет
  сгенерирован синусоидальный звук.

## Known Issues

- В репозитории отсутствуют реальные веса моделей (vLLM, XTTS‑v2, FAISS
  индексы). Их нужно загрузить отдельно.
- Поддержка Riva ASR и генерации PDF отчёта требует дополнительных
  зависимостей.
- Без запущенного vLLM необходимо использовать `?mock=1`/`X-Mock: 1` для
  `/rubric/score` и smoke‑теста.

