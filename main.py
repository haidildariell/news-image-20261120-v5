#!/usr/bin/env python3
"""Entrypoint: draw the entry image and write it to $MAKEFUN_OUTPUT_DIR."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_image  # noqa: E402

if __name__ == "__main__":
    build_image.main()
