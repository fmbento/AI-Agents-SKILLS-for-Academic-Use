#!/usr/bin/env python3
"""
_split_video.py — Split source webinar video into per-episode segments with audio enhancement.

Reads EPISODE_BOUNDARIES from _generate_captions.py (or inline config) and:
  1. Cuts the source video into epXX/epXX_video.mp4 segments
  2. Applies audio_enhance chain (adeclick, highpass, lowpass, gate, compressor, loudnorm)
  3. Re-encodes with dense keyframes (-g 30 -keyint_min 30)

Usage:
    python _split_video.py                        # Split all episodes
    python _split_video.py --ep 04                # Single episode
    python _split_video.py --audio-only           # Only re-process audio (video already split)

Requirements:
    ffmpeg in PATH
"""

import os
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 🔧 CUSTOMIZE: Source video path + episode boundaries
SOURCE_VIDEO = "source_webinar.mp4"  # relative to BASE

EPISODE_BOUNDARIES = [
    # (ep_label, abs_start_s, abs_end_s)
    ("ep01",    0,  700),
    ("ep02",  700, 1400),
    # ... add all episodes (total duration = sum of all segments)
]

# ══════════════════════════════════════════════════════════════
# Audio enhancement chain
# ══════════════════════════════════════════════════════════════

# https://www.ua.pt/bibliotecas
# Ordem: adeclick FIRST (evita cliques dos cortes de silêncio)
AUDIO_FILTER = (
    "adeclick,"
    "highpass=f=80,"
    "lowpass=f=13000,"
    "agate=threshold=-30dB:ratio=2:attack=5:release=50,"
    "acompressor=threshold=-20dB:ratio=3:attack=10:release=100,"
    "loudnorm=I=-16:LRA=11:TP=-1.5"
)

VIDEO_ENCODE = (
    "-c:v libx264 -preset fast -crf 18 "
    "-r 30 -g 30 -keyint_min 30 "
    "-profile:v high -level 4.0 "
    "-pix_fmt yuv420p"
)

AUDIO_ENCODE = "-c:a aac -b:a 192k -ar 48000"


def split_episode(ep_label, start_s, end_s, source=SOURCE_VIDEO):
    """Split one episode from source video with audio enhancement."""
    ep_dir = BASE / ep_label
    ep_dir.mkdir(parents=True, exist_ok=True)
    output = ep_dir / f"{ep_label}_video.mp4"

    duration = end_s - start_s

    cmd = (
        f'ffmpeg -y -ss {start_s} -i "{BASE / source}" -t {duration} '
        f'-vf "fps=30,format=yuv420p" '
        f'-af "{AUDIO_FILTER}" '
        f'{VIDEO_ENCODE} {AUDIO_ENCODE} '
        f'-movflags +faststart '
        f'"{output}"'
    )

    print(f"  {ep_label}: {start_s}s → {end_s}s ({duration:.0f}s) → {output}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if output.exists():
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"  {ep_label}: OK ({size_mb:.1f} MB)")
    else:
        print(f"  {ep_label}: FAILED")
        if result.stderr:
            # Show last 3 lines of error
            lines = result.stderr.strip().split('\n')
            for line in lines[-3:]:
                print(f"    {line}")
    return output.exists()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Split source video into episodes.')
    parser.add_argument('--ep', help='Single episode (e.g. 04)')
    parser.add_argument('--audio-only', action='store_true',
                        help='Only re-process audio on already-split videos')
    parser.add_argument('--source', help='Source video path', default=SOURCE_VIDEO)
    args = parser.parse_args()

    source = args.source
    source_path = BASE / source
    if not source_path.exists():
        print(f"[!] Source video not found: {source_path}")
        sys.exit(1)

    print(f"Source: {source_path}")
    print(f"Episodes: {len(EPISODE_BOUNDARIES)}")
    print()

    success = 0
    failed = 0

    for ep_label, start_s, end_s in EPISODE_BOUNDARIES:
        if args.ep and ep_label != f"ep{args.ep}":
            continue

        if args.audio_only:
            # Re-process audio on existing video
            ep_video = BASE / ep_label / f"{ep_label}_video.mp4"
            if not ep_video.exists():
                print(f"  {ep_label}: video not found, skipping")
                continue
            # ... (audio-only mode would use existing video, redo audio)
            print(f"  {ep_label}: audio-only mode not fully implemented yet")
            continue

        if split_episode(ep_label, start_s, end_s, source):
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} OK, {failed} failed")


if __name__ == "__main__":
    main()
