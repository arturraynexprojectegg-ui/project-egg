#!/usr/bin/env python3
"""Превью паттерна: python3 tools/preview_pattern.py PE-01.05 out.png"""
import sys, subprocess, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from brandkit import BrandKit
from chrome_util import CHROME

code, out = sys.argv[1], sys.argv[2]
k = BrandKit(code)
W, H = 1500, 520
parts = [k.pattern_rect(0, 0, 480, 520, 1, 1, None, 16, k.light),
         k.pattern_rect(510, 0, 480, 520, 1, 1, None, 16, k.brand_bg),
         k.pattern_rect(1020, 0, 480, 520, 1, 0.9, k.on(k.primary), 16, k.primary)]
logo = k.logo("primary", 60, 160, 360, 200)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(parts) + \
      f'<rect x="80" y="170" width="320" height="180" rx="12" fill="#FFFFFF"/>{logo}</svg>'
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
    f.write(f"<html><head><meta charset='utf-8'></head><body style='margin:0'>{svg}</body></html>"); p = f.name
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                "--virtual-time-budget=8000", f"--screenshot={out}", "file://" + p], capture_output=True)
print(out)
