#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered entry.png to the output directory.

The image is drawn by build_image.py (run locally, needs Pillow) and
stored in this repo. The grader runs this file as `python3 -P -s
/bot/main.py` in the stock python:3.13-slim image — standard library
only, no Pillow installed — so this entrypoint must NOT import Pillow:
it copies the image with the standard library alone. Output goes to
$MAKEFUN_OUTPUT_DIR, default /output (the grader's writable mount).
"""
import os
import shutil
from pathlib import Path

src = Path(__file__).with_name("entry.png")
out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
out_dir.mkdir(parents=True, exist_ok=True)
shutil.copyfile(src, out_dir / "entry.png")
print(f"copied {src} -> {out_dir / 'entry.png'}")
