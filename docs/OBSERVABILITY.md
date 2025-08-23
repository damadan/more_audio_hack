# Наблюдаемость

## Метрики Prometheus
| Метрика | Описание |
|---------|----------|
| `http_requests_total{method,endpoint,http_status}` | количество HTTP‑запросов |
| `http_request_latency_seconds{method,endpoint}` | латентность HTTP |
| `asr_partial_latency_seconds` | задержка частичных гипотез |
| `asr_final_latency_seconds` | задержка финальных гипотез |
| `llm_latency_seconds` | время ответа LLM |
| `dm_latency_seconds{mode}` | задержка диалогового менеджера |
| `tts_ttf_seconds{engine,mode}` | time‑to‑first audio |
| `tts_bytes_total{engine,mode}` | объём отданного аудио |
| `score_overall_hist` | гистограмма итоговых оценок |

Эндпоинт `GET /metrics` отдаёт их в формате Prometheus.
Пример запроса p95 в Prometheus:
```promql
histogram_quantile(0.95, sum(rate(http_request_latency_seconds_bucket[5m])) by (le,endpoint))
```

## Логи
- JSON формат, PII маскируется (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`).
- ASR чанки пишутся в `logs/stream.log`.

## TODO
- Переменная `LOGLEVEL` для управления уровнем логов.
- Дэшборды и алерты для SLO (см. [ARCHITECTURE.md](ARCHITECTURE.md#slo)).
