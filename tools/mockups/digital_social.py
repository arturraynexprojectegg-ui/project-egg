"""Соцсети: профиль Instagram на телефоне + 3 поста разных шаблонов."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import mix, contrast  # noqa: E402
import digital_web as dw  # noqa: E402
from digital_web import T, wrap, fit, fw, shadow, egg, eggs_group, tray_top  # noqa: E402

TITLE = "Социальные сети"
CAPTION = "Профиль @primeegg в Instagram и три шаблона постов: заголовок на фирменном цвете, паттерн со знаком и карточка продукта."

UI = "Inter, Helvetica, Arial, sans-serif"
IG_INK, IG_GREY, IG_LINE = "#111111", "#737373", "#DBDBDB"


def heads(k):
    h = k.t("headlines_es", ["Del campo a tu cocina", "Frescos cada mañana", "Calidad que se nota"])
    return h if isinstance(h, list) and h else ["Del campo a tu cocina"]


# ------------------------------------------------------------------ posts (base 400×400)
def fried_egg(cx, cy, r, yolk="#F6B21A"):
    pts = []
    import math
    n = 14
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + 0.09 * math.sin(i * 2.3) + 0.05 * math.cos(i * 3.7))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.92))
    d = f"M{(pts[0][0]+pts[1][0])/2:.1f},{(pts[0][1]+pts[1][1])/2:.1f} "
    for i in range(n):
        p1, p2 = pts[(i + 1) % n], pts[(i + 2) % n]
        d += f"Q{p1[0]:.1f},{p1[1]:.1f} {(p1[0]+p2[0])/2:.1f},{(p1[1]+p2[1])/2:.1f} "
    out = f'<path d="{d}Z" transform="translate(4,8)" fill="#2B2116" opacity="0.16"/>'
    out += f'<path d="{d}Z" fill="#FFFDF8"/>'
    out += f'<circle cx="{cx-r*0.08:.1f}" cy="{cy-r*0.05:.1f}" r="{r*0.4:.1f}" fill="{yolk}"/>'
    out += f'<circle cx="{cx-r*0.08:.1f}" cy="{cy-r*0.05:.1f}" r="{r*0.4:.1f}" fill="none" stroke="#C9820F" stroke-width="2" opacity="0.35"/>'
    out += f'<ellipse cx="{cx-r*0.2:.1f}" cy="{cy-r*0.18:.1f}" rx="{r*0.12:.1f}" ry="{r*0.07:.1f}" fill="#FFFFFF" opacity="0.7" transform="rotate(-30 {cx-r*0.2:.1f} {cy-r*0.18:.1f})"/>'
    return out


def post_headline(k, idx=0, bg=None):
    bg = bg or k.brand_bg
    oc = k.on(bg)
    out = f'<rect width="400" height="400" fill="{bg}"/>'
    out += f'<circle cx="360" cy="372" r="150" fill="{oc}" opacity="0.08"/>'
    out += fried_egg(328, 330, 96)
    acc = k.accent if contrast(k.accent, bg) >= 2 else oc
    out += f'<rect x="36" y="44" width="40" height="5" rx="2.5" fill="{acc}"/>'
    hs = heads(k)
    h = hs[idx % len(hs)]
    size, lines = fit(h, 50, 330, fw(k.head_font), 3, 30)
    for i, ln in enumerate(lines):
        out += T(36, 100 + size * 0.2 + i * size * 1.06, ln, size, oc, k.head_font, 700)
    out += k.logo("mono", 26, 300, 150, 76, color=oc, align="left")
    return out


def post_pattern(k):
    bg = k.primary
    oc = k.on(bg)
    out = f'<rect width="400" height="400" fill="{bg}"/>'
    if k.pattern_src:
        out += k.pattern_rect(0, 0, 400, 400, scale=0.8, opacity=0.22, color=oc)
    else:
        for j in range(5):
            for i in range(5):
                out += k.logo("mono", 12 + i * 80 + (40 if j % 2 else 0), 12 + j * 80, 50, 50, color=oc, opacity=0.12)
    g = k.uid("fd")
    out += (f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg}" stop-opacity="0"/>'
            f'<stop offset="0.45" stop-color="{bg}" stop-opacity="0.92"/><stop offset="1" stop-color="{bg}"/></linearGradient>')
    out += f'<rect x="0" y="270" width="400" height="130" fill="url(#{g})"/>'
    out += f'<circle cx="200" cy="184" r="112" fill="#2B2116" opacity="0.12"/>'
    out += f'<circle cx="200" cy="178" r="112" fill="{k.light}"/>'
    out += f'<circle cx="200" cy="178" r="100" fill="none" stroke="{k.primary}" stroke-width="1.5" opacity="0.35"/>'
    out += k.logo("mark", 128, 106, 144, 144)
    tg = k.t("taglines.es", "Huevos frescos de granja")
    size, lines = fit(tg, 24, 330, fw(k.head_font), 2, 16)
    y0 = 338 - (len(lines) - 1) * size * 0.6
    for i, ln in enumerate(lines):
        out += T(200, y0 + i * size * 1.15, ln, size, oc, k.head_font, 700, "middle")
    return out


def post_product(k):
    bg = k.light
    out = f'<rect width="400" height="400" fill="{bg}"/>'
    out += f'<circle cx="200" cy="168" r="128" fill="{mix(k.primary, bg, 0.86)}"/>'
    # открытая коробка на 6, вид сверху: крышка в фирменном цвете
    lx, ly, lw, lh = 92, 58, 216, 86
    out += f'<rect x="{lx}" y="{ly+6}" width="{lw}" height="{lh}" rx="10" fill="#2B2116" opacity="0.12"/>'
    out += f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="{k.primary}"/>'
    out += f'<rect x="{lx}" y="{ly+lh-12}" width="{lw}" height="12" fill="#000" opacity="0.10"/>'
    out += k.logo("mono", lx + 20, ly + 8, lw - 40, lh - 24, color=k.on(k.primary))
    out += f'<ellipse cx="200" cy="{ly+lh+124}" rx="118" ry="9" fill="#2B2116" opacity="0.16"/>'
    out += tray_top(k, lx, ly + lh, lw, 118, 3, 2)
    badge = k.t("products.carton.badge", "Del día")
    bc = k.accent if contrast(k.accent, bg) >= 1.6 else k.primary
    bw = len(badge) * 13 * 0.62 + 28
    out += f'<rect x="28" y="28" width="{bw:.1f}" height="30" rx="15" fill="{bc}"/>'
    out += T(28 + bw / 2, 48, badge.upper(), 12, k.on(bc), k.text_font, 800, "middle", ls=1)
    t1 = k.t("products.carton.title", "Huevos frescos")
    size, lines = fit(t1, 30, 280, fw(k.head_font), 1, 20)
    out += T(32, 330, lines[0], size, k.ink, k.head_font, 700)
    out += T(32, 360, k.t("products.carton.subtitle", "Categoría A · Talla L") + " · 6 / 12 uds", 15, k.ink, k.text_font, 500, op=0.7)
    cc = k.primary if contrast(k.primary, bg) >= 2.5 else k.ink
    out += f'<circle cx="346" cy="340" r="24" fill="{cc}"/>'
    out += f'<path d="M336,340 h20 m-7,-7 l7,7 l-7,7" fill="none" stroke="{k.on(cc)}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    return out


def post_eggs(k, bg):
    out = f'<rect width="400" height="400" fill="{bg}"/>'
    out += f'<circle cx="200" cy="200" r="130" fill="{k.on(bg)}" opacity="0.08"/>'
    out += eggs_group(k, 200, 300, 1.45)
    return out


def place(body, x, y, s, k, rx=0):
    cid = k.uid("ps")
    return (f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><g transform="translate({x:.1f},{y:.1f}) scale({s/400:.4f})">{body}</g></g>')


# ------------------------------------------------------------------ UI bits
def avatar(k, cx, cy, r, ring=True):
    out = ""
    if ring:
        g = k.uid("rg")
        c2 = k.accent if contrast(k.accent, "#FFFFFF") > 1.4 else mix(k.primary, "#FFFFFF", 0.4)
        out += (f'<linearGradient id="{g}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{c2}"/>'
                f'<stop offset="1" stop-color="{k.primary}"/></linearGradient>')
        out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r+r*0.14:.1f}" fill="none" stroke="url(#{g})" stroke-width="{max(1.5, r*0.08):.1f}"/>'
    out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{k.light}" stroke="#E6E2DA" stroke-width="0.8"/>'
    out += k.logo("mark", cx - r * 0.72, cy - r * 0.72, r * 1.44, r * 1.44)
    return out


def icon_heart(x, y, s, c=IG_INK):
    return (f'<path transform="translate({x},{y}) scale({s/24:.3f})" d="M12 20.5 C6 16 2.5 12.8 2.5 8.8 C2.5 6 4.6 4 7.2 4 C9.2 4 10.9 5.1 12 6.8 '
            f'C13.1 5.1 14.8 4 16.8 4 C19.4 4 21.5 6 21.5 8.8 C21.5 12.8 18 16 12 20.5 Z" fill="none" stroke="{c}" stroke-width="1.9" stroke-linejoin="round"/>')


def icon_comment(x, y, s, c=IG_INK):
    return (f'<path transform="translate({x},{y}) scale({s/24:.3f})" d="M20.5 12 A8.5 8.5 0 1 0 17.4 18.6 L21 20 L20 16.4 A8.4 8.4 0 0 0 20.5 12 Z" '
            f'fill="none" stroke="{c}" stroke-width="1.9" stroke-linejoin="round"/>')


def icon_send(x, y, s, c=IG_INK):
    return (f'<g transform="translate({x},{y}) scale({s/24:.3f})" fill="none" stroke="{c}" stroke-width="1.9" stroke-linejoin="round">'
            f'<path d="M21.5 3 L2.5 9.5 L10 13 L13.5 20.5 Z"/><path d="M10 13 L21.5 3"/></g>')


def icon_bookmark(x, y, s, c=IG_INK):
    return (f'<path transform="translate({x},{y}) scale({s/24:.3f})" d="M5.5 3 H18.5 V21 L12 15 L5.5 21 Z" fill="none" stroke="{c}" '
            f'stroke-width="1.9" stroke-linejoin="round"/>')


def post_card(k, x, y, s, body, likes, caption):
    hh, fh = 52, 92
    H = hh + s + fh
    out = shadow(x, y, s, H, 16, n=6, spread=3, op=0.03, dy=10)
    cid = k.uid("pc")
    out += f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{s}" height="{H}" rx="16"/></clipPath><g clip-path="url(#{cid})">'
    out += f'<rect x="{x}" y="{y}" width="{s}" height="{H}" fill="#FFFFFF"/>'
    out += avatar(k, x + 28, y + 26, 14)
    out += T(x + 52, y + 23, "primeegg", 13.5, IG_INK, UI, 700)
    out += T(x + 52, y + 39, "Madrid, España", 11.5, IG_GREY, UI)
    for i in range(3):
        out += f'<circle cx="{x+s-36+i*6}" cy="{y+26}" r="1.6" fill="{IG_INK}"/>'
    out += place(body, x, y + hh, s, k)
    fy = y + hh + s
    out += icon_heart(x + 14, fy + 12, 24) + icon_comment(x + 50, fy + 12, 24) + icon_send(x + 86, fy + 12, 24)
    out += icon_bookmark(x + s - 38, fy + 12, 24)
    out += T(x + 16, fy + 56, f"{likes} Me gusta", 13, IG_INK, UI, 700)
    cap = caption if len(caption) < 40 else caption[:38].rsplit(" ", 1)[0] + "…"
    out += (f'<text x="{x+16}" y="{fy+76}" font-family="{dw.ff(UI)}" font-size="12.5" fill="{IG_INK}">'
            f'<tspan font-weight="700">primeegg</tspan><tspan dx="5">{dw.escape(cap)}</tspan></text>')
    out += "</g>"
    return out, H


# ------------------------------------------------------------------ phone with profile
def mini_icon(kind, cx, cy, c):
    sw = 1.6
    if kind == "egg":
        return f'<path d="{dw.egg_path(cx, cy, 16, 21)}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
    if kind == "truck":
        return (f'<g fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round"><rect x="{cx-11}" y="{cy-7}" width="13" height="10" rx="1.5"/>'
                f'<path d="M{cx+2},{cy-4} h5 l4,4 v3 h-9"/><circle cx="{cx-6}" cy="{cy+5}" r="2.2" fill="#FFF"/><circle cx="{cx+6}" cy="{cy+5}" r="2.2" fill="#FFF"/></g>')
    if kind == "chef":
        return (f'<path d="M{cx-7},{cy+3} v-3 c-5,0 -6,-8 -1,-9 c1,-5 8,-6 9,-2 c2,-3 8,-2 8,3 c4,1 3,8 -1,8 v3 Z M{cx-7},{cy+3} h14 v5 h-14 Z" '
                f'fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" transform="translate(-1,-1)"/>')
    return (f'<g fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"><circle cx="{cx}" cy="{cy-2}" r="7"/>'
            f'<path d="M{cx-3},{cy-2} l2,2 l4,-4"/><path d="M{cx-4},{cy+4} l-2,6 l4,-1.5 l2,3 l1,-5 M{cx+4},{cy+4} l2,6 l-4,-1.5"/></g>')


def phone(k, X, Y, W, H, posts):
    out = f'<ellipse cx="{X+W/2:.1f}" cy="{Y+H+6:.1f}" rx="{W*0.46:.1f}" ry="10" fill="#2B2116" opacity="0.12"/>'
    out += shadow(X, Y, W, H, 46, n=8, spread=3, op=0.035, dy=12)
    out += f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="46" fill="#1B1C1F"/>'
    out += f'<rect x="{X+1.5}" y="{Y+1.5}" width="{W-3}" height="{H-3}" rx="44.5" fill="none" stroke="#4A4B50" stroke-width="1.5"/>'
    for yy, hh in ((120, 34), (168, 56)):
        out += f'<rect x="{X-2.5}" y="{Y+yy}" width="3" height="{hh}" rx="1.5" fill="#2A2B2F"/>'
    out += f'<rect x="{X+W-0.5}" y="{Y+150}" width="3" height="78" rx="1.5" fill="#2A2B2F"/>'
    sx, sy, sw, sh = X + 10, Y + 10, W - 20, H - 20
    cid = k.uid("ph")
    out += f'<clipPath id="{cid}"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="37"/></clipPath><g clip-path="url(#{cid})">'
    out += f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#FFFFFF"/>'
    out += T(sx + 34, sy + 26, "9:41", 13, "#111", UI, 700, "middle")
    out += f'<rect x="{sx+sw/2-46:.1f}" y="{sy+9}" width="92" height="25" rx="12.5" fill="#0B0B0C"/>'
    for i in range(4):
        out += f'<rect x="{sx+sw-74+i*4.5:.1f}" y="{sy+25-3-i*2}" width="3" height="{3+i*2}" rx="0.8" fill="#111"/>'
    out += f'<rect x="{sx+sw-46}" y="{sy+16}" width="20" height="10" rx="3" fill="none" stroke="#111" stroke-width="1.2"/><rect x="{sx+sw-44}" y="{sy+18}" width="14" height="6" rx="1.5" fill="#111"/>'
    # верхняя панель
    ty = sy + 64
    out += f'<rect x="{sx+16}" y="{ty-11}" width="9" height="8" rx="1.5" fill="{IG_INK}"/><path d="M{sx+17.5},{ty-11} v-2.5 a3,3 0 0 1 6,0 v2.5" fill="none" stroke="{IG_INK}" stroke-width="1.4"/>'
    out += T(sx + 31, ty - 2, "primeegg", 18, IG_INK, UI, 700)
    out += f'<path d="M{sx+118},{ty-9} l4,4 l4,-4" fill="none" stroke="{IG_INK}" stroke-width="1.6" stroke-linecap="round"/>'
    out += f'<rect x="{sx+sw-72}" y="{ty-17}" width="19" height="19" rx="5" fill="none" stroke="{IG_INK}" stroke-width="1.7"/><path d="M{sx+sw-62.5},{ty-12} v9 m-4.5,-4.5 h9" stroke="{IG_INK}" stroke-width="1.7" stroke-linecap="round"/>'
    for i in range(3):
        out += f'<rect x="{sx+sw-38}" y="{ty-15+i*6}" width="18" height="1.9" rx="1" fill="{IG_INK}"/>'
    # аватар + счётчики
    ay = sy + 108
    out += avatar(k, sx + 50, ay, 32)
    for i, (n, l) in enumerate((("248", "publicaciones"), ("5.312", "seguidores"), ("389", "seguidos"))):
        cx = sx + 124 + i * 60
        out += T(cx, ay - 1, n, 15, IG_INK, UI, 700, "middle")
        out += T(cx, ay + 15, l, 9.5, IG_INK, UI, 400, "middle")
    # био
    by = sy + 164
    out += T(sx + 16, by, "Primeegg Distribution", 13, IG_INK, UI, 700)
    out += T(sx + 16, by + 17, "Distribuidor de alimentos", 12, IG_GREY, UI)
    bio = [k.t("taglines.es", "Huevos frescos de granja"), "Huevos · Ovoproductos · HoReCa", "Pedidos: pedidos@primeegg.es"]
    for i, ln in enumerate(bio):
        ln = ln if len(ln) * 12 * 0.55 < sw - 32 else ln[:int((sw - 32) / 6.6)] + "…"
        out += T(sx + 16, by + 34 + i * 16, ln, 12, IG_INK, UI)
    out += f'<g fill="none" stroke="#00376B" stroke-width="1.5" stroke-linecap="round"><path d="M{sx+18},{by+84} l4,-4 m-2,-3 a2.6,2.6 0 0 1 3.7,0 a2.6,2.6 0 0 1 0,3.7 M{sx+20},{by+83} a2.6,2.6 0 0 1 -3.7,0 a2.6,2.6 0 0 1 0,-3.7"/></g>'
    out += T(sx + 30, by + 86, k.t("contacts.web", "primeegg.es"), 12, "#00376B", UI, 600)
    # кнопки
    yb = sy + 260
    bwid = (sw - 32 - 6 - 34) / 2
    fc = k.primary if contrast(k.primary, "#FFFFFF") >= 3 else k.ink
    out += f'<rect x="{sx+16}" y="{yb}" width="{bwid:.1f}" height="30" rx="8" fill="{fc}"/>'
    out += T(sx + 16 + bwid / 2, yb + 19.5, "Seguir", 13, k.on(fc), UI, 700, "middle")
    out += f'<rect x="{sx+19+bwid:.1f}" y="{yb}" width="{bwid:.1f}" height="30" rx="8" fill="#EFEFEF"/>'
    out += T(sx + 19 + bwid * 1.5, yb + 19.5, "Mensaje", 13, IG_INK, UI, 700, "middle")
    out += f'<rect x="{sx+sw-50}" y="{yb}" width="34" height="30" rx="8" fill="#EFEFEF"/>'
    out += (f'<g fill="none" stroke="{IG_INK}" stroke-width="1.5" stroke-linecap="round"><circle cx="{sx+sw-36}" cy="{yb+12}" r="3.5"/>'
            f'<path d="M{sx+sw-42},{yb+22} a6,5 0 0 1 12,0 M{sx+sw-27},{yb+10} v6 m-3,-3 h6"/></g>')
    # хайлайты
    hy = sy + 324
    hc = k.primary if contrast(k.primary, "#FFFFFF") >= 2 else k.ink
    for i, (kind, lab) in enumerate((("egg", "Granjas"), ("truck", "Pedidos"), ("chef", "HoReCa"), ("seal", "Calidad"))):
        cx = sx + 40 + i * 66
        out += f'<circle cx="{cx}" cy="{hy}" r="23" fill="none" stroke="{IG_LINE}" stroke-width="1.2"/>'
        out += f'<circle cx="{cx}" cy="{hy}" r="20" fill="{mix(k.primary, "#FFFFFF", 0.86)}"/>'
        out += mini_icon(kind, cx, hy, hc)
        out += T(cx, hy + 37, lab, 10.5, IG_INK, UI, 500, "middle")
    # вкладки
    gy = sy + 372
    out += f'<line x1="{sx}" y1="{gy+30}" x2="{sx+sw}" y2="{gy+30}" stroke="{IG_LINE}"/>'
    out += f'<rect x="{sx+sw/6-30:.1f}" y="{gy+29}" width="60" height="1.8" fill="{IG_INK}"/>'
    gx = sx + sw / 6
    for i in range(3):
        for j in range(3):
            out += f'<rect x="{gx-8+i*6:.1f}" y="{gy+7+j*6}" width="4.5" height="4.5" rx="0.8" fill="{IG_INK}"/>'
    out += f'<rect x="{sx+sw/2-9:.1f}" y="{gy+6}" width="18" height="17" rx="4" fill="none" stroke="{IG_GREY}" stroke-width="1.6"/><path d="M{sx+sw/2-2:.1f},{gy+11} v7 l6,-3.5 Z" fill="{IG_GREY}"/>'
    out += f'<rect x="{sx+sw*5/6-9:.1f}" y="{gy+6}" width="18" height="17" rx="4" fill="none" stroke="{IG_GREY}" stroke-width="1.6"/><circle cx="{sx+sw*5/6:.1f}" cy="{gy+13}" r="3" fill="none" stroke="{IG_GREY}" stroke-width="1.5"/>'
    # сетка
    cs = (sw - 2) / 3
    for n, body in enumerate(posts):
        i, j = n % 3, n // 3
        out += place(body, sx + i * (cs + 1), gy + 32 + j * (cs + 1), cs, k)
    # нижняя навигация
    ny = sy + sh - 52
    out += f'<rect x="{sx}" y="{ny}" width="{sw}" height="52" fill="#FFFFFF"/><line x1="{sx}" y1="{ny}" x2="{sx+sw}" y2="{ny}" stroke="{IG_LINE}"/>'
    for i in range(5):
        cx = sx + sw * (i + 0.5) / 5
        if i == 0:
            out += f'<path d="M{cx-9:.1f},{ny+25} L{cx:.1f},{ny+16} L{cx+9:.1f},{ny+25} V{ny+33} H{cx-9:.1f} Z" fill="none" stroke="{IG_INK}" stroke-width="1.8" stroke-linejoin="round"/>'
        elif i == 1:
            out += f'<circle cx="{cx-1:.1f}" cy="{ny+23}" r="7" fill="none" stroke="{IG_INK}" stroke-width="1.8"/><path d="M{cx+4:.1f},{ny+28} l5,5" stroke="{IG_INK}" stroke-width="1.8" stroke-linecap="round"/>'
        elif i == 2:
            out += f'<rect x="{cx-9:.1f}" y="{ny+15}" width="18" height="18" rx="5" fill="none" stroke="{IG_INK}" stroke-width="1.8"/><path d="M{cx:.1f},{ny+19} v10 m-5,-5 h10" stroke="{IG_INK}" stroke-width="1.8" stroke-linecap="round"/>'
        elif i == 3:
            out += f'<rect x="{cx-9:.1f}" y="{ny+15}" width="18" height="18" rx="5" fill="none" stroke="{IG_INK}" stroke-width="1.8"/><path d="M{cx-2.5:.1f},{ny+20} v8 l7,-4 Z" fill="{IG_INK}"/>'
        else:
            out += avatar(k, cx, ny + 24, 10, ring=False)
            out += f'<circle cx="{cx:.1f}" cy="{ny+24}" r="11.5" fill="none" stroke="{IG_INK}" stroke-width="1.4"/>'
    out += f'<rect x="{sx+sw/2-60:.1f}" y="{sy+sh-10}" width="120" height="4.5" rx="2.25" fill="#111" opacity="0.85"/>'
    out += "</g>"
    return out


def render(k, W=1680, H=700):
    grid = [post_headline(k, 0), post_pattern(k), post_product(k), post_eggs(k, k.light), post_headline(k, 1, k.dark),
            post_eggs(k, mix(k.primary, "#FFFFFF", 0.8)), post_headline(k, 2), post_product(k), post_pattern(k)]
    a, b, c = post_headline(k, 0), post_pattern(k), post_product(k)
    pw, ph = 300, 614
    s, gap = 340, 32
    total = pw + 70 + 3 * s + 2 * gap
    x0 = (W - total) / 2
    out = phone(k, x0, (H - ph) / 2 - 4, pw, ph, grid)
    hs = heads(k)
    data = [(a, "1.248", "Nuevo en el blog: " + hs[0].rstrip(".")),
            (b, "986", k.t("taglines.es", "Huevos frescos de granja")),
            (c, "2.031", "Pide tu oferta para hostelería")]
    cardH = 52 + s + 92
    for i, (body, likes, cap) in enumerate(data):
        x = x0 + pw + 70 + i * (s + gap)
        y = (H - cardH) / 2 - 4 + (-14 if i == 1 else 10)
        o, _ = post_card(k, x, y, s, body, likes, cap)
        out += o
    return out
