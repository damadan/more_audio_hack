# Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VLLM_BASE_URL` | Базовый URL OpenAI‑совместимого API vLLM | `http://localhost:8000` |
| `VLLM_MODEL` | Имя модели vLLM | `Qwen/Qwen2.5-14B-Instruct` |
| `VLLM_API_KEY` | API‑ключ (можно оставить пустым) | `dummy` |
| `RIVA_HOST` | `host:port` сервера NVIDIA Riva; пусто ⇒ заглушка | `localhost:50051` |
| `USE_XTTS` | Включить XTTS‑v2 (1/0) | `1` |
| `SILERO_VOICE` | Голос Silero (fallback) | `aidar` |
| `HR_EMB_BACKEND` | Бэкенд эмбеддингов (`CONSULTANTBERT`, `TAROT`, `BGE_M3`) | `BGE_M3` |
| `MOCK_ATS_URL` | URL мок‑сервиса ATS для `/ats/sync` | `http://localhost:9999/ats` |

Дополнительно, при интеграции Riva можно задать hotwords и флаги для
пунктуации/таймстампов (**TODO: переменные не реализованы**).

