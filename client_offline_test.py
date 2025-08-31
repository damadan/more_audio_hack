import argparse
import asyncio
import wave
from pathlib import Path

import websockets


CHUNK_SAMPLES = 320  # 20ms @ 16kHz
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # bytes for PCM16


async def send_audio(ws: websockets.WebSocketClientProtocol, wav_path: Path) -> None:
    with wave.open(str(wav_path), "rb") as wf:
        if wf.getframerate() != SAMPLE_RATE:
            raise ValueError(f"Unexpected sample rate: {wf.getframerate()}")
        if wf.getnchannels() != CHANNELS:
            raise ValueError(f"Unexpected channel count: {wf.getnchannels()}")
        if wf.getsampwidth() != SAMPLE_WIDTH:
            raise ValueError(f"Unexpected sample width: {wf.getsampwidth()}")

        frames_per_chunk = CHUNK_SAMPLES
        chunk_bytes = frames_per_chunk * SAMPLE_WIDTH
        while True:
            data = wf.readframes(frames_per_chunk)
            if not data:
                break
            if len(data) < chunk_bytes:
                # pad last chunk if necessary
                data += b"\x00" * (chunk_bytes - len(data))
            await ws.send(data)
        # signal end of stream
        await ws.send(b"")


async def recv_audio(ws: websockets.WebSocketClientProtocol, out_path: Path) -> None:
    with out_path.open("wb") as out_file:
        async for message in ws:
            if isinstance(message, bytes):
                out_file.write(message)
            else:
                print(f"Received non-binary message: {message}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Offline TTS client test")
    parser.add_argument("--ws", default="localhost", help="Host to connect to (without scheme and port)")
    parser.add_argument("--wav", required=True, help="Input WAV file (16kHz mono)")
    parser.add_argument("--out", default="tts_out.pcm", help="Output PCM file")
    args = parser.parse_args()

    uri = f"ws://{args.ws}:8000"
    wav_path = Path(args.wav)
    out_path = Path(args.out)

    async with websockets.connect(uri) as ws:
        recv_task = asyncio.create_task(recv_audio(ws, out_path))
        await send_audio(ws, wav_path)
        await recv_task

    print(f"ffmpeg -f s16le -ar 16000 -ac 1 -i {out_path} out.wav -y")


if __name__ == "__main__":
    asyncio.run(main())
