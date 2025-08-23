# Interview Assistant MVP (skeleton)

Этот репозиторий очищен. Содержит только README.
Исходный код сервисов ASR/TTS/LLM/IE/Scoring удалён.
Используй как заготовку для новой разработки.

## Запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Smoke test

После запуска сервиса можно проверить его доступность:

```bash
curl -sS localhost:8000/healthz
```
