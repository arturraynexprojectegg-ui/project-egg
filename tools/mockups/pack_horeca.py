"""HoReCa и опт: лоток на 30 яиц с бумажной обечайкой (вид сверху) и гофроящик на 360 яиц (изометрия)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import lum, mix  # noqa: E402

TITLE = "HoReCa и оптовые поставки"
CAPTION = ("Лоток на 30 яиц с фирменной бумажной обечайкой и гофроящик на 360 яиц (12 лотков) "
           "с одноцветной флексопечатью, манипуляционными знаками и транспортной этикеткой.")

PULP = "#D6CCBB"
PULP_D = "#B3A792"
PULP_L = "#E6DFD2"
SHELL_B = "#D9A877"
SHELL_W = "#F4EEE3"
CARD = "#C9A57A"          # гофрокартон
CARD_T = "#D7B78D"
CARD_S = "#B48F63"


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


def _shadow(defs, k, cx, cy, rx, ry, op=0.28):
    gid = k.uid("sh")
    defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="#2A2622" stop-opacity="{op}"/>'
                f'<stop offset="0.6" stop-color="#2A2622" stop-opacity="{op * 0.45:.3f}"/>'
                f'<stop offset="1" stop-color="#2A2622" stop-opacity="0"/></radialGradient>')
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{gid})"/>'


def _barcode(x, y, w, h, color, seed=7):
    """Правдоподобный штрихкод EAN-13 (декоративный)."""
    out, n, xx = [], 95, x
    unit = w / n
    v = seed
    i = 0
    while i < n:
        v = (v * 1103515245 + 12345) & 0x7FFFFFFF
        bw = 1 + (v >> 8) % 3
        guard = i < 3 or i > n - 4 or 45 <= i <= 49
        if guard:
            bw = 1
        if (i % 2 == 0) or guard and i % 2 == 0:
            hh = h + (6 if guard else 0)
            out.append(f'<rect x="{xx:.2f}" y="{y:.1f}" width="{bw * unit:.2f}" height="{hh:.1f}" fill="{color}"/>')
        xx += bw * unit
        i += bw
    return "".join(out)


def _ink(k):
    for c in (k.dark, k.ink, k.primary):
        if lum(c) < 0.08:
            return c
    return "#1C1B19"


# ------------------------------------------------------------------ лоток 30 яиц, вид сверху
def _tray(k, defs, cx, cy, rot=-7):
    out = []
    cols, rows = 6, 5
    px, py = 74, 86
    TW, TH = cols * px + 34, rows * py + 34
    x0, y0 = -TW / 2, -TH / 2
    out.append(_shadow(defs, k, cx + 22, cy + 26, TW * .62, TH * .6, .30))
    out.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot})">')
    pg = k.uid("tp")
    defs.append(f'<linearGradient id="{pg}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PULP_L}"/>'
                f'<stop offset="1" stop-color="{PULP}"/></linearGradient>')
    out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{TW:.1f}" height="{TH:.1f}" rx="16" fill="url(#{pg})"/>')
    out.append(f'<rect x="{x0 + 6:.1f}" y="{y0 + 6:.1f}" width="{TW - 12:.1f}" height="{TH - 12:.1f}" rx="12" '
               f'fill="none" stroke="{PULP_D}" stroke-opacity="0.6" stroke-width="2"/>')
    eg = {}
    for nm, base in (("b", SHELL_B), ("w", SHELL_W)):
        gid = k.uid("te")
        defs.append(f'<radialGradient id="{gid}" cx="0.36" cy="0.32" r="0.75">'
                    f'<stop offset="0" stop-color="{mix(base, "#FFFFFF", .6)}"/><stop offset="0.5" stop-color="{base}"/>'
                    f'<stop offset="1" stop-color="{mix(base, "#5E4128", .35)}"/></radialGradient>')
        eg[nm] = gid
    cell_c = mix(PULP, "#5E5240", .4)
    for j in range(rows):
        for i in range(cols):
            ex = x0 + 17 + (i + .5) * px
            ey = y0 + 17 + (j + .5) * py
            out.append(f'<rect x="{ex - px * .44:.1f}" y="{ey - py * .44:.1f}" width="{px * .88:.1f}" height="{py * .88:.1f}" '
                       f'rx="{px * .36:.1f}" fill="{cell_c}" opacity="0.55"/>')
    # пирамидки между ячейками
    for j in range(rows + 1):
        for i in range(cols + 1):
            if i in (0, cols) or j in (0, rows):
                continue
            sx, sy = x0 + 17 + i * px, y0 + 17 + j * py
            out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="9" fill="{PULP_L}"/>'
                       f'<circle cx="{sx - 2:.1f}" cy="{sy - 2:.1f}" r="4" fill="#FFFFFF" opacity="0.5"/>')
    kinds = "bbbbwbbbbbbbbwbbbbbbbbbbbbwbbb"
    for j in range(rows):
        for i in range(cols):
            ex = x0 + 17 + (i + .5) * px
            ey = y0 + 17 + (j + .5) * py
            r = (i * 5 + j * 3) % 7 - 3
            out.append(f'<ellipse cx="{ex + 6:.1f}" cy="{ey + 7:.1f}" rx="{px * .37:.1f}" ry="{py * .37:.1f}" fill="#3A3226" opacity="0.22"/>')
            out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{px * .38:.1f}" ry="{py * .40:.1f}" '
                       f'fill="url(#{eg[kinds[j * cols + i]]})" transform="rotate({r * 4} {ex:.1f} {ey:.1f})"/>')
            out.append(f'<ellipse cx="{ex - px * .13:.1f}" cy="{ey - py * .15:.1f}" rx="{px * .08:.1f}" ry="{py * .1:.1f}" '
                       f'fill="#FFFFFF" opacity="0.5"/>')
    # бумажная обечайка поперёк лотка
    bh = 148
    by = y0 + 17 + 2.5 * py - bh / 2 + 6
    out.append(f'<rect x="{x0 - 8:.1f}" y="{by + 10:.1f}" width="{TW + 16:.1f}" height="{bh:.1f}" fill="#2A2018" opacity="0.18"/>')
    band = k.brand_bg
    on = k.on(band)
    out.append(f'<rect x="{x0 - 10:.1f}" y="{by:.1f}" width="{TW + 20:.1f}" height="{bh:.1f}" fill="{k.light}"/>')
    out.append(k.pattern_rect(x0 - 10, by, TW + 20, bh, scale=0.5, opacity=0.08, color=k.primary))
    # загнутые края обечайки
    for xx in (x0 - 10, x0 + TW + 4):
        out.append(f'<rect x="{xx:.1f}" y="{by:.1f}" width="6" height="{bh:.1f}" fill="#000" opacity="0.10"/>')
    # левая фирменная панель
    lw = 170
    out.append(f'<rect x="{x0 - 4:.1f}" y="{by:.1f}" width="{lw:.1f}" height="{bh:.1f}" fill="{band}"/>')
    out.append(_txt(x0 - 4 + lw / 2, by + 68, "30", 58, on, k.head_font, 800, "middle"))
    out.append(_txt(x0 - 4 + lw / 2, by + 104, "HUEVOS", 16, on, k.text_font, 700, "middle", 4))
    out.append(_txt(x0 - 4 + lw / 2, by + 126, "Categoría A", 12, on, k.text_font, 500, "middle", 1, op=0.8))
    # логотип и тексты
    lx = x0 + lw + 14
    out.append(k.logo("primary", lx, by + 8, 150, bh - 16))
    tx = lx + 166
    tw = x0 + TW - 14 - tx
    title = k.t("products.horeca.title", "Huevos para hostelería")
    words = title.split()
    lines = [title]
    if len(title) > 16 and len(words) > 1:
        m = (len(words) + 1) // 2
        lines = [" ".join(words[:m]), " ".join(words[m:])]
    fs = min(_fit(l, 22, tw, .55) for l in lines)
    yy = by + 40
    for l in lines:
        out.append(_txt(tx, yy, l, fs, k.ink, k.head_font, 700))
        yy += fs * 1.1
    out.append(_txt(tx, yy + 8, k.t("products.horeca.subtitle", "Bandeja 30 uds · Talla M-L"), 13.5, k.ink,
                    k.text_font, 600, op=0.8, maxw=tw))
    out.append(f'<line x1="{tx:.1f}" y1="{yy + 22:.1f}" x2="{tx + tw:.1f}" y2="{yy + 22:.1f}" stroke="{k.ink}" stroke-opacity="0.2"/>')
    out.append(_txt(tx, yy + 40, "Lote L2611 · C.P. 24/12/2026", 11.5, k.ink, k.text_font, 500, op=0.65, maxw=tw))
    out.append(_txt(tx, yy + 55, "Conservar refrigerado tras la compra", 11, k.ink, k.text_font, 400, op=0.6, maxw=tw))
    out.append("</g>")
    return "".join(out)


# ------------------------------------------------------------------ иконки манипуляционных знаков
def _icon_fragile(x, y, s, c):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s / 48:.3f})" fill="none" stroke="{c}" stroke-width="3" '
            f'stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M12,4 L36,4 L34,20 Q32,30 24,31 Q16,30 14,20 Z"/><path d="M24,31 L24,42 M15,44 L33,44"/>'
            f'<path d="M22,5 L26,13 L21,17 L25,24" stroke-width="2.2"/></g>')


def _icon_up(x, y, s, c):
    a = ""
    for dx in (13, 35):
        a += f'<path d="M{dx},44 L{dx},12 M{dx - 8},20 L{dx},10 L{dx + 8},20"/>'
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s / 48:.3f})" fill="none" stroke="{c}" stroke-width="3.4" '
            f'stroke-linejoin="round" stroke-linecap="round">{a}<path d="M4,4 L44,4"/></g>')


def _icon_temp(x, y, s, c):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s / 48:.3f})" fill="none" stroke="{c}" stroke-width="3" '
            f'stroke-linecap="round"><path d="M19,30 L19,8 Q19,3 24,3 Q29,3 29,8 L29,30"/>'
            f'<circle cx="24" cy="37" r="8"/><circle cx="24" cy="37" r="4" fill="{c}" stroke="none"/>'
            f'<path d="M24,33 L24,14"/><path d="M33,10 L38,10 M33,17 L38,17 M33,24 L38,24" stroke-width="2.2"/></g>')


def _icon_dry(x, y, s, c):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s / 48:.3f})" fill="none" stroke="{c}" stroke-width="3" '
            f'stroke-linejoin="round" stroke-linecap="round"><path d="M4,24 Q24,0 44,24 Q38,20 34,24 Q29,20 24,24 Q19,20 14,24 Q10,20 4,24 Z"/>'
            f'<path d="M24,24 L24,40 Q24,45 19,44"/><path d="M8,32 L6,37 M40,32 L42,37" stroke-width="2.4"/></g>')


# ------------------------------------------------------------------ гофроящик, изометрия
def _box(k, defs, cx, cy):
    """cx,cy — передний нижний угол ящика."""
    out = []
    L, Wd, Ht = 400, 210, 250
    u = (0.90, 0.30)        # локальная x длинной стороны (слева-направо к углу)
    v = (0.74, -0.40)       # короткая сторона уходит вправо-вверх
    ink = _ink(k)
    # координаты
    lb = (cx - L * u[0], cy - L * u[1])
    fp = [(cx + 10, cy + 6), (lb[0] + 10, lb[1] + 6), (lb[0] + Wd * v[0] + 60, lb[1] + Wd * v[1] + 10),
          (cx + Wd * v[0] + 60, cy + Wd * v[1] + 10)]
    out.append(_shadow(defs, k, (cx + lb[0]) / 2 + 90, cy - 40, 360, 92, .26))
    out.append(f'<path d="M{" L".join(f"{a:.1f},{b:.1f}" for a, b in fp)} Z" fill="#2A2622" opacity="0.10"/>')

    def M(a, b, c, d, e, f, body):
        return f'<g transform="matrix({a:.4f},{b:.4f},{c:.4f},{d:.4f},{e:.2f},{f:.2f})">{body}</g>'

    # --- длинная сторона (фронт-лево)
    gl = k.uid("cl")
    defs.append(f'<linearGradient id="{gl}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(CARD, "#FFFFFF", .08)}"/>'
                f'<stop offset="1" stop-color="{mix(CARD, "#6B4E2E", .08)}"/></linearGradient>')
    f1 = [f'<rect width="{L}" height="{Ht}" fill="url(#{gl})"/>']
    for i in range(0, L, 6):
        f1.append(f'<line x1="{i}" y1="0" x2="{i}" y2="{Ht}" stroke="#8A6A44" stroke-opacity="0.05"/>')
    f1.append(f'<line x1="0" y1="2" x2="{L}" y2="2" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="3"/>')
    f1.append(k.logo("mono", 22, 34, 190, 140, color=ink, align="left"))
    tx = 226
    tw = L - tx - 22
    t = k.t("products.horeca.title", "Huevos para hostelería")
    words = t.split()
    lines = [t] if len(t) <= 14 or len(words) == 1 else [" ".join(words[:(len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])]
    fs = min(_fit(l, 22, tw, .56) for l in lines)
    yy = 66
    for l in lines:
        f1.append(_txt(tx, yy, l, fs, ink, k.head_font, 700))
        yy += fs * 1.1
    f1.append(f'<line x1="{tx}" y1="{yy:.1f}" x2="{L - 22}" y2="{yy:.1f}" stroke="{ink}" stroke-width="2"/>')
    f1.append(_txt(tx, yy + 40, "360", 40, ink, k.head_font, 800))
    f1.append(_txt(tx, yy + 60, "HUEVOS · 12 × 30", 12, ink, k.text_font, 700, ls=1.2, maxw=tw))
    f1.append(f'<rect x="0" y="{Ht - 46}" width="{L}" height="46" fill="{ink}" opacity="0.9"/>')
    f1.append(_txt(22, Ht - 18, "HUEVOS FRESCOS · CATEGORÍA A · TALLA M-L", 12.5, CARD, k.text_font, 700, ls=1.6, maxw=L - 170))
    f1.append(_txt(L - 22, Ht - 18, k.t("contacts.web", "primeegg.es"), 12.5, CARD, k.text_font, 700, "end", 0.8))
    out.append(M(u[0], u[1], 0, 1, lb[0], lb[1] - Ht, "".join(f1)))

    # --- короткая сторона (право)
    gs = k.uid("cs")
    defs.append(f'<linearGradient id="{gs}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CARD_S}"/>'
                f'<stop offset="1" stop-color="{mix(CARD_S, "#5A4024", .12)}"/></linearGradient>')
    f2 = [f'<rect width="{Wd}" height="{Ht}" fill="url(#{gs})"/>']
    for i in range(0, Wd, 6):
        f2.append(f'<line x1="{i}" y1="0" x2="{i}" y2="{Ht}" stroke="#5A4024" stroke-opacity="0.05"/>')
    # ручка-вырез
    f2.append(f'<rect x="{Wd / 2 - 34}" y="18" width="68" height="18" rx="9" fill="#3A2A18" opacity="0.75"/>')
    f2.append(f'<path d="M{Wd / 2 - 25},27 L{Wd / 2 + 25},27" stroke="#2A1D10" stroke-width="7" stroke-linecap="round" opacity="0.5"/>')
    sic = 34
    icons = [(_icon_fragile, "Frágil"), (_icon_up, "Este lado arriba"), (_icon_temp, "0–25 °C")]
    gap = (Wd - 24) / 3
    for i, (fn, lab) in enumerate(icons):
        ix = 12 + i * gap + gap / 2
        f2.append(f'<rect x="{ix - 24:.1f}" y="48" width="48" height="48" rx="3" fill="none" stroke="{ink}" stroke-width="1.6" opacity="0.9"/>')
        f2.append(fn(ix - sic / 2, 48 + (48 - sic) / 2, sic, ink))
        f2.append(_txt(ix, 110, lab, 8.6, ink, k.text_font, 700, "middle", 0.2, maxw=gap - 4))
    # транспортная этикетка
    lx, ly, lw_, lh_ = 14, 124, Wd - 28, 112
    f2.append(f'<rect x="{lx + 2}" y="{ly + 3}" width="{lw_}" height="{lh_}" fill="#000" opacity="0.12"/>')
    f2.append(f'<rect x="{lx}" y="{ly}" width="{lw_}" height="{lh_}" fill="#FFFFFF"/>')
    band = k.brand_bg
    f2.append(f'<rect x="{lx}" y="{ly}" width="{lw_}" height="26" fill="{band}"/>')
    f2.append(k.logo("mono", lx + 4, ly + 2, 70, 22, color=k.on(band), align="left"))
    f2.append(_txt(lx + lw_ - 6, ly + 17, "360 uds", 10, k.on(band), k.text_font, 700, "end"))
    rowsz = [("Producto", "Huevos frescos cat. A"), ("Lote", "L2611-0428"), ("Envasado", "26/11/2026"),
             ("Cons. pref.", "24/12/2026")]
    for i, (a, b) in enumerate(rowsz):
        yy = ly + 39 + i * 12
        f2.append(_txt(lx + 6, yy, a, 7.5, "#555555", k.text_font, 500))
        f2.append(_txt(lx + 56, yy, b, 7.5, "#1C1B19", k.text_font, 700, maxw=lw_ - 62))
    f2.append(_barcode(lx + 8, ly + 88, lw_ * .62, 16, "#1C1B19"))
    f2.append(_txt(lx + lw_ - 6, ly + 100, "ES 28001", 7.5, "#1C1B19", "Courier New, monospace", 700, "end"))
    out.append(M(v[0], v[1], 0, 1, cx, cy - Ht, "".join(f2)))

    # --- верх
    gt = k.uid("ct")
    defs.append(f'<linearGradient id="{gt}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(CARD_T, "#FFFFFF", .12)}"/>'
                f'<stop offset="1" stop-color="{CARD_T}"/></linearGradient>')
    f3 = [f'<rect width="{L}" height="{Wd}" fill="url(#{gt})"/>']
    f3.append(f'<line x1="0" y1="{Wd / 2}" x2="{L}" y2="{Wd / 2}" stroke="#7A5B36" stroke-opacity="0.55" stroke-width="2"/>')
    # фирменный скотч вдоль шва
    tape = k.primary
    f3.append(f'<rect x="-1" y="{Wd / 2 - 24}" width="{L + 2}" height="48" fill="{tape}" opacity="0.95"/>')
    f3.append(f'<rect x="-1" y="{Wd / 2 - 24}" width="{L + 2}" height="48" fill="#FFFFFF" opacity="0.10"/>')
    for i in range(3):
        f3.append(k.logo("mono", 24 + i * 130, Wd / 2 - 20, 100, 40, color=k.on(tape)))
    out.append(M(u[0], u[1], -v[0], -v[1], lb[0] - 0 + Wd * v[0], lb[1] - Ht + Wd * v[1], "".join(f3)))
    # скотч продолжается на короткую сторону
    out.append(M(v[0], v[1], 0, 1, cx, cy - Ht,
                 f'<rect x="{Wd / 2 - 24}" y="-1" width="48" height="16" fill="{tape}" opacity="0.95"/>'))
    # рёбра
    tb = (lb[0] + Wd * v[0], lb[1] - Ht + Wd * v[1])
    out.append(f'<path d="M{lb[0]:.1f},{lb[1] - Ht:.1f} L{cx:.1f},{cy - Ht:.1f} L{cx + Wd * v[0]:.1f},{cy - Ht + Wd * v[1]:.1f}" '
               f'fill="none" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="2"/>')
    out.append(f'<path d="M{cx:.1f},{cy - Ht:.1f} L{cx:.1f},{cy:.1f}" stroke="#6B4E2E" stroke-opacity="0.35" stroke-width="1.5"/>')
    return "".join(out)


def render(k, W=1680, H=700):
    defs = []
    s = min(W / 1680, H / 700)
    body = [f'<g transform="translate({(W - 1680 * s) / 2:.1f},{(H - 700 * s) / 2:.1f}) scale({s:.4f})">']
    body.append(_tray(k, defs, 500, 350))
    body.append(_box(k, defs, 1290, 610))
    body.append("</g>")
    return f'<defs>{"".join(defs)}</defs>' + "".join(body)
