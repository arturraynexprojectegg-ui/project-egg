#!/usr/bin/env python3
"""Builds sites/PE-04.05/index.html (ES) and uk.html (UA) with inline SVG."""
import re, json, html, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from strings import ES, UK

HERE = Path(__file__).parent
ROOT = Path("/Users/arturkasian/Project Egg/sites/PE-04.05")
A = ROOT / "assets"
_seq = [0]


def svgfile(name, vb=None, label=None, cls=None, w=None, h=None):
    s = (A / name).read_text().strip()
    m = re.match(r'<svg[^>]*viewBox="([^"]*)"[^>]*>', s)
    vbo = m.group(1)
    body = s[m.end():s.rfind("</svg>")]
    _seq[0] += 1
    p = f"s{_seq[0]}-"
    body = re.sub(r'id="([^"]+)"', lambda x: f'id="{p}{x.group(1)}"', body)
    body = re.sub(r'url\(#([^)]+)\)', lambda x: f'url(#{p}{x.group(1)})', body)
    body = re.sub(r'href="#([^"]+)"', lambda x: f'href="#{p}{x.group(1)}"', body)
    vb = vb or vbo
    _, _, vw, vh = vb.split()
    attrs = f'viewBox="{vb}" width="{w or vw}" height="{h or vh}"'
    if label:
        attrs += f' role="img" aria-label="{html.escape(label)}"'
    else:
        attrs += ' aria-hidden="true" focusable="false"'
    if cls:
        attrs += f' class="{cls}"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{body}</svg>'


CROWN = '<path d="M-11 14.8 L-13 5.8 L-5.7 9.4 L0 2.8 L5.7 9.4 L13 5.8 L11 14.8 Z"/><rect x="-11" y="16.3" width="22" height="2"/><circle cx="-13" cy="4.4" r="1.4"/><circle cx="0" cy="1.4" r="1.4"/><circle cx="13" cy="4.4" r="1.4"/>'


def crown(cls="crown"):
    return f'<svg class="{cls}" viewBox="-15 0 30 20" width="30" height="20" aria-hidden="true" focusable="false"><g fill="currentColor">{CROWN}</g></svg>'


def ornament():
    return '<div class="ornament" aria-hidden="true"><span></span>' + crown() + '<span></span></div>'


def cartouche(x, y, w, h, r):
    return (f"M{x+r} {y} H{x+w-r} A{r} {r} 0 0 0 {x+w} {y+r} V{y+h-r} A{r} {r} 0 0 0 {x+w-r} {y+h} "
            f"H{x+r} A{r} {r} 0 0 0 {x} {y+h-r} V{y+r} A{r} {r} 0 0 0 {x+r} {y} Z")


def hero_art(t):
    egg = "M300 128 C392 128 458 286 458 392 C458 490 390 556 300 556 C210 556 142 490 142 392 C142 286 208 128 300 128 Z"
    return f'''<svg class="hero-art" viewBox="0 0 600 760" width="600" height="760" role="img" aria-label="{html.escape(t['hero_art'])}">
<defs>
<radialGradient id="h-egg" cx="38%" cy="30%" r="78%"><stop offset="0" stop-color="#FFFDF7"/><stop offset=".45" stop-color="#F4EBD8"/><stop offset=".8" stop-color="#DCC9A6"/><stop offset="1" stop-color="#B9A07A"/></radialGradient>
<radialGradient id="h-glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#B8924A" stop-opacity=".28"/><stop offset="1" stop-color="#B8924A" stop-opacity="0"/></radialGradient>
<radialGradient id="h-shadow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#14050A" stop-opacity=".7"/><stop offset="1" stop-color="#14050A" stop-opacity="0"/></radialGradient>
<linearGradient id="h-sheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<path class="draw" d="{cartouche(40, 40, 520, 680, 34)}" fill="none" stroke="#B8924A" stroke-width="1.2"/>
<path class="draw draw-2" d="{cartouche(52, 52, 496, 656, 26)}" fill="none" stroke="#B8924A" stroke-width=".6"/>
<circle cx="300" cy="380" r="250" fill="url(#h-glow)"/>
<g class="egg-rise">
<ellipse cx="300" cy="566" rx="150" ry="18" fill="url(#h-shadow)"/>
<path d="{egg}" fill="url(#h-egg)"/>
<path d="M246 196 C220 236 200 296 196 346 C214 300 240 246 270 206 C266 194 254 188 246 196 Z" fill="url(#h-sheen)" opacity=".75"/>
<g transform="translate(300 455) rotate(-4)" fill="#6B2230" opacity=".78" font-family="'Courier New', monospace" text-anchor="middle">
<text y="0" font-size="27" font-weight="700" letter-spacing="2">1ES28001</text>
<text y="24" font-size="13" letter-spacing="3">C.P. 28/12</text>
</g>
</g>
<g class="label-in" transform="translate(300 640)">
<path d="{cartouche(-150, -38, 300, 76, 12)}" fill="#F3ECDC" stroke="#B8924A" stroke-width="1"/>
<path d="{cartouche(-143, -31, 286, 62, 8)}" fill="none" stroke="#5E1A26" stroke-width=".7"/>
<g transform="translate(0 -32) scale(.7)" fill="#B8924A">{CROWN}</g>
<text y="0" text-anchor="middle" font-family="'Abril Fatface', serif" font-size="21" letter-spacing="2" fill="#5E1A26">PRIMEEGG</text>
<line x1="-74" y1="8" x2="74" y2="8" stroke="#B8924A" stroke-width=".8"/>
<text y="25" text-anchor="middle" font-family="'Cormorant Garamond', serif" font-style="italic" font-weight="500" font-size="15" fill="#5E1A26">Selección de la casa · Categoría A</text>
</g>
<text x="300" y="96" fill="#B8924A" font-family="'Josefin Sans', sans-serif" font-size="10" letter-spacing="6" text-anchor="middle">MAISON · ESPAÑA · 2026</text>
</svg>'''


SPAIN = [(-1.78,43.37),(-2.0,43.32),(-2.93,43.40),(-3.8,43.47),(-4.5,43.40),(-5.66,43.56),(-5.85,43.66),(-6.5,43.56),
(-7.04,43.55),(-7.68,43.78),(-7.87,43.77),(-8.3,43.55),(-8.4,43.38),(-8.95,43.25),(-9.3,42.92),(-9.0,42.6),(-8.85,42.3),
(-8.85,42.1),(-8.87,41.87),(-8.6,42.05),(-8.15,42.05),(-7.9,41.88),(-7.2,41.95),(-6.6,41.95),(-6.2,41.6),(-6.9,41.0),
(-6.8,40.3),(-7.0,39.7),(-7.5,39.65),(-7.0,39.0),(-7.3,38.4),(-7.0,38.0),(-7.5,37.55),(-7.4,37.18),(-6.95,37.2),
(-6.4,36.8),(-6.3,36.5),(-5.6,36.0),(-5.35,36.15),(-4.4,36.7),(-3.5,36.72),(-2.45,36.83),(-2.2,36.72),(-1.65,37.35),
(-0.98,37.58),(-0.7,37.63),(-0.75,37.85),(-0.48,38.35),(0.23,38.73),(-0.0,38.9),(-0.33,39.47),(-0.03,39.98),(0.5,40.5),
(0.85,40.7),(1.25,41.1),(2.17,41.38),(3.2,41.9),(3.32,42.32),(3.17,42.43),(2.5,42.35),(1.7,42.5),(0.7,42.8),(-0.5,42.8),(-1.3,43.05)]
PORTUGAL = [(-8.87,41.87),(-8.67,41.15),(-8.75,40.64),(-8.87,40.15),(-9.38,39.36),(-9.5,38.78),(-9.2,38.69),(-8.9,38.5),
(-8.87,37.95),(-8.99,37.02),(-7.93,37.0),(-7.4,37.18),(-7.5,37.55),(-7.0,38.0),(-7.3,38.4),(-7.0,39.0),(-7.5,39.65),(-7.0,39.7),
(-6.8,40.3),(-6.9,41.0),(-6.2,41.6),(-6.6,41.95),(-7.2,41.95),(-7.9,41.88),(-8.15,42.05),(-8.6,42.05)]


def pj(lon, lat):
    return ((lon + 9.7) * 60, (43.95 - lat) * 78)


def smooth(pts):
    P = [pj(*p) for p in pts]
    n = len(P)
    mids = [((P[i][0] + P[(i+1) % n][0]) / 2, (P[i][1] + P[(i+1) % n][1]) / 2) for i in range(n)]
    d = f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f}"
    for i in range(n):
        d += f" Q{P[i][0]:.1f} {P[i][1]:.1f} {mids[i][0]:.1f} {mids[i][1]:.1f}"
    return d + " Z"


def spain_map(t):
    sp = smooth(SPAIN)
    pt = smooth(PORTUGAL)
    mx, my = pj(-3.70, 40.42)
    isl = ""
    for lon, lat, rx, ry, rot in [(2.95, 39.62, 30, 19, -20), (4.1, 39.96, 14, 6, -12), (1.43, 38.98, 9, 8, 0), (1.45, 38.7, 4, 3, 0)]:
        x, y = pj(lon, lat)
        isl += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" transform="rotate({rot} {x:.1f} {y:.1f})"/>'
    cities = ""
    for key, lon, lat, dx, anchor in t["cities"]:
        x, y = pj(lon, lat)
        cities += (f'<g class="city"><circle cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>'
                   f'<text x="{x+dx:.1f}" y="{y+5:.1f}" text-anchor="{anchor}">{key}</text></g>')
    bx, by = pj(3.0, 39.0)
    return f'''<svg class="map" viewBox="0 0 860 640" width="860" height="640" role="img" aria-label="{html.escape(t['map_label'])}">
<defs>
<clipPath id="m-land"><path d="{sp}"/></clipPath>
<pattern id="m-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#B8924A" stroke-width=".9" opacity=".55"/></pattern>
</defs>
<path d="{pt}" fill="none" stroke="#5E1A26" stroke-opacity=".28" stroke-width=".8" stroke-dasharray="2 4"/>
<path d="{sp}" fill="#EDE3CC"/>
<path d="{sp}" fill="url(#m-hatch)"/>
<g clip-path="url(#m-land)"><circle cx="{mx:.1f}" cy="{my:.1f}" r="246" fill="#5E1A26" fill-opacity=".16"/></g>
<circle cx="{mx:.1f}" cy="{my:.1f}" r="246" fill="none" stroke="#5E1A26" stroke-width="1.2" stroke-dasharray="1 5" stroke-linecap="round" opacity=".7"/>
<path d="{sp}" fill="none" stroke="#5E1A26" stroke-width="1.1"/>
<g fill="#EDE3CC" stroke="#5E1A26" stroke-width="1">{isl}</g>
<g class="cities">{cities}</g>
<g class="hub" transform="translate({mx:.1f} {my:.1f})">
<circle r="15" fill="#5E1A26"/><circle r="11" fill="none" stroke="#B8924A" stroke-width=".8"/>
<g transform="translate(0 -6.5) scale(.42)" fill="#D4B77A">{CROWN}</g>
<text x="0" y="36" text-anchor="middle" class="hub-label">{t['hub']}</text>
</g>
<text x="{mx+40:.1f}" y="{my+150:.1f}" class="zone-label">24 h</text>
<text x="{pj(1.3,42.1)[0]:.1f}" y="{pj(1.3,42.1)[1]:.1f}" class="zone-label z48" text-anchor="middle">48 h</text>
<text x="{bx:.1f}" y="{by+44:.1f}" class="zone-label z72" text-anchor="middle">72 h</text>
</svg>'''


def header(t):
    nav = "".join(f'<li><a href="#{a}">{n}</a></li>' for a, n in t["nav"])
    return f'''<a class="skip" href="#main">{t['skip']}</a>
<header class="site-header" id="top">
<div class="wrap header-in">
<a class="brand" href="#top" aria-label="{t['home']}">{svgfile('logo-horizontal.svg', vb='70 18 520 160', cls='logo-h', w=520, h=160)}</a>
<nav class="nav" id="nav" aria-label="{t['nav_label']}">
<ul class="nav-list">{nav}</ul>
<div class="nav-tools">
<div class="lang" role="group" aria-label="{t['lang_label']}">{t['lang_html']}</div>
<a class="btn btn-solid btn-sm" href="#presupuesto">{t['quote']}</a>
</div>
</nav>
<button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="{t['menu']}"><span></span><span></span></button>
</div>
</header>'''


def hero(t):
    facts = "".join(f"<li>{f}</li>" for f in t["hero_facts"])
    return f'''<section class="hero" aria-labelledby="hero-title">
<div class="hero-text">
<h1 id="hero-title" class="display">{t['hero_title']}</h1>
<p class="lead">{t['hero_text']}</p>
<div class="actions">
<a class="btn btn-solid" href="#presupuesto">{t['cta']}</a>
<a class="link-arrow" href="#productos">{t['hero_more']}<span aria-hidden="true"></span></a>
</div>
<ul class="hero-facts">{facts}</ul>
</div>
<div class="hero-panel">{hero_art(t)}</div>
</section>'''


def manifesto(t):
    return f'''<section class="manifesto" aria-label="{t['manifesto_label']}">
<div class="wrap narrow">
{ornament()}
<p class="quote">{t['manifesto']}</p>
<p class="manifesto-text">{t['positioning']}</p>
</div>
</section>'''


def spec_rows(rows):
    return "".join(f'<div class="row"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows)


def products(t):
    sizes = "".join(
        f'<li><svg viewBox="0 0 40 52" width="{w}" height="{round(w*1.3)}" aria-hidden="true" focusable="false"><path d="M20 2 C31 2 38 20 38 31 C38 43 30 50 20 50 C10 50 2 43 2 31 C2 20 9 2 20 2 Z"/></svg><b>{s}</b><span>{g}</span></li>'
        for (s, g), w in zip(t["sizes"], [30, 36, 42, 48]))
    soon = "".join(f"<li>{x}</li>" for x in t["soon_items"])
    return f'''<section class="section products" id="productos" aria-labelledby="prod-title">
<div class="wrap">
<header class="sec-head">
<h2 id="prod-title">{t['prod_title']}</h2>
<p class="sec-intro">{t['prod_intro']}</p>
</header>
<article class="cuvee" aria-labelledby="p1">
<figure class="cuvee-art">{svgfile('scene-pack_retail.svg', vb='60 200 1150 420', label=t['alt_retail'])}</figure>
<div class="cuvee-text">
<p class="cuvee-n" aria-hidden="true">I</p>
<h3 id="p1">{t['p1_title']}</h3>
<p class="sub">{t['p1_sub']}</p>
<p>{t['p1_text']}</p>
<ul class="sizes" aria-label="{t['sizes_label']}">{sizes}</ul>
<dl class="spec">{spec_rows(t['p1_spec'])}</dl>
</div>
</article>
<article class="cuvee cuvee-rev" aria-labelledby="p2">
<figure class="cuvee-art">{svgfile('scene-pack_powder.svg', vb='260 20 1220 640', label=t['alt_powder'])}</figure>
<div class="cuvee-text">
<p class="cuvee-n" aria-hidden="true">II</p>
<h3 id="p2">{t['p2_title']}</h3>
<p class="sub">{t['p2_sub']}</p>
<p>{t['p2_text']}</p>
<dl class="spec">{spec_rows(t['p2_spec'])}</dl>
</div>
</article>
<article class="soon" aria-labelledby="p3">
<div class="soon-head">
<p class="tag">{t['soon_tag']}</p>
<h3 id="p3">{t['p3_title']}</h3>
<p>{t['p3_text']}</p>
</div>
<ul class="soon-list">{soon}</ul>
</article>
</div>
</section>'''


def horeca(t):
    feats = "".join(f'<div class="feat"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in t["h_feats"])
    days = "".join(
        f'<li class="{"on" if on else "off"}"><abbr title="{full}">{d}</abbr><span>{tm if on else "—"}</span></li>'
        for d, full, on, tm in t["week"])
    return f'''<section class="section horeca" id="horeca" aria-labelledby="h-title">
<div class="wrap horeca-grid">
<div class="horeca-text">
<h2 id="h-title">{t['h_title']}</h2>
<p class="lead">{t['h_lead']}</p>
<dl class="feats">{feats}</dl>
</div>
<div class="horeca-side">
<figure class="horeca-art">{svgfile('scene-pack_horeca.svg', vb='200 50 1320 640', label=t['alt_horeca'])}</figure>
<div class="week">
<p class="week-title">{t['week_title']}</p>
<ol class="week-days">{days}</ol>
<p class="week-note">{t['week_note']}</p>
</div>
</div>
</div>
</section>'''


def distribution(t):
    legend = "".join(f'<li class="lg-{c}"><i aria-hidden="true"></i><span><b>{k}</b> {v}</span></li>' for c, k, v in t["legend"])
    facts = "".join(f'<div class="row"><dt>{k}</dt><dd>{v}</dd></div>' for k, v in t["d_facts"])
    return f'''<section class="section distribution" id="distribucion" aria-labelledby="d-title">
<div class="wrap">
<header class="sec-head sec-head-split">
<h2 id="d-title">{t['d_title']}</h2>
<p class="sec-intro">{t['d_intro']}</p>
</header>
<div class="dist-grid">
<figure class="map-fig">{spain_map(t)}
<figcaption><ul class="legend">{legend}</ul></figcaption>
</figure>
<div class="dist-text">
<dl class="spec spec-lg">{facts}</dl>
<figure class="truck">{svgfile('scene-logistics.svg', vb='40 90 1600 560', label=t['alt_truck'])}</figure>
</div>
</div>
</div>
</section>'''


def nbd(v):
    return re.sub(r"(\d) ", lambda m: m.group(1) + "&nbsp;", v)


def quality(t):
    parts = "".join(f'<li><span class="seg">{s}</span><span class="seg-k">{k}</span><span class="seg-v">{nbd(v)}</span></li>' for s, k, v in t["code"])
    checks = "".join(f"<li>{c}</li>" for c in t["q_checks"])
    plates = "".join(f'<li class="plate">{crown()}<b>{k}</b><span>{t["plate_note"]}</span></li>' for k in t["plates"])
    return f'''<section class="section quality" id="calidad" aria-labelledby="q-title">
<div class="wrap">
<header class="sec-head center">
<h2 id="q-title">{t['q_title']}</h2>
<p class="sec-intro">{t['q_intro']}</p>
</header>
<ol class="code" aria-label="{t['code_label']}">{parts}</ol>
<div class="q-grid">
<figure class="q-art">{svgfile('scene-pack_retail.svg', vb='1230 270 400 340', label=t['alt_eggs'])}</figure>
<div class="q-text">
<h3>{t['q_lot_title']}</h3>
<p>{t['q_lot_text']}</p>
<ul class="checks">{checks}</ul>
</div>
</div>
<ul class="plates" aria-label="{t['plates_label']}">{plates}</ul>
</div>
</section>'''


def steps(t):
    items = "".join(f'<li><span class="roman" aria-hidden="true">{r}</span><h3>{k}</h3><p>{v}</p></li>' for r, (k, v) in zip(["I", "II", "III", "IV"], t["steps"]))
    return f'''<section class="section steps" id="proceso" aria-labelledby="s-title">
<div class="wrap">
<h2 id="s-title">{t['s_title']}</h2>
<ol class="step-list">{items}</ol>
</div>
</section>'''


def form(t):
    f = t["form"]
    types = "".join(f'<label class="chip"><input type="radio" name="tipo" value="{v}" required><span>{n}</span></label>' for v, n in f["types"])
    prods = "".join(f'<label class="check"><input type="checkbox" name="productos" value="{v}"><span>{n}</span></label>' for v, n in f["products"])
    provs = "".join(f"<option>{p}</option>" for p in f["provinces"])
    vols = "".join(f'<option value="{v}">{n}</option>' for v, n in f["volumes"])
    R = '<span class="req" aria-hidden="true">*</span>'
    return f'''<section class="section quote-sec" id="presupuesto" aria-labelledby="f-title">
<div class="wrap quote-grid">
<div class="quote-intro">
<h2 id="f-title">{t['f_title']}</h2>
<p class="lead">{t['f_lead']}</p>
<dl class="spec contact-mini">
<div class="row"><dt>{t['c_phone']}</dt><dd><a href="tel:+34900000000">+34 900 000 000</a></dd></div>
<div class="row"><dt>{t['c_mail']}</dt><dd><a href="mailto:pedidos@primeegg.es">pedidos@primeegg.es</a></dd></div>
<div class="row"><dt>{t['c_hours']}</dt><dd>{t['hours']}</dd></div>
</dl>
</div>
<div class="form-card">
<form id="quote-form" novalidate>
<fieldset class="field field-full" id="g-tipo" aria-describedby="e-tipo">
<legend>{f['type_label']} {R}</legend>
<div class="chips">{types}</div>
<p class="err" id="e-tipo" aria-live="polite"></p>
</fieldset>
<div class="field"><label for="empresa">{f['company']} {R}</label><input id="empresa" name="empresa" type="text" autocomplete="organization" required aria-describedby="e-empresa"><p class="err" id="e-empresa" aria-live="polite"></p></div>
<div class="field"><label for="cif">{f['cif']} {R}</label><input id="cif" name="cif" type="text" required maxlength="9" autocapitalize="characters" spellcheck="false" placeholder="B12345678" aria-describedby="e-cif"><p class="err" id="e-cif" aria-live="polite"></p></div>
<div class="field"><label for="persona">{f['contact']} {R}</label><input id="persona" name="persona" type="text" autocomplete="name" required aria-describedby="e-persona"><p class="err" id="e-persona" aria-live="polite"></p></div>
<div class="field"><label for="email">{f['email']} {R}</label><input id="email" name="email" type="email" autocomplete="email" required aria-describedby="e-email"><p class="err" id="e-email" aria-live="polite"></p></div>
<div class="field"><label for="telefono">{f['phone']} {R}</label><input id="telefono" name="telefono" type="tel" autocomplete="tel" required placeholder="+34 600 000 000" aria-describedby="e-telefono"><p class="err" id="e-telefono" aria-live="polite"></p></div>
<div class="field"><label for="provincia">{f['province']} {R}</label><select id="provincia" name="provincia" required aria-describedby="e-provincia"><option value="">{f['choose']}</option>{provs}</select><p class="err" id="e-provincia" aria-live="polite"></p></div>
<fieldset class="field field-full" id="g-prod" aria-describedby="e-prod">
<legend>{f['products_label']} {R}</legend>
<div class="checks-grid">{prods}</div>
<p class="err" id="e-prod" aria-live="polite"></p>
</fieldset>
<div class="field field-full"><label for="volumen">{f['volume']} {R}</label><select id="volumen" name="volumen" required aria-describedby="e-volumen"><option value="">{f['choose']}</option>{vols}</select><p class="err" id="e-volumen" aria-live="polite"></p></div>
<div class="field field-full"><label for="comentario">{f['comment']}</label><textarea id="comentario" name="comentario" rows="4" placeholder="{f['comment_ph']}"></textarea></div>
<div class="field field-full"><label class="check consent"><input type="checkbox" id="rgpd" name="rgpd" required aria-describedby="e-rgpd"><span>{f['consent']}</span></label><p class="err" id="e-rgpd" aria-live="polite"></p></div>
<div class="field-full submit-row"><button class="btn btn-solid" type="submit">{f['submit']}</button><p class="fine">{f['fine']}</p></div>
</form>
<div class="success" id="quote-success" tabindex="-1" role="status" hidden>
{crown('crown crown-lg')}
<h3>{f['ok_title']}</h3>
<p>{f['ok_text']}</p>
<button class="link-arrow" type="button" id="quote-again">{f['again']}<span aria-hidden="true"></span></button>
</div>
</div>
</div>
</section>'''


def about(t):
    vals = "".join(f'<li><h3>{k}</h3><p>{v}</p></li>' for k, v in t["values"])
    faq = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in t["faq"])
    return f'''<section class="section about" id="nosotros" aria-labelledby="a-title">
<div class="wrap">
<div class="about-head">
<h2 id="a-title">{t['a_title']}</h2>
<div class="about-copy">
<p class="mission">{t['mission']}</p>
<p>{t['vision']}</p>
</div>
</div>
<ul class="values">{vals}</ul>
</div>
</section>
<section class="section faq" id="faq" aria-labelledby="faq-title">
<div class="wrap faq-grid">
<h2 id="faq-title">{t['faq_title']}</h2>
<div class="faq-list">{faq}</div>
</div>
</section>'''


def footer(t):
    legal = "".join(f'<li><a href="#" aria-disabled="true">{x}</a></li>' for x in t["legal"])
    nav = "".join(f'<li><a href="#{a}">{n}</a></li>' for a, n in t["nav"])
    return f'''<footer class="site-footer" id="contacto">
<div class="wrap foot-grid">
<div class="foot-brand">
{svgfile('logo-inverse.svg', vb='60 34 280 232', label='Primeegg — Maison · Huevos · Ovoproductos', cls='logo-inv', w=280, h=232)}
<p class="foot-tag">{t['tagline']}</p>
</div>
<div class="foot-col">
<h2 class="foot-h">{t['f_contact']}</h2>
<address>
<p>Primeegg Distribution SL</p>
<p>{t['address']}</p>
<p><a href="tel:+34900000000">+34 900 000 000</a></p>
<p><a href="mailto:pedidos@primeegg.es">pedidos@primeegg.es</a></p>
<p><a href="#top">primeegg.es</a></p>
</address>
</div>
<div class="foot-col">
<h2 class="foot-h">{t['f_nav']}</h2>
<ul class="foot-list">{nav}</ul>
</div>
<div class="foot-col">
<h2 class="foot-h">{t['f_lang']}</h2>
<div class="lang lang-foot" role="group" aria-label="{t['lang_label']}">{t['lang_html']}</div>
</div>
</div>
<div class="wrap foot-bottom">
<p>© 2026 Primeegg Distribution SL · {t['rights']}</p>
<ul class="legal">{legal}</ul>
</div>
</footer>'''


def page(t):
    css = (HERE / "site.css").read_text()
    js = (HERE / "site.js").read_text().replace("__MSG__", json.dumps(t["form"]["msgs"], ensure_ascii=False))
    pat = (A / "pattern.svg").read_text().strip().replace('"', "'").replace("#", "%23").replace("<", "%3C").replace(">", "%3E")
    css = css.replace("__PATTERN__", pat).replace("__LABEL_FONT__", t["label_font"])
    fav = (A / 'logo-mark.svg').read_text().strip().replace('"', "'").replace('#', '%23').replace('<', '%3C').replace('>', '%3E')
    body = "\n".join([header(t), '<main id="main">', hero(t), manifesto(t), products(t), horeca(t), distribution(t),
                      quality(t), steps(t), form(t), about(t), "</main>", footer(t)])
    body = re.sub(r'(\d) (h|год)(?=[\s.,<)])', r'\1&nbsp;\2', body)
    return f'''<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{t['meta']}">
<meta name="theme-color" content="#5E1A26">
<link rel="alternate" hreflang="es" href="index.html">
<link rel="alternate" hreflang="uk" href="uk.html">
<link rel="alternate" hreflang="x-default" href="index.html">
<link rel="icon" href="data:image/svg+xml,{fav}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{t["fonts"].replace("&", "&amp;")}" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{body}
<script>
{js}
</script>
</body>
</html>
'''


for t, fn in [(ES, "index.html"), (UK, "uk.html")]:
    _seq[0] = 0
    out = page(t)
    (ROOT / fn).write_text(out)
    print("wrote", fn, len(out) // 1024, "KB")
