"""Verify every overlay anchor term exists inside its episode window.

TEMPLATE — run AFTER customizing _build_all.py (EPISODES + OVERLAYS) and
BEFORE generating the final index.html. Confirms each anchor term appears in
the transcript inside the correct episode window (lesson #57).
"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import _build_all as b

data = json.loads((BASE / "_audio_source.json").read_text(encoding="utf-8-sig"))
segments = data.get("segments", [])

def norm(text):
    import unicodedata
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))

# Build a per-window set of normalized text
window_text = {}
for ep, start, end, *_ in b.EPISODES:
    texts = []
    for seg in segments:
        if start <= seg.get("start", 0) < end:
            texts.append(norm(seg.get("text", "")))
    window_text[ep] = " ".join(texts)

problems = 0
for ep, overlays in b.OVERLAYS.items():
    wt = window_text.get(ep, "")
    for (oid, kind, tag, title, body, terms, fullscreen) in overlays:
        hit = any(norm(t) in wt for t in terms)
        status = "OK " if hit else "MISS"
        if not hit:
            problems += 1
        print(f"{status} {ep}/{oid} [{tag}] {'|'.join(terms)}")
print(f"\nProblems: {problems}")
sys.exit(1 if problems else 0)
