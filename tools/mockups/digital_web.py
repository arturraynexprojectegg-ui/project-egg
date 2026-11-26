"""Сайт: главная страница в окне браузера (desktop) + та же страница на телефоне."""
from html import escape
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import mix, contrast  # noqa: E402

TITLE = "Сайт"
CAPTION = "Главная страница primeegg.es: шапка с меню, hero в фирменном цвете с иллюстрацией и карточки продуктов — на десктопе и в мобильной версии."

GENERIC = {"serif", "sans-serif", "monospace", "Georgia", "Helvetica", "Arial"}
WIDTH = {"Oswald": 0.47, "DM Serif Display": 0.5, "Baloo 2": 0.53, "Josefin Sans": 0.54, "Montserrat": 0.63,
         "Manrope": 0.58, "Fraunces": 0.56, "Nunito": 0.55, "Fredoka": 0.55, "Cormorant Garamond": 0.46, "Inter": 0.56}
SHELL_W, SHELL_B = "#F4EEE3", "#D9A877"


def ff(s):
    return ", ".join(p if p in GENERIC else f"'{p}'" for p in (q.strip() for q in s.split(",")))


def fw(font):
    return WIDTH.get(font.split(",")[0].strip(), 0.58)


def T(x, y, s, size, fill, font, weight=400, anchor="start", ls=0, op=None):
    o = f' opacity="{op}"' if op is not None else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{ff(font)}" font-size="{size:.1f}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{l}{o}>{escape(str(s))}</text>')


def wrap(text, size, maxw, factor):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) * size * factor > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def fit(text, size, maxw, factor, max_lines, min_size):
    while size > min_size:
        ls = wrap(text, size, maxw, factor)
        if len(ls) <= max_lines:
            return size, ls
        size -= 1
    return size, wrap(text, size, maxw, factor)[:max_lines]


def shadow(x, y, w, h, r, n=7, spread=3.0, op=0.028, dy=10):
    out = ""
    for i in range(n, 0, -1):
        e = i * spread
        out += (f'<rect x="{x-e:.1f}" y="{y-e+dy:.1f}" width="{w+2*e:.1f}" height="{h+2*e:.1f}" rx="{r+e:.1f}" '
                f'fill="#2B2116" opacity="{op}"/>')
    return out


def egg_path(cx, cy, w, h):
    rx, t, b = w / 2, cy - h / 2, cy + h / 2
    return (f"M{cx:.1f},{t:.1f} C{cx+0.70*rx:.1f},{t:.1f} {cx+rx:.1f},{cy-0.15*h:.1f} {cx+rx:.1f},{cy+0.1*h:.1f} "
            f"C{cx+rx:.1f},{cy+0.37*h:.1f} {cx+0.56*rx:.1f},{b:.1f} {cx:.1f},{b:.1f} "
            f"C{cx-0.56*rx:.1f},{b:.1f} {cx-rx:.1f},{cy+0.37*h:.1f} {cx-rx:.1f},{cy+0.1*h:.1f} "
            f"C{cx-rx:.1f},{cy-0.15*h:.1f} {cx-0.70*rx:.1f},{t:.1f} {cx:.1f},{t:.1f} Z")


def egg(k, cx, cy, w, h, col):
    g = k.uid("eg")
    out = (f'<radialGradient id="{g}" cx="0.36" cy="0.3" r="0.8"><stop offset="0" stop-color="{mix(col, "#FFFFFF", 0.55)}"/>'
           f'<stop offset="0.55" stop-color="{col}"/><stop offset="1" stop-color="{mix(col, "#5A3D22", 0.28)}"/></radialGradient>')
    out += f'<path d="{egg_path(cx, cy, w, h)}" fill="url(#{g})"/>'
    out += (f'<ellipse cx="{cx-w*0.17:.1f}" cy="{cy-h*0.2:.1f}" rx="{w*0.1:.1f}" ry="{h*0.13:.1f}" fill="#FFFFFF" opacity="0.45" '
            f'transform="rotate(-18 {cx-w*0.17:.1f} {cy-h*0.2:.1f})"/>')
    return out


def eggs_group(k, cx, by, s=1.0, bg=None):
    """Три яйца, стоящие на линии by, центр cx; s — масштаб (1 ≈ 150 px высотой)."""
    out = f'<ellipse cx="{cx:.1f}" cy="{by+2*s:.1f}" rx="{120*s:.1f}" ry="{11*s:.1f}" fill="#2B2116" opacity="0.18"/>'
    for dx, w, h, c in ((-58, 78, 104, SHELL_W), (52, 82, 110, SHELL_W), (-4, 96, 132, SHELL_B)):
        out += f'<ellipse cx="{cx+dx*s:.1f}" cy="{by:.1f}" rx="{w*0.36*s:.1f}" ry="{5*s:.1f}" fill="#2B2116" opacity="0.22"/>'
        out += egg(k, cx + dx * s, by - h * s / 2, w * s, h * s, c)
    return out


def tray_top(k, x, y, w, h, n=3, m=3):
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w*0.08:.1f}" fill="#D9D3C7"/>'
    out += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{w*0.08:.1f}" fill="none" stroke="#BDB5A6" stroke-width="1"/>'
    cw, ch = w / n, h / m
    for j in range(m):
        for i in range(n):
            ccx, ccy = x + cw * (i + 0.5), y + ch * (j + 0.5)
            r = min(cw, ch) * 0.42
            out += f'<circle cx="{ccx:.1f}" cy="{ccy:.1f}" r="{r:.1f}" fill="#C7BFAF"/>'
            col = SHELL_B if (i + j) % 3 == 1 else SHELL_W
            g = k.uid("te")
            out += (f'<radialGradient id="{g}" cx="0.38" cy="0.34" r="0.7"><stop offset="0" stop-color="{mix(col, "#FFFFFF", 0.6)}"/>'
                    f'<stop offset="1" stop-color="{mix(col, "#5A3D22", 0.15)}"/></radialGradient>')
            out += f'<ellipse cx="{ccx+r*0.06:.1f}" cy="{ccy+r*0.06:.1f}" rx="{r*0.86:.1f}" ry="{r*0.8:.1f}" fill="url(#{g})"/>'
    return out


def sack(k, cx, by, s=1.0):
    w, h = 74 * s, 92 * s
    x, y = cx - w / 2, by - h
    kraft = "#C9A57A"
    d = (f"M{x+6*s:.1f},{y+14*s:.1f} L{x+w-6*s:.1f},{y+14*s:.1f} L{x+w:.1f},{by-8*s:.1f} Q{x+w:.1f},{by:.1f} {x+w-8*s:.1f},{by:.1f} "
         f"L{x+8*s:.1f},{by:.1f} Q{x:.1f},{by:.1f} {x:.1f},{by-8*s:.1f} Z")
    out = f'<ellipse cx="{cx:.1f}" cy="{by+1:.1f}" rx="{w*0.62:.1f}" ry="{5*s:.1f}" fill="#2B2116" opacity="0.2"/>'
    out += f'<path d="{d}" fill="{kraft}"/>'
    out += f'<path d="M{x+w*0.62:.1f},{y+14*s:.1f} L{x+w-6*s:.1f},{y+14*s:.1f} L{x+w:.1f},{by-8*s:.1f} Q{x+w:.1f},{by:.1f} {x+w-8*s:.1f},{by:.1f} L{x+w*0.7:.1f},{by:.1f} Z" fill="#000" opacity="0.08"/>'
    out += f'<rect x="{x+4*s:.1f}" y="{y:.1f}" width="{w-8*s:.1f}" height="{16*s:.1f}" rx="{2*s:.1f}" fill="{mix(kraft, "#000000", 0.1)}"/>'
    for i in range(1, 8):
        xx = x + 4 * s + (w - 8 * s) * i / 8
        out += f'<line x1="{xx:.1f}" y1="{y+2*s:.1f}" x2="{xx:.1f}" y2="{y+14*s:.1f}" stroke="#8C6E4C" stroke-width="{0.8*s:.2f}" opacity="0.6"/>'
    lw, lh = w * 0.66, h * 0.42
    lx, ly = cx - lw / 2, y + 30 * s
    out += f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="{3*s:.1f}" fill="{k.primary}"/>'
    out += k.logo("mark", lx + lw * 0.2, ly + 4 * s, lw * 0.6, lh - 8 * s, color=k.on(k.primary))
    return out


def link_col(k):
    return k.primary if contrast(k.primary, "#FFFFFF") >= 3 else k.ink


def btn_fill(k, bg):
    return k.accent if contrast(k.accent, bg) >= 1.7 else k.on(bg)


def deco(k, x, y, w, h, bg, scale=1.0, rx=0):
    """Паттерн, а без него — мягкие дуги-«желтки» как запасной декор."""
    oc = k.on(bg)
    if k.pattern_src:
        return k.pattern_rect(x, y, w, h, scale=scale, opacity=0.14, color=oc, clip_rx=rx)
    cid = k.uid("dc")
    out = f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}"/></clipPath><g clip-path="url(#{cid})" opacity="0.10">'
    cx, cy = x + w * 0.74, y + h * 0.55
    for i in range(1, 9):
        out += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{i*h*0.16:.1f}" fill="none" stroke="{oc}" stroke-width="{1.4*scale:.2f}"/>'
    return out + "</g>"


def texts(k):
    nav = k.t("web.nav", ["Productos", "HoReCa", "Distribución", "Nosotros", "Contacto"])
    return dict(
        nav=nav if isinstance(nav, list) else ["Productos", "HoReCa", "Distribución", "Nosotros", "Contacto"],
        title=k.t("web.hero_title", "Huevos de granja, directos a tu cocina"),
        text=k.t("web.hero_text", "Distribuimos huevos frescos y ovoproductos a hostelería, tiendas e industria en toda España."),
        cta=k.t("web.cta", "Pedir oferta"),
        cards=[(k.t("products.carton.title", "Huevos frescos"), k.t("products.carton.subtitle", "Categoría A · Talla L")),
               (k.t("products.horeca.title", "Huevos para hostelería"), k.t("products.horeca.subtitle", "Bandeja 30 uds · Talla M-L")),
               (k.t("products.powder.title", "Huevo entero en polvo"), k.t("products.powder.subtitle", "Ovoproducto pasteurizado"))])


def card_illus(k, i, x, y, s):
    """Иллюстрация карточки продукта в квадрате s×s."""
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" rx="{s*0.1:.1f}" fill="{mix(k.primary, "#FFFFFF", 0.86)}"/>'
    cx = x + s / 2
    if i == 0:
        out += eggs_group(k, cx, y + s * 0.8, s / 300)
    elif i == 1:
        out += f'<ellipse cx="{cx:.1f}" cy="{y+s*0.82:.1f}" rx="{s*0.36:.1f}" ry="{s*0.04:.1f}" fill="#2B2116" opacity="0.15"/>'
        out += tray_top(k, x + s * 0.17, y + s * 0.17, s * 0.66, s * 0.62)
    else:
        out += sack(k, cx, y + s * 0.84, s / 132)
    return out


# ----------------------------------------------------------------- desktop
def desktop(k, X, Y, W, H, tx):
    out = shadow(X, Y, W, H, 12, n=8, spread=3.5, op=0.03, dy=14)
    cid = k.uid("bw")
    out += f'<clipPath id="{cid}"><rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="12"/></clipPath>'
    out += f'<g clip-path="url(#{cid})"><rect x="{X}" y="{Y}" width="{W}" height="{H}" fill="#FFFFFF"/>'
    # браузерная рамка
    out += f'<rect x="{X}" y="{Y}" width="{W}" height="44" fill="#EDEBE7"/><line x1="{X}" y1="{Y+44}" x2="{X+W}" y2="{Y+44}" stroke="#D8D5CF"/>'
    for i, c in enumerate(("#EE6A5F", "#F5BE4F", "#62C554")):
        out += f'<circle cx="{X+22+i*20}" cy="{Y+22}" r="6" fill="{c}"/>'
    out += f'<rect x="{X+100}" y="{Y+9}" width="210" height="35" rx="8" fill="#FFFFFF"/>'
    out += k.logo("mark", X + 112, Y + 18, 16, 16)
    out += T(X + 136, Y + 31, "Primeegg — Inicio", 12.5, "#3A3A3A", "Inter, sans-serif", 500)
    out += T(X + 296, Y + 31, "×", 13, "#9A9A9A", "Inter, sans-serif", 400, "end")
    ux = X + 340
    out += f'<rect x="{ux}" y="{Y+10}" width="{W-460}" height="24" rx="12" fill="#FFFFFF" stroke="#DAD7D1"/>'
    out += f'<rect x="{ux+14}" y="{Y+19}" width="8" height="7" rx="1.5" fill="#8A8A8A"/><path d="M{ux+15.5},{Y+19} v-2 a2.5,2.5 0 0 1 5,0 v2" fill="none" stroke="#8A8A8A" stroke-width="1.4"/>'
    out += T(ux + 30, Y + 26.5, "primeegg.es", 12.5, "#3A3A3A", "Inter, sans-serif")
    out += f'<circle cx="{X+W-34}" cy="{Y+22}" r="9" fill="{mix(k.primary, "#FFFFFF", 0.6)}"/>'
    for i in range(3):
        out += f'<rect x="{X+W-84}" y="{Y+16+i*5}" width="14" height="1.8" rx="0.9" fill="#7A7A7A"/>'

    cy0 = Y + 44
    # шапка сайта
    hh = 68
    out += k.logo("horizontal", X + 44, cy0 + 12, 190, hh - 24, align="left")
    lc = link_col(k)
    bt = "Área cliente"
    bw = len(bt) * 13 * 0.6 + 34
    bx = X + W - 44 - bw
    out += f'<rect x="{bx:.1f}" y="{cy0+hh/2-17:.1f}" width="{bw:.1f}" height="34" rx="17" fill="none" stroke="{lc}" stroke-width="1.5"/>'
    out += T(bx + bw / 2, cy0 + hh / 2 + 4.5, bt, 13, lc, k.text_font, 600, "middle")
    nx = bx - 36
    f = fw(k.text_font)
    for i, item in enumerate(reversed(tx["nav"])):
        out += T(nx, cy0 + hh / 2 + 5, item, 14, k.ink, k.text_font, 600 if i == len(tx["nav"]) - 1 else 500, "end")
        if i == len(tx["nav"]) - 1:
            iw = len(item) * 14 * f
            out += f'<rect x="{nx-iw:.1f}" y="{cy0+hh/2+13:.1f}" width="{iw:.1f}" height="2.5" rx="1.2" fill="{k.accent if contrast(k.accent, "#FFFFFF") > 1.6 else k.primary}"/>'
        nx -= len(item) * 14 * f + 30
    out += f'<line x1="{X}" y1="{cy0+hh}" x2="{X+W}" y2="{cy0+hh}" stroke="#ECE9E3"/>'

    # hero
    hy, hhgt = cy0 + hh, 306
    bg = k.brand_bg
    oc = k.on(bg)
    out += f'<rect x="{X}" y="{hy}" width="{W}" height="{hhgt}" fill="{bg}"/>'
    out += deco(k, X, hy, W, hhgt, bg)
    tx0 = X + 68
    eb = "DISTRIBUCIÓN · HUEVOS Y OVOPRODUCTOS"
    ebc = k.accent if contrast(k.accent, bg) >= 2.2 else oc
    hf = fw(k.head_font)
    size, lines = fit(tx["title"], 44, 560, hf, 2, 32)
    tl = wrap(tx["text"], 15.5, 500, fw(k.text_font))[:3]
    block = 16 + 24 + len(lines) * size * 1.08 + 14 + len(tl) * 23 + 22 + 46
    top = hy + (hhgt - block) / 2
    out += f'<rect x="{tx0}" y="{top+5:.1f}" width="22" height="2.5" fill="{ebc}"/>'
    out += T(tx0 + 32, top + 10, eb, 11.5, ebc, k.text_font, 700, ls=2)
    ty = top + 40 + size * 0.82
    for i, ln in enumerate(lines):
        out += T(tx0, ty + i * size * 1.08, ln, size, oc, k.head_font, 700)
    ty += (len(lines) - 1) * size * 1.08 + size * 0.26 + 14 + 17
    for i, ln in enumerate(tl):
        out += T(tx0, ty + i * 23, ln, 15.5, oc, k.text_font, 400, op=0.86)
    by = ty + (len(tl) - 1) * 23 + 7 + 22
    bfill = btn_fill(k, bg)
    cw = len(tx["cta"]) * 15 * 0.6 + 56
    out += f'<rect x="{tx0}" y="{by}" width="{cw:.1f}" height="46" rx="23" fill="{bfill}"/>'
    out += T(tx0 + cw / 2 - 8, by + 28.5, tx["cta"], 15, k.on(bfill), k.text_font, 700, "middle")
    out += f'<path d="M{tx0+cw-30:.1f},{by+23} h12 m-5,-5 l5,5 l-5,5" fill="none" stroke="{k.on(bfill)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    out += T(tx0 + cw + 28, by + 28.5, "Ver catálogo", 15, oc, k.text_font, 600)
    out += f'<line x1="{tx0+cw+28}" y1="{by+33}" x2="{tx0+cw+28+12*15*fw(k.text_font)*0.98:.1f}" y2="{by+33}" stroke="{oc}" stroke-width="1.2" opacity="0.6"/>'
    # иллюстрация
    icx, icy = X + W * 0.74, hy + hhgt * 0.52
    out += f'<circle cx="{icx:.1f}" cy="{icy:.1f}" r="128" fill="{oc}" opacity="0.10"/>'
    out += f'<circle cx="{icx:.1f}" cy="{icy:.1f}" r="94" fill="{oc}" opacity="0.10"/>'
    out += eggs_group(k, icx, icy + 82, 1.18)
    # плашка
    px, py = X + W - 250, hy + 40
    out += shadow(px, py, 178, 58, 12, n=4, spread=2, op=0.05, dy=5)
    out += f'<rect x="{px}" y="{py}" width="178" height="58" rx="12" fill="#FFFFFF"/>'
    out += f'<circle cx="{px+29}" cy="{py+29}" r="17" fill="{mix(k.primary, "#FFFFFF", 0.85)}"/>'
    out += (f'<g fill="none" stroke="{lc}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="{px+18}" y="{py+22}" width="13" height="10" rx="1.5"/><path d="M{px+31},{py+25} h5 l3.5,3.5 v3.5 h-8.5"/>'
            f'<circle cx="{px+22.5}" cy="{py+34}" r="2" fill="#FFFFFF"/><circle cx="{px+35}" cy="{py+34}" r="2" fill="#FFFFFF"/></g>')
    out += T(px + 54, py + 26, "Entrega 24/48 h", 13.5, k.ink, k.text_font, 700)
    out += T(px + 54, py + 43, "Cadena de frío", 12, k.ink, k.text_font, 400, op=0.6)

    # карточки
    sy = hy + hhgt
    out += f'<rect x="{X}" y="{sy}" width="{W}" height="{H-(sy-Y)}" fill="{mix(k.light, "#FFFFFF", 0.4)}"/>'
    out += T(tx0, sy + 44, "Nuestros productos", 22, k.ink, k.head_font, 700)
    out += T(X + W - 68, sy + 43, "Ver todos  →", 14, lc, k.text_font, 600, "end")
    gap = 24
    cwid = (W - 136 - 2 * gap) / 3
    for i, (t1, t2) in enumerate(tx["cards"]):
        cx = tx0 + i * (cwid + gap)
        cyy = sy + 66
        ch = 132
        out += shadow(cx, cyy, cwid, ch, 14, n=3, spread=2, op=0.03, dy=4)
        out += f'<rect x="{cx:.1f}" y="{cyy}" width="{cwid:.1f}" height="{ch}" rx="14" fill="#FFFFFF" stroke="#EAE6DE"/>'
        out += card_illus(k, i, cx + 12, cyy + 12, ch - 24)
        tx1 = cx + ch + 6
        tw = cwid - ch - 18
        s1, l1 = fit(t1, 17, tw, hf, 2, 14)
        yy = cyy + 34
        for j, ln in enumerate(l1):
            out += T(tx1, yy + j * s1 * 1.18, ln, s1, k.ink, k.head_font, 700)
        yy += (len(l1) - 1) * s1 * 1.18 + 22
        s2, l2 = fit(t2, 12.5, tw, fw(k.text_font), 2 if len(l1) == 1 else 1, 10.5)
        for j, ln in enumerate(l2):
            out += T(tx1, yy + j * 17, ln, s2, k.ink, k.text_font, 400, op=0.65)
        out += T(tx1, cyy + ch - 20, "Ver más  →", 13, lc, k.text_font, 700)
    out += "</g>"
    out += f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="12" fill="none" stroke="#000" stroke-opacity="0.08"/>'
    return out


# ----------------------------------------------------------------- mobile
def mobile(k, X, Y, W, H, tx):
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
    # статус-бар
    out += T(sx + 34, sy + 26, "9:41", 13, "#111", "Inter, sans-serif", 700, "middle")
    out += f'<rect x="{sx+sw/2-46:.1f}" y="{sy+9}" width="92" height="25" rx="12.5" fill="#0B0B0C"/>'
    for i in range(4):
        out += f'<rect x="{sx+sw-74+i*4.5:.1f}" y="{sy+25-3-i*2}" width="3" height="{3+i*2}" rx="0.8" fill="#111"/>'
    out += f'<rect x="{sx+sw-46}" y="{sy+16}" width="20" height="10" rx="3" fill="none" stroke="#111" stroke-width="1.2"/><rect x="{sx+sw-44}" y="{sy+18}" width="14" height="6" rx="1.5" fill="#111"/>'
    # шапка
    hy = sy + 44
    out += k.logo("horizontal", sx + 16, hy + 8, 128, 34, align="left")
    for i in range(3):
        out += f'<rect x="{sx+sw-38}" y="{hy+17+i*7}" width="20" height="2.2" rx="1.1" fill="{k.ink}"/>'
    # hero
    ry, rh = hy + 52, 352
    bg = k.brand_bg
    oc = k.on(bg)
    out += f'<rect x="{sx}" y="{ry}" width="{sw}" height="{rh}" fill="{bg}"/>'
    out += deco(k, sx, ry, sw, rh, bg, scale=0.6)
    icx = sx + sw / 2
    out += f'<circle cx="{icx:.1f}" cy="{ry+76:.1f}" r="58" fill="{oc}" opacity="0.10"/>'
    out += eggs_group(k, icx, ry + 118, 0.56)
    tx0 = sx + 20
    hf = fw(k.head_font)
    size, lines = fit(tx["title"], 26, sw - 40, hf, 3, 19)
    bfill = btn_fill(k, bg)
    by = ry + rh - 60
    ty = ry + 146 + size * 0.85
    for i, ln in enumerate(lines):
        out += T(tx0, ty + i * size * 1.1, ln, size, oc, k.head_font, 700)
    ty += (len(lines) - 1) * size * 1.1 + 24
    nl = max(1, int((by - 10 - ty) // 17) + 1)
    tl = wrap(tx["text"], 12, sw - 40, fw(k.text_font))
    if len(tl) > nl:
        tl = tl[:nl]; tl[-1] = tl[-1].rstrip(",.;") + "…"
    for i, ln in enumerate(tl):
        out += T(tx0, ty + i * 17, ln, 12, oc, k.text_font, 400, op=0.86)
    out += f'<rect x="{tx0}" y="{by}" width="{sw-40}" height="42" rx="21" fill="{bfill}"/>'
    out += T(icx, by + 26, tx["cta"] + "  →", 14, k.on(bfill), k.text_font, 700, "middle")
    # продукты
    py = ry + rh
    out += f'<rect x="{sx}" y="{py}" width="{sw}" height="{sh}" fill="{mix(k.light, "#FFFFFF", 0.4)}"/>'
    out += T(tx0, py + 34, "Nuestros productos", 17, k.ink, k.head_font, 700)
    lc = link_col(k)
    for i, (t1, t2) in enumerate(tx["cards"][:2]):
        cy = py + 50 + i * 96
        out += f'<rect x="{tx0}" y="{cy}" width="{sw-40}" height="84" rx="12" fill="#FFFFFF" stroke="#EAE6DE"/>'
        out += card_illus(k, i, tx0 + 8, cy + 8, 68)
        s1, l1 = fit(t1, 13.5, sw - 40 - 96, hf, 1, 11)
        if len(wrap(t1, s1, sw - 136, hf)) > 1:
            l1 = wrap(t1, 13, sw - 136, hf)[:2]; s1 = 13
        yy = cy + (26 if len(l1) > 1 else 32)
        for j, ln in enumerate(l1):
            out += T(tx0 + 86, yy + j * 15, ln, s1, k.ink, k.head_font, 700)
        yy += (len(l1) - 1) * 15 + 17
        s2, l2 = fit(t2, 11, sw - 136, fw(k.text_font), 1, 9)
        out += T(tx0 + 86, yy, l2[0], s2, k.ink, k.text_font, 400, op=0.65)
        out += T(tx0 + 86, cy + 72, "Ver más →", 11, lc, k.text_font, 700)
    out += f'<rect x="{sx+sw/2-60:.1f}" y="{sy+sh-12}" width="120" height="4.5" rx="2.25" fill="#111" opacity="0.85"/>'
    out += "</g>"
    return out


def render(k, W=1680, H=700):
    tx = texts(k)
    bw, bh = 1170, 632
    pw, ph = 300, 614
    ov = 34
    total = bw + pw - ov
    bx = (W - total) / 2
    by = (H - bh) / 2 - 6
    out = desktop(k, bx, by, bw, bh, tx)
    out += mobile(k, bx + bw - ov, by + 26, pw, ph, tx)
    return out
