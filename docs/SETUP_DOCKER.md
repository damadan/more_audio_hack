# Запуск в Docker

## docker-compose.yaml
```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    env_file: .env
    command: uvicorn main:app --host 0.0.0.0 --port ${APP_PORT:-8080}
    volumes:
      - ./data:/app/data
      - faiss-index:/app/index
  vllm:
    image: vllm/vllm-openai:latest
    profiles: ["real"]
    ports:
      - "8000:8000"
    command: python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-14B-Instruct --port 8000
    healthcheck:
      test: ["CMD","curl","-f","http://localhost:8000/v1/models"]
      interval: 30s
      timeout: 10s
      retries: 5
volumes:
  faiss-index:
```

## Запуск
```bash
docker compose up -d    # профиль real подтянет сервис vllm
```
Сервис доступен на `http://localhost:8080`.

## Остановка
```bash
docker compose down
```

## Примечания
- `.env` автоматически монтируется в контейнер `app`.
- Том `faiss-index` хранит FAISS индекс и кэш эмбеддингов.
- Для real режима задайте `VLLM_BASE_URL=http://vllm:8000` и `ATS_MODE=real` в `.env`.
