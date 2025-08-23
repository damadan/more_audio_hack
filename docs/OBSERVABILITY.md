# Наблюдаемость

## Метрики Prometheus

| Метрика | Описание |
|---------|----------|
| `http_requests_total{method,endpoint,http_status}` | количество HTTP‑запросов |
| `http_request_latency_seconds{method,endpoint}` | латентность HTTP |
| `asr_partial_latency_seconds` | задержка получения частичных гипотез |
| `asr_final_latency_seconds` | задержка финальных гипотез |
| `llm_latency_seconds` | время ответа LLM |
| `dm_latency_seconds{mode}` | задержка обработчика диалога |
| `tts_ttf_seconds{engine,mode}` | time‑to‑first audio |
| `tts_bytes_total{engine,mode}` | объём отданного аудио |
| `score_overall_hist` | гистограмма финальных оценок |

Метрики доступны по `GET /metrics`. Для просмотра p95 используйте запросы в
Prometheus или `histogram_quantile` в Grafana.

## Логи

- Формат JSON, PII маскируется (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`).
- Потоковые чанки ASR пишутся в `logs/stream.log`.
- Уровень логирования настраивается переменной `LOGLEVEL` (**TODO**).

## Дэшборды и алерты

- Рекомендуется настроить графики p95 латентности ASR/LLM/HTTP.
- Алерты на ошибки `5xx`, рост `asr_final_latency`, падение `llm_latency`.
- SLO: см. [ARCHITECTURE.md](ARCHITECTURE.md#целевые-slo).

