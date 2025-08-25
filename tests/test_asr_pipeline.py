import asyncio
import time
import numpy as np
import pytest

from app.audio.frames import AudioFrame
from app.audio.endpointing import EndpointDetector, Segment
from app.asr.online_vosk import OnlineASR
from app.asr.hybrid_refiner import HybridRefiner, RefinerConfig


def make_frame(t0: float, ms: int = 20) -> AudioFrame:
    pcm = np.ones(int(16000 * ms / 1000), dtype=np.int16)
    t1 = t0 + ms / 1000
    return AudioFrame(pcm=pcm, sample_rate=16000, t0=t0, t1=t1)


@pytest.mark.asyncio
async def test_asr_pipeline_partial_and_final():
    asr = OnlineASR(model_dir="")
    det = EndpointDetector(min_speech_ms=40, max_pause_ms=40)
    t = 0.0
    partial_times = []
    final_time = None
    segments = []
    for i in range(5):
        frame = make_frame(t)
        start = time.time()
        ev = asr.accept_frame(frame)
        if ev:
            partial_times.append(time.time() - start)
        segments.extend(list(det.push(frame, True)))
        t = frame.t1
    # add silence to trigger endpoint
    for _ in range(3):
        frame = make_frame(t)
        segments.extend(list(det.push(frame, False)))
        t = frame.t1
    for seg in segments:
        final_start = time.time()
        final_ev = asr.finalize_segment()
        final_time = time.time() - final_start
        assert final_ev is not None
    assert partial_times and final_time is not None
    assert min(partial_times) < final_time


@pytest.mark.asyncio
async def test_hybrid_refiner_produces_segment_final():
    refiner = HybridRefiner(RefinerConfig())
    frames = [make_frame(i * 0.02) for i in range(5)]
    seg = Segment(frames=frames, ts_start=0.0, ts_end=frames[-1].t1)
    ev = refiner.refine(seg, "en")
    assert ev.type == "segment_final"
    assert ev.revised_text
