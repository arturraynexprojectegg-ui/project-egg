"""Униформа: поло с логотипом на груди, фартук с нагрудником и карманом, кепка в 3/4."""

TITLE = "Униформа"
CAPTION = "Поло с вышитым логотипом, фартук с нагрудником и карманом для персонала HoReCa и склада, бейсболка со знаком."


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


def _shade(k, base, gid_p="g", horiz=True):
    """Градиент ткани: свет слева-сверху, тень справа."""
    gid = k.uid(gid_p)
    x2, y2 = ("1", "0.25") if horiz else ("0", "1")
    return gid, (f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
                 f'<stop offset="0" stop-color="{_mix(base, "#FFFFFF", 0.10)}"/>'
                 f'<stop offset="0.45" stop-color="{base}"/>'
                 f'<stop offset="1" stop-color="{_mix(base, "#000000", 0.18)}"/></linearGradient>')


def _drop(path, op=0.10):
    """Мягкая тень предмета, лежащего на фоне (без filter): несколько смещённых копий силуэта."""
    return "".join(f'<path d="{path}" fill="#000" opacity="{o}" transform="translate({dx},{dy})"/>'
                   for dx, dy, o in ((4, 6, op), (9, 14, op * 0.55), (15, 24, op * 0.3)))


def _stitch(d, color, op=0.55, w=1.3):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="5 3.5" '
            f'stroke-linecap="round" opacity="{op}"/>')


# ------------------------------------------------------------------- polo
def _polo(k, cx, y0, col):
    o = []
    on = k.on(col)
    trim = k.accent if _contrast(k.accent, col) > 1.6 else (k.light if _contrast(k.light, col) > 1.6 else k.dark)
    body = (f"M-58,10 L-150,32 C-188,44 -218,86 -244,156 L-184,186 L-170,168 "
            f"C-168,280 -172,390 -170,476 Q-168,486 -156,487 Q0,496 156,487 Q168,486 170,476 "
            f"C172,390 168,280 170,168 L184,186 L244,156 C218,86 188,44 150,32 L58,10 Z")
    o.append(f'<g transform="translate({cx},{y0})">')
    o.append(_drop(body, 0.09))
    gid, gdef = _shade(k, col)
    o.append(gdef)
    o.append(f'<path d="{body}" fill="url(#{gid})"/>')
    # sleeve cuffs with tipping
    for s in (-1, 1):
        cuff = f"M{s*244},156 L{s*184},186 L{s*178},174 L{s*236},142 Z"
        o.append(f'<path d="{cuff}" fill="{_mix(col, "#000000", 0.08)}"/>')
        o.append(f'<path d="M{s*240},149 L{s*181},180" stroke="{trim}" stroke-width="2.4"/>')
        o.append(_stitch(f"M{s*231},135 L{s*176},164", on, 0.35, 1))
        # sleeve seam
        o.append(f'<path d="M{s*150},32 C{s*160},80 {s*166},130 {s*170},168" fill="none" stroke="#000" stroke-opacity="0.14" stroke-width="1.5"/>')
    # soft folds & creases
    sg = k.uid("sf")
    o.append(f'<linearGradient id="{sg}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0.16"/></linearGradient>')
    o.append(f'<path d="M110,170 C118,280 112,390 118,484 Q150,486 156,487 Q168,486 170,476 C172,390 168,280 170,168 Z" fill="url(#{sg})"/>')
    for d, op in (("M-168,196 C-150,210 -140,232 -138,262", 0.10), ("M168,196 C150,214 142,236 140,270", 0.12),
                  ("M-120,420 C-100,440 -96,462 -98,482", 0.07), ("M60,430 C70,450 72,468 70,486", 0.07)):
        o.append(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="{op}" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<path d="M-130,250 C-120,320 -126,380 -112,440" fill="none" stroke="#FFFFFF" stroke-opacity="0.07" stroke-width="16" stroke-linecap="round"/>')
    o.append(_stitch("M-166,462 Q0,472 166,462", on, 0.35, 1))
    # back collar band & inner neck
    ccol = _mix(col, "#FFFFFF", 0.07)
    o.append(f'<path d="M-62,14 C-60,-18 60,-18 62,14 Q0,-2 -62,14 Z" fill="{ccol}" stroke="#000" stroke-opacity="0.18" stroke-width="1"/>')
    o.append(f'<path d="M-56,14 Q0,0 56,14 L16,58 L-16,58 Z" fill="{_mix(col, "#000000", 0.30)}"/>')
    o.append(f'<rect x="-16" y="56" width="32" height="104" fill="{_mix(col, "#000000", 0.05)}"/>')
    o.append(f'<path d="M-16,56 V160 H16 V56" fill="none" stroke="#000" stroke-opacity="0.18" stroke-width="1.4"/>')
    o.append(_stitch("M-10,62 V154 H10 V62", on, 0.35, 0.9))
    for by in (78, 108, 138):
        o.append(f'<circle cx="0" cy="{by}" r="5.2" fill="{_mix(col, "#FFFFFF", 0.25)}" stroke="#000" stroke-opacity="0.25" stroke-width="0.8"/>')
        o.append(f'<circle cx="-1.6" cy="{by}" r="0.9" fill="#000" opacity="0.4"/><circle cx="1.6" cy="{by}" r="0.9" fill="#000" opacity="0.4"/>')
    for s_ in (-1, 1):
        wing = f"M{s_*62},10 L{s_*86},30 Q{s_*66},66 {s_*34},104 L{s_*6},58 Q{s_*28},30 {s_*58},14 Z"
        o.append(f'<path d="{wing}" fill="#000" opacity="0.16" transform="translate({s_*4},5)"/>')
        o.append(f'<path d="{wing}" fill="{ccol}" stroke="#000" stroke-opacity="0.2" stroke-width="1"/>')
        o.append(f'<path d="M{s_*80},33 Q{s_*62},66 {s_*36},96" fill="none" stroke="{trim}" stroke-width="2.6"/>')
        o.append(f'<path d="M{s_*75},35 Q{s_*58},66 {s_*34},90" fill="none" stroke="{trim}" stroke-width="1.3" opacity="0.8"/>')
    # chest logo (wearer's left)
    o.append(k.logo("mono", 50, 104, 92, 70, color=on))
    o.append("</g>")
    return "".join(o)


# ------------------------------------------------------------------- apron
def _apron(k, cx, y0, col, strap, sc=0.84):
    o = []
    on = k.on(col)
    body = ("M-78,0 L78,0 C82,90 118,168 160,204 L174,560 Q0,568 -174,560 L-160,204 "
            "C-118,168 -82,90 -78,0 Z")
    o.append(f'<g transform="translate({cx},{y0}) scale({sc})">')
    # neck strap (behind)
    o.append(f'<path d="M-66,6 C-72,-70 -40,-104 0,-104 C40,-104 72,-70 66,6" fill="none" stroke="{_mix(strap, "#000000", 0.2)}" stroke-width="15"/>')
    o.append(f'<path d="M-66,6 C-72,-70 -40,-104 0,-104 C40,-104 72,-70 66,6" fill="none" stroke="{strap}" stroke-width="11"/>')
    o.append(_stitch("M-66,6 C-72,-70 -40,-104 0,-104 C40,-104 72,-70 66,6", "#000000", 0.18, 0.8))
    # waist ties (hanging)
    for s in (-1, 1):
        tie = f"M{s*162},214 C{s*196},220 {s*214},240 {s*210},300 C{s*206},340 {s*216},370 {s*212},404"
        o.append(f'<path d="{tie}" fill="none" stroke="#000" stroke-opacity="0.08" stroke-width="14" transform="translate(6,8)"/>')
        o.append(f'<path d="{tie}" fill="none" stroke="{strap}" stroke-width="11" stroke-linecap="round"/>')
        o.append(f'<path d="{tie}" fill="none" stroke="#000" stroke-opacity="0.12" stroke-width="2" transform="translate({s*3},0)"/>')
    o.append(_drop(body, 0.09))
    gid, gdef = _shade(k, col)
    o.append(gdef)
    o.append(f'<path d="{body}" fill="url(#{gid})"/>')
    # soft vertical folds
    for x, w, op, c in ((-110, 22, 0.05, "#000"), (-60, 14, 0.04, "#FFF"), (40, 18, 0.05, "#000"), (110, 24, 0.04, "#FFF")):
        o.append(f'<path d="M{x},380 C{x+4},450 {x-4},510 {x+2},556" fill="none" stroke="{c}" stroke-opacity="{op}" '
                 f'stroke-width="{w}" stroke-linecap="round"/>')
    # strap attachments (bar-tacks)
    for s in (-1, 1):
        o.append(f'<rect x="{s*66-8}" y="0" width="16" height="16" fill="{strap}"/>')
        o.append(f'<path d="M{s*66-6},4 L{s*66+6},12 M{s*66+6},4 L{s*66-6},12" stroke="#000" stroke-opacity="0.25" stroke-width="1"/>')
        o.append(f'<rect x="{s*167-7 if s>0 else -174}" y="204" width="14" height="20" fill="{strap}"/>')
    # hems
    o.append(_stitch("M-72,9 L72,9", on, 0.5))
    o.append(_stitch("M-71,12 C-75,96 -110,176 -152,212 L-165,552", on, 0.45))
    o.append(_stitch("M71,12 C75,96 110,176 152,212 L165,552", on, 0.45))
    o.append(_stitch("M-166,551 Q0,559 166,551", on, 0.5))
    # embroidered logo on the bib
    o.append(k.logo("mono", -72, 36, 144, 120, color=on))
    # front pocket
    px0, py0, pw, ph = -134, 300, 268, 130
    pk = _mix(col, "#000000", 0.07)
    o.append(f'<rect x="{px0}" y="{py0+4}" width="{pw}" height="{ph}" rx="4" fill="#000" opacity="0.10"/>')
    o.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="4" fill="{pk}"/>')
    o.append(k.pattern_rect(px0, py0, pw, 26, scale=0.3, opacity=0.35, color=on, clip_rx=3))
    o.append(f'<rect x="{px0}" y="{py0+26}" width="{pw}" height="1.2" fill="#000" opacity="0.15"/>')
    o.append(_stitch(f"M{px0+6},{py0+5} H{px0+pw-6}", on, 0.5, 1.1))
    o.append(_stitch(f"M{px0+6},{py0+31} V{py0+ph-6} H{px0+pw-6} V{py0+31}", on, 0.5, 1.1))
    for dx in (pw * 0.36, pw * 0.70):
        o.append(_stitch(f"M{px0+dx:.0f},{py0+31} V{py0+ph-6}", on, 0.45, 1.1))
    # pen in the narrow compartment
    pxp = px0 + pw * 0.53
    o.append(f'<rect x="{pxp-4:.0f}" y="{py0-30}" width="8" height="40" rx="3" fill="#2A2A2A"/>'
             f'<rect x="{pxp-1:.0f}" y="{py0-26}" width="2" height="24" rx="1" fill="#C9CDD1"/>')
    # woven label with accent
    lab = k.accent if _contrast(k.accent, col) > 1.5 else k.light
    o.append(f'<rect x="{px0+pw-44}" y="{py0+ph-30}" width="30" height="14" rx="1.5" fill="{lab}"/>')
    o.append(k.logo("mark", px0 + pw - 41, py0 + ph - 29, 24, 12, color=k.on(lab)))
    o.append("</g>")
    return "".join(o)


# ------------------------------------------------------------------- cap
def _cap(k, cx, cy, s, crown, visor):
    """Бейсболка в 3/4: перед повёрнут влево, козырёк выступает вперёд-влево."""
    o = [f'<g transform="translate({cx},{cy}) scale({s})">']
    dome = "M-132,10 C-146,-64 -104,-146 -14,-154 C80,-160 142,-100 138,-8 C100,12 -70,26 -132,10 Z"
    vis = "M-134,8 C-182,36 -170,104 -70,112 C6,118 64,88 72,22 C20,32 -70,30 -134,8 Z"
    o.append(_drop(dome, 0.08) + _drop(vis, 0.11))
    rg = k.uid("cr")
    o.append(f'<radialGradient id="{rg}" cx="0.30" cy="0.22" r="0.9"><stop offset="0" stop-color="{_mix(crown, "#FFFFFF", 0.3)}"/>'
             f'<stop offset="0.55" stop-color="{crown}"/><stop offset="1" stop-color="{_mix(crown, "#000000", 0.22)}"/></radialGradient>')
    o.append(f'<path d="{dome}" fill="url(#{rg})"/>')
    on = k.on(crown)
    # side shading (turned away from light)
    sg = k.uid("cs")
    o.append(f'<linearGradient id="{sg}" x1="0" y1="0" x2="1" y2="0"><stop offset="0.45" stop-color="#000" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="#000" stop-opacity="0.14"/></linearGradient><path d="{dome}" fill="url(#{sg})"/>')
    seams = ("M-4,-154 C-58,-126 -74,-56 -66,24", "M-4,-154 C-104,-128 -134,-56 -132,10",
             "M-4,-154 C30,-118 50,-60 52,24", "M-4,-154 C84,-136 132,-80 138,-8")
    for d in seams:
        o.append(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.17" stroke-width="1.6"/>')
    for d in ("M-12,-150 C-66,-120 -82,-54 -75,22", "M-14,-152 C-106,-122 -138,-56 -136,6",
              "M4,-150 C36,-116 58,-60 60,24", "M6,-152 C88,-132 128,-80 132,-8"):
        o.append(_stitch(d, on, 0.28, 0.9))
    for ex, ey in ((-100, -92), (22, -112), (104, -70)):
        o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="4.4" ry="3.4" fill="{_mix(crown, "#000000", 0.35)}" '
                 f'stroke="{_mix(crown, "#000000", 0.12)}" stroke-width="2"/>')
    o.append(f'<ellipse cx="-4" cy="-154" rx="13" ry="5.5" fill="{visor}"/>'
             f'<ellipse cx="-7" cy="-156" rx="7" ry="2.2" fill="#FFF" opacity="0.28"/>')
    # front logo across the two front panels, foreshortened
    o.append(f'<g transform="translate(-66,-62) skewY(-4) scale(0.86,1)">{k.logo("mark", -60, -50, 120, 100)}</g>')
    o.append(f'<path d="M-116,-28 C-110,-88 -78,-128 -36,-142" fill="none" stroke="#FFF" stroke-opacity="0.25" '
             f'stroke-width="9" stroke-linecap="round"/>')
    o.append(f'<path d="M-132,10 C-70,26 100,12 138,-8" fill="none" stroke="{_mix(crown, "#000000", 0.32)}" stroke-width="3"/>')
    # visor
    vg = k.uid("vg")
    o.append(f'<linearGradient id="{vg}" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="{_mix(visor, "#FFFFFF", 0.14)}"/>'
             f'<stop offset="1" stop-color="{_mix(visor, "#000000", 0.2)}"/></linearGradient>')
    o.append(f'<path d="{vis}" fill="url(#{vg})"/>')
    o.append(f'<path d="M-134,8 C-70,30 20,32 72,22" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="2"/>')
    for i in range(4):
        t = 7 + i * 7
        o.append(f'<path d="M{-140+i*3},{14+i*2} C{-172+t},{40+i*2} {-160+t},{102-t} -70,{108-t*0.8:.0f} '
                 f'C{4},{112-t*0.9:.0f} {58-t*0.6:.0f},{84-t*0.4:.0f} {66-t*0.3:.0f},{26+i}" fill="none" stroke="{k.on(visor)}" '
                 f'stroke-width="1" stroke-dasharray="5 3.5" opacity="0.32"/>')
    o.append(f'<path d="M-150,44 C-140,80 -110,96 -66,100" fill="none" stroke="#FFF" stroke-opacity="0.2" '
             f'stroke-width="6" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def render(k, W=1680, H=700):
    bg = k.brand_bg
    dark = k.dark
    polo = bg if _lum(bg) < 0.55 else k.primary
    apron = dark if _contrast(dark, polo) > 1.25 else _mix(dark, "#000000", 0.25)
    strap = k.accent if _contrast(k.accent, apron) > 1.6 else k.light
    crown = k.light
    visor = bg
    o = [_polo(k, 330, 110, polo), _apron(k, 850, 186, apron, strap)]
    o.append(_cap(k, 1370, 440, 1.45, crown, visor))
    return "".join(o)
