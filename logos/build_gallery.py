#!/usr/bin/env python3
"""Собирает logos/index.html — галерею всех концептов с inline SVG."""
import json, html, re
from pathlib import Path

ROOT = Path(__file__).parent
STYLES = {
    "01-minimal": "Минимализм и геометрия",
    "02-farm-craft": "Фермерский крафт",
    "03-mediterranean": "Средиземноморье",
    "04-premium": "Премиум",
    "05-corporate-b2b": "Корпоративный B2B",
    "06-friendly-retail": "Дружелюбный ретейл",
    "07-wordmark": "Типографика",
    "08-eco-organic": "Эко / органика",
}
FONTS = ["Fraunces:wght@300..900", "Playfair+Display:wght@400..900", "DM+Serif+Display",
         "Cormorant+Garamond:wght@300..700", "Libre+Baskerville:wght@400;700", "Abril+Fatface",
         "Lora:wght@400..700", "Montserrat:wght@300..900", "Manrope:wght@300..800",
         "Space+Grotesk:wght@300..700", "Syne:wght@400..800", "Bricolage+Grotesque:wght@300..800",
         "Outfit:wght@300..900", "Archivo+Black", "Josefin+Sans:wght@300..700", "Bebas+Neue",
         "Oswald:wght@300..700", "Inter:wght@300..900", "Fredoka:wght@300..700",
         "Baloo+2:wght@400..800", "Nunito:wght@300..900", "Quicksand:wght@300..700",
         "Pacifico", "Lobster", "Caveat:wght@400..700", "Yellowtail", "Rye"]

def strip_svg(svg: str) -> str:
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
    return svg.strip()

sections, total = [], 0
for i, (folder, name) in enumerate(STYLES.items(), 1):
    d = ROOT / folder
    meta_path = d / "meta.json"
    if not meta_path.exists():
        continue
    meta = json.loads(meta_path.read_text())
    cards = []
    for m in meta:
        f = d / m["file"]
        if not f.exists():
            continue
        lid = f"{i:02d}-{f.stem}"
        # уникализируем id внутри SVG, чтобы градиенты/clipPath не конфликтовали
        svg = strip_svg(f.read_text())
        ids = set(re.findall(r'id="([^"]+)"', svg))
        for x in sorted(ids, key=len, reverse=True):
            p = f"L{lid}-{x}"
            svg = svg.replace(f'id="{x}"', f'id="{p}"').replace(f"#{x})", f"#{p})") \
                     .replace(f'href="#{x}"', f'href="#{p}"')
        swatches = "".join(f'<i style="background:{html.escape(c)}"></i>' for c in m.get("colors", [])[:6])
        cards.append(f'''<article class="card" data-id="{lid}">
  <div class="art">{svg}</div>
  <div class="info">
    <label class="pick"><input type="checkbox" value="{lid}"><span class="num">{lid}</span></label>
    <h3>{html.escape(m.get("title",""))}</h3>
    <p>{html.escape(m.get("concept",""))}</p>
    <div class="sw">{swatches}</div>
  </div>
</article>''')
        total += 1
    sections.append(f'<section id="s{i:02d}"><h2><span>{i:02d}</span> {html.escape(name)}</h2><div class="grid">{"".join(cards)}</div></section>')

nav = "".join(f'<a href="#s{i:02d}">{i:02d} {html.escape(n)}</a>' for i, n in enumerate(STYLES.values(), 1))
fonts = "&".join(f"family={f}" for f in FONTS)

page = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Primeegg логотипы</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>
:root{{--bg:#F3EFE8;--card:#FAF7F2;--ink:#1d1b18;--muted:#6f685e;--line:#e2dbcf;--accent:#E0A100}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#16140f;--ink:#f1ece3;--muted:#a59d90;--line:#2d2a24;--card:#FAF7F2}}}}
:root[data-theme="dark"]{{--bg:#16140f;--ink:#f1ece3;--muted:#a59d90;--line:#2d2a24;--card:#FAF7F2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}}
header{{padding:40px 16px 16px;max-width:1400px;margin:auto}}
h1{{font:700 clamp(28px,4vw,44px)/1.1 Fraunces,serif;margin:0 0 8px}}
header p{{color:var(--muted);margin:0;max-width:720px}}
nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:6px;overflow-x:auto}}
nav a{{white-space:nowrap;color:var(--ink);text-decoration:none;font-size:13px;padding:6px 10px;border:1px solid var(--line);border-radius:99px}}
nav a:hover{{border-color:var(--accent)}}
main{{max-width:1400px;margin:auto;padding:0 16px 120px}}
section{{scroll-margin-top:60px}}
h2{{font:600 24px Fraunces,serif;margin:48px 0 16px}} h2 span{{color:var(--accent)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.card{{background:var(--card);color:#1d1b18;border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .2s}}
.card.on{{outline:3px solid var(--accent);outline-offset:-3px}}
.art{{aspect-ratio:4/3;display:grid;place-items:center;border-bottom:1px solid #ece5d8}}
.art svg{{width:100%;height:100%}}
.info{{padding:12px 14px 14px}}
.info h3{{margin:4px 0;font-size:15px}} .info p{{margin:0;font-size:13px;color:#6f685e}}
.pick{{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;color:#6f685e}}
.pick input{{width:18px;height:18px;accent-color:#E0A100}}
.num{{font-family:"Space Grotesk",monospace;font-weight:600}}
.sw{{display:flex;gap:4px;margin-top:8px}} .sw i{{width:16px;height:16px;border-radius:50%;border:1px solid #0002}}
.bar{{position:fixed;left:0;right:0;bottom:0;background:#1d1b18;color:#fff;padding:12px 16px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap;font-size:14px}}
.bar button{{background:#E0A100;color:#1d1b18;border:0;border-radius:8px;padding:8px 14px;font-weight:600;cursor:pointer}}
.bar code{{background:#fff1;padding:4px 8px;border-radius:6px;max-width:60vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
</style></head><body>
<header><h1>Primeegg Distribution SL. Концепты логотипа</h1>
<p>{total} концептов в 8 стилях. Отметьте понравившиеся (цель — 10–20), нажмите «Скопировать» и отправьте список в чат.</p></header>
<nav>{nav}</nav>
<main>{"".join(sections)}</main>
<div class="bar"><span>Выбрано: <b id="cnt">0</b></span><code id="list">—</code><button id="copy">Скопировать</button></div>
<script>
const KEY='primeegg-picks';let picks=[];
try{{picks=JSON.parse(localStorage.getItem(KEY)||'[]')}}catch(e){{}}
const boxes=[...document.querySelectorAll('.pick input')];
function render(){{boxes.forEach(b=>{{b.checked=picks.includes(b.value);b.closest('.card').classList.toggle('on',b.checked)}});
document.getElementById('cnt').textContent=picks.length;document.getElementById('list').textContent=picks.join(', ')||'—';
try{{localStorage.setItem(KEY,JSON.stringify(picks))}}catch(e){{}}}}
boxes.forEach(b=>b.addEventListener('change',()=>{{picks=b.checked?[...picks,b.value]:picks.filter(x=>x!==b.value);picks.sort();render()}}));
document.getElementById('copy').onclick=async()=>{{const t='Выбранные логотипы: '+picks.join(', ');
try{{await navigator.clipboard.writeText(t);document.getElementById('copy').textContent='Скопировано ✓'}}catch(e){{prompt('Скопируйте:',t)}}}};
render();
</script></body></html>'''
(ROOT / "index.html").write_text(page)
print(f"OK: {total} logos -> logos/index.html")
