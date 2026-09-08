#!/usr/bin/env python3
"""
_transcribe.py — Transcribe source webinar video with Faster-Whisper (word-level).

Output: _audio_source.json with word-level timestamps.

Usage:
    python _transcribe.py                          # Auto-detect source video
    python _transcribe.py --input source.mp4       # Specify source
    python _transcribe.py --model large-v3         # Model selection
    python _transcribe.py --language pt            # Force language

Requirements:
    pip install faster-whisper

Models (download on first use):
    large-v3  — best quality, ~3GB VRAM
    medium    — good quality, ~1.5GB VRAM
    small     — fast, lower quality, ~800MB VRAM
"""

import os
import sys
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 🔧 CUSTOMIZE: Source video to transcribe
SOURCE_VIDEO = "source_webinar.mp4"


def find_source_video():
    """Find the source video file."""
    # Try configured path
    path = BASE / SOURCE_VIDEO
    if path.exists():
        return path

    # Try common patterns
    for pattern in ["*.mp4", "*.webm", "*.mkv"]:
        matches = list(BASE.glob(pattern))
        if matches:
            return matches[0]

    return None


def extract_audio(video_path: Path, audio_path: Path):
    """Extract WAV audio from video for transcription."""
    print(f"Extracting audio: {video_path.name} → {audio_path.name} ...")
    cmd = (
        f'ffmpeg -y -i "{video_path}" '
        f'-vn -acodec pcm_s16le -ar 16000 -ac 1 '
        f'"{audio_path}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not audio_path.exists():
        print(f"  [!] Audio extraction failed: {result.stderr[:300]}")
        return False
    size_mb = audio_path.stat().st_size / (1024 * 1024)
    print(f"  Audio extracted: {size_mb:.1f} MB")
    return True


def transcribe(audio_path: Path, output_path: Path, model_size="large-v3", language="pt"):
    """Transcribe audio with Faster-Whisper."""
    print(f"Loading Faster-Whisper model '{model_size}'...")

    from faster_whisper import WhisperModel
    import time

    # Use CPU or GPU depending on availability
    device = "cuda" if _has_cuda() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"  Device: {device}, compute: {compute_type}")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"Transcribing: {audio_path.name} ...")
    start = time.time()

    segments_out = []
    segments_gen, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
    )

    print(f"  Detected language: {info.language} (probability: {info.language_probability:.2f})")

    for seg in segments_gen:
        words_out = []
        if seg.words:
            for w in seg.words:
                words_out.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "probability": round(w.probability, 3),
                })

        segments_out.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": words_out,
        })

        if len(segments_out) % 50 == 0:
            elapsed = time.time() - start
            print(f"  ... {len(segments_out)} segments ({elapsed:.0f}s)")

    elapsed = time.time() - start
    print(f"  Done: {len(segments_out)} segments in {elapsed:.0f}s")

    # Save JSON
    data = {
        "segments": segments_out,
        "metadata": {
            "model": model_size,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": segments_out[-1]["end"] if segments_out else 0,
        },
    }

    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    size_kb = output_path.stat().st_size / 1024
    print(f"  Saved: {output_path} ({size_kb:.0f} KB)")

    # Clean up audio
    audio_path.unlink(missing_ok=True)

    return True


def _has_cuda():
    """Check if CUDA GPU is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Transcribe video with Faster-Whisper.')
    parser.add_argument('--input', help='Source video path')
    parser.add_argument('--model', default='large-v3', help='Whisper model size')
    parser.add_argument('--language', default='pt', help='Language code')
    args = parser.parse_args()

    # Find source video
    source = None
    if args.input:
        source = Path(args.input)
        if not source.exists():
            print(f"[!] Video not found: {source}")
            sys.exit(1)
    else:
        source = find_source_video()
        if not source:
            print("[!] No source video found. Use --input to specify.")
            print(f"    Looked in: {BASE}")
            print(f"    Configured: {SOURCE_VIDEO}")
            sys.exit(1)

    print(f"Source: {source.name}")

    # Extract audio
    audio_path = BASE / "_temp_audio.wav"
    if not extract_audio(source, audio_path):
        sys.exit(1)

    # Transcribe
    output_path = BASE / "_audio_source.json"
    if transcribe(audio_path, output_path, args.model, args.language):
        print(f"\nTranscription complete: {output_path}")
    else:
        print("\n[!] Transcription failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
