# Наблюдаемость

## Метрики Prometheus

| Метрика | Описание |
|---------|----------|
| `http_requests_total{method,endpoint,http_status}` | количество HTTP‑запросов |
| `request_latency_seconds{method,endpoint}` | латентность HTTP |
| `asr_partial_latency` | задержка получения частичных гипотез |
| `asr_final_latency` | задержка финальных гипотез |
| `score_overall_hist` | гистограмма финальных оценок |
| `llm_latency` | время ответа LLM |

Метрики доступны по `GET /metrics`.

## Логи

- Формат JSON, PII маскируется (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`).
- Потоковые чанки ASR пишутся в `logs/stream.log`.
- Уровень логирования настраивается переменной `LOGLEVEL` (**TODO**).

## Дэшборды и алерты

- Рекомендуется настроить графики p95 латентности ASR/LLM/HTTP.
- Алерты на ошибки `5xx`, рост `asr_final_latency`, падение `llm_latency`.
- SLO: см. [ARCHITECTURE.md](ARCHITECTURE.md#целевые-slo).

