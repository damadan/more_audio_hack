# Тестирование и QA

## Unit/contract тесты

```bash
pytest
```

Покрывают парсеры, IE, матчинг, TTS, конечные точки API и т.д. Для успешного
прогона необходимы зависимости (`fastapi`, `pydantic`, `faiss`, `dateparser`,
`requests`).

## E2E smoke

```bash
python scripts/smoke_e2e.py
```

Скрипт выполняет цепочку IE → Coverage → Rubric → Final Score → Report и печатает
итоговые `overall` и `decision`.

## Нагрузочное тестирование

- Используйте `ab` или `locust` для проверки `/stream` и `/rubric/score`.
- Измеряйте латентность, сравнивайте с SLO.

## Статический анализ

```bash
flake8 .
```

## Известные проблемы

- Запуск тестов без установленных ML‑зависимостей приводит к ошибкам
  `ModuleNotFoundError` (см. `requirements.txt`).

