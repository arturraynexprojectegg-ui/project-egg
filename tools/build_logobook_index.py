#!/usr/bin/env python3
"""Оглавление логобуков: logobooks/index.html (локально) и logobooks/index.artifact.html (для публикации)."""
import json, re, html, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chrome_util import fonts_href, used_families

BRAND = "--brand" in sys.argv
ROOT = Path(__file__).resolve().parent.parent
LB = ROOT / "logobooks"
OUT = ROOT / ("brandbooks" if BRAND else "logobooks")
SUF = "Brandbook" if BRAND else "Logobook"
esc = lambda s: html.escape(str(s), quote=True)

cards, allsvg = [], ""
LEAD_LB = "{n} концептов, отобранных из 80. В каждом логобуке 12 разделов: концепция, версии, охранное поле, минимальные размеры, цвета, цветовые версии, типографика, недопустимое использование и знак в цифровой среде. Для каждого есть SVG для импорта в Figma."
LEAD_BB = "{n} брендбуков на базе логобуков. Платформа бренда, ценности, аудитория, голос, слоганы, цвет, типографика, фирменный паттерн, фотостиль и брендированные носители: упаковка для розницы и HoReCa, яичный порошок, логистика, документация, униформа, сайт и соцсети. Для каждого есть SVG для импорта в Figma."
for d in sorted(p for p in LB.glob("PE-*") if (p / "data.json").exists() and (not BRAND or (OUT / p.name / "brand.json").exists())):
    data = json.loads((d / "data.json").read_text())
    code = data["code"]
    svg = (d / "primary.svg").read_text()
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    for x in sorted(set(re.findall(r'\bid="([^"]+)"', svg)), key=len, reverse=True):
        p = f"i{code.replace('.', '')}-{x}"
        svg = svg.replace(f'id="{x}"', f'id="{p}"').replace(f"#{x})", f"#{p})").replace(f'href="#{x}"', f'href="#{p}"')
    allsvg += svg
    dots = "".join(f'<i style="background:{esc(c["hex"])}" title="{esc(c["name"])}"></i>' for c in data["palette"][:5])
    cards.append(f'''<article class="card">
  <a class="art" href="{code}/{code}_{SUF}.html" aria-label="Открыть {esc(data["name"])}">{svg}</a>
  <div class="info">
    <span class="code">{code}</span>
    <h2>{esc(data["name"])}</h2>
    <p>{esc((json.loads((OUT / code / "brand.json").read_text()).get("taglines", {}).get("es") if BRAND else None) or data.get("tagline", ""))}</p>
    <div class="row"><div class="dots">{dots}</div>
      <div class="links"><a href="{code}/{code}_{SUF}.html">{"Брендбук" if BRAND else "Логобук"}</a><a href="{code}/{code}_{SUF}_Figma.svg">SVG для Figma</a></div></div>
  </div>
</article>''')

fam = used_families(allsvg + " Inter Fraunces")
LEAD = (LEAD_BB if BRAND else LEAD_LB).format(n=len(cards))
body = f'''<title>{'Primeegg брендбуки' if BRAND else 'Primeegg логобуки'}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts_href(fam)}">
<style>
/* Сетка карточек-обложек; цвет задаёт каждый логотип, страница нейтральная тёплая */
:root{{color-scheme:light;--bg:#EFECE6;--card:#FFFFFF;--ink:#1C1B19;--muted:#6B665D;--line:#DAD5CC;--acc:#B07A00;
  --display:Fraunces,Georgia,serif;--text:Inter,system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;--acc:#E0A100;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;--acc:#E0A100;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 var(--text)}}
.wrap{{max-width:1400px;margin:auto;padding-block:48px 80px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--acc);text-transform:uppercase}}
h1{{font:600 clamp(32px,5vw,56px)/1.05 var(--display);margin:8px 0 12px;text-wrap:balance}}
.lead{{color:var(--muted);max-width:62ch;margin:0 0 32px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));gap:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;color:#1C1B19}}
.art{{display:block;aspect-ratio:4/3;max-width:100%;background:#FBFAF7;border-bottom:1px solid #ECE8E0}}
.art svg{{width:100%;height:100%;display:block}}
.art:focus-visible{{outline:3px solid var(--acc);outline-offset:-3px}}
.info{{padding:14px 16px 16px;display:flex;flex-direction:column;gap:4px;flex:1}}
.code{{font-size:12px;font-weight:700;letter-spacing:.12em;color:#B07A00}}
h2{{font:600 21px/1.2 var(--display);margin:0}}
.info p{{margin:0;color:#6B665D;font-size:14px;flex:1}}
.row{{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px;flex-wrap:wrap}}
.dots{{display:flex;gap:4px}} .dots i{{width:16px;height:16px;border-radius:50%;border:1px solid #0002}}
.links{{display:flex;gap:8px}}
.links a{{font-size:13px;font-weight:600;color:#1C1B19;text-decoration:none;border:1px solid #DAD5CC;border-radius:8px;padding:6px 10px}}
.links a:hover,.links a:focus-visible{{border-color:#B07A00;outline:none}}
</style>
<div class="wrap">
<div class="eyebrow">Primeegg Distribution SL · этап {"03" if BRAND else "02"}</div>
<h1>{"Брендбуки" if BRAND else "Логобуки"}</h1>
<p class="lead">{LEAD}</p>
<div class="grid">{"".join(cards)}</div>
</div>'''
(OUT / "index.artifact.html").write_text(body)
(OUT / "index.html").write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                               + body.replace("<div class=\"wrap\">", "</head><body><div class=\"wrap\">", 1) + "</body></html>")
print("index OK:", len(cards))
