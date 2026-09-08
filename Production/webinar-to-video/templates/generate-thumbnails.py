#!/usr/bin/env python3
"""Generate YouTube thumbnails for FCT Open Access Policy webinar series (6 episódios)."""

import subprocess
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
RENDERS_YT = os.path.join(BASE, 'renders', 'youtube')
THUMBS = os.path.join(RENDERS_YT, 'thumbnails')
os.makedirs(THUMBS, exist_ok=True)

FONTS = [
    'C:/Windows/Fonts/arial.ttf',
    'Arial.ttf',
    'segoeui.ttf',
    'calibri.ttf',
]
FONT = None
for f in FONTS:
    if os.path.exists(f):
        FONT = f.replace('\\', '/').replace(':', '\\:')
        break

EPISODES = [
    ("ep01-introducao-ciencia-aberta", "Introdução e Conceitos de Ciência Aberta", 90),
    ("ep02-plano-s-horizonte-europa", "Plano S e Requisitos do Horizonte Europa", 120),
    ("ep03-nova-politica-fct-vias", "Nova Política FCT: Vias Dourada e Transformativa", 120),
    ("ep04-via-verde-livros-teses", "Via Verde (RCAAP), Livros e Teses", 90),
    ("ep05-ferramentas-journal-checker-doaj", "Journal Checker Tool e DOAJ", 90),
    ("ep06-rights-retention-strategy-resumo", "Rights Retention Strategy e Resumo Prático", 120),
]

SIZE = "1280x720"

for i, (slug, title, ss) in enumerate(EPISODES, 1):
    input_mp4 = os.path.join(RENDERS_YT, f"{slug}.mp4")
    if not os.path.exists(input_mp4):
        print(f"  [-] {slug}.mp4 not found, skipping")
        continue

    output_jpg = os.path.join(THUMBS, f"{slug}-thumb.jpg")
    ep_label = f"EPISÓDIO {i}"

    if FONT:
        title_escaped = title.replace(':', '\\:').replace("'", "\\'")
        draw1 = (
            f"drawtext=fontfile={FONT}:text='{ep_label}':"
            f"fontcolor=white:fontsize=48:"
            f"x=60:y=60:"
            f"box=1:boxcolor=black@0.80:boxborderw=16"
        )
        draw2 = (
            f"drawtext=fontfile={FONT}:text='{title_escaped}':"
            f"fontcolor=yellow:fontsize=38:"
            f"x=60:y=150:"
            f"box=1:boxcolor=black@0.80:boxborderw=16"
        )
        vf_filter = f"crop=ih*16/9:ih,scale={SIZE},{draw1},{draw2}"
    else:
        vf_filter = f"crop=ih*16/9:ih,scale={SIZE}"

    cmd = [
        'ffmpeg', '-y',
        '-ss', str(ss),
        '-i', input_mp4,
        '-vframes', '1',
        '-vf', vf_filter,
        output_jpg
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(output_jpg):
        size_kb = os.path.getsize(output_jpg) / 1024
        print(f"  [+] EP {i}: {os.path.basename(output_jpg)} ({size_kb:.0f} KB)")
    else:
        print(f"  [!] EP {i}: FAILED")
        if result.stderr:
            print(f"      {result.stderr[:200]}")

print(f"\nDone: thumbnails => {THUMBS}")
