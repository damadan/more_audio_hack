# IE и JD‑matching

## Извлечение информации (IE)

1. **ESCOXLM‑R** (заглушка `tag_esco`) отмечает навыки и инструменты по
   ключевым словам.
2. **LLM JSON‑экстракция** — функция `extract_ie` при наличии LLM
   извлекает проекты и числовые метрики.
3. Для каждого навыка собираются `IEEvidence` с таймкодами (если
   запрошено `include_timestamps`).

Пример:

```bash
curl -X POST http://localhost:8080/ie/extract \
  -H 'Content-Type: application/json' \
  -d '{"transcript":"Мы используем Docker и Grafana"}'
```

Ответ:

```json
{
  "skills": [{"name": "Docker", "evidence": [{"quote": "Docker", "t0":0,"t1":0}]}],
  "tools": ["Grafana"],
  "years": {},
  "projects": [],
  "roles": []
}
```

## JD‑matching и Coverage

1. Индикаторы из `JD` преобразуются в эмбеддинги (`HR_EMB_BACKEND`).
2. FAISS индекс строится функцией `build_indicator_index`.
3. Транскрипт разбивается на предложения; каждое предложение сопоставляется с
   индикаторами (`match_spans`).
4. `compute_coverage` агрегирует лучшие совпадения в `Coverage`.

Пример покрытия:

```json
{
  "per_indicator": {"python": 0.9},
  "per_competency": {"Machine Learning": 0.9}
}
```

