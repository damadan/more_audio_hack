# API

Все ответы возвращаются в формате JSON, если не указано иное.

## `POST /interview/start`
Создаёт новую сессию интервью и возвращает идентификатор и URL WebSocket.

**Response**
```json
{"session_id": "uuid", "ws_url": "ws://host/stream/<id>"}
```

## `WS /stream/{session_id}`
Двунаправленный поток для передачи PCM 16 кГц и получения результатов ASR.

### Бинарные фреймы
Сырые PCM‑16LE. Для завершения передачи отправьте текстовое сообщение `END`.

### JSON‑сообщения
`ASRChunk` с типом `partial` или `final`.

```json
{"type": "partial", "t0": 0.0, "t1": 0.0, "text": "hello"}
```

## `POST /tts`
Синтез речи. Тело запроса — `TTSRequest`. Возвращает поток PCM или WAV.

```bash
curl -X POST http://localhost:8080/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Привет"}' --output out.wav
```

## `POST /dm/next`
Запрос следующего действия диалогового менеджера. Тело — `DMRequest`.

## `POST /ie/extract`
IE/NER из транскрипта. Тело — `IEExtractRequest`, ответ — `IE`.

## `POST /match/coverage`
Покрытие JD индикаторами. Тело — `CoverageRequest`, ответ — `Coverage`.

## `POST /rubric/score`
Оценка по рубрике. Тело — `RubricScoreRequest`, ответ — `Rubric`.

## `POST /score/final`
Финальный скоринг. Тело — `FinalScoreRequest`, ответ — `FinalScore`.

## `POST /report`
Генерация отчёта. Тело — `ReportRequest`, параметр `fmt=html|pdf`.

## `POST /ats/sync`
Синхронизация с ATS. Тело — `ATSSyncRequest`.

## `GET /healthz`
Проверка работоспособности.

## `GET /metrics`
Прометей‑метрики.

## Коды ошибок

- `400` — некорректный запрос
- `500` — ошибка сервера или внешнего сервиса
- `502` — недоступна интеграция (например, ATS)

Подробные описания схем см. в [SCHEMAS.md](SCHEMAS.md).

