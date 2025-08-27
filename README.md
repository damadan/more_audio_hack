# AI Interview Assistant

Этот репозиторий намеренно оставлен в виде одного README. Исходный код удалён из ветки по дате 2025-08-25.

## Архив
- Тег: `archive-pre-readme-only-20250825`
- Ветка: `archive/full-code-20250825`

## Причина
Очистка репозитория перед передачей прав и выпуск закрытой версии.

## Контакты
- info@example.com

## История
Снимок полного кода доступен по тегу `archive-pre-readme-only-20250825` и ветке `archive/full-code-20250825`.

## Качество и конфиг

* Навыки и синонимы расширяются в `data/skills_taxonomy.csv`. Каждая строка содержит колонку `canonical` и список `synonyms` через `;`.
* Веса скоринга, пороги RapidFuzz и семантического совпадения настраиваются в `config/scoring.yaml`.
* Для ускорения загрузки моделей Sentence-Transformers можно заранее скачать их в каталог, указанный переменной `MODELS_DIR`. Для кэша HuggingFace используется `HF_HOME` (по умолчанию `~/.cache/huggingface`).
* Docker-сборка: `docker build -t hr-match .` и запуск `docker run hr-match`.
