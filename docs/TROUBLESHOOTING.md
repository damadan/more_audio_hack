# Troubleshooting

| Проблема | Решение |
|----------|---------|
| Нет соединения с vLLM → `/dm/next` или `/rubric/score` 500 | Запустите vLLM или вызовите с `?mock=1` и `X-Mock: 1` (`ALLOW_*_MOCK` должно быть `1`). |
| `/ats/sync` возвращает 502 в режиме real | Установите `MOCK_ATS_URL` или переключите `ATS_MODE=mock` (по умолчанию). |
| Неверный `ws_url` в `/interview/start` | Проверьте `WS_BASE_URL`, `APP_PORT` и заголовки `X-Forwarded-*` у прокси. |
| Ошибка TTS или нет аудио | Загрузите веса XTTS/Silero или используйте синус‑фолбэк. |
| Отсутствует FAISS индекс | Том `faiss-index` пуст → пересоздайте его или выполните bootstrap (**TODO**). |
