#!/usr/bin/env python3
"""Экспорт графики концепта для сайта: python3 tools/export_assets.py PE-04.05 sites/PE-04.05/assets
Создаёт SVG-файлы:
  logo-<key>.svg (primary, horizontal, vertical, mark, wordmark, inverse), logo-mono-white.svg, logo-mono-dark.svg,
  pattern.svg (тайл), pattern-on-brand.svg (готовый фрагмент 1200×800 на фирменном цвете),
  scene-<name>.svg (мокапы 1680×700: pack_retail, pack_horeca, pack_powder, logistics, uniform, icons ...).
ВНИМАНИЕ: в логотипах и сценах есть <text> с Google Fonts — при подключении через <img> шрифты не загрузятся.
Вставляй такие SVG инлайном в HTML (fetch не нужен — просто вставь содержимое файла в разметку при сборке)."""
import sys, importlib, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from brandkit import BrandKit

code, out = sys.argv[1], Path(sys.argv[2])
lang = sys.argv[3] if len(sys.argv) > 3 else "es"
out.mkdir(parents=True, exist_ok=True)
k = BrandKit(code, lang)
VB = {"primary": (400, 300), "horizontal": (640, 200), "vertical": (400, 400), "mark": (200, 200),
      "wordmark": (640, 160), "inverse": (400, 300)}
wrap = lambda w, h, body: f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">{body}</svg>\n'
for key, (w, h) in VB.items():
    (out / f"logo-{key}.svg").write_text(wrap(w, h, k.logo(key, 0, 0, w, h)))
(out / "logo-mono-white.svg").write_text(wrap(400, 300, k.logo("mono", 0, 0, 400, 300, color="#FFFFFF")))
(out / "logo-mono-dark.svg").write_text(wrap(400, 300, k.logo("mono", 0, 0, 400, 300, color=k.ink)))
if k.pattern_src:
    (out / "pattern.svg").write_text(k.pattern_src)
    (out / "pattern-on-brand.svg").write_text(wrap(1200, 800, k.pattern_rect(0, 0, 1200, 800, 1, 0.35, k.on(k.brand_bg), 0, k.brand_bg)))
for name in ["icons", "pack_retail", "pack_horeca", "pack_powder", "logistics", "stationery", "uniform"]:
    try:
        mod = importlib.import_module(f"mockups.{name}")
        (out / f"scene-{name}.svg").write_text(wrap(1680, 700, mod.render(k, 1680, 700)))
    except Exception as e:
        print("skip", name, e)
print("assets ->", out, "| colors:", dict(primary=k.primary, accent=k.accent, dark=k.dark, light=k.light, ink=k.ink, brand_bg=k.brand_bg),
      "| fonts:", k.head_font, "/", k.text_font)
