#!/usr/bin/env python3
"""Launch EN caption translation as a detached Windows process with log."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
log = open(BASE / "_captions_en.log", "w", encoding="utf-8", buffering=1)

DETACHED = 0x00000008 | 0x00000200
p = subprocess.Popen(
    [sys.executable, str(BASE / "_generate_captions.py"),
     "--provider", "deeptrans"],
    cwd=str(BASE),
    stdout=log,
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=DETACHED,
    close_fds=True,
)
(BASE / "_captions_en.pid").write_text(str(p.pid))
print("CAPTIONS_PID", p.pid)
