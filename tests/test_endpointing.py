import numpy as np
from app.audio.frames import AudioFrame
from app.audio.endpointing import EndpointDetector


def make_frame(t0: float, speech: bool, ms: int = 20) -> AudioFrame:
    pcm = np.ones(int(16000 * ms / 1000), dtype=np.int16) if speech else np.zeros(int(16000 * ms / 1000), dtype=np.int16)
    t1 = t0 + ms / 1000
    return AudioFrame(pcm=pcm, sample_rate=16000, t0=t0, t1=t1)


def test_simple_endpointing():
    det = EndpointDetector(min_speech_ms=40, max_pause_ms=40, max_segment_ms=1000)
    t = 0.0
    segments = []
    for _ in range(5):  # 100ms speech
        frame = make_frame(t, True)
        segments.extend(list(det.push(frame, True)))
        t = frame.t1
    for _ in range(3):  # 60ms silence triggers endpoint
        frame = make_frame(t, False)
        segments.extend(list(det.push(frame, False)))
        t = frame.t1
    assert len(segments) == 1
    seg = segments[0]
    assert seg.ts_start == 0.0
    assert round(seg.ts_end, 2) == 0.1


def test_max_segment_split():
    det = EndpointDetector(min_speech_ms=40, max_pause_ms=1000, max_segment_ms=100)
    t = 0.0
    segments = []
    # generate 200ms speech -> should split into two segments due to max_segment_ms
    for _ in range(10):
        frame = make_frame(t, True)
        segments.extend(list(det.push(frame, True)))
        t = frame.t1
    assert len(segments) == 2
