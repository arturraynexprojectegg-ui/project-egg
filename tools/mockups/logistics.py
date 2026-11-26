"""Логистика: рефрижераторный фургон в фирменной ливрее + паллета с коробами под стрейч-плёнкой."""
from html import escape
import hashlib

TITLE = "Логистика"
CAPTION = "Рефрижераторный фургон в фирменной ливрее и паллета с коробами под стрейч-плёнкой с транспортной этикеткой."


def _mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i+2], 16)*(1-t)+int(b[i:i+2], 16)*t):02X}" for i in (0, 2, 4))


def _lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _lingrad(k, stops, x1=0, y1=0, x2=0, y2=1):
    gid = k.uid("lg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops)
    return gid, (f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')


def _shadow(k, cx, cy, rx, ry, op=0.22):
    gid = k.uid("sh")
    return (f'<radialGradient id="{gid}"><stop offset="0" stop-color="#000" stop-opacity="{op}"/>'
            f'<stop offset="0.6" stop-color="#000" stop-opacity="{op*0.45:.3f}"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>')


def _barcode(seed, x, y, w, h, color="#1C1B19"):
    hsh = hashlib.md5(seed.encode()).digest() * 4
    out, cx, i = [], x, 0
    while cx < x + w - 2:
        bw = 0.8 + (hsh[i % len(hsh)] % 3) * 0.8
        gap = 0.8 + (hsh[(i + 7) % len(hsh)] % 2) * 0.9
        if cx + bw > x + w:
            break
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{bw:.1f}" height="{h}"/>')
        cx += bw + gap
        i += 1
    return f'<g fill="{color}">{"".join(out)}</g>'


def _wheel(k, cx, cy, r=50):
    rim = k.uid("rim")
    o = (f'<radialGradient id="{rim}" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#E9ECEE"/>'
         f'<stop offset="1" stop-color="#9DA3A8"/></radialGradient>')
    o += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2A2A2A"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r-3}" fill="none" stroke="#3A3A3A" stroke-width="2"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r*0.62:.1f}" fill="url(#{rim})"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r*0.62:.1f}" fill="none" stroke="#7E848A" stroke-width="1.5"/>'
    import math
    for i in range(8):
        a = i * math.pi / 4 + 0.2
        o += (f'<ellipse cx="{cx + math.cos(a)*r*0.42:.1f}" cy="{cy + math.sin(a)*r*0.42:.1f}" '
              f'rx="{r*0.085:.1f}" ry="{r*0.085:.1f}" fill="#6B7176"/>')
    o += f'<circle cx="{cx}" cy="{cy}" r="{r*0.24:.1f}" fill="#B9BEC2" stroke="#80868B" stroke-width="1.2"/>'
    for i in range(6):
        a = i * math.pi / 3
        o += f'<circle cx="{cx + math.cos(a)*r*0.15:.1f}" cy="{cy + math.sin(a)*r*0.15:.1f}" r="1.8" fill="#5E6368"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="{r*0.07:.1f}" fill="#5E6368"/>'
    return o


def _snow(x, y, s, color):
    o = f'<g stroke="{color}" stroke-width="{s*0.12:.1f}" stroke-linecap="round" fill="none">'
    import math
    for i in range(3):
        a = i * math.pi / 3 + math.pi / 2
        dx, dy = math.cos(a) * s / 2, math.sin(a) * s / 2
        o += f'<line x1="{x-dx:.1f}" y1="{y-dy:.1f}" x2="{x+dx:.1f}" y2="{y+dy:.1f}"/>'
        for sg in (1, -1):
            px, py = x + sg * dx * 0.62, y + sg * dy * 0.62
            for b in (0.6, -0.6):
                bx = math.cos(a + (math.pi if sg < 0 else 0) + b * 1.0 + math.pi) * s * 0.16
                by = math.sin(a + (math.pi if sg < 0 else 0) + b * 1.0 + math.pi) * s * 0.16
                o += f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px+bx:.1f}" y2="{py+by:.1f}"/>'
    return o + "</g>"


# --------------------------------------------------------------------------- van
def _van(k, ox, G):
    """Фургон, обращённый кабиной вправо; ox — левый край, G — линия земли."""
    o = []
    X = lambda v: ox + v
    bg = k.brand_bg
    onbg = k.on(bg)
    web = escape(k.t("contacts.web", "primeegg.es"))
    phone = escape(k.t("contacts.phone", "+34 900 000 000"))
    tag = escape(k.t("taglines.es", "Huevos frescos de granja"))

    wr, wcy = 50, G - 50
    rear_cx, front_cx = X(250), X(890)
    # ---- ground shadows
    o.append(_shadow(k, X(520), G + 2, 560, 18, 0.20))
    o.append(_shadow(k, rear_cx, G + 1, 80, 9, 0.35))
    o.append(_shadow(k, front_cx, G + 1, 74, 9, 0.35))

    # ---- chassis & under-run
    o.append(f'<rect x="{X(30)}" y="{G-110}" width="{780}" height="22" fill="#2E3033"/>')
    o.append(f'<rect x="{X(2)}" y="{G-92}" width="30" height="14" rx="2" fill="#3A3D41"/>')      # rear under-run bar
    o.append(f'<rect x="{X(14)}" y="{G-104}" width="8" height="20" fill="#3A3D41"/>')
    # side under-run guard between wheels
    o.append(f'<rect x="{X(330)}" y="{G-84}" width="470" height="8" rx="2" fill="#B9BEC2"/>')
    o.append(f'<rect x="{X(330)}" y="{G-70}" width="470" height="8" rx="2" fill="#AEB3B8"/>')
    for gx in (340, 560, 790):
        o.append(f'<rect x="{X(gx)}" y="{G-110}" width="6" height="48" fill="#5A5E63"/>')
    # fuel tank
    o.append(f'<rect x="{X(610)}" y="{G-102}" width="110" height="40" rx="10" fill="#4A4E53"/>')
    o.append(f'<rect x="{X(615)}" y="{G-98}" width="100" height="6" rx="3" fill="#6A6F75"/>')

    # ---- box body
    bx0, bx1, by0, by1 = X(0), X(760), 110, G - 110
    bh = by1 - by0
    gw, gdef = _lingrad(k, [(0, "#FFFFFF", 1), (0.7, "#F4F3F0", 1), (1, "#E3E2DE", 1)])
    o.append(gdef)
    clip = k.uid("box")
    o.append(f'<clipPath id="{clip}"><rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="{bh}" rx="8"/></clipPath>')
    o.append(f'<rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="{bh}" rx="8" fill="url(#{gw})"/>')
    o.append(f'<g clip-path="url(#{clip})">')
    # brand band with a swoosh
    yL, yR = by1 - 118, by1 - 210
    band = (f'M{bx0-5},{yL} C{X(260)},{yL+6} {X(470)},{yR+60} {bx1+5},{yR} '
            f'L{bx1+5},{by1+5} L{bx0-5},{by1+5} Z')
    bclip = k.uid("band")
    o.append(f'<clipPath id="{bclip}"><path d="{band}"/></clipPath>')
    bgd, bgdef = _lingrad(k, [(0, bg, 1), (1, _mix(bg, "#000000", 0.14), 1)])
    o.append(bgdef)
    o.append(f'<path d="{band}" fill="url(#{bgd})"/>')
    o.append(f'<g clip-path="url(#{bclip})">{k.pattern_rect(bx0, yR - 10, bx1 - bx0, by1 - yR + 20, scale=0.9, opacity=0.13, color=onbg)}</g>')
    acc = k.accent if _contrast(k.accent, bg) > 1.35 and _contrast(k.accent, "#FFFFFF") > 1.3 else _mix(bg, "#FFFFFF", 0.45)
    o.append(f'<path d="M{bx0-5},{yL-14} C{X(260)},{yL-8} {X(470)},{yR+46} {bx1+5},{yR-14}" '
             f'fill="none" stroke="{acc}" stroke-width="8"/>')
    o.append("</g>")
    # logo on white
    o.append(k.logo("horizontal", X(46), by0 + 34, 430, 150, align="left"))
    tcol = k.primary if _contrast(k.primary, "#FFFFFF") >= 3 else k.dark
    o.append(f'<text x="{X(50)}" y="{by0+226}" font-family="{k.head_font}" font-size="30" '
             f'fill="{tcol}">{tag}</text>')
    # cold-chain badge, top right of the box
    o.append(f'<g>{_snow(X(704), by0+48, 30, tcol)}'
             f'<text x="{X(680)}" y="{by0+44}" text-anchor="end" font-family="{k.text_font}" font-size="15" '
             f'font-weight="700" letter-spacing="1.5" fill="{tcol}">FRÍO CONTROLADO</text>'
             f'<text x="{X(680)}" y="{by0+64}" text-anchor="end" font-family="{k.text_font}" font-size="14" '
             f'fill="#6B6A66">Transporte a 2–6 °C</text></g>')
    # contacts on the band
    o.append(f'<text x="{X(50)}" y="{by1-46}" font-family="{k.head_font}" font-size="40" font-weight="700" '
             f'fill="{onbg}">{web}</text>')
    o.append(f'<text x="{X(52)}" y="{by1-18}" font-family="{k.text_font}" font-size="18" letter-spacing="1" '
             f'fill="{onbg}" opacity="0.85">Huevos · Ovoproductos · HoReCa</text>')
    o.append(f'<text x="{bx1-36}" y="{by1-46}" text-anchor="end" font-family="{k.text_font}" font-size="28" '
             f'font-weight="700" fill="{onbg}">{phone}</text>')
    # box frame: top/bottom rails, corner posts, rear door seam
    o.append(f'<rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="{bh}" rx="8" fill="none" stroke="#B7BABD" stroke-width="2"/>')
    o.append(f'<rect x="{bx0}" y="{by0}" width="{bx1-bx0}" height="9" rx="4" fill="#D3D6D9"/>')
    o.append(f'<rect x="{bx0}" y="{by1-9}" width="{bx1-bx0}" height="9" rx="2" fill="#A9AEB2"/>')
    o.append(f'<rect x="{bx0}" y="{by0}" width="12" height="{bh}" rx="4" fill="#C7CBCE"/>')
    o.append(f'<rect x="{bx1-12}" y="{by0}" width="12" height="{bh}" rx="4" fill="#C7CBCE"/>')
    # marker lights
    for mx in (110, 300, 500, 700):
        o.append(f'<rect x="{X(mx)}" y="{by1-7}" width="14" height="5" rx="2" fill="#F2A53A"/>')
    o.append(f'<rect x="{bx0-4}" y="{by1-58}" width="8" height="40" rx="2" fill="#C8352B"/>')
    o.append(f'<rect x="{bx0-4}" y="{by1-58}" width="8" height="12" rx="2" fill="#F2A53A"/>')

    # ---- reefer unit on the front wall, above the cab
    rx0, ry0 = bx1 - 8, by0 + 22
    o.append(f'<path d="M{rx0},{ry0} L{rx0+58},{ry0+6} Q{rx0+66},{ry0+8} {rx0+66},{ry0+18} L{rx0+66},{ry0+92} '
             f'Q{rx0+66},{ry0+102} {rx0+56},{ry0+102} L{rx0},{ry0+104} Z" fill="#ECEDEE" stroke="#B2B6BA" stroke-width="2"/>')
    for i in range(6):
        o.append(f'<rect x="{rx0+14}" y="{ry0+22+i*11}" width="42" height="4" rx="2" fill="#9EA3A8"/>')

    # ---- cab
    c0 = bx1 + 6
    roof, G2 = by0 + 112, G - 72
    cab = (f'M{c0},{roof+8} Q{c0},{roof} {c0+10},{roof} L{c0+96},{roof} Q{c0+112},{roof} {c0+120},{roof+12} '
           f'L{c0+186},{roof+118} Q{c0+192},{roof+126} {c0+204},{roof+130} L{c0+250},{roof+146} '
           f'Q{c0+262},{roof+150} {c0+263},{roof+162} L{c0+266},{G2} L{front_cx+66},{G2} '
           f'A66,66 0 0 0 {front_cx-66},{G2} L{c0},{G2} Z')
    cg, cgdef = _lingrad(k, [(0, "#FFFFFF", 1), (0.75, "#F3F2EF", 1), (1, "#DCDBD7", 1)])
    o.append(cgdef)
    o.append(f'<path d="{cab}" fill="url(#{cg})" stroke="#B7BABD" stroke-width="2"/>')
    ccl = k.uid("cab")
    o.append(f'<clipPath id="{ccl}"><path d="{cab}"/></clipPath>')
    o.append(f'<g clip-path="url(#{ccl})">')
    o.append(f'<rect x="{c0-5}" y="{G2-80}" width="300" height="90" fill="url(#{bgd})"/>')
    o.append(f'<rect x="{c0-5}" y="{G2-94}" width="300" height="8" fill="{acc}"/>')
    o.append("</g>")
    # windshield edge (glass glimpse)
    o.append(f'<path d="M{c0+112},{roof+6} L{c0+186},{roof+118} L{c0+176},{roof+122} L{c0+102},{roof+10} Z" fill="#3E4A55"/>')
    # side window
    win = (f'M{c0+18},{roof+18} L{c0+96},{roof+18} Q{c0+104},{roof+18} {c0+108},{roof+24} L{c0+166},{roof+116} '
           f'L{c0+18},{roof+116} Z')
    wg, wgdef = _lingrad(k, [(0, "#5B6B78", 1), (1, "#2E3842", 1)], 0, 0, 1, 1)
    o.append(wgdef)
    o.append(f'<path d="{win}" fill="url(#{wg})" stroke="#2A2F35" stroke-width="3" stroke-linejoin="round"/>')
    o.append(f'<path d="M{c0+30},{roof+108} L{c0+92},{roof+26} L{c0+110},{roof+26} L{c0+48},{roof+108} Z" fill="#FFFFFF" opacity="0.12"/>')
    # door seams, handle, step, mirror
    o.append(f'<path d="M{c0+10},{roof+12} L{c0+10},{G2-4}" stroke="#A6AAAE" stroke-width="2" fill="none"/>')
    o.append(f'<path d="M{c0+176},{roof+124} L{c0+182},{G2-52}" stroke="#A6AAAE" stroke-width="2" fill="none"/>')
    o.append(f'<rect x="{c0+24}" y="{roof+134}" width="36" height="9" rx="4" fill="#9AA0A5"/>')
    o.append(k.logo("mark", c0 + 76, roof + 132, 86, 74))
    o.append(f'<path d="M{c0+174},{roof+70} L{c0+194},{roof+72} L{c0+196},{roof+112} L{c0+176},{roof+112} Z" fill="#2E3033"/>')
    o.append(f'<rect x="{c0+168}" y="{roof+98}" width="22" height="6" fill="#2E3033"/>')
    # headlight, indicator, grille, bumper
    hg, hgdef = _lingrad(k, [(0, "#FFFFFF", 1), (1, "#D9DEE2", 1)], 0, 0, 1, 1)
    o.append(hgdef)
    o.append(f'<path d="M{c0+226},{roof+142} L{c0+258},{roof+152} Q{c0+263},{roof+156} {c0+263},{roof+166} '
             f'L{c0+263},{roof+182} L{c0+232},{roof+172} Q{c0+222},{roof+166} {c0+224},{roof+150} Z" '
             f'fill="url(#{hg})" stroke="#8D9398" stroke-width="2"/>')
    o.append(f'<path d="M{c0+212},{roof+150} L{c0+226},{roof+154} L{c0+225},{roof+166} L{c0+212},{roof+160} Z" fill="#F2A53A"/>')
    for i in range(3):
        o.append(f'<rect x="{c0+254}" y="{roof+192+i*12}" width="10" height="6" rx="2" fill="#3A3D41"/>')
    o.append(f'<path d="M{c0+236},{G2-58} L{c0+270},{G2-58} Q{c0+276},{G2-58} {c0+276},{G2-50} L{c0+276},{G2+4} '
             f'Q{c0+276},{G2+12} {c0+268},{G2+12} L{c0+222},{G2+12} Z" fill="#3A3D41"/>')
    o.append(f'<rect x="{c0+262}" y="{G2-40}" width="12" height="10" rx="2" fill="#E9ECEE"/>')
    o.append(f'<rect x="{c0+30}" y="{G2+2}" width="70" height="10" rx="3" fill="#3A3D41"/>')

    # ---- wheels, arches, mudflap
    o.append(f'<rect x="{rear_cx-66}" y="{G-114}" width="132" height="16" rx="5" fill="#26282B"/>')
    o.append(f'<path d="M{front_cx-66},{G2} A66,66 0 0 1 {front_cx+66},{G2}" fill="#26282B"/>')
    o.append(_wheel(k, rear_cx, wcy, wr))
    o.append(_wheel(k, front_cx, wcy, wr))
    o.append(f'<rect x="{rear_cx+74}" y="{G-92}" width="10" height="70" rx="2" fill="#2A2A2A"/>')
    return "".join(o)


# --------------------------------------------------------------------------- pallet
def _pallet(k, x, G):
    o = []
    cols, rows, cw, ch = 3, 5, 94, 58
    W = cols * cw
    dx, dy = 70, -40                      # глубина в косой проекции
    ph = 46                               # высота паллеты
    top = G - ph - rows * ch
    kraft, kraft_s, kraft_t = "#C9A57A", "#A9865C", "#DBBD92"
    wood, wood_s, wood_d = "#D2AE7C", "#B08D5E", "#8E6E45"
    ink = k.dark if _lum(k.dark) < 0.2 else k.ink
    o.append(_shadow(k, x + W / 2 + 40, G + 2, W / 2 + 90, 16, 0.24))
    # ---- pallet side face
    P = lambda px, py: f"{px:.1f},{py:.1f}"
    def para(x0, y0, w, h, fill, stroke=None):
        pts = " ".join([P(x0, y0), P(x0 + dx * w, y0 + dy * w), P(x0 + dx * w, y0 + dy * w + h), P(x0, y0 + h)])
        st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
        return f'<polygon points="{pts}" fill="{fill}"{st}/>'
    px1 = x + W
    gap = " ".join([P(x, G - ph), P(x + W, G - ph), P(x + W + dx, G - ph + dy), P(x + W + dx, G + dy), P(x + W, G), P(x, G)])
    o.append(f'<polygon points="{gap}" fill="#4A3B28"/>')
    o.append(para(px1, G - ph, 1, 12, wood_s, wood_d))
    for f in (0, 0.45, 0.88):
        o.append(para(px1 + dx * f, G - ph + 12 + dy * f, 0.12, 28, _mix(wood_s, "#000000", 0.08), wood_d))
    o.append(para(px1, G - 12, 1, 12, wood_s, wood_d))
    # ---- pallet front (EUR)
    o.append(f'<rect x="{x}" y="{G-ph}" width="{W}" height="12" fill="{wood}" stroke="{wood_d}" stroke-width="1"/>')
    for bxp in (0, W / 2 - 22, W - 44):
        o.append(f'<rect x="{x+bxp:.1f}" y="{G-ph+12}" width="44" height="28" fill="{wood_s}" stroke="{wood_d}" stroke-width="1"/>')
        o.append(f'<rect x="{x+bxp+8:.1f}" y="{G-ph+18}" width="28" height="12" fill="{wood}" opacity="0.6"/>')
    o.append(f'<text x="{x+22}" y="{G-ph+30}" text-anchor="middle" font-family="{k.text_font}" font-size="8" '
             f'font-weight="700" fill="{wood_d}">EPAL</text>')
    o.append(f'<rect x="{x}" y="{G-12}" width="{W}" height="12" fill="{wood}" stroke="{wood_d}" stroke-width="1"/>')
    # ---- cartons: top, side, front
    o.append(para(x, top, 1, 0, kraft_t))
    tp = " ".join([P(x, top), P(x + dx, top + dy), P(x + W + dx, top + dy), P(x + W, top)])
    o.append(f'<polygon points="{tp}" fill="{kraft_t}" stroke="#9C7B52" stroke-width="1"/>')
    for i in range(1, cols):
        o.append(f'<line x1="{x+i*cw}" y1="{top}" x2="{x+i*cw+dx}" y2="{top+dy}" stroke="#9C7B52" stroke-width="1"/>')
    o.append(f'<line x1="{x+dx/2}" y1="{top+dy/2}" x2="{x+W+dx/2}" y2="{top+dy/2}" stroke="#9C7B52" stroke-width="1"/>')
    for i in range(cols):          # brand tape on top flaps
        cx0 = x + i * cw + cw / 2
        o.append(f'<polygon points="{P(cx0-6, top)} {P(cx0-6+dx, top+dy)} {P(cx0+6+dx, top+dy)} {P(cx0+6, top)}" '
                 f'fill="{k.brand_bg}" opacity="0.9"/>')
    sp = " ".join([P(x + W, top), P(x + W + dx, top + dy), P(x + W + dx, G - ph + dy), P(x + W, G - ph)])
    o.append(f'<polygon points="{sp}" fill="{kraft_s}" stroke="#8C6C45" stroke-width="1"/>')
    for r in range(1, rows):
        yy = top + r * ch
        o.append(f'<line x1="{x+W}" y1="{yy}" x2="{x+W+dx}" y2="{yy+dy}" stroke="#8C6C45" stroke-width="1"/>')
    o.append(f'<line x1="{x+W+dx/2}" y1="{top+dy/2}" x2="{x+W+dx/2}" y2="{G-ph+dy/2}" stroke="#8C6C45" stroke-width="1"/>')
    for r in range(rows):
        for c in range(cols):
            cx0, cy0 = x + c * cw, top + r * ch
            o.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" fill="{kraft}" stroke="#9C7B52" stroke-width="1"/>')
            o.append(f'<rect x="{cx0+1}" y="{cy0+1}" width="{cw-2}" height="5" fill="#FFFFFF" opacity="0.12"/>')
            o.append(k.logo("mono", cx0 + 22, cy0 + 8, cw - 44, 30, color=ink, opacity=0.85))
            o.append(f'<text x="{cx0+cw/2}" y="{cy0+48}" text-anchor="middle" font-family="{k.text_font}" font-size="7.5" '
                     f'font-weight="700" letter-spacing="0.6" fill="{ink}" opacity="0.8">360 uds · L</text>')
    # corner boards
    o.append(f'<rect x="{x-3}" y="{top-2}" width="9" height="{rows*ch+4}" fill="#EDE9E1" stroke="#C8C2B6" stroke-width="1"/>')
    o.append(f'<rect x="{x+W-6}" y="{top-2}" width="9" height="{rows*ch+4}" fill="#EDE9E1" stroke="#C8C2B6" stroke-width="1"/>')
    # ---- stretch film
    fp = " ".join([P(x - 6, top + 26), P(x + W + 4, top + 26), P(x + W + dx + 4, top + 26 + dy),
                   P(x + W + dx + 4, G - ph + dy + 6), P(x + W + 4, G - ph + 8), P(x - 6, G - ph + 8)])
    fg, fgdef = _lingrad(k, [(0, "#FFFFFF", 0.42), (0.35, "#FFFFFF", 0.10), (0.6, "#FFFFFF", 0.28), (1, "#FFFFFF", 0.08)], 0, 0, 1, 0.3)
    o.append(fgdef)
    o.append(f'<polygon points="{fp}" fill="url(#{fg})" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="1.5"/>')
    for i, yy in enumerate(range(int(top + 50), int(G - ph), 34)):
        op = 0.35 if i % 2 else 0.22
        o.append(f'<path d="M{x-6},{yy} Q{x+W/2},{yy+5} {x+W+4},{yy+2} L{x+W+dx+4},{yy+2+dy}" '
                 f'fill="none" stroke="#FFFFFF" stroke-opacity="{op}" stroke-width="2"/>')
    o.append(f'<polygon points="{P(x+40, top+26)} {P(x+70, top+26)} {P(x+10, G-ph+8)} {P(x-6, G-ph+8)} {P(x-6, G-ph-40)}" '
             f'fill="#FFFFFF" opacity="0.16"/>')
    o.append(f'<polygon points="{P(x+W-60, top+26)} {P(x+W-44, top+26)} {P(x+W-150, G-ph+8)} {P(x+W-166, G-ph+8)}" '
             f'fill="#FFFFFF" opacity="0.12"/>')
    # ---- shipping label on the film
    lx, ly, lw, lh = x + W / 2 - 100, top + 96, 200, 150
    o.append(f'<rect x="{lx+3}" y="{ly+4}" width="{lw}" height="{lh}" rx="3" fill="#000" opacity="0.12"/>')
    o.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="3" fill="#FFFFFF" stroke="#D6D3CC" stroke-width="1"/>')
    hb = k.brand_bg
    o.append(f'<path d="M{lx},{ly+3} Q{lx},{ly} {lx+3},{ly} L{lx+lw-3},{ly} Q{lx+lw},{ly} {lx+lw},{ly+3} L{lx+lw},{ly+34} L{lx},{ly+34} Z" fill="{hb}"/>')
    o.append(k.logo("mono", lx + 6, ly + 4, 110, 26, color=k.on(hb), align="left"))
    o.append(f'<text x="{lx+lw-8}" y="{ly+15}" text-anchor="end" font-family="{k.text_font}" font-size="7.5" '
             f'font-weight="700" fill="{k.on(hb)}">PALET 04/12</text>'
             f'<text x="{lx+lw-8}" y="{ly+27}" text-anchor="end" font-family="{k.text_font}" font-size="7.5" '
             f'fill="{k.on(hb)}" opacity="0.85">2–6 °C</text>')
    t = lambda yy, s, sz=8, w="400", op=1: (f'<text x="{lx+8}" y="{yy}" font-family="{k.text_font}" font-size="{sz}" '
                                           f'font-weight="{w}" fill="#1C1B19" opacity="{op}">{s}</text>')
    o.append(t(ly + 47, "DESTINATARIO", 6.5, "700", 0.55))
    o.append(t(ly + 58, "Hotel Mirador S.A. · Muelle 3", 8.5, "700"))
    o.append(t(ly + 69, "Av. del Puerto 41 · 46024 Valencia", 7.5))
    o.append(f'<line x1="{lx+8}" y1="{ly+76}" x2="{lx+lw-8}" y2="{ly+76}" stroke="#1C1B19" stroke-opacity="0.25"/>')
    o.append(t(ly + 87, "Huevos frescos cat. A · L · 60 cajas", 7.5, "700"))
    o.append(t(ly + 98, "Lote L2611-04 · Cons. pref. 24/12/2026", 7.2, "400", 0.8))
    o.append(_barcode("sscc" + k.code, lx + 8, ly + 104, lw - 16, 30))
    o.append(f'<text x="{lx+lw/2}" y="{ly+lh-7}" text-anchor="middle" font-family="{k.text_font}" font-size="7" '
             f'letter-spacing="1.2" fill="#1C1B19">(00) 3 8412345 000012647 1</text>')
    return "".join(o)


def render(k, W=1680, H=700):
    G = 632
    van = _van(k, 92, G)
    pal = _pallet(k, 1236, G)
    return f'<g>{van}{pal}</g>'
