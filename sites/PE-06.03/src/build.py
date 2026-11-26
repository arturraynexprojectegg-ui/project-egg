#!/usr/bin/env python3
"""Сборка sites/PE-06.03/index.html (ES) и uk.html (UA) из template.html.
Синтаксис шаблона:
  {{испанский||український}}          — текст на двух языках
  @@svg:file.svg|viewBox|aria-label|class@@ — инлайн SVG из ../assets (viewBox можно оставить пустым)
  @@map@@, @@egg@@, @@provinces@@     — сгенерированные фрагменты
Запуск: python3 sites/PE-06.03/src/build.py"""
import math, re
from pathlib import Path

HERE = Path(__file__).parent
SITE = HERE.parent
ASSETS = SITE / "assets"
TPL = (HERE / "template.html").read_text()

_uses = {}


def inline_svg(name, viewbox, label, cls):
    src = (ASSETS / name).read_text().strip()
    n = _uses.get(name, 0)
    _uses[name] = n + 1
    if n:  # повторное использование — уникализируем id
        suf = f"_{n}"
        src = re.sub(r'id="([^"]+)"', rf'id="\1{suf}"', src)
        src = re.sub(r'url\(#([^)]+)\)', rf'url(#\1{suf})', src)
        src = re.sub(r'href="#([^"]+)"', rf'href="#\1{suf}"', src)
    m = re.match(r'<svg[^>]*viewBox="([^"]+)"[^>]*>', src)
    vb = viewbox or m.group(1)
    attrs = f'viewBox="{vb}" class="{cls}" preserveAspectRatio="xMidYMid meet"'
    if label:
        attrs += f' role="img" aria-label="{label}"'
    else:
        attrs += ' aria-hidden="true" focusable="false"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>' + src[m.end():]


# ---------- Hero: жареное яйцо-солнце ----------
def egg_svg(label):
    cx, cy, R = 360, 360, 300
    pts = []
    N = 18
    for i in range(N):
        t = 2 * math.pi * i / N
        r = R * (1 + 0.055 * math.sin(5 * t + 0.6) + 0.035 * math.sin(3 * t + 2.1) + 0.02 * math.cos(7 * t))
        pts.append((cx + r * math.cos(t) * 1.04, cy + r * math.sin(t) * 0.94))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(N):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % N], pts[(i + 2) % N]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    d += "Z"
    yr = 104
    rays = "".join(
        f'<line x1="{cx + (yr + 26) * math.cos(a):.1f}" y1="{cy + (yr + 26) * math.sin(a):.1f}" '
        f'x2="{cx + (yr + 66) * math.cos(a):.1f}" y2="{cy + (yr + 66) * math.sin(a):.1f}"/>'
        for a in [math.pi * 2 * k / 12 - math.pi / 2 for k in range(12)])
    return f'''<svg class="egg" viewBox="0 0 720 720" role="img" aria-label="{label}">
<defs><radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFD36B" stop-opacity=".95"/><stop offset=".55" stop-color="#FFC44D" stop-opacity=".45"/><stop offset="1" stop-color="#FFB020" stop-opacity="0"/></radialGradient>
<radialGradient id="yolkg" cx="38%" cy="34%" r="70%"><stop offset="0" stop-color="#FFC63F"/><stop offset=".7" stop-color="#FFB020"/><stop offset="1" stop-color="#F39A12"/></radialGradient></defs>
<path class="egg-white-shadow" d="{d}" transform="translate(10 18)" fill="#22304D" opacity=".12"/>
<path class="egg-white" d="{d}" fill="#FFFFFF" stroke="#2B8FCB" stroke-width="9" stroke-linejoin="round"/>
<circle class="egg-glow" cx="{cx}" cy="{cy}" r="{yr + 120}" fill="url(#glow)"/>
<g class="egg-rays" stroke="#FFB020" stroke-width="17" stroke-linecap="round">{rays}</g>
<circle class="egg-yolk" cx="{cx}" cy="{cy}" r="{yr}" fill="url(#yolkg)"/>
<ellipse cx="{cx - 36}" cy="{cy - 38}" rx="26" ry="20" fill="#FFFFFF" opacity=".65" transform="rotate(-30 {cx - 36} {cy - 38})"/>
<circle cx="{cx - 4}" cy="{cy - 62}" r="7" fill="#FFFFFF" opacity=".5"/>
</svg>'''


# ---------- Карта Испании ----------
def P(lon, lat):
    return (lon + 10) * 40 + 20, (44.2 - lat) * 51.2 + 20


SPAIN = [(-9.3, 43.0), (-8.9, 43.3), (-8.3, 43.55), (-7.7, 43.77), (-7.0, 43.55), (-5.8, 43.66), (-4.5, 43.42),
         (-3.8, 43.48), (-3.0, 43.37), (-1.8, 43.39), (-1.4, 43.05), (-0.7, 42.85), (0.7, 42.86), (1.45, 42.45),
         (2.2, 42.43), (3.17, 42.33), (3.2, 41.9), (2.2, 41.35), (1.0, 41.05), (0.8, 40.7), (0.1, 40.0),
         (-0.3, 39.5), (0.2, 38.75), (-0.5, 38.3), (-0.75, 37.6), (-1.6, 37.25), (-2.0, 36.75), (-2.9, 36.73),
         (-4.4, 36.7), (-5.35, 36.15), (-5.6, 36.0), (-6.0, 36.3), (-6.4, 36.8), (-7.4, 37.2), (-7.5, 37.6),
         (-7.0, 38.2), (-7.3, 38.5), (-7.0, 39.0), (-7.5, 39.6), (-7.0, 39.7), (-6.9, 40.25), (-6.8, 41.0),
         (-6.2, 41.6), (-6.6, 41.95), (-7.2, 41.9), (-8.1, 41.8), (-8.9, 41.9), (-8.9, 42.4), (-9.1, 42.75)]
PORTUGAL = [(-8.9, 41.9), (-8.7, 41.2), (-8.9, 40.2), (-9.5, 38.75), (-8.9, 38.5), (-8.8, 37.95), (-8.99, 37.0),
            (-7.9, 37.0), (-7.4, 37.2), (-7.5, 37.6), (-7.0, 38.2), (-7.3, 38.5), (-7.0, 39.0), (-7.5, 39.6),
            (-7.0, 39.7), (-6.9, 40.25), (-6.8, 41.0), (-6.2, 41.6), (-6.6, 41.95), (-7.2, 41.9), (-8.1, 41.8)]


def smooth(points):
    pts = [P(*p) for p in points]
    N = len(pts)
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(N):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % N], pts[(i + 2) % N]
        k = 8
        c1 = (p1[0] + (p2[0] - p0[0]) / k, p1[1] + (p2[1] - p0[1]) / k)
        c2 = (p2[0] - (p3[0] - p1[0]) / k, p2[1] - (p3[1] - p1[1]) / k)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + "Z"


CITIES = [("Madrid", -3.70, 40.42), ("Barcelona", 2.17, 41.39), ("Valencia", -0.38, 39.47),
          ("Sevilla", -5.98, 37.39), ("Málaga", -4.42, 36.72), ("Bilbao", -2.93, 43.26),
          ("Zaragoza", -0.88, 41.65), ("Valladolid", -4.72, 41.65), ("A Coruña", -8.41, 43.36),
          ("Murcia", -1.13, 37.99), ("Córdoba", -4.78, 37.88), ("Toledo", -4.02, 39.86)]


def km(a, b):
    la = math.radians((a[2] + b[2]) / 2)
    dx = (a[1] - b[1]) * 111 * math.cos(la)
    dy = (a[2] - b[2]) * 111
    return math.hypot(dx, dy)


def map_svg(label, lang):
    hub = CITIES[0]
    hx, hy = P(hub[1], hub[2])
    R24 = 340  # km
    rpx = R24 / 111 * 51.2
    sp = smooth(SPAIN)
    pt = smooth(PORTUGAL)
    city = ""
    for name, lon, lat in CITIES[1:]:
        x, y = P(lon, lat)
        z24 = km(hub, (name, lon, lat)) <= R24
        anchor = "end" if lon > 1 or name in ("Valencia", "Murcia") else "start"
        dx, dy = (-12 if anchor == "end" else 12), 5
        if name == "Zaragoza":
            anchor, dx, dy = "middle", 0, -13
        city += (f'<g class="city {"z24" if z24 else "z48"}"><circle cx="{x:.1f}" cy="{y:.1f}" r="6.5"/>'
                 f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{name}</text></g>')
    isl = "".join(f'<ellipse cx="{P(lo, la)[0]:.1f}" cy="{P(lo, la)[1]:.1f}" rx="{rx}" ry="{ry}" transform="rotate({rt} {P(lo, la)[0]:.1f} {P(lo, la)[1]:.1f})"/>'
                  for lo, la, rx, ry, rt in [(2.95, 39.62, 22, 14, -20), (4.1, 39.97, 10, 5, -10), (1.42, 38.98, 8, 6, 30), (1.45, 38.7, 3, 2, 0)])
    can_lbl = "Canarias" if lang == "es" else "Канари"
    bal_lbl = "Baleares" if lang == "es" else "Балеари"
    canary = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>' for x, y, rx, ry in
                     [(52, 422, 6, 4), (70, 428, 5, 4), (92, 420, 12, 8), (122, 426, 10, 6), (144, 432, 11, 8), (170, 414, 9, 5), (184, 404, 5, 4)])
    return f'''<svg class="map" viewBox="0 0 640 470" role="img" aria-label="{label}">
<defs><clipPath id="spclip"><path d="{sp}"/></clipPath></defs>
<path d="{pt}" class="pt"/>
<path d="{sp}" class="es z48fill"/>
<g clip-path="url(#spclip)"><circle cx="{hx:.1f}" cy="{hy:.1f}" r="{rpx:.1f}" class="z24fill"/></g>
<path d="{sp}" class="es-line"/>
<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{rpx:.1f}" class="ring"/>
<g class="isl">{isl}</g>
<text x="{P(2.9, 39.0)[0]:.1f}" y="{P(2.9, 39.0)[1] + 8:.1f}" class="lbl-s" text-anchor="middle">{bal_lbl}</text>
<g class="canary"><rect x="30" y="392" width="176" height="60" rx="14"/>{canary}<text x="118" y="446" text-anchor="middle" class="lbl-s">{can_lbl}</text></g>
{city}
<g class="hub" transform="translate({hx:.1f} {hy:.1f})">
<g stroke="#FFB020" stroke-width="3.2" stroke-linecap="round">{"".join(f'<line x1="{15*math.cos(a):.1f}" y1="{15*math.sin(a):.1f}" x2="{22*math.cos(a):.1f}" y2="{22*math.sin(a):.1f}"/>' for a in [math.pi*k/6 for k in range(12)])}</g>
<circle r="10" fill="#FFB020" stroke="#1A2540" stroke-width="2"/></g>
<text x="{hx + 28:.1f}" y="{hy + 6:.1f}" class="lbl-hub">Madrid · hub</text>
</svg>'''


PROVS = ["A Coruña", "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Baleares", "Barcelona",
         "Bizkaia", "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ceuta", "Ciudad Real", "Córdoba", "Cuenca",
         "Gipuzkoa", "Girona", "Granada", "Guadalajara", "Huelva", "Huesca", "Jaén", "La Rioja", "Las Palmas", "León",
         "Lleida", "Lugo", "Madrid", "Málaga", "Melilla", "Murcia", "Navarra", "Ourense", "Palencia", "Pontevedra",
         "Salamanca", "Santa Cruz de Tenerife", "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo",
         "Valencia", "Valladolid", "Zamora", "Zaragoza"]


def build(lang):
    global _uses
    _uses = {}
    side = 0 if lang == "es" else 1
    html = re.sub(r"\{\{(.*?)\|\|(.*?)\}\}", lambda m: m.group(1 + side), TPL, flags=re.S)
    html = html.replace("@@egg@@", egg_svg("Huevo frito con yema en forma de sol" if lang == "es" else "Яєчня з жовтком у формі сонця"))
    html = html.replace("@@map@@", map_svg(
        "Mapa de España: entrega en 24 h en un radio de unos 340 km desde Madrid y en 48 h en el resto de la península" if lang == "es"
        else "Мапа Іспанії: доставка за 24 год у радіусі близько 340 км від Мадрида і за 48 год — на решті півострова", lang))
    html = html.replace("@@provinces@@", "".join(f'<option>{p}</option>' for p in PROVS))
    html = re.sub(r"@@svg:([^|@]+)\|([^|@]*)\|([^|@]*)\|([^|@]*)@@", lambda m: inline_svg(*m.groups()), html)
    assert "{{" not in html and "@@" not in html, "unresolved template marker"
    return html


(SITE / "index.html").write_text(build("es"))
(SITE / "uk.html").write_text(build("uk"))
print("ok", len((SITE / "index.html").read_text()) // 1024, "KB")
