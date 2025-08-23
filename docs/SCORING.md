# Система оценивания

## Rubric scoring
- `build_rubric_prompt` формирует запрос с JD, транскриптом/IE и Coverage.
- `LLMClient.generate_json` (Qwen в JSON‑режиме) вызывается дважды; `merge_rubrics` объединяет результаты (self‑consistency ≥2).
- Возвращаются `scores` (0‑5), `red_flags` и `evidence` с таймкодами.
- Mock режим: `score_rubric_mock` выдаёт детерминированные баллы.

Пример фрагмента промпта:
```
You are evaluating a candidate.
Score each competency from 0 to 5...
```

## Финальный скоринг
- `build_features` собирает признаки: `coverage_*`, `rubric_*`, `years_*`, `count_metrics`, `count_numbers`, `contradictions`, `toxicity`, `ko_flags`, `asr_conf`, `title_canonical`.
- `_predict_probability` использует CatBoost (`models/catboost.cbm` + `calibrator.pkl`) при наличии, иначе простую логистическую регрессию.
- Пороги решения:
  - `prob > 0.8` → `move`
  - `0.6 < prob ≤ 0.8` → `discuss`
  - иначе `reject`
- Гистограмма `score_overall_hist` фиксирует распределение итоговых баллов.
