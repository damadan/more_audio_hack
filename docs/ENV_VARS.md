# Переменные окружения

| Переменная | Тип/значение по умолчанию | Описание |
|------------|---------------------------|----------|
| `APP_HOST` | `str`, `0.0.0.0` | Адрес, на котором слушает FastAPI. |
| `APP_PORT` | `int`, `8080` | Порт HTTP и WebSocket сервера. |
| `WS_BASE_URL` | `str`, `ws://localhost:8080` | Базовый URL для `ws_url` в `/interview/start`. |
| `VLLM_BASE_URL` | `str`, *нет* | Базовый URL сервера vLLM. |
| `VLLM_MODEL` | `str`, `Qwen/Qwen2.5-14B-Instruct` | Имя модели vLLM. |
| `VLLM_API_KEY` | `str`, пусто | API‑ключ для vLLM (опционально). |
| `ALLOW_RUBRIC_MOCK` | `int`, `1` | Разрешить mock `/rubric/score`. |
| `ALLOW_DM_MOCK` | `int`, `1` | Разрешить mock `/dm/next`. |
| `ATS_MODE` | `str`, `mock` | Режим интеграции с ATS (`mock`/`real`). |
| `MOCK_ATS_URL` | `str`, *нет* | Endpoint ATS для real режима. |
| `HR_EMB_BACKEND` | `str`, `BGE_M3` | Бэкенд эмбеддингов JD. |
| `TTS_ENGINE` | `str`, `xtts` | **TODO:** выбор движка TTS (не используется в коде). |
| `SILERO_VOICE` | `str`, `aidar` | **TODO:** голос Silero (не используется в коде). |
| `FAISS_INDEX_PATH` | `str`, `data/faiss.index` | **TODO:** путь к FAISS индексу (не используется в коде). |
