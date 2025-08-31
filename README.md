# Interview Assistant MVP

## Quickstart

### CPU

1. Install Docker:

   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo apt-get install -y docker-compose-plugin
   ```

2. Start the service:

   ```bash
   make run-server
   ```

3. Run an offline test and convert the output to WAV:

   ```bash
   make test-offline
   ffmpeg -f s16le -ar 16000 -ac 1 -i tts_out.pcm out.wav -y
   ```

4. Measure latency:

   ```bash
   python measure_latency.py --ws ws://localhost:8000 --wav ru_test.wav
   ```

5. Stop the containers:

   ```bash
   docker compose down
   ```

### GPU

1. Install Docker and NVIDIA Container Toolkit:

   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo apt-get install -y docker-compose-plugin nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```

2. Start the GPU service:

   ```bash
   make run-gpu
   ```

3. Run an offline test and convert the output to WAV:

   ```bash
   make test-offline
   ffmpeg -f s16le -ar 16000 -ac 1 -i tts_out.pcm out.wav -y
   ```

4. Measure latency:

   ```bash
   python measure_latency.py --ws ws://localhost:8000 --wav ru_test.wav
   ```

5. Stop the containers:

   ```bash
   docker compose down
   ```

## Presets

| Environment | `ASR_MODEL` | `ASR_COMPUTE_TYPE` |
|-------------|-------------|--------------------|
| CPU         | small       | int8               |
| GPU         | large-v3    | float16            |

## Supported Russian voices for Piper

- denis
- dmitri
- irina
- ruslan

## Latency reduction tips

- Use smaller ASR models (`ASR_MODEL=small`).
- Run ASR and TTS on GPU when available (`ASR_DEVICE=gpu`).
- Stream shorter audio chunks (20 ms) to the server.
- Preload models to avoid cold starts.
