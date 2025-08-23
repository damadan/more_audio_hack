# Система оценивания

## Rubric scoring

- Промпт строится функцией `build_rubric_prompt` и включает JD,
  транскрипт/IE и (опционально) Coverage.
- Запрос выполняется дважды (`generate_json`), результаты валидируются и
  объединяются `merge_rubrics` для устойчивости.
- Возвращаются `scores` (0–5), `red_flags` и `evidence` с таймкодами.

Пример промпта (сокр.):

```
You are evaluating a candidate.
Score each competency from 0 to 5...
```

## Финальный скоринг

Функция `final_score` строит признаки `build_features` и предсказывает
вероятность успеха:

- `coverage_*` — покрытие компетенций
- `rubric_*` — оценки рубрики
- `years_*` — годы опыта
- `count_metrics`, `count_numbers`, `contradictions`, `toxicity`, `ko_flags`
- `asr_conf`, `title_canonical`

Если присутствует модель `models/catboost.cbm` и `calibrator.pkl`, используется
CatBoost. Иначе применяется простая логистическая регрессия по средним
`coverage` и `rubric`.

Пороговые значения:

- `prob > 0.8` → `move`
- `prob > 0.6` → `discuss`
- иначе → `reject`

`SCORE_OVERALL_HIST` фиксирует распределение итоговых оценок.

