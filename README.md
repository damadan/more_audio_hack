# Interview Assistant MVP

## Quickstart

### CPU

```bash
pip install -r requirements.txt
make run-server
make run-client
```

### GPU

```bash
docker compose --profile gpu up --build --gpus all
```

## Supported Russian voices for Piper

- denis
- dmitri
- irina
- ruslan

## Latency reduction tips

- Use smaller ASR models (`ASR_MODEL=small`).
- Run ASR and TTS on GPU when available (`ASR_DEVICE=gpu`).
- Stream shorter audio chunks (20 ms) to the server.
- Preload models to avoid cold starts.
