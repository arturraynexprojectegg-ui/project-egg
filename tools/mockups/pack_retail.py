"""Розничная упаковка: закрытая коробка на 6 яиц, открытая коробка на 12 яиц и яйца со штампом."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import lum, mix  # noqa: E402

TITLE = "Упаковка для розницы"
CAPTION = ("Коробки на 6 и 12 яиц из формованной целлюлозы с фирменной этикеткой "
           "и яйца со штампом знака и кодом производителя ЕС.")

PULP = "#D9D0C1"          # формованная целлюлоза (переработанный картон)
PULP_D = "#B9AE9C"
PULP_L = "#E8E1D5"
SHELL_W = "#F4EEE3"
SHELL_B = "#D9A877"
EGG_CODE = "1ES28001"


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fit(text, size, maxw, k=0.56):
    """Уменьшает кегль, чтобы строка гарантированно влезла в maxw (оценка по средней ширине знака)."""
    w = len(str(text)) * size * k
    return size if w <= maxw else max(8.0, size * maxw / w)


def _txt(x, y, s, size, fill, font, weight=400, anchor="start", ls=0, op=None, maxw=None, k=0.56):
    if maxw:
        size = _fit(s, size, maxw, k + ls / max(size, 1))
    o = f' opacity="{op}"' if op is not None else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size:.1f}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{l}{o}>{_esc(s)}</text>')


def _egg_d(cx, cy, w, h):
    t, b, m = cy - h / 2, cy + h / 2, cy + 0.08 * h
    l, r = cx - w / 2, cx + w / 2
    return (f"M{cx:.1f},{t:.1f} C{cx + .28 * w:.1f},{t:.1f} {r:.1f},{cy - .22 * h:.1f} {r:.1f},{m:.1f} "
            f"C{r:.1f},{cy + .36 * h:.1f} {cx + .27 * w:.1f},{b:.1f} {cx:.1f},{b:.1f} "
            f"C{cx - .27 * w:.1f},{b:.1f} {l:.1f},{cy + .36 * h:.1f} {l:.1f},{m:.1f} "
            f"C{l:.1f},{cy - .22 * h:.1f} {cx - .28 * w:.1f},{t:.1f} {cx:.1f},{t:.1f} Z")


def _shadow(defs, k, cx, cy, rx, ry, op=0.28):
    gid = k.uid("sh")
    defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="#2A2622" stop-opacity="{op}"/>'
                f'<stop offset="0.6" stop-color="#2A2622" stop-opacity="{op * 0.45:.3f}"/>'
                f'<stop offset="1" stop-color="#2A2622" stop-opacity="0"/></radialGradient>')
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{gid})"/>'


def _shell_grads(defs, k):
    g = {}
    for name, base in (("w", SHELL_W), ("b", SHELL_B)):
        gid = k.uid("egg" + name)
        defs.append(f'<radialGradient id="{gid}" cx="0.36" cy="0.30" r="0.78">'
                    f'<stop offset="0" stop-color="{mix(base, "#FFFFFF", 0.55)}"/>'
                    f'<stop offset="0.45" stop-color="{base}"/>'
                    f'<stop offset="1" stop-color="{mix(base, "#6B4A2E", 0.32)}"/></radialGradient>')
        g[name] = gid
    return g


def _egg(g, cx, cy, w, h, kind="b", rot=0, hl=True):
    tr = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    out = f'<g{tr}><path d="{_egg_d(cx, cy, w, h)}" fill="url(#{g[kind]})"/>'
    if hl:
        out += (f'<ellipse cx="{cx - w * .17:.1f}" cy="{cy - h * .2:.1f}" rx="{w * .09:.1f}" ry="{h * .12:.1f}" '
                f'fill="#FFFFFF" opacity="0.45" transform="rotate(-18 {cx - w * .17:.1f} {cy - h * .2:.1f})"/>')
    return out + "</g>"


def _stamp_ink(k):
    for c in (k.primary, k.dark, k.ink):
        if lum(c) < 0.2:
            return c
    return k.ink


# ------------------------------------------------------------------ коробка на 6 (закрыта, вид спереди-сверху)
def _carton6(k, defs, x0, yb, W=380):
    out = []
    D = 196          # экранная глубина крышки
    hb = 50          # высота основания (ячейки)
    hl = 56          # высота передней стенки крышки
    cw = W / 3
    ytop = yb - hb - hl         # передняя кромка крышки
    yback = ytop - D
    out.append(_shadow(defs, k, x0 + W / 2 + 18, yb + 4, W * .62, 26, .34))

    pg = k.uid("pulp")
    defs.append(f'<linearGradient id="{pg}" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{PULP_L}"/><stop offset="1" stop-color="{PULP}"/></linearGradient>')
    fg = k.uid("pulpf")
    defs.append(f'<linearGradient id="{fg}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{PULP}"/><stop offset="1" stop-color="{PULP_D}"/></linearGradient>')

    # основание: три выпуклости ячеек
    d = f"M{x0 + 8:.1f},{yb - hb:.1f} "
    for i in range(3):
        a, b = x0 + 8 + i * (W - 16) / 3, x0 + 8 + (i + 1) * (W - 16) / 3
        m = (a + b) / 2
        d += (f"L{a + 4:.1f},{yb - hb + 6:.1f} C{a + 6:.1f},{yb - 4:.1f} {m - 30:.1f},{yb:.1f} {m:.1f},{yb:.1f} "
              f"C{m + 30:.1f},{yb:.1f} {b - 6:.1f},{yb - 4:.1f} {b - 4:.1f},{yb - hb + 6:.1f} ")
    d += f"L{x0 + W - 8:.1f},{yb - hb:.1f} Z"
    out.append(f'<path d="{d}" fill="url(#{fg})"/>')
    for i in range(3):
        m = x0 + 8 + (i + .5) * (W - 16) / 3
        out.append(f'<ellipse cx="{m - 16:.1f}" cy="{yb - hb * .5:.1f}" rx="14" ry="10" fill="#FFFFFF" opacity="0.22"/>')
    # тень от крышки на основание
    out.append(f'<rect x="{x0 + 8:.1f}" y="{yb - hb:.1f}" width="{W - 16:.1f}" height="7" fill="#5A4E3E" opacity="0.18"/>')

    # передняя стенка крышки (слегка расширяется книзу)
    out.append(f'<path d="M{x0 + 4:.1f},{ytop:.1f} L{x0 + W - 4:.1f},{ytop:.1f} L{x0 + W:.1f},{yb - hb:.1f} '
               f'L{x0:.1f},{yb - hb:.1f} Z" fill="url(#{fg})"/>')
    # замок-язычок
    out.append(f'<path d="M{x0 + W / 2 - 26:.1f},{yb - hb:.1f} L{x0 + W / 2 + 26:.1f},{yb - hb:.1f} '
               f'Q{x0 + W / 2 + 22:.1f},{yb - hb + 20:.1f} {x0 + W / 2:.1f},{yb - hb + 20:.1f} '
               f'Q{x0 + W / 2 - 22:.1f},{yb - hb + 20:.1f} {x0 + W / 2 - 26:.1f},{yb - hb:.1f} Z" fill="{PULP_D}"/>')
    # верх крышки
    out.append(f'<path d="M{x0 + 22:.1f},{yback:.1f} L{x0 + W - 22:.1f},{yback:.1f} Q{x0 + W - 6:.1f},{yback:.1f} '
               f'{x0 + W - 5:.1f},{yback + 12:.1f} L{x0 + W - 4:.1f},{ytop:.1f} L{x0 + 4:.1f},{ytop:.1f} '
               f'L{x0 + 5:.1f},{yback + 12:.1f} Q{x0 + 6:.1f},{yback:.1f} {x0 + 22:.1f},{yback:.1f} Z" fill="url(#{pg})"/>')
    out.append(f'<line x1="{x0 + 4:.1f}" y1="{ytop:.1f}" x2="{x0 + W - 4:.1f}" y2="{ytop:.1f}" '
               f'stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="2"/>')

    # обечайка-этикетка: охватывает верх и переднюю стенку
    bx, bw = x0 + 30, W - 60
    bg = k.light
    out.append(f'<rect x="{bx:.1f}" y="{yback + 10:.1f}" width="{bw:.1f}" height="{ytop - yback - 10:.1f}" fill="{bg}"/>')
    # затенение передней части обечайки
    band = k.brand_bg
    out.append(f'<path d="M{bx:.1f},{ytop:.1f} L{bx + bw:.1f},{ytop:.1f} L{bx + bw + 1.5:.1f},{yb - hb:.1f} '
               f'L{bx - 1.5:.1f},{yb - hb:.1f} Z" fill="{band}"/>')
    out.append(f'<rect x="{bx - 1.5:.1f}" y="{ytop:.1f}" width="{bw + 3:.1f}" height="{hl:.1f}" fill="#000" opacity="0.08"/>')
    on = k.on(band)
    out.append(_txt(x0 + W / 2, ytop + 22, "6 HUEVOS FRESCOS", 15, on, k.head_font, 700, "middle", 2.5, maxw=bw - 30))
    out.append(_txt(x0 + W / 2, ytop + 40, k.t("products.carton.subtitle", "Categoría A · Talla L"), 11, on,
                    k.text_font, 500, "middle", 0.6, op=0.85, maxw=bw - 40))

    # содержимое верха — в координатах этикетки, сжатых по вертикали (печать лежит на плоскости крышки)
    LW, LHs = bw, ytop - yback - 10
    sy = 0.72
    LH = LHs / sy
    g = [f'<g transform="translate({bx:.1f},{yback + 10:.1f}) scale(1,{sy})">']
    g.append(k.pattern_rect(0, LH - 52, LW, 52, scale=0.45, opacity=0.18, color=k.primary))
    g.append(k.logo("primary", 18, 10, LW * .52, LH - 84))
    tx = LW * .52 + 30
    tw = LW - tx - 14
    title = k.t("products.carton.title", "Huevos frescos")
    words = title.split()
    if len(words) >= 2 and len(title) > 12:
        mid = (len(words) + 1) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [title]
    fs = min(_fit(l, 30, tw, .55) for l in lines)
    ty = 62 if len(lines) == 2 else 80
    for i, l in enumerate(lines):
        g.append(_txt(tx, ty + i * fs * 1.08, l, fs, k.ink, k.head_font, 700))
    badge = k.t("products.carton.badge", "Camperas")
    bfs = _fit(badge, 15, tw - 26, .62)
    bwid = min(tw, len(badge) * bfs * .62 + 28)
    byy = ty + len(lines) * fs * 1.08 + 8
    acc = k.accent if abs(lum(k.accent) - lum(k.light)) > 0.15 else k.primary
    g.append(f'<rect x="{tx:.1f}" y="{byy:.1f}" width="{bwid:.1f}" height="30" rx="15" fill="{acc}"/>')
    g.append(_txt(tx + bwid / 2, byy + 20.5, badge.upper(), bfs, k.on(acc), k.text_font, 700, "middle", 1.2))
    g.append(f'<line x1="18" y1="{LH - 60:.1f}" x2="{LW - 18:.1f}" y2="{LH - 60:.1f}" stroke="{k.ink}" stroke-opacity="0.18"/>')
    g.append(_txt(18, LH - 32, k.t("taglines.es", "Huevos frescos de granja"), 15, k.ink, k.text_font, 500,
                  op=0.8, maxw=LW - 150))
    g.append(_txt(LW - 18, LH - 32, "M  L  XL", 14, k.ink, k.text_font, 700, "end", 1.5, op=0.6))
    g.append("</g>")
    out += g
    # лёгкий блик по верхней плоскости
    hg = k.uid("hl")
    defs.append(f'<linearGradient id="{hg}" x1="0" y1="0" x2="1" y2="0.6"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.35"/>'
                f'<stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')
    out.append(f'<rect x="{bx:.1f}" y="{yback + 10:.1f}" width="{bw:.1f}" height="{ytop - yback - 10:.1f}" fill="url(#{hg})"/>')
    # вертикальные кромки обечайки
    for xx in (bx, bx + bw):
        out.append(f'<line x1="{xx:.1f}" y1="{yback + 10:.1f}" x2="{xx:.1f}" y2="{ytop:.1f}" stroke="#000" stroke-opacity="0.12"/>')
    return "".join(out)


# ------------------------------------------------------------------ коробка на 12 (открыта, вид спереди-сверху)
def _carton12(k, defs, g, x0, yb, W=600):
    out = []
    n = 6
    cw = W / n
    D = 160          # экранная глубина основания
    hb = 52
    ytop = yb - hb
    yback = ytop - D
    LID = 186        # экранная высота открытой крышки
    out.append(_shadow(defs, k, x0 + W / 2 + 22, yb + 6, W * .6, 28, .32))

    fg = k.uid("pf")
    defs.append(f'<linearGradient id="{fg}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{PULP}"/><stop offset="1" stop-color="{PULP_D}"/></linearGradient>')
    lg = k.uid("pl")
    defs.append(f'<linearGradient id="{lg}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{mix(PULP, "#8A7E6C", .18)}"/><stop offset="1" stop-color="{PULP_L}"/></linearGradient>')

    # открытая крышка (внутренняя сторона) — откинута назад
    ly = yback - LID
    out.append(f'<path d="M{x0 + 10:.1f},{yback + 4:.1f} L{x0 + 2:.1f},{ly + 14:.1f} Q{x0 + 2:.1f},{ly:.1f} {x0 + 18:.1f},{ly:.1f} '
               f'L{x0 + W - 18:.1f},{ly:.1f} Q{x0 + W - 2:.1f},{ly:.1f} {x0 + W - 2:.1f},{ly + 14:.1f} '
               f'L{x0 + W - 10:.1f},{yback + 4:.1f} Z" fill="url(#{lg})"/>')
    # внутренние купола крышки
    for i in range(n):
        cx = x0 + (i + .5) * cw
        out.append(f'<rect x="{cx - cw * .36:.1f}" y="{ly + 22:.1f}" width="{cw * .72:.1f}" height="{LID - 60:.1f}" rx="{cw * .3:.1f}" '
                   f'fill="#7A6E5C" opacity="0.10"/>')
    # печать на внутренней стороне крышки: фирменная плашка
    px, pw, py, ph = x0 + 64, W - 128, ly + 30, LID - 76
    out.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="6" fill="{k.light}"/>')
    out.append(k.pattern_rect(px, py, pw, ph, scale=0.5, opacity=0.12, color=k.primary, clip_rx=6))
    out.append(k.logo("horizontal", px + 20, py + 12, pw * .5, ph - 24, align="left"))
    rx = px + pw * .5 + 44
    rw = pw - (rx - px) - 18
    out.append(f'<line x1="{rx - 22:.1f}" y1="{py + 18:.1f}" x2="{rx - 22:.1f}" y2="{py + ph - 18:.1f}" stroke="{k.ink}" stroke-opacity="0.18"/>')
    out.append(_txt(rx, py + ph / 2 - 6, k.t("taglines.es", "Huevos frescos de granja"), 17, k.ink, k.head_font, 700, maxw=rw))
    out.append(_txt(rx, py + ph / 2 + 16, "Recogidos a diario · España", 12, k.ink, k.text_font, 500, op=0.7, maxw=rw))
    # тень от крышки на кромку
    out.append(f'<rect x="{x0 + 10:.1f}" y="{yback - 2:.1f}" width="{W - 20:.1f}" height="8" fill="#4A4032" opacity="0.18"/>')

    # верхняя плоскость основания
    out.append(f'<rect x="{x0:.1f}" y="{yback:.1f}" width="{W:.1f}" height="{D:.1f}" rx="10" fill="{PULP_L}"/>')
    # ячейки и яйца: два ряда
    rows = [(yback + D * .30, 0), (yback + D * .74, 1)]
    kinds = ["b", "b", "w", "b", "b", "b", "b", "w", "b", "b", "b", "b"]
    ew, eh = cw * .66, cw * .80
    for r, (cy, ri) in enumerate(rows):
        for i in range(n):
            cx = x0 + (i + .5) * cw
            rw_, rh_ = cw * .44, D * .2
            out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rw_:.1f}" ry="{rh_:.1f}" fill="{mix(PULP, "#6E624F", .35)}"/>')
            out.append(f'<ellipse cx="{cx:.1f}" cy="{cy + 2:.1f}" rx="{rw_ - 3:.1f}" ry="{rh_ - 3:.1f}" fill="{mix(PULP, "#4A4032", .45)}"/>')
            ecy = cy - eh * .28
            out.append(_egg(g, cx, ecy, ew, eh, kinds[r * n + i], rot=(-4 + (i * 7) % 9)))
            # передняя губа ячейки закрывает низ яйца
            out.append(f'<path d="M{cx - rw_:.1f},{cy:.1f} A{rw_:.1f},{rh_:.1f} 0 0 0 {cx + rw_:.1f},{cy:.1f} '
                       f'L{cx + rw_ - 2:.1f},{cy - 3:.1f} Q{cx:.1f},{cy + rh_ * .55:.1f} {cx - rw_ + 2:.1f},{cy - 3:.1f} Z" fill="{PULP_L}"/>')
            out.append(f'<path d="M{cx - rw_ + 2:.1f},{cy - 3:.1f} Q{cx:.1f},{cy + rh_ * .55:.1f} {cx + rw_ - 2:.1f},{cy - 3:.1f}" '
                       f'fill="none" stroke="#5A4E3E" stroke-opacity="0.18" stroke-width="2"/>')
    # передняя стенка основания с ячейками
    d = f"M{x0:.1f},{ytop - 6:.1f} "
    for i in range(n):
        a, b = x0 + 4 + i * (W - 8) / n, x0 + 4 + (i + 1) * (W - 8) / n
        m = (a + b) / 2
        d += (f"L{a + 3:.1f},{ytop + 6:.1f} C{a + 5:.1f},{yb - 4:.1f} {m - 26:.1f},{yb:.1f} {m:.1f},{yb:.1f} "
              f"C{m + 26:.1f},{yb:.1f} {b - 5:.1f},{yb - 4:.1f} {b - 3:.1f},{ytop + 6:.1f} ")
    d += f"L{x0 + W:.1f},{ytop - 6:.1f} Z"
    out.append(f'<path d="{d}" fill="url(#{fg})"/>')
    # фирменная лента на передней кромке
    band = k.brand_bg
    on = k.on(band)
    out.append(f'<rect x="{x0 + 60:.1f}" y="{ytop - 6:.1f}" width="{W - 120:.1f}" height="40" fill="{band}"/>')
    out.append(f'<rect x="{x0 + 60:.1f}" y="{ytop + 28:.1f}" width="{W - 120:.1f}" height="6" fill="#000" opacity="0.10"/>')
    out.append(k.logo("mono", x0 + 72, ytop - 3, 150, 34, color=on, align="left"))
    out.append(_txt(x0 + W - 76, ytop + 19, "12 HUEVOS · " + k.t("products.carton.subtitle", "Categoría A · Talla L"),
                    12.5, on, k.text_font, 700, "end", 1.2, maxw=W - 120 - 190))
    for i in range(n):
        m = x0 + 4 + (i + .5) * (W - 8) / n
        out.append(f'<ellipse cx="{m - 14:.1f}" cy="{yb - 14:.1f}" rx="11" ry="6" fill="#FFFFFF" opacity="0.2"/>')
    return "".join(out)


# ------------------------------------------------------------------ яйца со штампом
def _stamp(k, cx, cy, w, rot, ink):
    s = w / 120
    out = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot}) scale({s:.3f})" opacity="0.86">']
    out.append(k.logo("mono", -32, -50, 64, 44, color=ink))
    out.append(_txt(0, 8, EGG_CODE, 15, ink, "Courier New, monospace", 700, "middle", 0.4))
    out.append(_txt(0, 23, "C.P. 28/12", 9.5, ink, "Courier New, monospace", 700, "middle", 0.6, op=0.9))
    out.append("</g>")
    return "".join(out)


def _eggs(k, defs, g, x0, yb):
    out = []
    ink = _stamp_ink(k)
    out.append(_shadow(defs, k, x0 + 175, yb - 6, 215, 30, .26))
    # заднее коричневое яйцо, переднее белое, лежащее справа
    back = (x0 + 190, yb - 128, 140, 186, "b", 4)
    front = (x0 + 70, yb - 88, 124, 164, "w", -7)
    out.append(_shadow(defs, k, back[0] + 14, yb - 34, 82, 14, .30))
    out.append(_egg(g, *back))
    out.append(_stamp(k, back[0] + 2, back[1] + 16, 112, back[5], ink))
    out.append(_shadow(defs, k, front[0] + 12, yb + 2, 74, 13, .34))
    out.append(_egg(g, *front))
    out.append(_stamp(k, front[0] + 2, front[1] + 14, 104, front[5], ink))
    cx, cy = x0 + 285, yb - 44
    out.append(_shadow(defs, k, cx + 6, yb + 4, 88, 13, .38))
    out.append(_egg(g, cx, cy, 96, 128, "b", 84))
    out.append(_stamp(k, cx + 4, cy - 2, 92, -4, ink))
    return "".join(out)


def render(k, W=1680, H=700):
    defs = []
    g = _shell_grads(defs, k)
    body = []
    yb = 600
    sx, sy = W / 1680, H / 700
    s = min(sx, sy)
    body.append(f'<g transform="translate({(W - 1680 * s) / 2:.1f},{(H - 700 * s) / 2:.1f}) scale({s:.4f})">')
    body.append(_carton6(k, defs, 80, yb, 430))
    body.append(_carton12(k, defs, g, 580, yb, 610))
    body.append(_eggs(k, defs, g, 1255, yb))
    body.append("</g>")
    return f'<defs>{"".join(defs)}</defs>' + "".join(body)
