# Запуск в Docker

## Требования

- Docker 20+
- docker-compose 2+
- Для vLLM/XTTS рекомендуется GPU (NVIDIA, поддержка `--gpus all`).

## docker-compose

В репозитории есть пример `docker-compose.yaml`:

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    env_file: .env
    command: uvicorn main:app --host 0.0.0.0 --port 8080
    volumes:
      - ./data:/app/data
      - faiss-index:/app/index
volumes:
  faiss-index:
```

## Запуск

```bash
docker compose up -d
docker compose logs -f app
```

Сервис будет доступен на `http://localhost:8080`.

Остановка:

```bash
docker compose down
```

## Типичные проблемы

- Отсутствие GPU ⇒ vLLM/XTTS работают медленно; используйте CPU или
  уменьшите модель.
- Ошибка подключения к vLLM ⇒ проверьте `VLLM_BASE_URL` внутри контейнера.
- Недоступен Riva ⇒ убедитесь, что `RIVA_HOST` доступен из контейнера.

