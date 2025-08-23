# API
Все ответы в JSON, если не указано иное. Схемы описаны в [SCHEMAS.md](SCHEMAS.md).

## POST /interview/start
Создаёт сессию интервью и возвращает `session_id` и `ws_url`.
`ws_url` берётся из `WS_BASE_URL` или собирается из `X-Forwarded-Proto`/`X-Forwarded-Host`.
```bash
curl -s -X POST http://localhost:8080/interview/start
```
Пример ответа:
```json
{"session_id":"uuid","ws_url":"ws://localhost:8080/stream/uuid"}
```

## WS /stream/{session_id}
WebSocket для передачи PCM 16 кГц (бинарные фреймы) и получения `ASRChunk`.
- Бинарные кадры: PCM16LE. Текст `END` завершает поток.
- JSON кадры: `{"type":"partial|final","t0":0.0,"t1":0.0,"text":"..."}`.

## POST /tts
Синтез речи. Тело — `TTSRequest`. Возвращает поток WAV (`audio/wav`) или PCM (`audio/L16`).
```bash
curl -X POST http://localhost:8080/tts -H 'Content-Type: application/json' -d '{"text":"Привет"}' --output out.wav
```

## POST /dm/next
Возвращает следующее действие диалогового менеджера (`NextAction`).
Mock режим включается `?mock=1` или заголовком `X-Mock: 1`. Если `VLLM_BASE_URL` недоступен, мок используется автоматически.

## POST /ie/extract
IE/NER из транскрипта. Тело — `IEExtractRequest`, ответ — `IE`.

## POST /match/coverage
Расчёт покрытия JD. Тело — `CoverageRequest`, ответ — `Coverage`.

## POST /rubric/score
Оценка по рубрике. Тело — `RubricScoreRequest`, ответ — `Rubric`. Поддерживает mock так же, как `/dm/next`.

## POST /score/final
Финальный скоринг. Тело — `FinalScoreRequest`, ответ — `FinalScore`.

## POST /report
Генерация отчёта. Тело — `ReportRequest`. `fmt=html` (по умолчанию) или `fmt=pdf`.

## POST /ats/sync
Синхронизация с ATS. Тело — `ATSSyncRequest`.
- По умолчанию `ATS_MODE=mock` → статус `202` и `{"status":"mock-accepted"}`.
- При `ATS_MODE=real` запрос пересылается на `MOCK_ATS_URL`.

## GET /healthz
Проверка работоспособности.

## GET /metrics
Prometheus‑метрики.

## Коды ошибок
- `400` — валидация или неверный запрос
- `500` — ошибка сервера/LLM
- `502` — внешняя интеграция недоступна (ATS)
