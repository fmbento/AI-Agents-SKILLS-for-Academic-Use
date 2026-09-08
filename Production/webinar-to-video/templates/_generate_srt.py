#!/usr/bin/env python3
"""hyperframes_srt.py — Generate SRT subtitle files from HyperFrames index.html overlays.

Reads a HyperFrames composition (index.html), extracts every visual overlay
(div.clip elements with data-start/data-duration), and writes an SRT file
alongside the video source so you can verify overlay timings in VLC or any
media player that supports external subtitles.

Usage:
    python hyperframes_srt.py ep01/index.html           # single episode
    python hyperframes_srt.py ep01 ep02 ep03            # multiple
    python hyperframes_srt.py .                          # all ep*/ dirs found
    python hyperframes_srt.py --auto                     # scan cwd for ep*/

Skips:
    - <video> and <audio> elements (not visual overlays)
    - SFX <audio id="sfx-*"> elements (not visual)
    - Intro (ov-intro) - shown at 0-5s, not a content overlay
    - Outro (ov-outro) - shown at end, not a content overlay

Output:
    SRT file saved as <ep_dir>/<video_filename>.srt
    Default video filename: epXX_video.mp4
"""

import os
import re
import sys
import glob
import argparse
from pathlib import Path

# ── Windows: force UTF-8 stdout to avoid UnicodeEncodeError ──
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── If BeautifulSoup is not available, fall back to regex parsing ──
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def format_srt_time(seconds_float):
    """Convert seconds (float) to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds_float // 3600)
    minutes = int((seconds_float % 3600) // 60)
    seconds = int(seconds_float % 60)
    milliseconds = int(round((seconds_float % 1) * 1000))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def extract_overlays_bs4(html_path):
    """Extract overlay entries using BeautifulSoup (preferred)."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    entries = []
    for el in soup.find_all('div', class_='clip'):
        el_id = el.get('id', '')
        start_str = el.get('data-start')
        duration_str = el.get('data-duration')

        if not start_str or not duration_str:
            continue

        # Skip non-visual elements
        if el_id in ('main-video', 'ov-intro', 'ov-outro'):
            continue
        # Skip SFX audio containers (detected by class)
        classes = el.get('class', [])

        try:
            start = float(start_str)
            duration = float(duration_str)
        except (ValueError, TypeError):
            continue

        end = start + duration

        # Extract tag (concept-tag), title (overlay-title), and subtitle (overlay-body)
        tag_text = ""
        title_text = ""
        body_text = ""

        tag_el = el.find(class_='concept-tag')
        if tag_el:
            tag_text = tag_el.get_text(strip=True)

        title_el = el.find(class_='overlay-title')
        if title_el:
            title_text = title_el.get_text(separator=' ', strip=True)
            # Normalize: remove emoji + text pattern like "⚠" or "💡"
            title_text = re.sub(r'[\U0001F300-\U0001FFFF]\s*', '', title_text).strip()

        body_el = el.find(class_='overlay-body')
        if body_el:
            body_text = body_el.get_text(separator=' ', strip=True)

        # Build SRT text
        parts = []
        if tag_text:
            parts.append(f"[{tag_text}]")
        if title_text:
            parts.append(title_text)
        if body_text:
            parts.append(body_text)

        text_content = ' | '.join(parts) if parts else el.get_text(separator=' ', strip=True)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        if text_content:
            entries.append({
                'start': start,
                'end': end,
                'text': text_content,
                'id': el_id,
            })

    return entries


def extract_overlays_regex(html_path):
    """Extract overlay entries using regex (fallback when BeautifulSoup is unavailable)."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []

    # Find all div.clip elements with data-start and data-duration
    # Pattern: <div id="NAME" class="clip ..." data-start="N" data-duration="N"
    pattern = r'<div\s+id="([^"]+)"\s+class="clip\s+([^"]+)"[^>]*data-start="([\d.]+)"[^>]*data-duration="([\d.]+)"[^>]*>(.*?)</div>\s*(?=<div\s+id="|<audio|</div>\s*$|<!--|$)'

    for m in re.finditer(pattern, content, re.DOTALL):
        el_id, classes, start_str, duration_str, inner = m.groups()

        # Skip non-visual
        if el_id in ('main-video', 'main-audio', 'ov-intro', 'ov-outro'):
            continue
        if 'overlay-center' not in classes and 'overlay-bottom' not in classes:
            continue

        try:
            start = float(start_str)
            duration = float(duration_str)
        except (ValueError, TypeError):
            continue
        end = start + duration

        # Extract tag, title, body via regex
        tag_match = re.search(r'class="concept-tag"[^>]*>\s*(.*?)\s*</div>', inner, re.DOTALL)
        title_match = re.search(r'class="overlay-title"[^>]*>\s*(.*?)\s*</div>', inner, re.DOTALL)
        body_match = re.search(r'class="overlay-body"[^>]*>\s*(.*?)\s*</div>', inner, re.DOTALL)

        tag_text = strip_html(tag_match.group(1)) if tag_match else ''
        title_text = strip_html(title_match.group(1)) if title_match else ''
        body_text = strip_html(body_match.group(1)) if body_match else ''

        # Clean title text
        title_text = re.sub(r'[\U0001F300-\U0001FFFF]\s*', '', title_text).strip()

        parts = []
        if tag_text:
            parts.append(f"[{tag_text}]")
        if title_text:
            parts.append(title_text)
        if body_text:
            parts.append(body_text)

        text_content = ' | '.join(parts)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        if text_content:
            entries.append({
                'start': start,
                'end': end,
                'text': text_content,
                'id': el_id,
            })

    return entries


def strip_html(text):
    """Remove HTML tags, keep text."""
    return re.sub(r'<[^>]+>', '', text).strip()


def hyperframes_to_srt(html_path, srt_path=None):
    """Convert a HyperFrames index.html to an SRT subtitle file.

    Args:
        html_path: Path to index.html
        srt_path: Output SRT path. If None, autogenerated from video filename.

    Returns:
        Tuple of (srt_path, entry_count) or (None, 0) on failure.
    """
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"  [!] Not found: {html_path}")
        return None, 0

    if HAS_BS4:
        entries = extract_overlays_bs4(str(html_path))
    else:
        entries = extract_overlays_regex(str(html_path))

    if not entries:
        print(f"  [!] No overlays found in {html_path}")
        return None, 0

    # Sort chronologically
    entries.sort(key=lambda x: x['start'])

    # Determine output path
    if srt_path is None:
        ep_dir = html_path.parent
        video_name = f"{ep_dir.name}_video.mp4"
        srt_path = ep_dir / f"{video_name}.srt"
    else:
        srt_path = Path(srt_path)

    # Write SRT
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries, 1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(entry['start'])} --> {format_srt_time(entry['end'])}\n")
            f.write(f"{entry['text']}\n\n")

    print(f"  {srt_path.name}: {len(entries)} subtitles => {srt_path}")
    return srt_path, len(entries)


def find_episodes(base_dir='.'):
    """Discover all ep*/ directories containing index.html."""
    base = Path(base_dir)
    episodes = sorted(base.glob('ep*/index.html'))
    return episodes


def main():
    parser = argparse.ArgumentParser(
        description='Generate SRT subtitle files from HyperFrames overlays '
                    'for VLC preview verification.'
    )
    parser.add_argument(
        'paths', nargs='*',
        help='Path(s) to index.html, ep directories, or . for all ep*/ '
             '(default: --auto)'
    )
    parser.add_argument(
        '--auto', action='store_true',
        help='Auto-detect all ep*/index.html in current directory'
    )
    args = parser.parse_args()

    # Resolve input paths
    html_paths = []

    if args.paths:
        for p in args.paths:
            path = Path(p)
            if path.is_file() and path.suffix == '.html':
                html_paths.append(path)
            elif path.is_dir():
                index = path / 'index.html'
                if index.exists():
                    html_paths.append(index)
                # Also check for ep* inside this dir
                for ep in sorted(path.glob('ep*/index.html')):
                    if ep not in html_paths:
                        html_paths.append(ep)
            elif p == '.':
                html_paths.extend(find_episodes('.'))
    elif args.auto:
        html_paths.extend(find_episodes('.'))
    else:
        # Default: auto-detect
        html_paths.extend(find_episodes('.'))

    if not html_paths:
        print("No index.html files found. Usage:")
        print("  python hyperframes_srt.py ep01/index.html")
        print("  python hyperframes_srt.py --auto")
        sys.exit(1)

    # Sort by episode number
    html_paths.sort(key=lambda p: (
        int(re.search(r'ep(\d+)', str(p)).group(1))
        if re.search(r'ep(\d+)', str(p)) else 0
    ))

    total_entries = 0
    total_files = 0

    for html_path in html_paths:
        ep_name = html_path.parent.name
        result, count = hyperframes_to_srt(html_path)
        if result:
            total_entries += count
            total_files += 1

    print(f"\nDone: {total_files} SRT files, {total_entries} total subtitles.")


if __name__ == '__main__':
    main()
