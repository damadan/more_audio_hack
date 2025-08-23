# ASR и TTS

## Поток ASR

- WebSocket `/stream/{session_id}` принимает бинарные фреймы PCM 16 кГц.
- Опциональный параметр `use_vad` включает `webrtcvad`.
- Конец фразы определяется по тишине ≥ 400 мс или по сообщению `END`.
- Riva ASR (если настроен) запускается с опциями:
  - `enable_automatic_punctuation=True`
  - `enable_word_time_offsets=True`
  - `speech_contexts` с hotwords
- Ответы имеют форму `ASRChunk` (`partial` каждые ~250 мс, `final` после
  тишины).

## Синтез речи

- Основной движок — **XTTS‑v2** (`tts_models/multilingual/multi-dataset/xtts_v2`).
- Fallback — **Silero RU** (`snakers4/silero-models`).
- Форматы вывода: WAV (`audio/wav`) или сырые PCM (`audio/L16`).
- Функция `synthesize` выбирает доступный движок, `stream_bytes` стримит
  аудио небольшими чанками.
- Поддерживается барж‑ин: клиент может прервать TTS и начать отправлять PCM.
- Допустимы пользовательские голоса: XTTS принимает `speaker_wav`, Silero —
  название голоса (`SILERO_VOICE`).

## Параметры формата

- Частота дискретизации: XTTS — до 24 кГц, Silero — 16 кГц
- Каналы: моно, 16‑бит signed little‑endian

