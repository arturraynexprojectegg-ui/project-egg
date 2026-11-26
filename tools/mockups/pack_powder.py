"""Яичный порошок: крафт-мешок 25 кг и розничный дой-пак 500 г."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import lum, mix  # noqa: E402

TITLE = "Яичный порошок"
CAPTION = ("Крафт-мешок 25 кг с прошитым верхом и одноцветной печатью спецификации "
           "и розничный дой-пак 500 г с окном в форме яйца.")

KRAFT = "#C9A57A"
POWDER = "#EBC35A"
SHELL_B = "#D9A877"
SHELL_W = "#F4EEE3"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fit(text, size, maxw, k=0.56):
    w = len(str(text)) * size * k
    return size if w <= maxw else max(7.0, size * maxw / w)


def _txt(x, y, s, size, fill, font, weight=400, anchor="start", ls=0, op=None, maxw=None, k=0.56):
    if maxw:
        size = _fit(s, size, maxw, k + ls / max(size, 1))
    o = f' opacity="{op}"' if op is not None else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{l}{o}>{_esc(s)}</text>')


def _lines(text, maxlen=14):
    w = text.split()
    if len(text) <= maxlen or len(w) == 1:
        return [text]
    best = None
    for i in range(1, len(w)):
        a, b = " ".join(w[:i]), " ".join(w[i:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]:
            best = (sc, [a, b])
    return best[1]


def _subtitle(k):
    """Подзаголовок без указания фасовки (вес задаётся самой упаковкой)."""
    sub = k.t("products.powder.subtitle", "Ovoproducto pasteurizado")
    parts = [p for p in sub.split(" · ") if not any(w in p.lower() for w in ("kg", " g", "saco", "bolsa"))]
    return " · ".join(parts) or "Ovoproducto pasteurizado"


def _shadow(defs, k, cx, cy, rx, ry, op=0.28):
    gid = k.uid("sh")
    defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="#2A2622" stop-opacity="{op}"/>'
                f'<stop offset="0.6" stop-color="#2A2622" stop-opacity="{op * 0.45:.3f}"/>'
                f'<stop offset="1" stop-color="#2A2622" stop-opacity="0"/></radialGradient>')
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{gid})"/>'


def _barcode(x, y, w, h, color, seed=11):
    out, n, xx, v, i = [], 95, x, seed, 0
    unit = w / n
    while i < n:
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        guard = i < 3 or i > n - 4 or 45 <= i <= 49
        bw = 1 if guard else 1 + (v >> 8) % 3
        if i % 2 == 0:
            out.append(f'<rect x="{xx:.2f}" y="{y:.1f}" width="{bw * unit:.2f}" height="{h + (5 if guard else 0):.1f}" fill="{color}"/>')
        xx += bw * unit
        i += bw
    return "".join(out)


def _ink(k):
    for c in (k.dark, k.ink, k.primary):
        if lum(c) < 0.08:
            return c
    return "#1C1B19"


def _egg_d(cx, cy, w, h):
    t, b, m = cy - h / 2, cy + h / 2, cy + 0.08 * h
    l, r = cx - w / 2, cx + w / 2
    return (f"M{cx:.1f},{t:.1f} C{cx + .28 * w:.1f},{t:.1f} {r:.1f},{cy - .22 * h:.1f} {r:.1f},{m:.1f} "
            f"C{r:.1f},{cy + .36 * h:.1f} {cx + .27 * w:.1f},{b:.1f} {cx:.1f},{b:.1f} "
            f"C{cx - .27 * w:.1f},{b:.1f} {l:.1f},{cy + .36 * h:.1f} {l:.1f},{m:.1f} "
            f"C{l:.1f},{cy - .22 * h:.1f} {cx - .28 * w:.1f},{t:.1f} {cx:.1f},{t:.1f} Z")


def _speckles(x, y, w, h, n, color, seed=3, op=0.35):
    out, v = [], seed
    for _ in range(n):
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        px = x + (v % 1000) / 1000 * w
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        py = y + (v % 1000) / 1000 * h
        r = 0.8 + (v >> 12) % 3 * 0.5
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>')
    return f'<g fill="{color}" opacity="{op}">{"".join(out)}</g>'


# ------------------------------------------------------------------ крафт-мешок 25 кг
def _sack(k, defs, x, yb, W=410, H=580):
    out = []
    ink = _ink(k)
    y = yb - H
    out.append(_shadow(defs, k, x + W / 2 + 24, yb - 2, W * .66, 30, .34))
    # контур мешка: слегка «подушкой», низ со складкой
    b = 10
    d = (f"M{x + 6:.1f},{y + 30:.1f} L{x + W - 6:.1f},{y + 30:.1f} "
         f"Q{x + W + b:.1f},{y + H * .5:.1f} {x + W:.1f},{yb - 26:.1f} "
         f"Q{x + W - 2:.1f},{yb:.1f} {x + W - 30:.1f},{yb:.1f} L{x + 30:.1f},{yb:.1f} "
         f"Q{x + 2:.1f},{yb:.1f} {x:.1f},{yb - 26:.1f} Q{x - b:.1f},{y + H * .5:.1f} {x + 6:.1f},{y + 30:.1f} Z")
    gx = k.uid("kx")
    defs.append(f'<linearGradient id="{gx}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="{mix(KRAFT, "#5E4128", .22)}"/>'
                f'<stop offset="0.12" stop-color="{mix(KRAFT, "#FFFFFF", .06)}"/>'
                f'<stop offset="0.45" stop-color="{mix(KRAFT, "#FFFFFF", .12)}"/>'
                f'<stop offset="0.88" stop-color="{KRAFT}"/>'
                f'<stop offset="1" stop-color="{mix(KRAFT, "#5E4128", .26)}"/></linearGradient>')
    cid = k.uid("sk")
    defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    out.append(f'<path d="{d}" fill="url(#{gx})"/>')
    g = [f'<g clip-path="url(#{cid})">']
    g.append(_speckles(x, y + 30, W, H - 30, 260, "#7A5A36", 5, .25))
    # складки боковых фальцев
    for xx, o in ((x + 26, .10), (x + W - 26, .12)):
        g.append(f'<line x1="{xx:.1f}" y1="{y + 40:.1f}" x2="{xx:.1f}" y2="{yb - 30:.1f}" stroke="#5E4128" stroke-opacity="{o}" stroke-width="2"/>')
    # нижняя складка дна
    g.append(f'<path d="M{x:.1f},{yb - 44:.1f} Q{x + W / 2:.1f},{yb - 30:.1f} {x + W:.1f},{yb - 44:.1f}" fill="none" '
             f'stroke="#5E4128" stroke-opacity="0.16" stroke-width="2"/>')
    g.append(f'<rect x="{x:.1f}" y="{yb - 44:.1f}" width="{W:.1f}" height="44" fill="#5E4128" opacity="0.06"/>')

    # ----- печать (одна краска)
    cx = x + W / 2
    py = y + 56
    g.append(k.logo("mono", x + 80, py, W - 160, 116, color=ink))
    py += 124
    title = k.t("products.powder.title", "Huevo entero en polvo")
    ls = _lines(title, 16)
    fs = min(_fit(l, 30, W - 70, .55) for l in ls)
    for l in ls:
        py += fs * 1.02
        g.append(_txt(cx, py, l.upper() if len(l) < 18 else l, fs, ink, k.head_font, 700, "middle"))
    py += 22
    g.append(_txt(cx, py, _subtitle(k), 13.5, ink, k.text_font, 600,
                  "middle", 1.2, maxw=W - 80))
    # таблица спецификации
    py += 16
    tx, tw = x + 46, W - 92
    rows = [("Proteína", "≥ 45 %"), ("Grasa", "≥ 40 %"), ("Humedad", "≤ 5 %"), ("pH", "8,5 – 9,5"),
            ("Salmonella", "Ausencia / 25 g"), ("Origen", "España")]
    rh = 19
    g.append(f'<rect x="{tx:.1f}" y="{py:.1f}" width="{tw:.1f}" height="{rh * (len(rows) + 1) + 6:.1f}" fill="none" '
             f'stroke="{ink}" stroke-width="1.6"/>')
    g.append(f'<rect x="{tx:.1f}" y="{py:.1f}" width="{tw:.1f}" height="{rh + 2:.1f}" fill="{ink}"/>')
    g.append(_txt(tx + 10, py + 14.5, "ESPECIFICACIÓN", 10.5, KRAFT, k.text_font, 700, ls=1.5))
    g.append(_txt(tx + tw - 10, py + 14.5, "por 100 g", 10, KRAFT, k.text_font, 500, "end"))
    for i, (a, b2) in enumerate(rows):
        yy = py + rh * (i + 1) + 17
        if i:
            g.append(f'<line x1="{tx + 8:.1f}" y1="{yy - 14:.1f}" x2="{tx + tw - 8:.1f}" y2="{yy - 14:.1f}" stroke="{ink}" stroke-opacity="0.35"/>')
        g.append(_txt(tx + 10, yy, a, 11, ink, k.text_font, 500))
        g.append(_txt(tx + tw - 10, yy, b2, 11, ink, k.text_font, 700, "end"))
    py += rh * (len(rows) + 1) + 6
    # вес
    py += 52
    g.append(f'<text x="{x + 46:.1f}" y="{py:.1f}" font-family="{k.head_font}" font-size="44" font-weight="800" fill="{ink}">'
             f'25 kg<tspan font-size="19" font-weight="700" dx="6">neto</tspan></text>')
    g.append(_txt(x + 48, py + 25, "PESO NETO · NET WEIGHT", 9.5, ink, k.text_font, 700, ls=1.4, op=0.85))
    g.append(_barcode(x + W - 46 - 120, py - 38, 120, 32, ink))
    g.append(_txt(x + W - 46, py + 12, "8 437000 280013", 9.5, ink, "Courier New, monospace", 700, "end"))
    g.append(_txt(cx, yb - 22, "Lote 2611-P · Cons. pref. 11/2027 · Conservar en lugar fresco y seco", 9.5, ink,
                  k.text_font, 500, "middle", op=0.85, maxw=W - 70))
    g.append("</g>")
    out += g
    # прошитый верх: сложенный край и креп-лента со строчкой
    top = (f"M{x + 4:.1f},{y + 34:.1f} L{x + 2:.1f},{y + 8:.1f} ")
    n = 26
    for i in range(n + 1):
        xx = x + 2 + (W - 4) * i / n
        top += f"L{xx:.1f},{y + (4 if i % 2 else 9):.1f} "
    top += f"L{x + W - 2:.1f},{y + 8:.1f} L{x + W - 4:.1f},{y + 34:.1f} Z"
    out.append(f'<path d="{top}" fill="{mix(KRAFT, "#5E4128", .12)}"/>')
    out.append(f'<rect x="{x + 2:.1f}" y="{y + 12:.1f}" width="{W - 4:.1f}" height="24" fill="{mix(KRAFT, "#FFFFFF", .22)}"/>')
    for i in range(0, int(W - 4), 5):
        out.append(f'<line x1="{x + 2 + i:.1f}" y1="{y + 12:.1f}" x2="{x + 2 + i:.1f}" y2="{y + 36:.1f}" stroke="#8A6A44" stroke-opacity="0.10"/>')
    out.append(f'<line x1="{x + 8:.1f}" y1="{y + 24:.1f}" x2="{x + W - 8:.1f}" y2="{y + 24:.1f}" stroke="#4A3A26" '
               f'stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(f'<rect x="{x + 2:.1f}" y="{y + 36:.1f}" width="{W - 4:.1f}" height="5" fill="#3A2A18" opacity="0.12"/>')
    return "".join(out)


# ------------------------------------------------------------------ дой-пак 500 г
def _doypack(k, defs, x, yb, W=268, H=440):
    out = []
    y = yb - H
    out.append(_shadow(defs, k, x + W / 2 + 18, yb - 4, W * .66, 22, .34))
    r = 5
    sl = y + 56          # конец плоского верхнего шва, ниже — наполненный объём
    d = (f"M{x + r:.1f},{y:.1f} L{x + W - r:.1f},{y:.1f} Q{x + W:.1f},{y:.1f} {x + W:.1f},{y + r:.1f} "
         f"L{x + W:.1f},{sl:.1f} C{x + W + 10:.1f},{sl + 80:.1f} {x + W + 10:.1f},{yb - 120:.1f} {x + W + 8:.1f},{yb - 34:.1f} "
         f"Q{x + W + 8:.1f},{yb - 2:.1f} {x + W - 22:.1f},{yb:.1f} "
         f"Q{x + W / 2:.1f},{yb + 8:.1f} {x + 22:.1f},{yb:.1f} Q{x - 8:.1f},{yb - 2:.1f} {x - 8:.1f},{yb - 34:.1f} "
         f"C{x - 10:.1f},{yb - 120:.1f} {x - 10:.1f},{sl + 80:.1f} {x:.1f},{sl:.1f} "
         f"L{x:.1f},{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} Z")
    cid = k.uid("dp")
    defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    split = y + H * .60
    band = k.brand_bg
    on = k.on(band)
    g = [f'<g clip-path="url(#{cid})">']
    g.append(f'<rect x="{x - 10:.1f}" y="{y:.1f}" width="{W + 20:.1f}" height="{H + 10:.1f}" fill="{k.light}"/>')
    g.append(k.pattern_rect(x - 10, y, W + 20, split - y, scale=0.45, opacity=0.08, color=k.primary))
    # нижняя фирменная часть с мягкой волной
    g.append(f'<path d="M{x - 10:.1f},{split:.1f} Q{x + W * .3:.1f},{split - 22:.1f} {x + W * .55:.1f},{split - 8:.1f} '
             f'T{x + W + 10:.1f},{split - 14:.1f} L{x + W + 10:.1f},{yb + 10:.1f} L{x - 10:.1f},{yb + 10:.1f} Z" fill="{band}"/>')
    # окно-яйцо с порошком
    ex, ey, ew, eh = x + W / 2, y + 214, 112, 146
    pg = k.uid("pw")
    defs.append(f'<radialGradient id="{pg}" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="{mix(POWDER, "#FFFFFF", .35)}"/>'
                f'<stop offset="1" stop-color="{mix(POWDER, "#B07A1E", .25)}"/></radialGradient>')
    wid = k.uid("ew")
    defs.append(f'<clipPath id="{wid}"><path d="{_egg_d(ex, ey, ew, eh)}"/></clipPath>')
    g.append(f'<path d="{_egg_d(ex, ey, ew + 10, eh + 10)}" fill="{k.light}"/>')
    g.append(f'<g clip-path="url(#{wid})"><rect x="{ex - ew:.1f}" y="{ey - eh:.1f}" width="{ew * 2:.1f}" height="{eh * 2:.1f}" fill="url(#{pg})"/>'
             f'{_speckles(ex - ew / 2, ey - eh / 2, ew, eh, 90, "#9A6A1A", 9, .35)}'
             f'<path d="M{ex - ew:.1f},{ey - eh * .18:.1f} Q{ex - ew * .2:.1f},{ey - eh * .32:.1f} {ex + ew:.1f},{ey - eh * .22:.1f} '
             f'L{ex + ew:.1f},{ey - eh:.1f} L{ex - ew:.1f},{ey - eh:.1f} Z" fill="#FFFFFF" opacity="0.55"/>'
             f'<ellipse cx="{ex - ew * .22:.1f}" cy="{ey - eh * .05:.1f}" rx="10" ry="28" fill="#FFFFFF" opacity="0.35" '
             f'transform="rotate(14 {ex - ew * .22:.1f} {ey - eh * .05:.1f})"/></g>')
    g.append(f'<path d="{_egg_d(ex, ey, ew, eh)}" fill="none" stroke="{k.primary}" stroke-width="2.5"/>')
    # логотип вверху
    g.append(k.logo("horizontal", x + 24, y + 54, W - 48, 70))
    # тексты на фирменной части
    title = k.t("products.powder.title", "Huevo entero en polvo")
    ls = _lines(title, 14)
    fs = min(_fit(l, 25, W - 48, .55) for l in ls)
    ty = split + 26
    for l in ls:
        ty += fs * 1.02
        g.append(_txt(x + 24, ty, l, fs, on, k.head_font, 700))
    g.append(_txt(x + 24, ty + 22, _subtitle(k), 12, on, k.text_font,
                  500, op=0.85, maxw=W - 48))
    g.append(_txt(x + W - 24, yb - 28, "500 g", 30, on, k.head_font, 800, "end"))
    g.append(_txt(x + 24, yb - 30, "Rinde 40 huevos", 11, on, k.text_font, 600, op=0.85, maxw=W - 140))
    # объём: боковые тени и блик
    sg = k.uid("dv")
    defs.append(f'<linearGradient id="{sg}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="#000" stop-opacity="0.16"/><stop offset="0.12" stop-color="#000" stop-opacity="0"/>'
                f'<stop offset="0.3" stop-color="#FFFFFF" stop-opacity="0.16"/><stop offset="0.42" stop-color="#FFFFFF" stop-opacity="0"/>'
                f'<stop offset="0.86" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.22"/></linearGradient>')
    g.append(f'<rect x="{x - 10:.1f}" y="{y:.1f}" width="{W + 20:.1f}" height="{H + 10:.1f}" fill="url(#{sg})"/>')
    # дно-гассет
    g.append(f'<path d="M{x - 6:.1f},{yb - 34:.1f} Q{x + W / 2:.1f},{yb - 12:.1f} {x + W + 6:.1f},{yb - 34:.1f}" fill="none" '
             f'stroke="#000" stroke-opacity="0.16" stroke-width="2"/>')
    # верхний шов и зип
    for i in range(0, W, 4):
        g.append(f'<line x1="{x + i:.1f}" y1="{y + 5:.1f}" x2="{x + i:.1f}" y2="{y + 17:.1f}" stroke="#000" stroke-opacity="0.045"/>')
    # заломы от наполнения
    for a, b2 in ((x + 6, x + 46), (x + W - 6, x + W - 46)):
        g.append(f'<path d="M{a:.1f},{sl:.1f} Q{(a + b2) / 2:.1f},{sl + 24:.1f} {b2:.1f},{sl + 70:.1f}" fill="none" stroke="#000" stroke-opacity="0.07" stroke-width="3"/>')
    g.append(f'<line x1="{x:.1f}" y1="{y + 32:.1f}" x2="{x + W:.1f}" y2="{y + 32:.1f}" stroke="#000" stroke-opacity="0.12" stroke-width="3"/>')
    g.append(f'<line x1="{x:.1f}" y1="{y + 35:.1f}" x2="{x + W:.1f}" y2="{y + 35:.1f}" stroke="#FFFFFF" stroke-opacity="0.4" stroke-width="1.5"/>')
    g.append("</g>")
    out += g
    # надсечки для отрыва
    for xx, s in ((x, 1), (x + W, -1)):
        out.append(f'<path d="M{xx - s * 1:.1f},{y + 26:.1f} L{xx + s * 7:.1f},{y + 30:.1f} L{xx - s * 1:.1f},{y + 34:.1f} Z" fill="{k.paper}"/>')
    return "".join(out)


# ------------------------------------------------------------------ горка порошка, яйцо и скорлупа
def _still(k, defs, x, yb):
    out = []
    out.append(_shadow(defs, k, x + 120, yb + 2, 170, 20, .30))
    pg = k.uid("hp")
    defs.append(f'<linearGradient id="{pg}" x1="0" y1="0" x2="0.4" y2="1"><stop offset="0" stop-color="{mix(POWDER, "#FFFFFF", .3)}"/>'
                f'<stop offset="1" stop-color="{mix(POWDER, "#A8721C", .22)}"/></linearGradient>')
    d = (f"M{x:.1f},{yb:.1f} C{x + 30:.1f},{yb - 8:.1f} {x + 70:.1f},{yb - 74:.1f} {x + 112:.1f},{yb - 80:.1f} "
         f"C{x + 150:.1f},{yb - 82:.1f} {x + 196:.1f},{yb - 12:.1f} {x + 236:.1f},{yb:.1f} Z")
    out.append(f'<path d="{d}" fill="url(#{pg})"/>')
    cid = k.uid("hc")
    defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    out.append(f'<g clip-path="url(#{cid})">{_speckles(x, yb - 82, 236, 82, 70, "#8E5E14", 4, .35)}'
               f'<path d="M{x + 60:.1f},{yb:.1f} C{x + 80:.1f},{yb - 50:.1f} {x + 100:.1f},{yb - 76:.1f} {x + 112:.1f},{yb - 80:.1f} '
               f'C{x + 96:.1f},{yb - 40:.1f} {x + 92:.1f},{yb - 20:.1f} {x + 96:.1f},{yb:.1f} Z" fill="#FFFFFF" opacity="0.22"/></g>')
    # рассыпанные крупинки
    out.append(_speckles(x - 20, yb - 6, 280, 10, 26, mix(POWDER, "#A8721C", .2), 8, .9))
    # яйцо
    eg = k.uid("eg")
    defs.append(f'<radialGradient id="{eg}" cx="0.36" cy="0.3" r="0.78"><stop offset="0" stop-color="{mix(SHELL_B, "#FFFFFF", .55)}"/>'
                f'<stop offset="0.45" stop-color="{SHELL_B}"/><stop offset="1" stop-color="{mix(SHELL_B, "#6B4A2E", .32)}"/></radialGradient>')
    ex, ey = x + 200, yb - 70
    out.append(_shadow(defs, k, ex + 10, yb, 56, 10, .34))
    out.append(f'<path d="{_egg_d(ex, ey, 100, 132)}" fill="url(#{eg})" transform="rotate(8 {ex} {ey})"/>')
    out.append(f'<ellipse cx="{ex - 18:.1f}" cy="{ey - 30:.1f}" rx="9" ry="16" fill="#FFFFFF" opacity="0.45" transform="rotate(-14 {ex - 18:.1f} {ey - 30:.1f})"/>')
    # половинка скорлупы: внутренность и зубчатый край
    hx, hy, rw = x + 6, yb - 30, 40
    out.append(_shadow(defs, k, hx + 6, yb, 50, 8, .3))
    wg = k.uid("hw")
    defs.append(f'<linearGradient id="{wg}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(SHELL_W, "#FFFFFF", .4)}"/>'
                f'<stop offset="1" stop-color="{mix(SHELL_W, "#7A6A50", .32)}"/></linearGradient>')
    jag = []
    for i in range(13):
        t = i / 12
        px = hx - rw + 2 * rw * t
        py = hy + 9 * (1 - (2 * t - 1) ** 2) ** .5 - (5 if i % 2 else 0)
        jag.append(f"L{px:.1f},{py:.1f}")
    g = [f'<g transform="rotate(-10 {hx} {hy})">']
    g.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{rw}" ry="10" fill="{mix(SHELL_W, "#9A8866", .45)}"/>')
    g.append(f'<path d="M{hx - rw:.1f},{hy:.1f} {" ".join(jag)} C{hx + rw:.1f},{hy + 30:.1f} {hx + 20:.1f},{yb + 4:.1f} {hx:.1f},{yb + 4:.1f} '
             f'C{hx - 20:.1f},{yb + 4:.1f} {hx - rw:.1f},{hy + 30:.1f} {hx - rw:.1f},{hy:.1f} Z" fill="url(#{wg})"/>')
    g.append(f'<ellipse cx="{hx - 16:.1f}" cy="{hy + 16:.1f}" rx="7" ry="4" fill="#FFFFFF" opacity="0.6"/></g>')
    out += g
    return "".join(out)


def render(k, W=1680, H=700):
    defs = []
    s = min(W / 1680, H / 700)
    body = [f'<g transform="translate({(W - 1680 * s) / 2:.1f},{(H - 700 * s) / 2:.1f}) scale({s:.4f})">']
    yb = 640
    body.append(_sack(k, defs, 300, yb))
    body.append(_doypack(k, defs, 800, yb))
    body.append(_still(k, defs, 1160, yb))
    body.append("</g>")
    return f'<defs>{"".join(defs)}</defs>' + "".join(body)
