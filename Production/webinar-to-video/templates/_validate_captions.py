"""Validate PT/EN caption alignment for all episodes.

TEMPLATE — derives the episode list from _build_all.py (EPISODES), so it works
for any number of episodes. Checks per episode: equal block counts, identical
timestamps, untranslated blocks, and box-drawing characters.

Note (lesson #61): an untranslated block (PT == EN) is NOT always an error —
UI text (e.g. "Add Data, New Dataset.") and proper names (e.g. "R3Data.")
are identical in both languages. Inspect the flagged block before fixing.
"""
import re
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
import _build_all as b  # noqa: E402

pat = re.compile(r'\d+\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\n(.*?)(?:\n\n|\Z)', re.S)

def read(p):
    return pat.findall(p.read_text(encoding='utf-8-sig')) if p.exists() else []

allok = True
total_pt = total_en = 0
for ep, _start, _end, *_ in b.EPISODES:
    pt = read(BASE / ep / (ep + '_video.pt.srt'))
    en = read(BASE / ep / (ep + '_video.en.srt'))
    total_pt += len(pt)
    total_en += len(en)
    same_times = len(pt) == len(en) and all(a[:2] == b2[:2] for a, b2 in zip(pt, en))
    identical = sum(1 for a, b2 in zip(pt, en) if a[2].strip() == b2[2].strip())
    box = sum(1 for a, b2 in zip(pt, en) if '\u251c' in b2[2] or '\u2500' in b2[2])
    ok = same_times and identical == 0
    allok = allok and ok
    ts = 'OK' if same_times else 'MISMATCH'
    print('%s: PT=%d EN=%d times=%s untranslated=%d boxchars=%d' % (ep, len(pt), len(en), ts, identical, box))

print('TOTAL_PT=%d TOTAL_EN=%d' % (total_pt, total_en))
print('ALL_OK' if allok else 'ISSUES_FOUND')
