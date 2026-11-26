# Authored vector art for PE-03.06 «Sello» site: map, dishes, eggs, icons.
import math

C = dict(cob="#1F4E9C", ter="#C8553D", saf="#F2A541", ind="#0E2140", cal="#F4ECDC",
         terd="#AD4630", sand="#E9DCC3", plate="#FBF6EC")


def egg_path(cx, cy, w, h):
    # same proportions as the medallion egg
    rx = w / 2
    top, bot = cy - h / 2, cy + h / 2
    k1, k2 = 0.56, 0.755
    return (f"M {cx:.1f} {top:.1f} C {cx+rx*.56:.1f} {top:.1f} {cx+rx:.1f} {top+h*.346:.1f} {cx+rx:.1f} {top+h*k2:.1f} "
            f"C {cx+rx:.1f} {top+h*.985:.1f} {cx+rx*.56:.1f} {bot:.1f} {cx:.1f} {bot:.1f} "
            f"C {cx-rx*.56:.1f} {bot:.1f} {cx-rx:.1f} {top+h*.985:.1f} {cx-rx:.1f} {top+h*k2:.1f} "
            f"C {cx-rx:.1f} {top+h*.346:.1f} {cx-rx*.56:.1f} {top:.1f} {cx:.1f} {top:.1f} Z")


def beads(cx, cy, r, n, rr, fill, rx=None, ry=None):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = cx + (rx or r) * math.cos(a)
        y = cy + (ry or r) * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"/>')
    return "".join(out)


# ---------- Map of Spain ----------
SPAIN = [(-9.3, 43.0), (-8.9, 43.35), (-8.2, 43.72), (-7.0, 43.56), (-5.8, 43.62), (-4.5, 43.42), (-3.8, 43.48),
         (-3.0, 43.38), (-1.8, 43.38), (-1.4, 43.05), (-0.7, 42.85), (0.7, 42.82), (1.45, 42.6), (2.2, 42.42),
         (3.17, 42.43), (3.2, 41.95), (2.8, 41.65), (2.15, 41.33), (1.0, 41.05), (0.85, 40.7), (0.0, 40.02),
         (-0.33, 39.45), (0.2, 38.75), (-0.5, 38.32), (-0.75, 37.85), (-0.85, 37.6), (-1.6, 37.25), (-1.9, 36.75),
         (-2.5, 36.82), (-3.5, 36.72), (-4.42, 36.7), (-5.2, 36.42), (-5.6, 36.02), (-6.0, 36.25), (-6.3, 36.55),
         (-6.4, 36.82), (-6.9, 37.15), (-7.4, 37.18), (-7.5, 37.6), (-7.0, 38.0), (-7.3, 38.45), (-7.0, 38.9),
         (-7.3, 39.4), (-7.0, 39.7), (-6.9, 40.2), (-6.8, 40.55), (-6.85, 41.0), (-6.2, 41.6), (-6.6, 41.95),
         (-7.2, 41.88), (-8.1, 41.8), (-8.2, 42.1), (-8.87, 41.87), (-8.85, 42.3), (-9.0, 42.6)]
K = 46


def P(lon, lat):
    return ((lon + 9.6) * K + 10, (44.0 - lat) * K * 1.3 + 10)


def smooth(points):
    # Catmull-Rom -> Bezier, closed
    n = len(points)
    d = f"M {points[0][0]:.1f} {points[0][1]:.1f} "
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + "Z"


def island(lon, lat, rx, ry, rot=0):
    x, y = P(lon, lat)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" transform="rotate({rot} {x:.1f} {y:.1f})"/>'


def spain_map(t):
    pts = [P(*p) for p in SPAIN]
    land = smooth(pts)
    mad = P(-3.7, 40.42)
    cities = [("A Coruña", -8.4, 43.36, "s"), ("Bilbao", -2.93, 43.26, "s"), ("Zaragoza", -0.88, 41.65, "n"),
              ("Barcelona", 2.17, 41.39, "w"), ("Valencia", -0.38, 39.47, "w"), ("Sevilla", -5.98, 37.39, "n"),
              ("Málaga", -4.42, 36.72, "n"), ("Valladolid", -4.72, 41.65, "n")]
    regions = [(n, a, b) for n, (a, b) in zip(t["map_regions"], [(-7.9, 42.75), (-4.9, 42.05), (-0.75, 41.2),
               (1.45, 41.95), (-6.15, 39.15), (-2.9, 39.25), (-4.6, 37.6)])]
    cities = [(t["map_cities"][i],) + c[1:] for i, c in enumerate(cities)]
    r24 = 2.35 * K * 1.3
    o = [f'<svg class="map" viewBox="0 0 680 520" role="img" aria-labelledby="mapT mapD">',
         f'<title id="mapT">{t["map_title"]}</title><desc id="mapD">{t["map_desc"]}</desc>',
         f'<defs><clipPath id="landClip"><path d="{land}"/></clipPath>',
         '<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<rect width="10" height="10" fill="{C["ter"]}"/><rect width="3" height="10" fill="#B94C35"/></pattern></defs>',
         f'<path d="{land}" fill="{C["ter"]}"/>',
         f'<g clip-path="url(#landClip)"><circle class="z24" cx="{mad[0]:.1f}" cy="{mad[1]:.1f}" r="{r24:.1f}" fill="{C["saf"]}"/>']
    # 24h extra pockets around Barcelona, Valencia, Sevilla
    for lon, lat in [(2.17, 41.39), (-0.38, 39.47), (-5.98, 37.39)]:
        x, y = P(lon, lat)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.85*K*1.3:.1f}" fill="{C["saf"]}"/>')
    o.append('</g>')
    o.append(f'<path d="{land}" fill="none" stroke="{C["cal"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    o.append(f'<g fill="{C["ter"]}" stroke="{C["cal"]}" stroke-width="2">' + island(2.95, 39.6, 26, 17, -10)
             + island(4.1, 39.97, 11, 6, -15) + island(1.42, 38.98, 9, 7) + '</g>')
    # routes
    o.append(f'<g stroke="{C["ind"]}" stroke-width="1.6" stroke-dasharray="2 5" stroke-linecap="round" fill="none" opacity=".75">')
    for name, lon, lat, _ in cities:
        x, y = P(lon, lat)
        mx, my = (mad[0] + x) / 2, (mad[1] + y) / 2 - 14
        o.append(f'<path d="M {mad[0]:.1f} {mad[1]:.1f} Q {mx:.1f} {my:.1f} {x:.1f} {y:.1f}"/>')
    o.append('</g>')
    o.append(f'<g font-family="Josefin Sans, Montserrat, sans-serif" font-weight="700" font-size="10.5" letter-spacing="1.6" fill="{C["ind"]}" opacity=".62" text-anchor="middle">')
    for name, lon, lat in regions:
        x, y = P(lon, lat)
        o.append(f'<text x="{x:.1f}" y="{y:.1f}">{name}</text>')
    o.append('</g>')
    o.append(f'<g font-family="Josefin Sans, Montserrat, sans-serif" font-size="13" font-weight="600" fill="{C["cal"]}">')
    for name, lon, lat, pos in cities:
        x, y = P(lon, lat)
        dx, dy, anc = {"n": (0, -11, "middle"), "s": (0, 20, "middle"), "w": (-10, 4, "end"), "e": (10, 4, "start")}[pos]
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{C["ind"]}" stroke="{C["cal"]}" stroke-width="1.5"/>'
                 f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}" stroke="{C["ind"]}" stroke-width="3" paint-order="stroke">{name}</text>')
    o.append('</g>')
    # hub = medallion
    hx, hy = mad
    o.append(f'<g class="hub"><circle cx="{hx:.1f}" cy="{hy:.1f}" r="19" fill="{C["cob"]}"/>'
             + beads(hx, hy, 15.5, 16, 1.1, C["cal"]) +
             f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="12.5" fill="{C["cal"]}"/>'
             f'<path d="{egg_path(hx, hy+.5, 11, 15)}" fill="{C["ter"]}"/><circle cx="{hx:.1f}" cy="{hy+2.4:.1f}" r="2.6" fill="{C["saf"]}"/>'
             f'<text x="{hx+26:.1f}" y="{hy+5:.1f}" font-family="DM Serif Display, Playfair Display, serif" font-size="19" fill="{C["ind"]}">{t["map_cities"][8]}</text></g>')
    o.append('</svg>')
    return "".join(o)


# ---------- egg sizes ----------
def egg_sizes(t):
    sizes = [("S", "< 53 g", 40), ("M", "53–63 g", 47), ("L", "63–73 g", 54), ("XL", "≥ 73 g", 61)]
    o = [f'<svg class="sizes" viewBox="0 0 360 120" role="img" aria-label="{t["sizes_aria"]}">']
    x = 45
    for i, (s, g, h) in enumerate(sizes):
        fill = C["cal"] if i % 2 == 0 else "#D9A273"
        o.append(f'<path d="{egg_path(x, 78 - h/2, h*.77, h)}" fill="{fill}" stroke="{C["ind"]}" stroke-width="1.6"/>')
        o.append(f'<text x="{x}" y="100" text-anchor="middle" font-family="DM Serif Display, Playfair Display, serif" font-size="17" fill="{C["ind"]}">{s}</text>')
        o.append(f'<text x="{x}" y="116" text-anchor="middle" font-family="Josefin Sans, Montserrat, sans-serif" font-size="10.5" font-weight="600" fill="{C["ind"]}">{g}</text>')
        x += 90
    o.append('</svg>')
    return "".join(o)


# ---------- dishes ----------
def plate(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy+6}" r="140" fill="{C["ind"]}" opacity=".18"/>'
            f'<circle cx="{cx}" cy="{cy}" r="140" fill="{C["cob"]}"/>' + beads(cx, cy, 131, 44, 3, C["cal"]) +
            f'<circle cx="{cx}" cy="{cy}" r="122" fill="{C["plate"]}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="106" fill="none" stroke="{C["cob"]}" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="100" fill="none" stroke="{C["saf"]}" stroke-width="1.5" stroke-dasharray="1 6" stroke-linecap="round"/>')


def sector(cx, cy, r, a0, a1):
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M {cx} {cy} L {x0:.1f} {y0:.1f} A {r} {r} 0 {large} 1 {x1:.1f} {y1:.1f} Z"


def tortilla(label):
    cx = cy = 170
    a0, a1 = -18, 32
    body = (f'<circle cx="{cx}" cy="{cy}" r="90" fill="#C9772A"/>'
            f'<circle cx="{cx}" cy="{cy}" r="83" fill="#F2B552"/>'
            f'<ellipse cx="{cx-30}" cy="{cy-26}" rx="16" ry="9" fill="#E39A3C" transform="rotate(-20 {cx-30} {cy-26})"/>'
            f'<ellipse cx="{cx+18}" cy="{cy+40}" rx="20" ry="10" fill="#E39A3C" transform="rotate(15 {cx+18} {cy+40})"/>'
            f'<ellipse cx="{cx-40}" cy="{cy+30}" rx="9" ry="6" fill="#D98A33"/>'
            f'<ellipse cx="{cx+10}" cy="{cy-50}" rx="8" ry="5" fill="#D98A33"/>')
    cut = sector(cx, cy, 93, a0, a1)
    mid = math.radians((a0 + a1) / 2)
    dx, dy = 26 * math.cos(mid), 26 * math.sin(mid)
    inner = sector(cx, cy, 90, a0, a1)
    return (f'<svg viewBox="0 0 340 340" role="img" aria-label="{label}">' + plate(cx, cy) +
            f'<mask id="tcut"><rect width="340" height="340" fill="#fff"/><path d="{cut}" fill="#000"/></mask>'
            f'<g mask="url(#tcut)">{body}</g>'
            f'<g transform="translate({dx:.1f} {dy:.1f})"><path d="{inner}" fill="#FBE3A0"/>'
            f'<path d="{sector(cx, cy, 90, a0+2, a1-2)}" fill="#F2B552" transform="translate(-3 -2)"/>'
            f'<circle cx="{cx+62:.0f}" cy="{cy+12:.0f}" r="5" fill="#FBE3A0"/><circle cx="{cx+48:.0f}" cy="{cy+4:.0f}" r="4" fill="#FBE3A0"/></g>'
            '</svg>')


def flan(label):
    beadsel = beads(170, 246, 0, 36, 2.6, C["cal"], rx=122, ry=30)
    return (f'<svg viewBox="0 0 340 340" role="img" aria-label="{label}">'
            f'<ellipse cx="170" cy="258" rx="140" ry="40" fill="{C["ind"]}" opacity=".18"/>'
            f'<ellipse cx="170" cy="248" rx="140" ry="38" fill="{C["cob"]}"/>' + beadsel +
            f'<ellipse cx="170" cy="244" rx="112" ry="26" fill="{C["plate"]}"/>'
            f'<ellipse cx="170" cy="244" rx="96" ry="20" fill="#9C4220"/>'
            f'<path d="M 92 238 Q 170 256 248 238 L 222 120 Q 170 132 118 120 Z" fill="#F4BE55"/>'
            f'<path d="M 108 236 L 124 124 Q 132 126 140 127 L 128 240 Z" fill="#F8D17E"/>'
            f'<path d="M 222 120 L 248 238 Q 236 241 224 243 Z" fill="#E2A23E"/>'
            f'<ellipse cx="170" cy="121" rx="52" ry="12" fill="#8E3B1F"/>'
            f'<path d="M 118 121 Q 116 150 124 152 Q 132 150 130 128 Q 140 138 146 132 Q 154 172 162 170 Q 170 166 168 133 '
            f'Q 184 136 192 132 Q 196 150 204 150 Q 212 146 210 129 Q 218 126 222 121 Z" fill="#A6461F"/>'
            f'<ellipse cx="156" cy="118" rx="16" ry="3" fill="#C2653A"/>'
            '</svg>')


def mayonesa(label):
    return (f'<svg viewBox="0 0 340 340" role="img" aria-label="{label}">'
            f'<ellipse cx="160" cy="292" rx="112" ry="16" fill="{C["ind"]}" opacity=".2"/>'
            # whisk behind
            f'<g transform="rotate(38 226 170)"><rect x="220" y="40" width="12" height="96" rx="6" fill="{C["ind"]}"/>'
            f'<g fill="none" stroke="#9AA7BF" stroke-width="3"><ellipse cx="226" cy="178" rx="16" ry="46"/><ellipse cx="226" cy="178" rx="7" ry="46"/></g></g>'
            f'<path d="M 54 176 Q 60 290 160 290 Q 260 290 266 176 Z" fill="{C["cob"]}"/>'
            f'<path d="M 64 214 Q 160 236 256 214" fill="none" stroke="{C["saf"]}" stroke-width="5"/>'
            + "".join(f'<circle cx="{x}" cy="{246 + (abs(x-160)/100)**2*-18:.1f}" r="3" fill="{C["cal"]}"/>' for x in range(84, 240, 19)) +
            f'<ellipse cx="160" cy="176" rx="106" ry="22" fill="#163B78"/>'
            f'<ellipse cx="160" cy="176" rx="98" ry="17" fill="#FBEBB5"/>'
            f'<path d="M 118 178 Q 128 152 150 156 Q 152 138 168 136 Q 162 150 178 156 Q 200 158 204 178 Q 160 190 118 178 Z" fill="#FFF4CF"/>'
            f'<path d="M 140 168 Q 160 160 186 168" fill="none" stroke="#EAD48C" stroke-width="2.5" stroke-linecap="round"/>'
            f'<path d="{egg_path(286, 262, 40, 52)}" fill="#D9A273"/>'
            f'<path d="M 30 278 Q 34 250 56 248 L 62 258 L 70 250 L 78 262 Q 74 284 52 286 Q 34 286 30 278 Z" fill="{C["plate"]}"/>'
            f'<ellipse cx="54" cy="262" rx="12" ry="8" fill="{C["saf"]}"/>'
            '</svg>')


# ---------- icons (24px, stroke) ----------
ICONS = {
    "tray": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="8" cy="10" r="1.6"/><circle cx="12" cy="10" r="1.6"/><circle cx="16" cy="10" r="1.6"/><circle cx="8" cy="14" r="1.6"/><circle cx="12" cy="14" r="1.6"/><circle cx="16" cy="14" r="1.6"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14.5l2.4 2.2L16 12.5"/>',
    "person": '<circle cx="12" cy="8" r="3.6"/><path d="M4.5 20c.8-4 3.6-6 7.5-6s6.7 2 7.5 6"/>',
    "route": '<circle cx="6" cy="18" r="2.4"/><circle cx="18" cy="6" r="2.4"/><path d="M8.2 17c6 0 2-9 7.6-10"/>',
    "truck": '<path d="M2.5 6.5h11v9h-11zM13.5 9.5h4l3.5 3.5v2.5h-7.5"/><circle cx="7" cy="17.5" r="1.9"/><circle cx="17" cy="17.5" r="1.9"/>',
    "thermo": '<path d="M10 4.5a2 2 0 0 1 4 0v9.2a4 4 0 1 1-4 0z"/><path d="M12 9v7.5"/>',
    "box": '<path d="M3.5 8L12 4l8.5 4v8.5L12 20.5 3.5 16.5z"/><path d="M3.5 8L12 12l8.5-4M12 12v8.5"/>',
    "form": '<rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M8.5 8.5h7M8.5 12h7M8.5 15.5h4"/>',
    "egg": '<path d="M12 3.5c3.4 0 6 5.2 6 9.6 0 4-2.7 7.4-6 7.4s-6-3.4-6-7.4c0-4.4 2.6-9.6 6-9.6z"/>',
    "seal": '<circle cx="12" cy="10" r="6"/><path d="M9.2 9.8l2 2 3.6-3.6M8.5 15l-1.5 5.5 5-2 5 2-1.5-5.5"/>',
    "farm": '<path d="M3.5 11L12 4.5l8.5 6.5M5.5 9.5V20h13V9.5"/><path d="M9.5 20v-5.5h5V20"/>',
    "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="M4 7l8 6 8-6"/>',
    "phone": '<path d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 6 6l1.5-2 4 1.5v3a2 2 0 0 1-2 2A16 16 0 0 1 4.5 5.5a2 2 0 0 1 2-2z"/>',
    "chat": '<path d="M4 5.5h16v10H10l-4 3.5v-3.5H4z"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def petal():
    # 4-petal flower from the azulejo
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-16 -16 32 32">'
            '<g fill="#C8553D"><path d="M13.6-13.6c2.2 2.2.4 7.4-2.3 10.1-2.3 2.3-5.6 2.2-7.8 0s-2.3-5.5 0-7.8C6.2-14 11.4-15.8 13.6-13.6z"/>'
            '<path d="M13.6-13.6c2.2 2.2.4 7.4-2.3 10.1-2.3 2.3-5.6 2.2-7.8 0s-2.3-5.5 0-7.8C6.2-14 11.4-15.8 13.6-13.6z" transform="rotate(90)"/>'
            '<path d="M13.6-13.6c2.2 2.2.4 7.4-2.3 10.1-2.3 2.3-5.6 2.2-7.8 0s-2.3-5.5 0-7.8C6.2-14 11.4-15.8 13.6-13.6z" transform="rotate(180)"/>'
            '<path d="M13.6-13.6c2.2 2.2.4 7.4-2.3 10.1-2.3 2.3-5.6 2.2-7.8 0s-2.3-5.5 0-7.8C6.2-14 11.4-15.8 13.6-13.6z" transform="rotate(270)"/></g>'
            '<circle r="4" fill="#F2A541"/></svg>')


def stamped_egg(label):
    # egg with the printed code, for Calidad
    return (f'<svg viewBox="0 0 260 320" role="img" aria-label="{label}">'
            f'<ellipse cx="130" cy="300" rx="84" ry="10" fill="{C["ind"]}" opacity=".16"/>'
            f'<path d="{egg_path(130, 160, 196, 270)}" fill="#E0AE80"/>'
            f'<ellipse cx="88" cy="110" rx="18" ry="34" fill="#F0CDA8" opacity=".75" transform="rotate(18 88 110)"/>'
            f'<g fill="none" stroke="{C["cob"]}" stroke-width="2.4" opacity=".92"><circle cx="130" cy="168" r="34"/></g>'
            + beads(130, 168, 28, 20, 1.3, C["cob"]) +
            f'<path d="{egg_path(130, 168, 20, 27)}" fill="{C["cob"]}"/>'
            f'<text x="130" y="236" text-anchor="middle" font-family="Josefin Sans, Montserrat, sans-serif" font-weight="700" font-size="26" letter-spacing="2" fill="{C["cob"]}">1ES28001</text>'
            '</svg>')
