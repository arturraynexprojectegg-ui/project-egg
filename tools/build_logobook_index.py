#!/usr/bin/env python3
"""Оглавление логобуков / брендбуков с переключателем UA / ES.
  python3 tools/build_logobook_index.py          -> logobooks/index.html, logobooks/index.artifact.html
  python3 tools/build_logobook_index.py --brand  -> brandbooks/index.html, brandbooks/index.artifact.html"""
import json, re, html, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chrome_util import fonts_href, used_families
from brandkit import load_lang

BRAND = "--brand" in sys.argv
ROOT = Path(__file__).resolve().parent.parent
LB = ROOT / "logobooks"
OUT = ROOT / ("brandbooks" if BRAND else "logobooks")
SUF = "Brandbook" if BRAND else "Logobook"
esc = lambda s: html.escape(str(s), quote=True)

TXT = {
    "uk": {"eyebrow": "Primeegg Distribution SL · етап " + ("03" if BRAND else "02"),
           "h1": "Брендбуки" if BRAND else "Логобуки",
           "lead": ("{n} брендбуків на основі логобуків: платформа бренду, цінності, аудиторія, голос, слогани, колір, типографіка, "
                    "фірмовий патерн, фотостиль і брендовані носії — упаковка для роздрібу та HoReCa, яєчний порошок, логістика, "
                    "документація, уніформа, сайт і соцмережі. Для кожного є SVG для імпорту у Figma." if BRAND else
                    "{n} концептів, відібраних із 80. У кожному логобуці 12 розділів: концепція, версії, охоронне поле, мінімальні розміри, "
                    "кольори, колірні версії, типографіка, неприпустиме використання й знак у цифровому середовищі. Для кожного є SVG для імпорту у Figma."),
           "open": "Брендбук" if BRAND else "Логобук", "figma": "SVG для Figma", "title": "Primeegg брендбуки" if BRAND else "Primeegg логобуки"},
    "es": {"eyebrow": "Primeegg Distribution SL · fase " + ("03" if BRAND else "02"),
           "h1": "Manuales de marca" if BRAND else "Manuales de logotipo",
           "lead": ("{n} manuales de marca basados en los manuales de logotipo: plataforma de marca, valores, público, tono, eslóganes, color, "
                    "tipografía, patrón corporativo, estilo fotográfico y aplicaciones: envases para retail y hostelería, huevo en polvo, logística, "
                    "papelería, uniformes, web y redes sociales. Cada uno incluye un SVG para importar en Figma." if BRAND else
                    "{n} conceptos seleccionados entre 80. Cada manual tiene 12 apartados: concepto, versiones, área de protección, tamaños mínimos, "
                    "colores, versiones de color, tipografía, usos incorrectos y el símbolo en entornos digitales. Cada uno incluye un SVG para importar en Figma."),
           "open": "Manual de marca" if BRAND else "Manual", "figma": "SVG para Figma", "title": "Primeegg manuales"},
}
SFX = {"uk": "UA", "es": "ES"}

codes = sorted(p.name for p in LB.glob("PE-*") if (p / "data.json").exists()
               and (not BRAND or (OUT / p.name / "brand.json").exists()))
arts, allsvg = {}, ""
for code in codes:
    svg = re.sub(r"<title>.*?</title>", "", (LB / code / "primary.svg").read_text(), flags=re.S)
    for x in sorted(set(re.findall(r'\bid="([^"]+)"', svg)), key=len, reverse=True):
        p = f"i{code.replace('.', '')}-{x}"
        svg = svg.replace(f'id="{x}"', f'id="{p}"').replace(f"#{x})", f"#{p})").replace(f'href="#{x}"', f'href="#{p}"')
    arts[code] = svg
    allsvg += svg


def grid(lang):
    t = TXT[lang]
    cards = []
    for code in codes:
        d = load_lang(LB / code / "data.json", lang)
        sub = d.get("tagline", "")
        if BRAND:
            b = load_lang(OUT / code / "brand.json", lang)
            sub = b.get("taglines", {}).get("es") or sub
        dots = "".join(f'<i style="background:{esc(c["hex"])}" title="{esc(c["name"])}"></i>' for c in d["palette"][:5])
        page = f"{code}/{code}_{SUF}_{SFX[lang]}.html"
        fig = f"{code}/{code}_{SUF}_Figma_{SFX[lang]}.svg"
        cards.append(f'''<article class="card">
  <a class="art" href="{page}" aria-label="{esc(t["open"])} {esc(d["name"])}">{arts[code] if lang == "uk" else arts[code].replace('id="i', 'id="e').replace('#i', '#e')}</a>
  <div class="info"><span class="code">{code}</span><h2>{esc(d["name"])}</h2><p>{esc(sub)}</p>
    <div class="row"><div class="dots">{dots}</div>
      <div class="links"><a href="{page}">{esc(t["open"])}</a><a href="{fig}">{esc(t["figma"])}</a></div></div></div>
</article>''')
    return (f'<section class="lang-block" data-lang="{lang}"{"" if lang == "uk" else " hidden"} lang="{lang}">'
            f'<div class="eyebrow">{esc(t["eyebrow"])}</div><h1>{esc(t["h1"])}</h1>'
            f'<p class="lead">{esc(t["lead"].format(n=len(codes)))}</p><div class="grid">{"".join(cards)}</div></section>')


fam = used_families(allsvg + " Inter Playfair Display")
body = f'''<title>{TXT["uk"]["title"]}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts_href(fam)}">
<style>
/* Сетка карточек-обложек; цвет задаёт каждый логотип, страница нейтральная тёплая */
:root{{color-scheme:light;--bg:#EFECE6;--card:#FFFFFF;--ink:#1C1B19;--muted:#6B665D;--line:#DAD5CC;--acc:#B07A00;
  --display:"Playfair Display",Georgia,serif;--text:Inter,system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;--acc:#E0A100;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;--acc:#E0A100;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 var(--text)}}
.wrap{{max-width:1400px;margin:auto;padding-block:24px 80px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.switch{{display:flex;justify-content:flex-end;gap:6px;margin-bottom:16px}}
.switch button{{font:700 13px/1 var(--text);letter-spacing:.08em;padding:9px 14px;border-radius:10px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer}}
.switch button[aria-pressed="true"]{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.switch button:focus-visible{{outline:3px solid var(--acc);outline-offset:2px}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--acc);text-transform:uppercase}}
h1{{font:600 clamp(32px,5vw,56px)/1.05 var(--display);margin:8px 0 12px;text-wrap:balance}}
.lead{{color:var(--muted);max-width:66ch;margin:0 0 32px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));gap:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;color:#1C1B19}}
.art{{display:block;aspect-ratio:4/3;max-width:100%;background:#FBFAF7;border-bottom:1px solid #ECE8E0}}
.art svg{{width:100%;height:100%;display:block}}
.art:focus-visible{{outline:3px solid var(--acc);outline-offset:-3px}}
.info{{padding:14px 16px 16px;display:flex;flex-direction:column;gap:4px;flex:1;min-width:0}}
.code{{font-size:12px;font-weight:700;letter-spacing:.12em;color:#B07A00}}
h2{{font:600 21px/1.2 var(--display);margin:0}}
.info p{{margin:0;color:#6B665D;font-size:14px;flex:1}}
.row{{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px;flex-wrap:wrap}}
.dots{{display:flex;gap:4px}} .dots i{{width:16px;height:16px;border-radius:50%;border:1px solid #0002}}
.links{{display:flex;gap:8px;flex-wrap:wrap}}
.links a{{font-size:13px;font-weight:600;color:#1C1B19;text-decoration:none;border:1px solid #DAD5CC;border-radius:8px;padding:6px 10px}}
.links a:hover,.links a:focus-visible{{border-color:#B07A00;outline:none}}
</style>
<div class="wrap">
<div class="switch" role="group" aria-label="Мова / Idioma">
  <button type="button" id="btn-uk" data-l="uk" aria-pressed="true">UA · Українська</button>
  <button type="button" id="btn-es" data-l="es" aria-pressed="false">ES · Español</button>
</div>
{grid("uk")}
{grid("es")}
</div>
<script>
(function(){{
  const T={{uk:{json.dumps(TXT["uk"]["title"], ensure_ascii=False)},es:{json.dumps(TXT["es"]["title"], ensure_ascii=False)}}};
  function show(l){{
    document.querySelectorAll('.lang-block').forEach(s=>s.hidden=s.dataset.lang!==l);
    document.querySelectorAll('.switch button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.l===l));
    document.documentElement.lang=l; document.title=T[l];
    try{{localStorage.setItem('pe-lang',l)}}catch(e){{}}
  }}
  document.querySelectorAll('.switch button').forEach(b=>b.addEventListener('click',()=>show(b.dataset.l)));
  let l=(location.hash==='#es'||location.hash==='#uk')?location.hash.slice(1):null;
  if(!l){{try{{l=localStorage.getItem('pe-lang')}}catch(e){{}}}}
  show(l==='es'?'es':'uk');
}})();
</script>'''
(OUT / "index.artifact.html").write_text(body)
(OUT / "index.html").write_text('<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                + body.replace('<div class="wrap">', '</head><body><div class="wrap">', 1) + "</body></html>")
print("index OK:", OUT.name, len(codes))
