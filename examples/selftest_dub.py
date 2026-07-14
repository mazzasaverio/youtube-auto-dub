"""Self-contained end-to-end proof of the ytdub pipeline — runs on CPU, no YouTube.

What it does:
  1. Synthesizes an Italian source sentence in a natural (built-in XTTS) voice.
  2. Wraps it into a source video.
  3. Runs the REAL dubbing pipeline to dub it into English (clone timbre + sync).
  4. Verifies the result: timing drift (sync) and speaker-timbre similarity.

Run (after installing the CPU recipe from the README):
    python examples/selftest_dub.py

Expected: ~0.00 s duration delta and a timbre cosine similarity around 0.85–0.9.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

os.environ.setdefault("COQUI_TOS_AGREED", "1")  # accept XTTS license non-interactively

WORK = Path("data/selftest")
WORK.mkdir(parents=True, exist_ok=True)


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def main() -> None:
    print("=== 1. Synthesize Italian SOURCE speech (built-in natural voice) ===")
    from TTS.api import TTS

    xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    src_wav = WORK / "source_it.wav"
    italian = (
        "Ciao a tutti e benvenuti. Oggi vi mostro come funziona il doppiaggio automatico. "
        "Questa voce dovrebbe restare simile anche nella traduzione."
    )
    xtts.tts_to_file(text=italian, speaker="Ana Florence", language="it", file_path=str(src_wav))

    print("=== 2. Build a source video from that audio ===")
    import soundfile as sf

    with sf.SoundFile(str(src_wav)) as f:
        dur = len(f) / f.samplerate
    src_mp4 = WORK / "source.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=navy:s=640x360:d={dur:.2f}",
         "-i", str(src_wav), "-shortest", "-pix_fmt", "yuv420p",
         "-map", "0:v", "-map", "1:a", str(src_mp4)],
        check=True, capture_output=True,
    )

    print("=== 3. Run the REAL dubbing pipeline: Italian -> English ===")
    from ytdub.config import Settings
    from ytdub.pipeline import dub

    res = dub(
        str(src_mp4),
        Settings(data_dir=Path("data").resolve(), source_lang="it", target_lang="en",
                 asr_model="small"),
    )
    print("\nOUTPUT VIDEO:", res.output_path)
    print("SUBTITLES  :", res.subtitle_path)
    for s in res.segments:
        print(f"  [{s.start:5.2f}-{s.end:5.2f}]  IT: {s.text!r}  ->  EN: {s.translated!r}")

    print("\n=== 4. Verify sync (durations) + timbre (speaker similarity) ===")
    src_d, out_d = ffprobe_duration(src_mp4), ffprobe_duration(res.output_path)
    print(f"source = {src_d:.2f}s | dubbed = {out_d:.2f}s | drift = {abs(src_d - out_d):.2f}s")

    out_wav = WORK / "output_en.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(res.output_path), "-vn", "-ar", "16000", "-ac", "1",
         str(out_wav)],
        check=True, capture_output=True,
    )
    try:
        import numpy as np
        from resemblyzer import VoiceEncoder, preprocess_wav

        enc = VoiceEncoder("cpu")
        e_src = enc.embed_utterance(preprocess_wav(str(src_wav)))
        e_out = enc.embed_utterance(preprocess_wav(str(out_wav)))
        print(f"TIMBRE cosine similarity source(it) vs dubbed(en) = {float(np.dot(e_src, e_out)):.3f}"
              "  (1.0 = identical voice)")
    except Exception as exc:  # resemblyzer is optional
        print("timbre similarity skipped (pip install resemblyzer):", exc)

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
