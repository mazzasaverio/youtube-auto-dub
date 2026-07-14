# Optional container image for ytdub. The primary way to run this is still a local
# `uv pip install` (see README) — this image just makes the CLI portable/reproducible.
#
# Build:  docker build -t ytdub .
# Run:    docker run --rm -v "$PWD/data:/app/data" ytdub dub "https://youtu.be/ID" -t en
#
# Ships the XTTS backend by default. Models (~2 GB) download on first run into the
# mounted volume; add `--gpus all` on a CUDA host for acceleration.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir ".[xtts]"

ENV YTDUB_DATA_DIR=/app/data
ENTRYPOINT ["ytdub"]
CMD ["--help"]
