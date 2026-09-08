#!/usr/bin/env python3
"""Launch _split_video.py as a detached Windows process — with a duplicate guard."""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PIDFILE = BASE / "_split.pid"

# Guard: refuse to start a second split while one is already running.
if PIDFILE.exists():
    old_pid = int(PIDFILE.read_text().strip() or 0)
    if old_pid:
        try:
            import psutil
            if psutil.pid_exists(old_pid):
                proc = psutil.Process(old_pid)
                cmd = " ".join(proc.cmdline() or [])
                if "_split_video.py" in cmd:
                    print("ALREADY_RUNNING", old_pid)
                    raise SystemExit(0)
        except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass

log = open(BASE / "_split.log", "w", encoding="utf-8", buffering=1)

DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
p = subprocess.Popen(
    [sys.executable, str(BASE / "_split_video.py")],
    cwd=str(BASE),
    stdout=log,
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=DETACHED,
    close_fds=True,
)
PIDFILE.write_text(str(p.pid))
print("SPLIT_PID", p.pid)
