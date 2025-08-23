# ASR и TTS

## ASR поток
- WebSocket `/stream/{session_id}` принимает PCM 16 кГц.
- `use_vad=1` включает `webrtcvad`; иначе используется простая эвристика по энергии.
- Riva ASR (если настроен) включён с `enable_automatic_punctuation`, `enable_word_time_offsets`, `speech_contexts`.
- Конец фразы: тишина ≥400 мс или текстовое сообщение `END`.
- Ответы в формате `ASRChunk` (`partial` каждые ~250 мс, `final` после окончания).
- При отсутствии Riva используется встроенный стек без распознавания слов (**TODO: интеграция VAD/AEC**).

## TTS
- Функция `synthesize` пробует **XTTS‑v2**, затем **Silero**, затем возвращает синус (mock).
- `stream_bytes` порционно отдаёт аудио и фиксирует метрики `tts_ttf_seconds` (time to first audio) и `tts_bytes_total`.
- Форматы: WAV (`audio/wav`) или сырой PCM16 (`audio/L16`).
- Поддерживается барж‑ин: клиент может начать отправлять PCM, не дожидаясь окончания TTS.
- **TODO:** выбор движка через `TTS_ENGINE`, голос Silero через `SILERO_VOICE`.
