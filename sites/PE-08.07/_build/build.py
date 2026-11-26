#!/usr/bin/env python3
"""Builds sites/PE-08.07/index.html (ES) and uk.html (UA) from one structure."""
import re, json, urllib.parse, sys
from pathlib import Path

SITE = Path("/Users/arturkasian/Project Egg/sites/PE-08.07")
A = SITE / "assets"
sys.path.insert(0, str(Path(__file__).parent))
from content import T, PROVINCIAS  # noqa

_counter = [0]


def svg(name, viewBox=None, cls="", label=None, prefix=None):
    """Inline an asset SVG: optional crop, ids prefixed, a11y attributes."""
    src = (A / name).read_text()
    src = re.sub(r"<\?xml.*?\?>", "", src).strip()
    m = re.match(r"<svg([^>]*)>(.*)</svg>\s*$", src, re.S)
    attrs, body = m.group(1), m.group(2)
    vb = viewBox or re.search(r'viewBox="([^"]+)"', attrs).group(1)
    _counter[0] += 1
    p = prefix or f"s{_counter[0]}-"
    ids = set(re.findall(r'id="([^"]+)"', body))
    for i in sorted(ids, key=len, reverse=True):
        body = body.replace(f'id="{i}"', f'id="{p}{i}"')
        body = body.replace(f"url(#{i})", f"url(#{p}{i})")
        body = body.replace(f'href="#{i}"', f'href="#{p}{i}"')
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    c = f' class="{cls}"' if cls else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{c} {a11y} preserveAspectRatio="xMidYMid meet">{body}</svg>'


def favicon():
    s = (A / "logo-mark.svg").read_text()
    return "data:image/svg+xml," + urllib.parse.quote(s)


def pattern_uri(color):
    s = (A / "pattern.svg").read_text().replace("#8A9A5B", color).replace("#A3B46C", color)
    return "data:image/svg+xml," + urllib.parse.quote(s)


ICONS = {
    "tray": '<rect x="3" y="6" width="26" height="20" rx="4"/><circle cx="10" cy="13" r="2.6"/><circle cx="16" cy="13" r="2.6"/><circle cx="22" cy="13" r="2.6"/><circle cx="10" cy="20" r="2.6"/><circle cx="16" cy="20" r="2.6"/><circle cx="22" cy="20" r="2.6"/>',
    "calendar": '<rect x="4" y="7" width="24" height="21" rx="4"/><path d="M4 13h24M11 4v6M21 4v6"/><path d="M12 20.5l3 3 6-6"/>',
    "person": '<circle cx="16" cy="11" r="5"/><path d="M6 27c1.5-6 5.5-9 10-9s8.5 3 10 9"/>',
    "clock": '<circle cx="16" cy="16" r="12"/><path d="M16 9v7l5 3"/>',
    "cold": '<path d="M16 3v26M5 9.5l22 13M5 22.5l22-13"/><path d="M12 5l4 3 4-3M12 27l4-3 4 3"/>',
    "box": '<path d="M4 10l12-6 12 6v12l-12 6-12-6z"/><path d="M4 10l12 6 12-6M16 16v12"/>',
    "leaf": '<path d="M16 3C22 3 26 12 26 18c0 6-4.5 10-10 10S6 24 6 18C6 12 10 3 16 3z"/><path d="M16 26c-.5-6 .5-13 0-20M16 21l-5-4M16 15l5-4"/>',
    "check": '<path d="M6 16.5l6.5 6.5L26 9.5"/>',
    "arrow": '<path d="M5 16h21M19 9l7 7-7 7"/>',
    "lot": '<path d="M5 5h13l9 9-13 13-9-9z"/><circle cx="11" cy="11" r="2"/>',
    "lab": '<path d="M12 4h8M13 4v8L6 25a2 2 0 0 0 2 3h16a2 2 0 0 0 2-3l-7-13V4"/><path d="M9 20h14"/>',
    "seal": '<circle cx="16" cy="13" r="8"/><path d="M11 20l-2 9 7-4 7 4-2-9"/>',
    "phone": '<path d="M8 4h5l2 6-3 2a15 15 0 0 0 8 8l2-3 6 2v5a3 3 0 0 1-3 3C14 27 5 18 5 7a3 3 0 0 1 3-3z"/>',
    "mail": '<rect x="4" y="7" width="24" height="18" rx="3"/><path d="M5 9l11 8 11-8"/>',
    "pin": '<path d="M16 29s-9-9-9-16a9 9 0 0 1 18 0c0 7-9 16-9 16z"/><circle cx="16" cy="13" r="3"/>',
    "seed": '<ellipse cx="16" cy="17" rx="7" ry="9"/><path d="M16 8c0-3 2-5 5-5" />',
}


def icon(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'


LEAFMARK = '<svg class="node" viewBox="0 0 100 152" aria-hidden="true" focusable="false"><path d="M50 0 C78 0 100 45 100 80 C100 110 78 130 50 130 C22 130 0 110 0 80 C0 45 22 0 50 0 Z" fill="#8A9A5B"/><path d="M50 122 C46.5 92 53.5 52 50 11" fill="none" stroke="#F3EAD3" stroke-width="6" stroke-linecap="round"/><path d="M49.2 101 Q37 95 24 83 M50.2 80 Q64 74 78 60 M51 61 Q38 55 27 42 M51.2 43 Q62 37 72 26" fill="none" stroke="#F3EAD3" stroke-width="5" stroke-linecap="round"/><path d="M50 129 C51.5 139 56 146 64 150" fill="none" stroke="#2F5D3A" stroke-width="6" stroke-linecap="round"/></svg>'

WAVE_TOP = '<svg class="wave wave--top" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 90 L0 52 C180 18 360 8 560 30 C760 52 900 76 1100 56 C1260 40 1360 22 1440 30 L1440 90 Z" fill="currentColor"/></svg>'
WAVE_BOT = '<svg class="wave wave--bot" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 0 L0 38 C200 70 420 84 640 60 C840 38 1000 20 1200 40 C1320 52 1390 62 1440 58 L1440 0 Z" fill="currentColor"/></svg>'


def nb(o):
    if isinstance(o, str):
        o = re.sub(r"(\d) (kg|g|h|km|m²|uds|%|°C|г|кг|км|год|м²|×)", "\\1&nbsp;\\2", o)
        return re.sub(r"(≈|<|&lt;|≥|×) (?=\d)", "\\1&nbsp;", o)
    if isinstance(o, dict): return {k: nb(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return type(o)(nb(x) for x in o)
    return o


def build(lang):
    t = nb(T[lang])
    other = "uk.html" if lang == "es" else "index.html"
    _counter[0] = 0
    fonts_es = "family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..900,0..100;1,9..144,300..900,0..100&family=Nunito:ital,wght@0,400..800;1,400..600"
    fonts = fonts_es if lang == "es" else fonts_es + "&family=Playfair+Display:ital,wght@0,400..800;1,400..700"
    disp = "'Fraunces', Georgia, serif" if lang == "es" else "'Playfair Display', Georgia, serif"
    dispvar = '"SOFT" 100, "WONK" 0' if lang == "es" else "normal"

    nav = "".join(f'<li><a href="#{h}">{n}</a></li>' for h, n in t["nav"])
    lang_sw = (f'<div class="lang" role="group" aria-label="{t["lang_label"]}">'
               + (f'<span aria-current="true" lang="es">ES</span><a href="uk.html" hreflang="uk" lang="uk" title="Українська">UA</a>'
                  if lang == "es" else
                  f'<a href="index.html" hreflang="es" lang="es" title="Español">ES</a><span aria-current="true" lang="uk">UA</span>')
               + '</div>')

    logo = svg("logo-horizontal.svg", "116 24 420 132", "logo", "Primeegg")
    logo_inv = svg("logo-inverse.svg", "38 94 322 124", "logo", "Primeegg")

    # ---------- products ----------
    p = t["prod"]
    sizes = "".join(
        f'<li><span class="egg" style="--s:{s}" aria-hidden="true"></span><b>{n}</b><small>{g}</small></li>'
        for (n, g), s in zip(p["sizes"], [0.72, 0.84, 0.94, 1.06]))
    fresh_specs = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in p["fresh_specs"])
    powder_rows = "".join(
        f'<tr><th scope="row">{n}<small>{u}</small></th><td>{a}</td><td>{b}</td></tr>' for n, u, a, b in p["powder_rows"])
    soon = "".join(f'<li>{icon("seed")}<span><b>{n}</b>{d}</span></li>' for n, d in p["soon"])

    # ---------- timeline ----------
    tl_files = ["tl-granja", "tl-recogida", "tl-clasificacion", "tl-envasado", "tl-ruta", "tl-cocina"]
    steps = "".join(
        f'<li class="tl-step"><div class="tl-art">{svg(f + ".svg", cls="tl-illo", label=alt)}</div>{LEAFMARK}'
        f'<div class="tl-text"><h3>{h}</h3><p class="tl-when">{w}</p><p>{d}</p></div></li>'
        for f, (h, w, d, alt) in zip(tl_files, t["tl"]["steps"]))

    nums = "".join(
        f'<li><span class="n-fig">{fig}</span><span class="n-lab">{lab}</span></li>' for fig, lab in t["eco"]["items"])

    # ---------- horeca ----------
    h = t["horeca"]
    hfeat = "".join(f'<li>{icon(i)}<div><h3>{a}</h3><p>{b}</p></div></li>' for i, a, b in h["features"])
    week = "".join(
        f'<li class="{"on" if on else ""}"><abbr title="{full}">{d}</abbr>{LEAFMARK if on else "<i></i>"}</li>'
        for d, full, on in h["week"])

    # ---------- distribution ----------
    d = t["dist"]
    zones = "".join(f'<li class="z z-{k}"><span class="sw" aria-hidden="true"></span><div><b>{a}</b><span>{b}</span></div></li>' for k, a, b in d["zones"])
    dfacts = "".join(f'<li>{icon(i)}<div><h3>{a}</h3><p>{b}</p></div></li>' for i, a, b in d["facts"])

    # ---------- quality ----------
    q = t["qual"]
    code = "".join(f'<li class="c-{k}"><span class="c-val">{v}</span><span class="c-lab"><b>{a}</b>{b}</span></li>' for k, v, a, b in q["code"])
    lots = "".join(f'<li>{icon(i)}<div><h3>{a}</h3><p>{b}</p></div></li>' for i, a, b in q["lots"])
    certs = "".join(f'<li>{icon("seal")}<b>{c}</b><span>{q["cert_note"]}</span></li>' for c in q["certs"])

    # ---------- how ----------
    how = "".join(f'<li><span class="how-n" aria-hidden="true">{i+1}</span><h3>{a}</h3><p>{b}</p></li>' for i, (a, b) in enumerate(t["how"]["steps"]))

    # ---------- form ----------
    f = t["form"]
    types = "".join(
        f'<label class="pill"><input type="radio" name="tipo" value="{v}" required><span>{n}</span></label>' for v, n in f["types"])
    prods = "".join(
        f'<label class="chk"><input type="checkbox" name="productos" value="{v}"><span>{n}</span></label>' for v, n in f["products"])
    provs = "".join(f"<option>{x}</option>" for x in PROVINCIAS)
    vols = "".join(f'<option value="{v}">{n}</option>' for v, n in f["volumes"])

    # ---------- about ----------
    ab = t["about"]
    values = "".join(f'<li>{icon("leaf")}<div><h3>{a}</h3><p>{b}</p></div></li>' for a, b in ab["values"])
    faq = "".join(f'<details><summary><span>{qq}</span>{icon("arrow", "ico chev")}</summary><div class="ans"><p>{aa}</p></div></details>' for qq, aa in t["faq"]["items"])

    c = t["contacts"]
    jsmsg = json.dumps(f["msg"], ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["title"]}</title>
<meta name="description" content="{t["desc"]}">
<meta name="theme-color" content="#2F5D3A">
<link rel="alternate" hreflang="es" href="index.html">
<link rel="alternate" hreflang="uk" href="uk.html">
<link rel="alternate" hreflang="x-default" href="index.html">
<link rel="icon" href="{favicon()}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<style>
:root{{
  --bg:#FAF6EC; --shell:#F3EAD3; --mist:#EDF0DC; --mist-2:#E4E9CF;
  --forest:#2F5D3A; --forest-2:#264D30; --sage:#8A9A5B; --leaf:#A3B46C; --deep:#1C2E22;
  --ink:#1C2E22; --ink-2:#45554A; --sage-ink:#55652F; --line:rgba(47,93,58,.2); --line-2:rgba(47,93,58,.34);
  --err:#9B3B23;
  --f-disp:{disp}; --f-body:'Nunito', 'Helvetica Neue', Arial, sans-serif; --disp-var:{dispvar};
  --wrap:1240px; --gut:clamp(16px,4.2vw,56px);
  --sec:clamp(88px,11vw,168px);
  --r-blob:58% 42% 52% 48% / 46% 54% 46% 54%;
  --ease:cubic-bezier(.16,1,.3,1);
}}
*,*::before,*::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%;scroll-padding-top:84px}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:1.0625rem;line-height:1.62;overflow-x:hidden;text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}}
::selection{{background:var(--leaf);color:var(--deep)}}
img,svg{{max-width:100%}}
a{{color:var(--forest);text-underline-offset:.22em;text-decoration-thickness:1px}}
a:hover{{text-decoration-thickness:2px}}
:focus-visible{{outline:2.5px solid var(--forest);outline-offset:3px;border-radius:6px}}
.dark :focus-visible{{outline-color:var(--leaf)}}
h1,h2,h3{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-weight:500;line-height:1.08;letter-spacing:-.015em;margin:0;text-wrap:balance;color:var(--deep)}}
h2{{font-size:clamp(2.1rem,4.4vw,3.6rem);font-weight:400}}
h3{{font-size:1.3rem;font-weight:600;line-height:1.2;letter-spacing:-.005em}}
p{{margin:0}}
em{{font-style:italic}}
main{{overflow-x:clip}}
.wrap{{max-width:var(--wrap);margin-inline:auto;padding-inline:var(--gut)}}
.lead{{font-size:clamp(1.12rem,1.5vw,1.3rem);line-height:1.55;color:var(--ink-2);max-width:56ch}}
.muted{{color:var(--ink-2)}}
.note{{font-size:.88rem;color:var(--ink-2);max-width:70ch}}
.sec{{padding-block:var(--sec);position:relative}}
.sec-head{{display:grid;gap:22px;max-width:780px;margin-bottom:clamp(48px,6vw,88px)}}
.skip{{position:absolute;left:12px;top:-60px;z-index:100;background:var(--forest);color:#fff;padding:10px 16px;border-radius:999px}}
.skip:focus{{top:12px}}
.ico{{width:28px;height:28px;flex:none;color:var(--forest)}}
::-webkit-scrollbar{{width:12px}}::-webkit-scrollbar-track{{background:var(--bg)}}::-webkit-scrollbar-thumb{{background:var(--mist-2);border-radius:10px;border:3px solid var(--bg)}}
html{{scrollbar-color:var(--mist-2) var(--bg)}}

/* buttons */
.btn{{display:inline-flex;align-items:center;gap:10px;font:700 1rem/1 var(--f-body);padding:16px 26px;border-radius:999px;text-decoration:none;border:1.5px solid var(--forest);transition:background .35s var(--ease),color .35s var(--ease),transform .35s var(--ease),box-shadow .35s var(--ease);cursor:pointer}}
.btn .ico{{width:20px;height:20px;color:currentColor;transition:transform .35s var(--ease)}}
.btn--solid{{background:var(--forest);color:var(--bg)}}
.btn--solid:hover{{background:var(--forest-2);box-shadow:0 10px 24px -12px rgba(28,46,34,.55);transform:translateY(-1px)}}
.btn--line{{color:var(--forest);background:transparent}}
.btn--line:hover{{background:var(--mist)}}
.btn:hover .ico{{transform:translateX(3px)}}
.btn--sm{{padding:11px 18px;font-size:.92rem}}

/* header */
.site-h{{position:sticky;top:0;z-index:50;background:var(--bg);transition:box-shadow .4s var(--ease),border-color .4s;border-bottom:1px solid transparent}}
.site-h.scrolled{{border-bottom-color:var(--line);box-shadow:0 8px 24px -20px rgba(28,46,34,.4)}}
.site-h .wrap{{display:flex;align-items:center;gap:24px;height:76px}}
.brand{{display:block;flex:none;line-height:0;border-radius:8px}}
.brand .logo{{height:46px;width:auto}}
.nav{{margin-left:auto;display:flex;align-items:center;gap:22px}}
.nav ul{{display:flex;gap:4px;list-style:none;margin:0;padding:0}}
.nav ul a{{display:block;padding:8px 11px;border-radius:999px;text-decoration:none;color:var(--ink);font-weight:600;font-size:.96rem;transition:background .3s,color .3s}}
.nav ul a:hover{{background:var(--mist);color:var(--forest)}}
.lang{{display:flex;align-items:center;border:1.5px solid var(--line-2);border-radius:999px;padding:3px;font-weight:800;font-size:.8rem;letter-spacing:.06em}}
.lang a,.lang span{{padding:6px 10px;border-radius:999px;line-height:1;text-decoration:none}}
.lang span{{background:var(--forest);color:var(--bg)}}
.lang a{{color:var(--forest)}}
.lang a:hover{{background:var(--mist)}}
.burger{{display:none;margin-left:auto;width:48px;height:48px;border-radius:50%;border:1.5px solid var(--line-2);background:transparent;cursor:pointer;color:var(--forest);align-items:center;justify-content:center}}
.burger span{{display:block;width:20px;height:2px;background:currentColor;border-radius:2px;position:relative;transition:transform .35s var(--ease),background .2s}}
.burger span::before,.burger span::after{{content:"";position:absolute;left:0;width:20px;height:2px;background:currentColor;border-radius:2px;transition:transform .35s var(--ease)}}
.burger span::before{{top:-6px}}.burger span::after{{top:6px}}
.burger[aria-expanded="true"] span{{background:transparent}}
.burger[aria-expanded="true"] span::before{{transform:translateY(6px) rotate(45deg)}}
.burger[aria-expanded="true"] span::after{{transform:translateY(-6px) rotate(-45deg)}}
@media (max-width:1180px){{
  .burger{{display:inline-flex}}
  .nav{{position:fixed;inset:76px 0 auto 0;background:var(--bg);flex-direction:column;align-items:stretch;gap:20px;padding:20px var(--gut) 32px;border-bottom:1px solid var(--line);box-shadow:0 24px 40px -30px rgba(28,46,34,.5);max-height:calc(100dvh - 76px);overflow:auto;display:none}}
  .nav.open{{display:flex}}
  .nav ul{{flex-direction:column;gap:0}}
  .nav ul a{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-size:1.6rem;font-weight:400;padding:12px 4px;border-radius:0;border-bottom:1px solid var(--line)}}
  .nav ul a:hover{{background:transparent}}
  .nav .lang{{align-self:flex-start}}
  .nav .btn{{justify-content:center}}
}}

/* hero */
.hero{{padding-block:clamp(32px,5vw,80px) clamp(8px,2vw,24px);position:relative;overflow:hidden}}
.hero .wrap{{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr);gap:clamp(24px,5vw,80px);align-items:center}}
.hero h1{{font-size:clamp(3rem,7.4vw,6rem);font-weight:340;line-height:.98;letter-spacing:-.03em}}
.hero h1 em{{display:block;color:var(--forest);font-weight:400}}
.hero .lead{{margin-top:clamp(24px,3vw,36px);max-width:44ch}}
.hero-cta{{display:flex;flex-wrap:wrap;gap:14px;margin-top:clamp(32px,4vw,48px)}}
.hero-for{{margin-top:clamp(40px,5vw,64px);display:flex;flex-wrap:wrap;gap:10px 28px;padding:0;list-style:none;font-weight:700;color:var(--sage-ink);font-size:.95rem}}
.hero-for li{{display:flex;align-items:center;gap:8px}}
.hero-for .ico{{width:20px;height:20px;color:var(--sage)}}
.hero-art{{position:relative;justify-self:end;width:min(100%,560px)}}
.hero-illo{{display:block;width:100%;height:auto}}
.tag{{position:absolute;left:66%;top:34%;transform:rotate(5deg);background:var(--bg);border:1.5px solid var(--forest);border-radius:10px 22px 22px 10px;padding:12px 18px 12px 26px;font-size:.84rem;line-height:1.4;box-shadow:0 14px 28px -18px rgba(28,46,34,.45);max-width:220px}}
.tag::before{{content:"";position:absolute;left:9px;top:50%;width:8px;height:8px;margin-top:-4px;border-radius:50%;border:1.5px solid var(--forest);background:var(--mist)}}
.tag b{{display:block;white-space:nowrap;font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-size:1.02rem;font-weight:600;color:var(--forest)}}
.tag span{{color:var(--ink-2)}}
@media (prefers-reduced-motion:no-preference){{
  .js .hero-illo .ln{{stroke-dasharray:1;animation:draw 2.6s var(--ease) both;animation-delay:calc(var(--i,0)*70ms + .15s)}}
  .js .hero-illo .wash{{animation:breathe 1.6s var(--ease) both}}
  .js .hero-illo .seeds{{animation:fade 1.2s 1.4s var(--ease) both}}
  .js .tag{{animation:hang 1.4s 1.2s var(--ease) both}}
  .js .hero-copy>*{{animation:rise 1.1s var(--ease) both}}
  .js .hero-copy>*:nth-child(2){{animation-delay:.12s}}.js .hero-copy>*:nth-child(3){{animation-delay:.22s}}.js .hero-copy>*:nth-child(4){{animation-delay:.32s}}
}}
@keyframes draw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
@keyframes breathe{{from{{transform:scale(.94);opacity:0;transform-origin:50% 55%}}to{{transform:scale(1);opacity:1;transform-origin:50% 55%}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px);filter:blur(4px)}}to{{opacity:1;transform:none;filter:none}}}}
@keyframes hang{{from{{opacity:0;transform:rotate(-4deg) translateY(-10px)}}to{{opacity:1;transform:rotate(5deg)}}}}

/* waves / tinted sections */
.tint{{background:var(--mist);position:relative}}
.tint-shell{{background:var(--shell)}}
.wave{{position:absolute;left:0;width:100%;height:clamp(36px,6vw,90px);display:block;pointer-events:none}}
.wave--top{{bottom:100%;margin-bottom:-1px}}
.wave--bot{{top:100%;margin-top:-1px}}
.tint .wave{{color:var(--mist)}} .tint-shell .wave{{color:var(--shell)}} .dark .wave{{color:var(--deep)}}

/* products */
.prod{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(32px,6vw,96px);align-items:center}}
.prod+.prod{{margin-top:clamp(80px,10vw,150px)}}
.prod--rev .prod-art{{order:2}}
.prod-art{{position:relative;isolation:isolate}}
.prod-art::before{{content:"";position:absolute;inset:6% 2% 2% 2%;background:var(--shell);border-radius:var(--r-blob);z-index:-1}}
.prod--rev .prod-art::before{{background:var(--mist);border-radius:44% 56% 40% 60% / 58% 44% 56% 42%}}
.prod-art svg{{display:block;width:100%;height:auto}}
.prod h3{{font-size:clamp(1.8rem,3vw,2.5rem);font-weight:400;letter-spacing:-.02em}}
.prod-body>p{{margin-top:16px;color:var(--ink-2);max-width:52ch}}
.sizes{{display:flex;align-items:flex-end;gap:clamp(14px,2.4vw,30px);list-style:none;padding:0;margin:32px 0 8px}}
.sizes li{{display:grid;justify-items:center;gap:6px;text-align:center}}
.sizes .egg{{display:block;width:calc(44px*var(--s));height:calc(58px*var(--s));border:2px solid var(--forest);border-radius:50% 50% 50% 50% / 60% 60% 40% 40%;background:var(--bg)}}
.sizes b{{font-weight:800;color:var(--forest);line-height:1}}
.sizes small{{font-size:.8rem;color:var(--ink-2);line-height:1.2}}
.specs{{display:grid;gap:0;margin:28px 0 0;border-top:1px solid var(--line)}}
.specs div{{display:grid;grid-template-columns:minmax(0,10.5rem) minmax(0,1fr);gap:16px;padding:13px 0;border-bottom:1px solid var(--line)}}
.specs dt{{font-weight:800;font-size:.9rem;color:var(--sage-ink)}}
.specs dd{{margin:0}}
.ptable{{width:100%;border-collapse:collapse;margin-top:28px;font-variant-numeric:tabular-nums}}
.ptable th,.ptable td{{text-align:left;padding:14px 12px 14px 0;border-bottom:1px solid var(--line);vertical-align:top;font-size:.98rem}}
.ptable thead th{{font-size:.8rem;font-weight:800;color:var(--sage-ink);letter-spacing:.04em;padding-block:8px}}
.ptable tbody th{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-weight:600;font-size:1.12rem;color:var(--deep)}}
.ptable tbody th small{{display:block;font-family:var(--f-body);font-weight:400;font-size:.85rem;color:var(--ink-2);margin-top:2px}}
.soon{{margin-top:clamp(80px,10vw,140px);border:1.5px dashed var(--line-2);border-radius:48px 120px 56px 140px / 60px 90px 70px 110px;padding:clamp(28px,4vw,56px);display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(24px,4vw,64px);align-items:start}}
.soon h3{{font-size:clamp(1.6rem,2.6vw,2.1rem);font-weight:400}}
.soon p{{margin-top:12px;color:var(--ink-2)}}
.soon ul{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px 32px}}
.soon li{{display:flex;gap:14px;align-items:flex-start}}
.soon li .ico{{color:var(--sage)}}
.soon li b{{display:block;font-weight:800}}
.soon li span{{color:var(--ink-2);font-size:.95rem;line-height:1.45}}

/* timeline */
#granja{{padding-top:calc(var(--sec)*.8)}}
#granja .sec-head{{margin-inline:auto;text-align:center;justify-items:center}}
.tl{{list-style:none;margin:0 auto;padding:0;position:relative;max-width:1080px}}
.tl::before{{content:"";position:absolute;left:50%;top:40px;bottom:40px;width:2px;margin-left:-1px;background:repeating-linear-gradient(to bottom,var(--sage) 0 10px,transparent 10px 18px)}}
.tl-step{{display:grid;grid-template-columns:minmax(0,1fr) 64px minmax(0,1fr);align-items:center;gap:clamp(16px,3vw,40px);position:relative}}
.tl-step+.tl-step{{margin-top:clamp(24px,3vw,40px)}}
.tl-step .node{{grid-column:2;grid-row:1;width:34px;height:auto;justify-self:center;background:var(--mist);padding:8px 0;box-sizing:content-box}}
.tl-art{{grid-column:1;grid-row:1;justify-self:end;width:min(100%,360px)}}
.tl-text{{grid-column:3;grid-row:1;max-width:400px}}
.tl-step:nth-child(even) .tl-art{{grid-column:3;justify-self:start}}
.tl-step:nth-child(even) .tl-text{{grid-column:1;justify-self:end;text-align:right}}
.tl-illo{{display:block;width:100%;height:auto}}
.tl-text h3{{font-size:clamp(1.5rem,2.4vw,2rem);font-weight:500}}
.tl-when{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-style:italic;color:var(--sage-ink);margin:6px 0 12px;font-size:1.05rem}}
.tl-text p:last-child{{color:var(--ink-2)}}

/* numbers */
.dark{{background:var(--deep);color:var(--shell);position:relative}}
.dark h2,.dark h3{{color:var(--bg)}}
.dark .lead,.dark .note{{color:#C9D1BC}}
.dark a{{color:var(--leaf)}}
.eco::after{{content:"";position:absolute;inset:0;background-image:url("{pattern_uri('#A3B46C')}");background-size:150px;opacity:.07;pointer-events:none}}
.eco .wrap{{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(40px,6vw,100px);align-items:start}}
.nums{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0}}
.nums li{{padding:28px 24px 30px 0;border-top:1px solid rgba(163,180,108,.35);display:grid;gap:10px;align-content:start}}
.nums li:nth-child(even){{padding-left:24px;border-left:1px solid rgba(163,180,108,.35)}}
.n-fig{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-weight:300;font-size:clamp(2.8rem,5vw,4.4rem);line-height:1;color:var(--leaf);letter-spacing:-.03em;font-variant-numeric:lining-nums}}
.n-fig sup{{font-size:.4em;vertical-align:super;margin-left:2px;font-weight:400}}
.n-lab{{color:#DCE2CE;max-width:30ch}}
.eco .note{{margin-top:24px;font-style:italic}}

/* horeca */
.hc-top{{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(32px,5vw,72px);align-items:center}}
.hc-top .sec-head{{margin-bottom:0}}
.hc-bot{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:clamp(32px,5vw,72px);align-items:start;margin-top:clamp(48px,6vw,88px)}}
.hc-bot .feat{{grid-template-columns:repeat(2,minmax(0,1fr));gap:32px 36px}}
.feat{{list-style:none;margin:0;padding:0;display:grid;gap:26px}}
.feat li{{display:flex;gap:18px;align-items:flex-start}}
.feat li .ico{{margin-top:2px}}
.feat h3{{font-family:var(--f-body);font-weight:800;font-size:1.08rem;letter-spacing:0}}
.feat p{{color:var(--ink-2);margin-top:4px;font-size:.98rem}}
.horeca-art{{position:relative;isolation:isolate}}
.horeca-art::before{{content:"";position:absolute;inset:4% 0 0 0;background:var(--mist);border-radius:52% 48% 40% 60% / 50% 60% 40% 50%;z-index:-1}}
.horeca-art svg{{display:block;width:100%;height:auto}}
.week{{padding:22px 24px;border-radius:28px;background:var(--bg);border:1px solid var(--line);box-shadow:0 18px 40px -34px rgba(28,46,34,.6)}}
.week h3{{font-family:var(--f-body);font-weight:800;font-size:.95rem;letter-spacing:0}}
.week ul{{list-style:none;padding:0;margin:14px 0 10px;display:grid;grid-template-columns:repeat(7,1fr);gap:6px;text-align:center}}
.week li{{display:grid;justify-items:center;gap:8px;font-weight:800;font-size:.85rem;color:var(--ink-2)}}
.week abbr{{text-decoration:none}}
.week li i{{display:block;width:16px;height:22px;border-radius:50%;border:1.5px dashed var(--line-2)}}
.week li .node{{width:16px;height:auto;background:none;padding:0}}
.week li.on{{color:var(--forest)}}
.week p{{font-size:.88rem;color:var(--ink-2)}}

/* distribution */
.dist-grid{{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:clamp(32px,5vw,80px);align-items:start}}
.map svg{{display:block;width:100%;height:auto}}
.map figcaption{{font-size:.85rem;color:var(--ink-2);margin-top:8px}}
.zones{{list-style:none;margin:0 0 36px;padding:0;display:grid;gap:14px}}
.zones li{{display:flex;gap:14px;align-items:flex-start}}
.zones b{{display:block;font-weight:800}}
.zones span{{color:var(--ink-2);font-size:.95rem}}
.sw{{flex:none;width:22px;height:22px;border-radius:50%;margin-top:2px;border:1.5px solid var(--forest)}}
.z-24 .sw{{background:#C4CF9C}} .z-48 .sw{{background:var(--mist-2)}} .z-isl .sw{{background:var(--shell);border-style:dashed}}
.dfacts{{list-style:none;margin:0;padding:28px 0 0;border-top:1px solid var(--line);display:grid;gap:24px}}
.dfacts li{{display:flex;gap:16px}}
.dfacts h3{{font-family:var(--f-body);font-weight:800;font-size:1.05rem;letter-spacing:0}}
.dfacts p{{color:var(--ink-2);font-size:.97rem;margin-top:2px}}
.van{{margin-top:clamp(56px,7vw,100px);position:relative;isolation:isolate}}
.van::before{{content:"";position:absolute;inset:14% 0 0 0;background:var(--shell);border-radius:200px 200px 60px 60px / 120px 120px 40px 40px;z-index:-1}}
.van svg{{display:block;width:100%;height:auto}}

/* quality */
.qual-top{{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:clamp(32px,5vw,80px);align-items:center}}
.code{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:auto auto auto auto;justify-content:start;gap:0}}
.code li{{display:grid;grid-template-rows:auto auto;align-content:start;gap:14px;padding-right:clamp(12px,2vw,28px)}}
.c-val{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-weight:400;font-size:clamp(2.6rem,6vw,5rem);line-height:1;color:var(--forest);letter-spacing:.01em;padding-bottom:12px;border-bottom:2px solid var(--forest);font-variant-numeric:lining-nums tabular-nums}}
.c-lab{{font-size:.9rem;color:var(--ink-2);line-height:1.4;max-width:15ch}}
.c-lab b{{display:block;color:var(--ink);font-weight:800}}
.code-cap{{margin-top:28px}}
.eggs-art svg{{display:block;width:100%;height:auto}}
.eggs-art{{position:relative;isolation:isolate}}
.eggs-art::before{{content:"";position:absolute;inset:6% 4%;background:var(--shell);border-radius:var(--r-blob);z-index:-1}}
.lots{{list-style:none;margin:clamp(56px,7vw,96px) 0 0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(24px,4vw,56px)}}
.lots li{{display:grid;gap:12px;align-content:start}}
.lots h3{{font-size:1.3rem}}
.lots p{{color:var(--ink-2)}}
.certs-h{{margin-top:clamp(56px,7vw,96px);font-family:var(--f-body);font-weight:800;font-size:1rem;letter-spacing:0}}
.certs{{list-style:none;margin:16px 0 0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}
.certs li{{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;align-items:center;padding:18px 20px;border:1.5px dashed var(--line-2);border-radius:26px 40px 26px 40px}}
.certs li .ico{{grid-row:span 2;color:var(--sage)}}
.certs b{{font-size:.95rem;line-height:1.25}}
.certs span{{font-size:.8rem;color:var(--ink-2)}}

/* how */
.how ol{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:clamp(20px,3vw,40px);position:relative}}
.how ol::before{{content:"";position:absolute;top:27px;left:28px;right:12%;height:2px;background:repeating-linear-gradient(to right,var(--sage) 0 10px,transparent 10px 18px)}}
.how li{{position:relative;display:grid;gap:12px;align-content:start}}
.how-n{{width:56px;height:56px;border-radius:50% 50% 50% 50% / 58% 58% 42% 42%;background:var(--bg);border:2px solid var(--forest);display:grid;place-items:center;font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-size:1.5rem;color:var(--forest);margin-bottom:8px;position:relative}}
.how h3{{font-size:1.28rem}}
.how li p{{color:var(--ink-2);font-size:.98rem}}

/* form */
.quote .wrap{{display:grid;grid-template-columns:minmax(0,.75fr) minmax(0,1.25fr);gap:clamp(40px,6vw,96px);align-items:start}}
.quote-aside{{position:sticky;top:110px;display:grid;gap:24px}}
.direct{{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:14px}}
.direct li{{display:flex;gap:12px;align-items:center}}
.direct a{{font-weight:700;text-decoration:none}}
.direct a:hover{{text-decoration:underline}}
.form{{background:var(--bg);border-radius:36px;padding:clamp(24px,4vw,52px);box-shadow:0 30px 60px -48px rgba(28,46,34,.55);border:1px solid var(--line)}}
.fgrid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px 24px}}
.fgrid .full{{grid-column:1/-1}}
fieldset{{border:0;margin:0;padding:0;min-width:0}}
legend,.flabel{{display:block;font-weight:800;font-size:.94rem;margin-bottom:8px;padding:0;color:var(--ink)}}
.req{{color:var(--forest)}}
.opt{{font-weight:400;color:var(--ink-2)}}
input[type=text],input[type=email],input[type=tel],select,textarea{{width:100%;font:inherit;font-size:1rem;color:var(--ink);background:#FFFDF8;border:1.5px solid var(--line-2);border-radius:14px;padding:13px 15px;transition:border-color .25s,box-shadow .25s;caret-color:var(--forest)}}
textarea{{min-height:120px;resize:vertical}}
select{{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3E%3Cpath d='M5 8l5 5 5-5' fill='none' stroke='%232F5D3A' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;background-size:18px;padding-right:44px}}
input::placeholder,textarea::placeholder{{color:#6A776C}}
input:hover,select:hover,textarea:hover{{border-color:var(--sage)}}
input:focus-visible,select:focus-visible,textarea:focus-visible{{outline:none;border-color:var(--forest);box-shadow:0 0 0 4px rgba(163,180,108,.4)}}
[aria-invalid="true"]{{border-color:var(--err)!important}}
.err{{color:var(--err);font-size:.86rem;font-weight:700;margin-top:6px;display:none}}
.err.show{{display:block}}
.pills{{display:flex;flex-wrap:wrap;gap:10px}}
.pill{{position:relative}}
.pill input{{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}}
.pill span{{display:block;padding:11px 18px;border-radius:999px;border:1.5px solid var(--line-2);font-weight:700;font-size:.95rem;transition:background .25s,color .25s,border-color .25s;background:#FFFDF8}}
.pill input:hover+span{{border-color:var(--sage)}}
.pill input:checked+span{{background:var(--forest);color:var(--bg);border-color:var(--forest)}}
.pill input:focus-visible+span{{outline:2.5px solid var(--forest);outline-offset:3px}}
.chks{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 20px}}
.chk{{display:flex;gap:10px;align-items:flex-start;cursor:pointer;line-height:1.35;font-size:.97rem}}
.chk input{{appearance:none;flex:none;width:22px;height:22px;margin:0;border:1.5px solid var(--line-2);border-radius:7px;background:#FFFDF8;display:grid;place-items:center;cursor:pointer;transition:background .2s,border-color .2s}}
.chk input::after{{content:"";width:10px;height:6px;border-left:2px solid var(--bg);border-bottom:2px solid var(--bg);transform:rotate(-45deg) translate(1px,-1px);opacity:0}}
.chk input:checked{{background:var(--forest);border-color:var(--forest)}}
.chk input:checked::after{{opacity:1}}
.chk input:focus-visible{{outline:2.5px solid var(--forest);outline-offset:2px}}
.rgpd{{font-size:.92rem;color:var(--ink-2)}}
.form-foot{{display:flex;flex-wrap:wrap;gap:16px 24px;align-items:center;justify-content:space-between;margin-top:8px}}
.form-foot .note{{font-size:.84rem}}
.success{{display:none;text-align:left;padding:clamp(8px,2vw,24px) 0}}
.success.show{{display:grid;gap:16px}}
.success svg.node{{width:44px;height:auto}}
.success h3{{font-size:clamp(1.6rem,3vw,2.2rem);font-weight:400}}

/* about */
.about-head{{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(24px,5vw,80px);align-items:start}}
.mission{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-weight:300;font-size:clamp(1.4rem,2.5vw,2.15rem);line-height:1.3;letter-spacing:-.01em;max-width:34ch;color:var(--deep);text-wrap:pretty;margin:0}}
.mission em{{color:var(--forest)}}
.about-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(40px,6vw,96px);margin-top:clamp(56px,7vw,100px);align-items:start}}
.vision{{display:grid;gap:14px;max-width:46ch}}
.vision h3{{font-size:1.5rem}}
.vision p{{color:var(--ink-2)}}
.values{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px 36px}}
.values li{{display:grid;gap:10px;align-content:start}}
.values .ico{{color:var(--sage);width:30px;height:30px}}
.values h3{{font-size:1.25rem}}
.values p{{color:var(--ink-2);font-size:.98rem}}
.faq{{margin-top:clamp(80px,10vw,150px);display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:clamp(32px,5vw,80px)}}
details{{border-bottom:1px solid var(--line)}}
details:first-child{{border-top:1px solid var(--line)}}
summary{{list-style:none;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:22px 4px;cursor:pointer;font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-size:clamp(1.12rem,1.7vw,1.35rem);font-weight:500;color:var(--deep);border-radius:8px}}
summary::-webkit-details-marker{{display:none}}
summary:hover{{color:var(--forest)}}
.chev{{width:22px;height:22px;transform:rotate(90deg);transition:transform .4s var(--ease)}}
details[open] .chev{{transform:rotate(-90deg)}}
.ans{{padding:0 4px 24px;color:var(--ink-2);max-width:68ch}}

/* footer */
.site-f{{background:var(--deep);color:#D4DBC7;position:relative;overflow:hidden;padding:clamp(110px,12vw,170px) 0 36px}}
.site-f::after{{content:"";position:absolute;inset:0;background-image:url("{pattern_uri('#A3B46C')}");background-size:150px;opacity:.06;pointer-events:none}}
.site-f .wrap{{position:relative;z-index:1}}
.f-wave{{top:0;color:var(--bg);z-index:1}}
.f-top{{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr) minmax(0,.9fr);gap:clamp(32px,5vw,72px)}}
.f-top .logo{{height:62px;width:auto;display:block}}
.f-claim{{font-family:var(--f-disp);font-variation-settings:var(--disp-var);font-size:clamp(1.6rem,2.6vw,2.2rem);font-weight:300;color:var(--bg);margin-top:28px;line-height:1.15;max-width:16ch}}
.f-h{{font-family:var(--f-body);font-variation-settings:normal;font-weight:800;font-size:.85rem;letter-spacing:.08em;color:var(--leaf);margin:0 0 16px}}
.f-list{{list-style:none;margin:0;padding:0;display:grid;gap:12px}}
.f-list li{{display:flex;gap:12px;align-items:flex-start}}
.f-list .ico{{color:var(--leaf);width:22px;height:22px;margin-top:2px}}
.site-f a{{color:var(--bg);text-decoration-color:rgba(243,234,211,.4)}}
.site-f a:hover{{color:var(--leaf)}}
.f-bot{{margin-top:clamp(56px,7vw,96px);padding-top:24px;border-top:1px solid rgba(163,180,108,.25);display:flex;flex-wrap:wrap;gap:16px 32px;align-items:center;justify-content:space-between;font-size:.88rem}}
.f-legal{{display:flex;flex-wrap:wrap;gap:8px 22px;list-style:none;margin:0;padding:0}}
.site-f .lang{{border-color:rgba(163,180,108,.45)}}
.site-f .lang span{{background:var(--leaf);color:var(--deep)}}
.site-f .lang a{{color:var(--bg)}}
.site-f .lang a:hover{{background:rgba(163,180,108,.18)}}

/* responsive */
@media (max-width:1000px){{
  .hero .wrap{{grid-template-columns:1fr}}
  .hero-art{{justify-self:center;width:min(100%,480px);margin-top:8px}}
  .prod,.hc-top,.hc-bot,.dist-grid,.qual-top,.quote .wrap,.about-grid,.about-head,.faq,.eco .wrap,.soon{{grid-template-columns:1fr}}
  .prod--rev .prod-art{{order:0}}
  .quote-aside{{position:static}}
  .lots{{grid-template-columns:1fr}}
  .certs{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .how ol{{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:48px}}
  .how ol::before{{display:none}}
  .f-top{{grid-template-columns:1fr 1fr}}
  .f-top>:first-child{{grid-column:1/-1}}
}}
@media (max-width:760px){{
  body{{font-size:1rem}}
  .tl::before{{left:17px}}
  .tl-step{{grid-template-columns:34px minmax(0,1fr);gap:8px 18px;align-items:start}}
  .tl-step .node{{grid-column:1;grid-row:1;width:26px;padding:6px 4px;margin-top:4px}}
  .tl-step .tl-art,.tl-step:nth-child(even) .tl-art{{grid-column:2;grid-row:2;justify-self:start;width:min(100%,300px)}}
  .tl-step .tl-text,.tl-step:nth-child(even) .tl-text{{grid-column:2;grid-row:1;text-align:left;justify-self:start}}
  .tl-step+.tl-step{{margin-top:40px}}
  #granja .sec-head{{text-align:left;justify-items:start}}
  .nums{{grid-template-columns:1fr}}
  .nums li:nth-child(even){{padding-left:0;border-left:0}}
  .fgrid,.chks,.hc-bot .feat{{grid-template-columns:1fr}}
  .soon ul{{grid-template-columns:1fr}}
  .code li{{padding-right:10px}}
  .c-lab{{font-size:.8rem}}
  .specs div{{grid-template-columns:1fr;gap:2px}}
  .values{{grid-template-columns:1fr}}
  .f-top{{grid-template-columns:1fr}}
  .how ol{{grid-template-columns:1fr;row-gap:32px}}
  .certs{{grid-template-columns:1fr}}
  .brand .logo{{height:40px}}
  .hero-cta .btn{{flex:1 1 auto;justify-content:center}}
  .tag{{left:auto;right:0;top:0;bottom:auto;font-size:.78rem;max-width:180px;padding:10px 14px 10px 24px}}
  .ptable th,.ptable td{{padding-right:8px;font-size:.9rem}}
}}
@media (max-width:400px){{
  .c-val{{font-size:2.3rem}}
  .sizes{{gap:12px}}
}}
@media (prefers-reduced-motion:reduce){{
  html{{scroll-behavior:auto}}
  *,*::before,*::after{{transition-duration:.01ms!important;animation:none!important}}
}}
</style>
</head>
<body>
<a class="skip" href="#main">{t["skip"]}</a>
<header class="site-h" id="top">
  <div class="wrap">
    <a class="brand" href="#top" aria-label="{t["home_label"]}">{logo}</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="{t["menu"]}"><span></span></button>
    <nav class="nav" id="nav" aria-label="{t["nav_label"]}">
      <ul>{nav}</ul>
      {lang_sw}
      <a class="btn btn--solid btn--sm" href="#presupuesto">{t["cta_quote"]}</a>
    </nav>
  </div>
</header>

<main id="main">
<section class="hero" aria-labelledby="hero-t">
  <div class="wrap">
    <div class="hero-copy">
      <h1 id="hero-t">{t["hero_h1"]}</h1>
      <p class="lead">{t["hero_text"]}</p>
      <div class="hero-cta">
        <a class="btn btn--solid" href="#granja">{t["hero_cta"]}{icon("arrow")}</a>
        <a class="btn btn--line" href="#presupuesto">{t["cta_quote"]}</a>
      </div>
      <ul class="hero-for">{"".join(f'<li>{icon("leaf")}{x}</li>' for x in t["hero_for"])}</ul>
    </div>
    <div class="hero-art">
      {svg("illo-hero.svg", cls="hero-illo", label=t["hero_alt"])}
      <p class="tag"><b>{t["tag"][0]}</b><span>{t["tag"][1]}</span></p>
    </div>
  </div>
</section>

<section class="sec" id="productos" aria-labelledby="prod-t">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="prod-t">{p["h2"]}</h2>
      <p class="lead">{p["lead"]}</p>
    </div>

    <article class="prod">
      <div class="prod-art">{svg("scene-pack_retail.svg", "560 150 650 440", label=p["fresh_alt"])}</div>
      <div class="prod-body">
        <h3>{p["fresh_h"]}</h3>
        <p>{p["fresh_p"]}</p>
        <ul class="sizes" aria-label="{p["sizes_label"]}">{sizes}</ul>
        <dl class="specs">{fresh_specs}</dl>
      </div>
    </article>

    <article class="prod prod--rev">
      <div class="prod-art">{svg("scene-pack_powder.svg", "280 40 1160 640", label=p["powder_alt"])}</div>
      <div class="prod-body">
        <h3>{p["powder_h"]}</h3>
        <p>{p["powder_p"]}</p>
        <table class="ptable">
          <caption class="sr-only" style="position:absolute;left:-9999px">{p["powder_h"]}</caption>
          <thead><tr><th scope="col">{p["powder_cols"][0]}</th><th scope="col">{p["powder_cols"][1]}</th><th scope="col">{p["powder_cols"][2]}</th></tr></thead>
          <tbody>{powder_rows}</tbody>
        </table>
        <p class="note" style="margin-top:14px">{p["powder_note"]}</p>
      </div>
    </article>

    <aside class="soon" aria-labelledby="soon-t">
      <div><h3 id="soon-t">{p["soon_h"]}</h3><p>{p["soon_p"]}</p></div>
      <ul>{soon}</ul>
    </aside>
  </div>
</section>

<section class="sec tint" id="granja" aria-labelledby="tl-t">
  {WAVE_TOP}
  <div class="wrap">
    <div class="sec-head">
      <h2 id="tl-t">{t["tl"]["h2"]}</h2>
      <p class="lead">{t["tl"]["lead"]}</p>
    </div>
    <ol class="tl">{steps}</ol>
  </div>
</section>

<section class="sec dark eco" id="sostenibilidad" aria-labelledby="eco-t">
  {WAVE_TOP}
  <div class="wrap">
    <div>
      <h2 id="eco-t">{t["eco"]["h2"]}</h2>
      <p class="lead" style="margin-top:22px">{t["eco"]["lead"]}</p>
      <p class="note">{t["eco"]["note"]}</p>
    </div>
    <ul class="nums">{nums}</ul>
  </div>
  {WAVE_BOT}
</section>

<section class="sec horeca" id="horeca" aria-labelledby="hc-t" style="padding-top:calc(var(--sec) + 40px)">
  <div class="wrap">
    <div class="hc-top">
      <div class="sec-head">
        <h2 id="hc-t">{h["h2"]}</h2>
        <p class="lead">{h["lead"]}</p>
      </div>
      <div class="horeca-art">{svg("scene-pack_horeca.svg", "215 80 1290 560", label=h["alt"])}</div>
    </div>
    <div class="hc-bot">
      <ul class="feat">{hfeat}</ul>
      <div class="week">
        <h3>{h["week_h"]}</h3>
        <ul aria-label="{h["week_h"]}">{week}</ul>
        <p>{h["week_p"]}</p>
      </div>
    </div>
  </div>
</section>

<section class="sec tint" id="distribucion" aria-labelledby="ds-t">
  {WAVE_TOP}
  <div class="wrap">
    <div class="sec-head">
      <h2 id="ds-t">{d["h2"]}</h2>
      <p class="lead">{d["lead"]}</p>
    </div>
    <div class="dist-grid">
      <figure class="map" style="margin:0">{svg("map-spain.svg", label=d["map_alt"])}<figcaption>{d["map_cap"]}</figcaption></figure>
      <div>
        <ul class="zones">{zones}</ul>
        <ul class="dfacts">{dfacts}</ul>
      </div>
    </div>
    <div class="van">{svg("scene-logistics.svg", "60 90 1560 570", label=d["van_alt"])}</div>
  </div>
  {WAVE_BOT}
</section>

<section class="sec" id="calidad" aria-labelledby="q-t" style="padding-top:calc(var(--sec) + 40px)">
  <div class="wrap">
    <div class="sec-head">
      <h2 id="q-t">{q["h2"]}</h2>
      <p class="lead">{q["lead"]}</p>
    </div>
    <div class="qual-top">
      <figure style="margin:0">
        <ul class="code" aria-label="{q["code_label"]}">{code}</ul>
        <figcaption class="note code-cap">{q["code_cap"]}</figcaption>
      </figure>
      <div class="eggs-art">{svg("scene-pack_retail.svg", "1240 320 410 280", label=q["eggs_alt"])}</div>
    </div>
    <ul class="lots">{lots}</ul>
    <h3 class="certs-h">{q["certs_h"]}</h3>
    <ul class="certs">{certs}</ul>
  </div>
</section>

<section class="sec tint how" id="como" aria-labelledby="how-t">
  {WAVE_TOP}
  <div class="wrap">
    <div class="sec-head">
      <h2 id="how-t">{t["how"]["h2"]}</h2>
      <p class="lead">{t["how"]["lead"]}</p>
    </div>
    <ol>{how}</ol>
  </div>
</section>

<section class="sec tint quote" id="presupuesto" aria-labelledby="f-t" style="padding-top:0">
  <div class="wrap">
    <div class="quote-aside">
      <h2 id="f-t">{f["h2"]}</h2>
      <p class="lead">{f["lead"]}</p>
      <ul class="direct">
        <li>{icon("phone")}<a href="tel:{c["phone"].replace(" ", "")}">{c["phone"]}</a></li>
        <li>{icon("mail")}<a href="mailto:{c["email"]}">{c["email"]}</a></li>
      </ul>
      <p class="note">{f["aside_note"]}</p>
    </div>
    <div class="form">
      <form id="quote-form" novalidate>
        <div class="fgrid">
          <fieldset class="full" id="f-tipo" aria-describedby="tipo-err">
            <legend>{f["l_type"]} <span class="req" aria-hidden="true">*</span></legend>
            <div class="pills">{types}</div>
            <p class="err" id="tipo-err"></p>
          </fieldset>
          <div><label class="flabel" for="empresa">{f["l_company"]} <span class="req" aria-hidden="true">*</span></label><input type="text" id="empresa" name="empresa" required autocomplete="organization" aria-describedby="empresa-err"><p class="err" id="empresa-err"></p></div>
          <div><label class="flabel" for="cif">CIF / NIF <span class="req" aria-hidden="true">*</span></label><input type="text" id="cif" name="cif" required placeholder="B12345678" autocapitalize="characters" pattern="^([A-HJNP-SUVWa-hjnp-suvw][0-9]{{7}}[0-9A-Ja-j]|[0-9]{{8}}[A-Za-z]|[XYZxyz][0-9]{{7}}[A-Za-z])$" aria-describedby="cif-err"><p class="err" id="cif-err"></p></div>
          <div><label class="flabel" for="persona">{f["l_person"]} <span class="req" aria-hidden="true">*</span></label><input type="text" id="persona" name="persona" required autocomplete="name" aria-describedby="persona-err"><p class="err" id="persona-err"></p></div>
          <div><label class="flabel" for="email">E-mail <span class="req" aria-hidden="true">*</span></label><input type="email" id="email" name="email" required autocomplete="email" placeholder="{f["ph_email"]}" aria-describedby="email-err"><p class="err" id="email-err"></p></div>
          <div><label class="flabel" for="tel">{f["l_phone"]} <span class="req" aria-hidden="true">*</span></label><input type="tel" id="tel" name="telefono" required autocomplete="tel" placeholder="+34 600 000 000" pattern="^\\+?[0-9 ()\\-]{{9,17}}$" aria-describedby="tel-err"><p class="err" id="tel-err"></p></div>
          <div><label class="flabel" for="prov">{f["l_prov"]} <span class="req" aria-hidden="true">*</span></label><select id="prov" name="provincia" required aria-describedby="prov-err"><option value="">{f["ph_prov"]}</option>{provs}</select><p class="err" id="prov-err"></p></div>
          <fieldset class="full" id="f-prod" aria-describedby="prod-err">
            <legend>{f["l_products"]} <span class="req" aria-hidden="true">*</span></legend>
            <div class="chks">{prods}</div>
            <p class="err" id="prod-err"></p>
          </fieldset>
          <div class="full"><label class="flabel" for="vol">{f["l_volume"]} <span class="req" aria-hidden="true">*</span></label><select id="vol" name="volumen" required aria-describedby="vol-err"><option value="">{f["ph_volume"]}</option>{vols}</select><p class="err" id="vol-err"></p></div>
          <div class="full"><label class="flabel" for="com">{f["l_comment"]} <span class="opt">{f["optional"]}</span></label><textarea id="com" name="comentario" placeholder="{f["ph_comment"]}"></textarea></div>
          <div class="full"><label class="chk rgpd"><input type="checkbox" id="rgpd" name="rgpd" required aria-describedby="rgpd-err"><span>{f["l_rgpd"]}</span></label><p class="err" id="rgpd-err"></p></div>
          <div class="full form-foot">
            <p class="note">{f["req_note"]}</p>
            <button class="btn btn--solid" type="submit">{f["submit"]}{icon("arrow")}</button>
          </div>
        </div>
      </form>
      <div class="success" id="quote-ok" role="status" tabindex="-1">
        {LEAFMARK}
        <h3>{f["ok_h"]}</h3>
        <p class="muted">{f["ok_p"]}</p>
        <p><button class="btn btn--line btn--sm" type="button" id="quote-again">{f["ok_again"]}</button></p>
      </div>
    </div>
  </div>
  <svg class="wave wave--bot" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true" focusable="false" style="color:var(--mist)"><path d="M0 0 L0 38 C200 70 420 84 640 60 C840 38 1000 20 1200 40 C1320 52 1390 62 1440 58 L1440 0 Z" fill="currentColor"/></svg>
</section>

<section class="sec" id="nosotros" aria-labelledby="ab-t" style="padding-top:calc(var(--sec) + 40px)">
  <div class="wrap">
    <div class="about-head">
      <h2 id="ab-t">{ab["h2"]}</h2>
      <p class="mission">{ab["mission"]}</p>
    </div>
    <div class="about-grid">
      <div class="vision">
        <h3>{ab["vision_h"]}</h3>
        <p>{ab["vision"]}</p>
        <p>{ab["positioning"]}</p>
      </div>
      <ul class="values" aria-label="{ab["values_label"]}">{values}</ul>
    </div>
    <div class="faq" id="faq">
      <div><h2>{t["faq"]["h2"]}</h2><p class="muted" style="margin-top:18px;max-width:34ch">{t["faq"]["lead"]}</p></div>
      <div>{faq}</div>
    </div>
  </div>
</section>
</main>

<footer class="site-f" id="contacto">
  <svg class="wave f-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M0 0 L0 38 C200 70 420 84 640 60 C840 38 1000 20 1200 40 C1320 52 1390 62 1440 58 L1440 0 Z" fill="currentColor"/></svg>
  <div class="wrap">
    <div class="f-top">
      <div>
        {logo_inv}
        <p class="f-claim">{t["foot_claim"]}</p>
      </div>
      <div>
        <h2 class="f-h">{t["foot_contact"]}</h2>
        <ul class="f-list">
          <li>{icon("phone")}<a href="tel:{c["phone"].replace(" ", "")}">{c["phone"]}</a></li>
          <li>{icon("mail")}<a href="mailto:{c["email"]}">{c["email"]}</a></li>
          <li>{icon("pin")}<span>{c["address"]}</span></li>
          <li>{icon("leaf")}<span>{c["web"]}</span></li>
        </ul>
      </div>
      <div>
        <h2 class="f-h">{t["foot_nav"]}</h2>
        <ul class="f-list">{"".join(f'<li><a href="#{hh}">{nn}</a></li>' for hh, nn in t["nav"][:5])}<li><a href="#faq">FAQ</a></li></ul>
      </div>
    </div>
    <div class="f-bot">
      <p>© 2026 Primeegg Distribution SL · {t["foot_rights"]}</p>
      <ul class="f-legal">{"".join(f'<li><a href="#">{x}</a></li>' for x in t["legal"])}</ul>
      {lang_sw}
    </div>
  </div>
</footer>

<script>
(function(){{
  document.documentElement.classList.add('js');
  var hl=document.querySelectorAll('.hero-illo .ln');for(var i=0;i<hl.length;i++)hl[i].style.setProperty('--i',i);
  var h=document.querySelector('.site-h'),b=document.querySelector('.burger'),n=document.getElementById('nav');
  function onS(){{h.classList.toggle('scrolled',window.scrollY>8)}}onS();window.addEventListener('scroll',onS,{{passive:true}});
  function setNav(o){{b.setAttribute('aria-expanded',o);n.classList.toggle('open',o);b.setAttribute('aria-label',o?{json.dumps(t["menu_close"], ensure_ascii=False)}:{json.dumps(t["menu"], ensure_ascii=False)})}}
  b.addEventListener('click',function(){{setNav(b.getAttribute('aria-expanded')!=='true')}});
  n.addEventListener('click',function(e){{if(e.target.closest('a'))setNav(false)}});
  document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&b.getAttribute('aria-expanded')==='true'){{setNav(false);b.focus()}}}});
  window.matchMedia('(min-width:1181px)').addEventListener('change',function(m){{if(m.matches)setNav(false)}});

  var M={jsmsg};
  var f=document.getElementById('quote-form'),ok=document.getElementById('quote-ok');
  function show(id,msg){{var e=document.getElementById(id+'-err');if(!e)return;e.textContent=msg||'';e.classList.toggle('show',!!msg)}}
  function mark(el,bad){{if(el)el.setAttribute('aria-invalid',bad?'true':'false')}}
  function checkField(el){{
    var id=el.id,v=el.value.trim(),msg='';
    if(el.type==='checkbox'){{if(!el.checked)msg=M.rgpd}}
    else if(!v)msg=M.required;
    else if(id==='email'&&el.validity.typeMismatch)msg=M.email;
    else if(id==='cif'&&el.validity.patternMismatch)msg=M.cif;
    else if(id==='tel'&&el.validity.patternMismatch)msg=M.tel;
    mark(el,!!msg);show(id,msg);return !msg;
  }}
  var fields=['empresa','cif','persona','email','tel','prov','vol','rgpd'].map(function(i){{return document.getElementById(i)}});
  fields.forEach(function(el){{
    el.addEventListener('blur',function(){{if(el.type!=='checkbox'&&el.value.trim())checkField(el)}});
    el.addEventListener('input',function(){{if(el.getAttribute('aria-invalid')==='true')checkField(el)}});
    el.addEventListener('change',function(){{if(el.getAttribute('aria-invalid')==='true')checkField(el)}});
  }});
  function checkGroup(name,id,msg){{
    var c=f.querySelectorAll('input[name="'+name+'"]'),any=false;for(var i=0;i<c.length;i++)if(c[i].checked)any=true;
    show(id,any?'':msg);document.getElementById('f-'+id).setAttribute('aria-invalid',any?'false':'true');return any;
  }}
  f.addEventListener('change',function(e){{
    if(e.target.name==='tipo')checkGroup('tipo','tipo',M.type);
    if(e.target.name==='productos'&&document.getElementById('prod-err').classList.contains('show'))checkGroup('productos','prod',M.products);
  }});
  f.addEventListener('submit',function(e){{
    e.preventDefault();
    var first=null,okAll=true;
    if(!checkGroup('tipo','tipo',M.type)){{okAll=false;first=first||f.querySelector('input[name="tipo"]')}}
    fields.slice(0,6).forEach(function(el){{if(!checkField(el)){{okAll=false;first=first||el}}}});
    if(!checkGroup('productos','prod',M.products)){{okAll=false;first=first||f.querySelector('input[name="productos"]')}}
    [fields[6],fields[7]].forEach(function(el){{if(!checkField(el)){{okAll=false;first=first||el}}}});
    if(!okAll){{first.focus();return}}
    f.style.display='none';ok.classList.add('show');ok.focus();
  }});
  document.getElementById('quote-again').addEventListener('click',function(){{
    f.reset();f.querySelectorAll('[aria-invalid]').forEach(function(x){{x.setAttribute('aria-invalid','false')}});
    ok.classList.remove('show');f.style.display='';f.querySelector('input').focus();
  }});
}})();
</script>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    for lang, fn in (("es", "index.html"), ("uk", "uk.html")):
        out = build(lang)
        (SITE / fn).write_text(out)
        print(fn, len(out) // 1024, "KB")
