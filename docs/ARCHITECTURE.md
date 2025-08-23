# Архитектура

## Компоненты
- **Клиент** — отправляет PCM‑поток и принимает TTS.
- **ASR** — `/stream/{session_id}` обрабатывает аудио (Riva либо встроенный эвристический VAD).
- **DM/LLM** — строит следующий вопрос по JD и истории (`app/dialog_manager.py`).
- **IE/Matching** — извлекает навыки и проекты (`app/ie.py`) и сравнивает их с JD через FAISS (`app/match.py`).
- **Rubric** — оценивает компетенции с помощью LLM (`/rubric/score`).
- **Scorer** — агрегирует покрытие и рубрику в итоговый балл (`app/scoring.py`).
- **Report/ATS** — формирует HTML/PDF отчёт и синхронизирует решение с ATS.
- **Observability** — Prometheus‑метрики, JSON‑логи.

## Диаграммы

### Компонентная
```mermaid
graph LR
    client((Client)) <--> asr[ASR]
    asr --> dm[DM/LLM]
    dm --> ie[IE/Matching]
    ie --> rubric[Rubric]
    rubric --> scorer[Scorer]
    scorer --> report[Report]
    scorer --> ats[ATS]
    dm --> tts[TTS]
    tts --> client
```

### Последовательность вопрос→ответ
```mermaid
sequenceDiagram
    participant C as Client
    participant A as ASR
    participant D as DM/LLM
    participant T as TTS
    C->>A: PCM 16 kHz
    A-->>C: ASRChunk partial/final
    C->>D: /dm/next
    D-->>C: Next question
    C->>T: /tts
    T-->>C: WAV/PCM
```

### Поток данных IE→Report
```mermaid
flowchart LR
    IE[IE/NER] --> Cov[Coverage]
    Cov --> Rubric
    Rubric --> Score
    Score --> Report
```

## SLO
- ASR partial p95 ≤ 400 мс
- ASR final p95 ≤ 900 мс
- TTF‑audio ≤ 300–400 мс
- WER RU ≤ 7–8 %
