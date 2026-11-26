"""Пиктограммы: 8 линейных иконок в одной системе + пример на фирменном цвете."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brandkit import mix, contrast  # noqa: E402
from digital_web import T, fit, fw, shadow, egg_path  # noqa: E402

TITLE = "Пиктограммы"
CAPTION = "Восемь линейных пиктограмм на сетке 64 px с единой толщиной линии и скруглениями — для сайта, упаковки, презентаций и навигации."

SW = 3.2  # толщина линии в единицах сетки 64

ICONS = [
    ("egg", "Huevo", "Huevos frescos"),
    ("tray", "Bandeja", "30 unidades"),
    ("powder", "Huevo en polvo", "Ovoproducto"),
    ("truck", "Distribución", "Entrega 24/48 h"),
    ("chef", "Hostelería", "Canal HoReCa"),
    ("farm", "Granja", "Origen trazable"),
    ("quality", "Calidad", "Control por lote"),
    ("cold", "Cadena de frío", "Conservación 4–8 °C"),
]


def glyph(name, line, detail, bg):
    """Пиктограмма в сетке 64×64: только path/circle/rect со stroke=line; detail — акцентная деталь или None."""
    d = detail or line
    s = f'fill="none" stroke="{line}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'
    sd = f'fill="none" stroke="{d}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'
    if name == "egg":
        return (f'<path d="{egg_path(32, 33, 36, 46)}" {s}/>'
                f'<path d="M23.5,30 C23.8,24.5 26,20 29.5,17.5" {sd}/>')
    if name == "tray":
        out = f'<rect x="6" y="15" width="52" height="34" rx="7" {s}/>'
        for j, cy in enumerate((25.5, 38.5)):
            for i, cx in enumerate((19, 32, 45)):
                out += f'<circle cx="{cx}" cy="{cy}" r="4.2" {sd if (i + j) == 1 else s}/>'
        return out + f'<path d="M11,55 H53" {s}/>'
    if name == "powder":
        return (f'<path d="M24.5,22 C15,26 12,39 13.5,51 Q14.3,57 20,57 H44 Q49.7,57 50.5,51 C52,39 49,26 39.5,22" {s}/>'
                f'<path d="M24.5,22 H39.5 M25,22 L22,13 M39,22 L42,13 M22,13 L27,9.5 L32,13 L37,9.5 L42,13" {s}/>'
                f'<path d="{egg_path(32, 41, 11, 14)}" {sd}/>')
    if name == "truck":
        return (f'<path d="M37,44 V17 H7 V44 H11" {s}/><path d="M37,24 H47 L56,34 V44 H52" {s}/>'
                f'<path d="M21,44 H42" {s}/><path d="M41,29 H46 L50,34 H41 Z" {s}/>'
                f'<circle cx="16" cy="46" r="5" fill="{bg}" stroke="{line}" stroke-width="{SW}"/>'
                f'<circle cx="47" cy="46" r="5" fill="{bg}" stroke="{line}" stroke-width="{SW}"/>'
                f'<path d="{egg_path(22, 30.5, 9.5, 12)}" {sd}/>')
    if name == "chef":
        return (f'<path d="M21,42 V34 C13,33.5 10.5,22 18,19 C19,11.5 27.5,8.5 32,13.5 C36.5,8.5 45,11.5 46,19 '
                f'C53.5,22 51,33.5 43,34 V42" {s}/>'
                f'<rect x="21" y="42" width="22" height="10" rx="2.5" {s}/>'
                f'<path d="M28,34 V42 M36,34 V42" {sd}/>')
    if name == "farm":
        return (f'<path d="M9,31 L32,13 L55,31" {s}/><path d="M15,27 V54 H49 V27" {s}/>'
                f'<rect x="25" y="39" width="14" height="15" rx="1" {s}/><path d="M25,39 L39,54 M39,39 L25,54" {sd}/>'
                f'<circle cx="32" cy="28.5" r="3.2" {s}/><path d="M6,54 H58" {s}/>')
    if name == "quality":
        return (f'<circle cx="32" cy="26" r="16" {s}/><path d="M25,26.5 L30,31.5 L39.5,21" {sd}/>'
                f'<path d="M24.5,39.5 L20,56 L26.5,52.5 L30,58 L32,42" {s}/><path d="M39.5,39.5 L44,56 L37.5,52.5 L34,58 L32,42" {s}/>')
    if name == "cold":
        return (f'<path d="M16,38 V14 A6,6 0 0 1 28,14 V38 A10,10 0 1 1 16,38 Z" {s}/>'
                f'<path d="M22,41 V23" {sd}/><circle cx="22" cy="46" r="4" fill="{d}"/>'
                f'<path d="M47,9 V31 M37.5,14.5 L56.5,25.5 M37.5,25.5 L56.5,14.5" {s}/>'
                f'<path d="M43.5,10.5 L47,13 L50.5,10.5 M43.5,29.5 L47,27 L50.5,29.5" {s}/>')
    return ""


def icon(name, x, y, size, line, detail, bg):
    return f'<g transform="translate({x:.1f},{y:.1f}) scale({size/64:.4f})">{glyph(name, line, detail, bg)}</g>'


def colors(k, bg="#FFFFFF"):
    line = k.primary if contrast(k.primary, bg) >= 3 else k.ink
    if line != k.primary:
        detail = k.primary if contrast(k.primary, bg) >= 1.4 else None
    else:
        detail = k.accent if contrast(k.accent, bg) >= 1.5 and k.accent != k.primary else None
    return line, detail


def render(k, W=1680, H=700):
    out = ""
    tw, th, gap = 206, 284, 18
    gx, gy = 96, (H - 2 * th - gap) / 2
    line, detail = colors(k)
    grid_c = mix(k.primary, "#FFFFFF", 0.9)
    for n, (name, lab, sub) in enumerate(ICONS):
        i, j = n % 4, n // 4
        x, y = gx + i * (tw + gap), gy + j * (th + gap)
        out += shadow(x, y, tw, th, 18, n=4, spread=2, op=0.025, dy=5)
        out += f'<rect x="{x}" y="{y:.1f}" width="{tw}" height="{th}" rx="18" fill="#FFFFFF" stroke="#ECE8E0"/>'
        out += T(x + 20, y + 32, f"{n+1:02d}", 12, k.ink, k.text_font, 600, op=0.4, ls=1)
        # сетка-ключ
        isz = 120
        ix, iy = x + (tw - isz) / 2, y + 44
        u = isz / 64
        out += f'<rect x="{ix:.1f}" y="{iy:.1f}" width="{isz}" height="{isz}" fill="none" stroke="{grid_c}" stroke-width="1"/>'
        for t in (16, 32, 48):
            out += f'<path d="M{ix+t*u:.1f},{iy:.1f} V{iy+isz:.1f} M{ix:.1f},{iy+t*u:.1f} H{ix+isz:.1f}" stroke="{grid_c}" stroke-width="0.8"/>'
        out += f'<circle cx="{ix+isz/2:.1f}" cy="{iy+isz/2:.1f}" r="{26*u:.1f}" fill="none" stroke="{grid_c}" stroke-width="1"/>'
        out += icon(name, ix, iy, isz, line, detail, "#FFFFFF")
        size, ls_ = fit(lab, 19, tw - 32, fw(k.head_font), 1, 14)
        out += T(x + tw / 2, y + th - 58, ls_[0], size, k.ink, k.head_font, 700, "middle")
        out += T(x + tw / 2, y + th - 34, sub, 12.5, k.ink, k.text_font, 400, "middle", op=0.6)

    # ---------------- фирменная плашка
    px = gx + 4 * tw + 3 * gap + 36
    pw = W - 96 - px
    py, ph = gy, 2 * th + gap
    bg = k.brand_bg
    oc = k.on(bg)
    out += shadow(px, py, pw, ph, 24, n=6, spread=3, op=0.03, dy=10)
    out += f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph}" rx="24" fill="{bg}"/>'
    if k.pattern_src:
        out += k.pattern_rect(px, py, pw, 118, scale=0.7, opacity=0.13, color=oc, clip_rx=24)
        g = k.uid("pf")
        out += (f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{bg}"/></linearGradient><rect x="{px:.1f}" y="{py+60:.1f}" width="{pw:.1f}" height="60" fill="url(#{g})"/>')
    out += k.logo("mono", px + 32, py + 22, 210, 84, color=oc, align="left")
    out += T(px + 36, py + 136, "Por qué Primeegg", 26, oc, k.head_font, 700)
    pl, pd = oc, (k.accent if contrast(k.accent, bg) >= 2 else None)
    feats = [("cold", "Cadena de frío", "Rutas refrigeradas"), ("quality", "Calidad", "Control en cada lote"),
             ("chef", "HoReCa", "Formatos para cocina"), ("truck", "24/48 h", "Entrega en toda España")]
    cw = (pw - 72) / 2
    for n, (name, lab, sub) in enumerate(feats):
        i, j = n % 2, n // 2
        cx, cy = px + 36 + i * cw, py + 166 + j * 132
        out += f'<circle cx="{cx+32:.1f}" cy="{cy+30:.1f}" r="33" fill="{oc}" opacity="0.12"/>'
        out += icon(name, cx + 6, cy + 4, 52, pl, pd, bg)
        out += T(cx, cy + 92, lab, 16, oc, k.head_font, 700)
        out += T(cx, cy + 112, sub, 12, oc, k.text_font, 400, op=0.78)
    # размеры
    ry = py + ph - 122
    out += f'<line x1="{px+36:.1f}" y1="{ry:.1f}" x2="{px+pw-36:.1f}" y2="{ry:.1f}" stroke="{oc}" stroke-opacity="0.2"/>'
    out += T(px + 36, ry + 28, "TAMAÑOS MÍNIMOS", 10.5, oc, k.text_font, 700, ls=1.6, op=0.75)
    xx = px + 36
    chip_l, chip_d = colors(k, "#FFFFFF")
    for sz in (48, 32, 24, 16):
        out += f'<rect x="{xx:.1f}" y="{ry+42+(48-sz)/2:.1f}" width="{sz+16}" height="{sz+16}" rx="{6+sz*0.12:.1f}" fill="#FFFFFF"/>'
        out += icon("egg", xx + 8, ry + 50 + (48 - sz) / 2, sz, chip_l, chip_d, "#FFFFFF")
        xx += sz + 16 + 14
    out += T(px + pw - 36, ry + 28, "Retícula 64 px · línea 3,2", 12, oc, k.text_font, 500, "end", op=0.75)
    return out
