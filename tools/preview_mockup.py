#!/usr/bin/env python3
"""python3 tools/preview_mockup.py <scene> <out.png> [PE-коды...]"""
import sys, subprocess, tempfile, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from brandkit import BrandKit
from chrome_util import CHROME, fonts_href

scene, out = sys.argv[1], sys.argv[2]
codes = sys.argv[3:] or ["PE-01.05", "PE-04.05", "PE-06.05", "PE-08.07"]
mod = importlib.import_module(f"mockups.{scene}")
importlib.reload(mod)
W, H = 1680, 700
rows = []
for i, c in enumerate(codes):
    k = BrandKit(c)
    rows.append(f'<g transform="translate(0,{i*(H+40)})"><rect width="{W}" height="{H}" fill="#FBFAF7"/>'
                f'<text x="12" y="24" font-family="Inter" font-size="16" fill="#999">{c}</text>{mod.render(k, W, H)}</g>')
TH = len(codes) * (H + 40)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{TH}" viewBox="0 0 {W} {TH}">{"".join(rows)}</svg>'
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
    f.write(f'<html><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts_href(display="block")}"></head><body style="margin:0">{svg}</body></html>')
    p = f.name
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{TH}",
                "--virtual-time-budget=15000", f"--screenshot={out}", "file://" + p], capture_output=True)
print(out)
