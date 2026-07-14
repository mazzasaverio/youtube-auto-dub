"""Diarization stage — *who* speaks *when* (optional, for multi-voice dubbing).

When enabled, we tag every transcribed segment with a speaker label, then clone one voice
per speaker — so a multi-speaker video comes out dubbed in *multiple* voices.

Two backends:
  * ``embedding`` (**default, token-free**) — embed each segment's audio with a speaker
    encoder and cluster them. No gated models, no Hugging Face token: it keeps the
    "runs free for everyone" promise. Pass the speaker count with ``--speakers`` or let
    it auto-estimate.
  * ``pyannote`` — pyannote speaker-diarization-3.1. More accurate, but needs a free HF
    token and one-time terms acceptance.

The clustering (:func:`cluster_embeddings`) and overlap-matching (:func:`assign_speakers`)
are pure and unit-tested; only the model calls need heavy dependencies.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ytdub.logging import stage_logger
from ytdub.models import Segment

log = stage_logger("diarize")


@dataclass
class SpeakerTurn:
    start: float
    end: float
    speaker: str


def assign_speakers(segments: list[Segment], turns: list[SpeakerTurn]) -> list[Segment]:
    """Tag each segment with the speaker whose turns overlap it most.

    Pure function: given transcription segments and diarization turns (both on the same
    timeline, in seconds), return new segments with ``.speaker`` set. A segment with no
    overlap falls back to the nearest turn's speaker, so nothing is left unlabeled.
    """
    if not turns:
        return segments

    out: list[Segment] = []
    for seg in segments:
        best_speaker: str | None = None
        best_overlap = 0.0
        for turn in turns:
            overlap = min(seg.end, turn.end) - max(seg.start, turn.start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn.speaker

        if best_speaker is None:  # no overlap -> nearest turn by midpoint distance
            mid = (seg.start + seg.end) / 2
            best_speaker = min(
                turns, key=lambda t: abs((t.start + t.end) / 2 - mid)
            ).speaker

        out.append(
            Segment(
                index=seg.index,
                start=seg.start,
                end=seg.end,
                text=seg.text,
                translated=seg.translated,
                audio_path=seg.audio_path,
                speaker=best_speaker,
            )
        )
    return out


def diarize(audio_path: Path, *, device: str = "cpu", hf_token: str | None = None) -> list[SpeakerTurn]:
    """Run pyannote speaker diarization and return the speaker turns.

    Requires ``pip install 'ytdub[diarize-pyannote]'`` and a Hugging Face token (env
    ``HF_TOKEN``) after accepting the model terms at hf.co/pyannote/speaker-diarization-3.1.
    """
    from pyannote.audio import Pipeline  # lazy, heavy

    token = hf_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise RuntimeError(
            "Diarization needs a Hugging Face token. Accept the terms at "
            "hf.co/pyannote/speaker-diarization-3.1 and set HF_TOKEN."
        )

    log.info("Loading pyannote speaker-diarization-3.1")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1", use_auth_token=token
    )
    if device in ("cuda", "mps"):
        import torch

        pipeline.to(torch.device(device))

    diarization = pipeline(str(audio_path))
    turns = [
        SpeakerTurn(start=float(turn.start), end=float(turn.end), speaker=str(speaker))
        for turn, _, speaker in diarization.itertracks(yield_label=True)
    ]
    n_speakers = len({t.speaker for t in turns})
    log.success(f"{len(turns)} turns across {n_speakers} speaker(s)")
    return turns


# --- Token-free embedding diarization --------------------------------------


def cluster_embeddings(embeddings, num_speakers: int = 0, threshold: float = 0.75) -> list[int]:
    """Cluster L2-normalizable speaker embeddings into speaker labels (pure, unit-tested).

    ``num_speakers`` > 0 forces that many clusters (deterministic cosine k-means); 0
    auto-estimates via average-linkage agglomerative merging until the closest two
    clusters are less similar than ``threshold``. Returns a label per embedding.
    """
    import numpy as np

    x = np.asarray(embeddings, dtype=np.float64)
    n = len(x)
    if n <= 1:
        return [0] * n
    x = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)  # unit vectors -> dot == cosine

    if num_speakers and num_speakers >= 1:
        k = min(num_speakers, n)
        # Deterministic k-means++ style seeding (farthest-point), then Lloyd iterations.
        centroids = [x[0]]
        for _ in range(1, k):
            dist = 1.0 - (x @ np.array(centroids).T).max(axis=1)
            centroids.append(x[int(np.argmax(dist))])
        c = np.array(centroids)
        labels = np.full(n, -1)
        for _ in range(50):
            new = (x @ c.T).argmax(axis=1)
            if np.array_equal(new, labels):
                break
            labels = new
            for j in range(k):
                members = x[labels == j]
                if len(members):
                    m = members.mean(axis=0)
                    c[j] = m / (np.linalg.norm(m) + 1e-9)
        return labels.tolist()

    # Auto: average-linkage agglomerative clustering by cosine similarity.
    clusters = [[i] for i in range(n)]
    while len(clusters) > 1:
        best_sim, bi, bj = -1.0, -1, -1
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                sim = float(np.mean([x[a] @ x[b] for a in clusters[i] for b in clusters[j]]))
                if sim > best_sim:
                    best_sim, bi, bj = sim, i, j
        if best_sim < threshold:
            break
        clusters[bi] += clusters[bj]
        del clusters[bj]
    labels = [0] * n
    for lbl, members in enumerate(clusters):
        for idx in members:
            labels[idx] = lbl
    return labels


def assign_speakers_by_embedding(
    audio_path: Path, segments: list[Segment], *, num_speakers: int = 0, device: str = "cpu"
) -> list[Segment]:
    """Tag segments with speaker labels using a speaker encoder + clustering (no HF token).

    Embeds each segment's audio slice with Resemblyzer's voice encoder, clusters the
    embeddings, and writes ``speaker`` labels like ``SPK0`` / ``SPK1``.
    """
    import numpy as np
    from pydub import AudioSegment
    from resemblyzer import VoiceEncoder, preprocess_wav

    encoder = VoiceEncoder(device if device in ("cuda", "cpu") else "cpu")
    audio = AudioSegment.from_file(audio_path).set_channels(1).set_frame_rate(16000)

    embeddings = []
    for seg in segments:
        clip = audio[int(seg.start * 1000) : int(seg.end * 1000)]
        samples = np.array(clip.get_array_of_samples()).astype(np.float32)
        if clip.sample_width == 2:
            samples /= 32768.0
        wav = preprocess_wav(samples, source_sr=16000)
        embeddings.append(encoder.embed_utterance(wav))

    labels = cluster_embeddings(embeddings, num_speakers=num_speakers)
    n = len(set(labels))
    log.success(f"Embedding diarization: {n} voice(s) across {len(segments)} segments")
    return [
        Segment(
            index=s.index, start=s.start, end=s.end, text=s.text,
            translated=s.translated, audio_path=s.audio_path, speaker=f"SPK{labels[i]}",
        )
        for i, s in enumerate(segments)
    ]
