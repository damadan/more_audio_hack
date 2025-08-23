# Локальная установка

## Подготовка Python окружения

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка `.env`

```bash
cp .env.example .env
# при необходимости измените VLLM_BASE_URL, RIVA_HOST и др.
```

## Запуск vLLM с Qwen

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct --host 0.0.0.0 --port 8000
```

## Запуск FastAPI сервиса

```bash
make run  # uvicorn main:app --host 0.0.0.0 --port 8080
```

Проверка:

```bash
curl http://localhost:8080/healthz
```

## Riva ASR

- Установите NVIDIA Riva сервер и Python SDK.
- Пропишите `RIVA_HOST` в `.env`.
- Для заглушки оставьте переменную пустой — WebSocket поток будет
  использовать простую эвристику VAD.
- Поддерживаются hotwords, `enable_automatic_punctuation` и `enable_word_time_offsets`.

## XTTS‑v2 и Silero

XTTS‑v2 используется по умолчанию; при ошибке происходит fallback на Silero RU.

Пример проверки:

```python
from app.tts import synthesize, pcm_to_wav
pcm, sr = synthesize("Привет", voice=None)
open("out.wav", "wb").write(pcm_to_wav(pcm, sr))
```

## Снижение задержек

- Используйте небольшие аудио‑чанки (20 мс) в WebSocket.
- Прогрейте vLLM до начала интервью.
- Кэшируйте TTS‑ответы на стороне клиента.

