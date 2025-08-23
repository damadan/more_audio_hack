# IE и JD‑matching

## Извлечение информации
1. `tag_esco` имитирует ESCOXLM‑R и помечает навыки/инструменты по ключевым словам.
2. `extract_ie` при наличии LLM дополняет данные числами, датами и метриками проектов, возвращая `IE` с `IEEvidence` (цитата, t0, t1).
3. **TODO:** полноценный NER и нормализация ролей.

Пример:
```bash
curl -X POST http://localhost:8080/ie/extract \
  -H 'Content-Type: application/json' \
  -d '{"transcript":"Мы использовали Docker и Grafana"}'
```

## JD‑matching и Coverage
1. Индикаторы из `JD` преобразуются в эмбеддинги (`HR_EMB_BACKEND`: `BGE_M3`/`CONSULTANTBERT`/`TAROT`).
2. `build_indicator_index` строит FAISS индекс; `match_spans` ищет совпадения по предложениям.
3. `compute_coverage` агрегирует лучшие попадания в `Coverage` по индикатору и компетенции.
4. Ожидаемые значения: фраза про Docker/FastAPI даёт `coverage` для индикатора *serving* > 0.6.

Пример покрытия:
```json
{"per_indicator":{"python":0.9},"per_competency":{"ML":0.9}}
```
