"""Деловая документация: бланк письма, счёт-фактура A4, конверты DL, визитки (лицо и оборот)."""
from html import escape

TITLE = "Деловая документация"
CAPTION = "Фирменный бланк и счёт-фактура A4, конверты DL и визитки сотрудника — лицо с паттерном и оборот с контактами."


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


def _place(cx, cy, w, h, rot, body, k, lift=1.0):
    """Предмет w×h с центром (cx,cy), повёрнутый на rot°, с мягкой тенью от света сверху-слева."""
    sh = ""
    for dx, dy, grow, op in ((2, 3, 0, 0.10), (5, 8, 3, 0.06), (9, 15, 8, 0.035), (14, 24, 14, 0.02)):
        dx, dy, grow = dx * lift, dy * lift, grow * lift
        sh += (f'<g transform="translate({cx+dx:.1f},{cy+dy:.1f}) rotate({rot})">'
               f'<rect x="{-w/2-grow/2:.1f}" y="{-h/2-grow/2:.1f}" width="{w+grow:.1f}" height="{h+grow:.1f}" '
               f'rx="{3+grow/2:.1f}" fill="#000" opacity="{op}"/></g>')
    return sh + f'<g transform="translate({cx},{cy}) rotate({rot}) translate({-w/2},{-h/2})">{body}</g>'


def _paper(k, w, h, base="#FFFFFF", rx=1.5):
    gid = k.uid("pp")
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{base}"/>'
            f'<stop offset="1" stop-color="{_mix(base, "#000000", 0.05)}"/></linearGradient>'
            f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{gid})"/>')


def _ctx(k):
    c = {}
    c["web"] = escape(k.t("contacts.web", "primeegg.es"))
    c["email"] = escape(k.t("contacts.email", "pedidos@primeegg.es"))
    c["phone"] = escape(k.t("contacts.phone", "+34 900 000 000"))
    c["addr"] = escape(k.t("contacts.address", "Polígono Industrial, Nave 12 · 28000 Madrid"))
    c["domain"] = c["email"].split("@")[-1] if "@" in c["email"] else c["web"]
    c["tag"] = escape(k.t("taglines.es", "Huevos frescos de granja"))
    c["hcol"] = k.primary if _contrast(k.primary, "#FFFFFF") >= 3 else k.dark
    c["acc"] = k.accent if _contrast(k.accent, "#FFFFFF") > 1.5 else k.primary
    return c


def _t(k, x, y, s, size=7, w="400", fill="#2B2A27", anchor="start", font=None, op=1, ls=0):
    f = font or k.text_font
    extra = f' letter-spacing="{ls}"' if ls else ""
    o = f' opacity="{op}"' if op != 1 else ""
    return (f'<text x="{x}" y="{y}" font-family="{f}" font-size="{size}" font-weight="{w}" fill="{fill}" '
            f'text-anchor="{anchor}"{extra}{o}>{s}</text>')


# ------------------------------------------------------------------- letterhead
def _letterhead(k, c, w, h):
    o = [_paper(k, w, h)]
    o.append(k.logo("horizontal", 30, 28, 170, 56, align="left"))
    for i, s in enumerate(["Primeegg Distribution SL", c["addr"], c["phone"], c["email"]]):
        o.append(_t(k, w - 28, 42 + i * 10, s, 6.2, "700" if i == 0 else "400", "#55534E", "end"))
    o.append(f'<rect x="30" y="100" width="{w-60}" height="1.2" fill="{c["acc"]}"/>')
    o.append(_t(k, w - 30, 128, "Madrid, 26 de noviembre de 2026", 7, fill="#55534E", anchor="end"))
    for i, s in enumerate(["Restaurante La Lonja SL", "A/A Dpto. de Compras", "C/ Mayor 12 · 28013 Madrid"]):
        o.append(_t(k, 30, 150 + i * 11, s, 7.2, "700" if i == 0 else "400"))
    o.append(_t(k, 30, 210, "Estimado cliente:", 7.5, "700"))
    y = 228
    for para in (7, 5, 6, 3):
        for j in range(para):
            ln = w - 60 - (0 if j < para - 1 else 120 + (para * 23) % 90)
            o.append(f'<rect x="30" y="{y}" width="{ln}" height="3.2" rx="1.6" fill="#D8D6D1"/>')
            y += 10
        y += 10
    o.append(_t(k, 30, y + 8, "Atentamente,", 7.2))
    o.append(f'<path d="M32,{y+34} c10,-14 18,6 26,-4 s12,-10 20,2 s10,4 18,-6" fill="none" stroke="{c["hcol"]}" stroke-width="1.2"/>')
    o.append(_t(k, 30, y + 52, "Lucía Martín · Responsable comercial", 7, "700"))
    o.append(k.pattern_rect(0, h - 22, w, 22, scale=0.35, opacity=0.9, bg=k.brand_bg, clip_rx=0))
    o.append(_t(k, w / 2, h - 32, f'{c["web"]}  ·  {c["phone"]}  ·  {c["email"]}', 6.2, fill="#77756F", anchor="middle"))
    return "".join(o)


# ------------------------------------------------------------------- invoice
def _invoice(k, c, w, h):
    o = [_paper(k, w, h)]
    bg = k.brand_bg
    onbg = k.on(bg)
    o.append(f'<rect width="{w}" height="6" fill="{bg}"/>')
    o.append(k.logo("horizontal", 28, 26, 160, 54, align="left"))
    o.append(_t(k, w - 28, 50, "FACTURA", 22, "700", c["hcol"], "end", k.head_font, ls=1.5))
    o.append(_t(k, w - 28, 64, "Nº F-2026/0418  ·  26/11/2026", 7, fill="#55534E", anchor="end"))
    o.append(_t(k, w - 28, 74, "Albarán A-11873  ·  Pedido 5520", 7, fill="#55534E", anchor="end"))
    # parties
    pb = mix_light = _mix(k.primary, "#FFFFFF", 0.93)
    o.append(f'<rect x="28" y="94" width="{(w-66)/2}" height="68" rx="3" fill="#F5F4F1"/>')
    o.append(f'<rect x="{28+(w-66)/2+10}" y="94" width="{(w-66)/2}" height="68" rx="3" fill="{pb}"/>')
    col2 = 28 + (w - 66) / 2 + 18
    o.append(_t(k, 36, 107, "EMISOR", 5.8, "700", "#8A8882", ls=1))
    o.append(_t(k, col2, 107, "CLIENTE", 5.8, "700", "#8A8882", ls=1))
    for i, s in enumerate(["Primeegg Distribution SL", "CIF B-00000000", c["addr"].replace(" · ", ", "), c["phone"]]):
        o.append(_t(k, 36, 120 + i * 10, s, 6.4 if i else 7, "700" if i == 0 else "400"))
    for i, s in enumerate(["Restaurante La Lonja SL", "CIF B-12345678", "C/ Mayor 12, 28013 Madrid", "compras@lalonja.es"]):
        o.append(_t(k, col2, 120 + i * 10, s, 6.4 if i else 7, "700" if i == 0 else "400"))
    # table
    ty = 178
    cols = [(36, "REF.", "start"), (86, "DESCRIPCIÓN", "start"), (w - 128, "CANT.", "end"),
            (w - 82, "PRECIO", "end"), (w - 36, "IMPORTE", "end")]
    o.append(f'<rect x="28" y="{ty}" width="{w-56}" height="18" rx="2" fill="{bg}"/>')
    for x, s, a in cols:
        o.append(_t(k, x, ty + 12, s, 6, "700", onbg, a, ls=0.8))
    rows = [("HF-L30", "Huevos frescos cat. A · L · bandeja 30", "40", "6,90", "276,00"),
            ("HF-M30", "Huevos frescos cat. A · M · bandeja 30", "25", "6,20", "155,00"),
            ("HC-XL12", "Huevos camperos XL · estuche 12", "60", "3,85", "231,00"),
            ("OP-HE5", "Huevo entero pasteurizado · bag 5 kg", "12", "18,40", "220,80"),
            ("OP-CL1", "Clara líquida pasteurizada · brik 1 kg", "20", "4,10", "82,00"),
            ("OP-PV1", "Huevo entero en polvo · bolsa 1 kg", "8", "14,50", "116,00")]
    zebra = _mix(k.primary, "#FFFFFF", 0.94)
    for i, r in enumerate(rows):
        yy = ty + 18 + i * 19
        if i % 2:
            o.append(f'<rect x="28" y="{yy}" width="{w-56}" height="19" fill="{zebra}"/>')
        for (x, _, a), s in zip(cols, r):
            o.append(_t(k, x, yy + 12.5, s, 6.6, "700" if x == 36 else "400", "#2B2A27", a))
        o.append(f'<rect x="28" y="{yy+18.6}" width="{w-56}" height="0.5" fill="#DAD8D3"/>')
    # totals
    yy = ty + 18 + len(rows) * 19 + 14
    tx = w - 170
    for i, (a, b) in enumerate([("Base imponible", "1.080,80 €"), ("IVA 4 %", "43,23 €")]):
        o.append(_t(k, tx, yy + i * 13, a, 6.8, fill="#55534E"))
        o.append(_t(k, w - 36, yy + i * 13, b, 6.8, anchor="end"))
    o.append(f'<rect x="{tx-8}" y="{yy+22}" width="{w-28-tx+8}" height="22" rx="2" fill="{bg}"/>')
    o.append(_t(k, tx, yy + 37, "TOTAL", 8, "700", onbg, ls=1))
    o.append(_t(k, w - 36, yy + 37, "1.124,03 €", 9.5, "700", onbg, "end"))
    # payment & notes
    o.append(_t(k, 36, yy, "FORMA DE PAGO", 5.8, "700", "#8A8882", ls=1))
    o.append(_t(k, 36, yy + 12, "Transferencia a 30 días", 6.6))
    o.append(_t(k, 36, yy + 23, "IBAN ES00 0000 0000 00 0000000000", 6.6))
    o.append(_t(k, 36, yy + 34, "Vencimiento: 26/12/2026", 6.6))
    ny = yy + 70
    o.append(f'<rect x="28" y="{ny}" width="{w-56}" height="0.8" fill="#DAD8D3"/>')
    o.append(_t(k, 36, ny + 14, "Producto conservado y transportado a 2–6 °C · Registro sanitario ES 00.00000/M", 6, fill="#77756F"))
    o.append(_t(k, 36, ny + 24, "Lotes: L2611-04, L2611-05, OP-2611-A · Código de granja 3ES28000001", 6, fill="#77756F"))
    o.append(f'<text x="{w/2}" y="{h-46}" text-anchor="middle" font-family="{k.head_font}" font-size="10" '
             f'font-style="italic" fill="{c["hcol"]}">{c["tag"]}</text>')
    o.append(f'<rect x="0" y="{h-30}" width="{w}" height="30" fill="{_mix(k.primary, "#FFFFFF", 0.92)}"/>')
    o.append(f'<rect x="0" y="{h-30}" width="{w}" height="1.5" fill="{c["acc"]}"/>')
    o.append(_t(k, w / 2, h - 18, "Primeegg Distribution SL · CIF B-00000000 · Inscrita en el Registro Mercantil de Madrid",
                5.6, fill="#66645F", anchor="middle"))
    o.append(_t(k, w / 2, h - 9, f'{c["web"]}  ·  {c["email"]}  ·  {c["phone"]}', 5.6, fill="#66645F", anchor="middle"))
    return "".join(o)


# ------------------------------------------------------------------- envelopes
def _env_front(k, c, w, h):
    o = [_paper(k, w, h, "#FFFFFF", 2)]
    o.append(k.logo("horizontal", 22, 18, 150, 50, align="left"))
    o.append(_t(k, 24, 80, "Primeegg Distribution SL", 6.4, "700", "#55534E"))
    o.append(_t(k, 24, 90, c["addr"], 6.2, fill="#77756F"))
    # postage indicia
    o.append(f'<rect x="{w-104}" y="18" width="82" height="44" rx="2" fill="none" stroke="#8A8882" stroke-width="0.9"/>')
    o.append(_t(k, w - 63, 34, "FRANQUEO", 6.2, "700", "#77756F", "middle", ls=1))
    o.append(_t(k, w - 63, 44, "PAGADO", 6.2, "700", "#77756F", "middle", ls=1))
    o.append(_t(k, w - 63, 55, "Autorización 28/0418", 5.2, fill="#8A8882", anchor="middle"))
    # window with address
    wx, wy, ww, wh = w - 250, h - 112, 220, 74
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="4" fill="#F1F3F4"/>')
    for i, s in enumerate(["Restaurante La Lonja SL", "A/A Dpto. de Compras", "C/ Mayor 12", "28013 Madrid"]):
        o.append(_t(k, wx + 18, wy + 20 + i * 12, s, 8, "700" if i == 0 else "400", "#3A3936"))
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="4" fill="#FFFFFF" opacity="0.28" stroke="#C9CDD0" stroke-width="1"/>')
    o.append(f'<path d="M{wx+8},{wy+wh-6} L{wx+60},{wy+6}" stroke="#FFFFFF" stroke-width="10" opacity="0.4"/>')
    o.append(k.pattern_rect(0, h - 14, w, 14, scale=0.25, opacity=0.9, bg=k.brand_bg, clip_rx=0))
    return "".join(o)


def _env_back(k, c, w, h):
    o = [_paper(k, w, h, "#FFFFFF", 2)]
    bg = k.brand_bg
    fp = f"M0,0 L{w},0 L{w/2+18},{h*0.56} Q{w/2},{h*0.62} {w/2-18},{h*0.56} Z"
    cid = k.uid("flap")
    o.append(f'<path d="M0,{h} L{w*0.46},{h*0.48} M{w},{h} L{w*0.54},{h*0.48}" stroke="#DAD8D3" stroke-width="1.2" fill="none"/>')
    o.append(f'<path d="{fp}" fill="#000" opacity="0.05" transform="translate(0,3)"/>')
    o.append(f'<clipPath id="{cid}"><path d="{fp}"/></clipPath>')
    o.append(f'<path d="{fp}" fill="{bg}"/>')
    o.append(f'<g clip-path="url(#{cid})">{k.pattern_rect(0, 0, w, h*0.62, scale=0.45, opacity=0.22, color=k.on(bg))}</g>')
    o.append(k.logo("mono", w / 2 - 48, h * 0.12, 96, 70, color=k.on(bg)))
    o.append(_t(k, w / 2, h - 22, c["web"], 8, "700", c["hcol"], "middle", ls=1))
    return "".join(o)


# ------------------------------------------------------------------- business cards
def _card_front(k, c, w, h):
    bg = k.brand_bg
    o = [f'<rect width="{w}" height="{h}" rx="6" fill="{bg}"/>']
    o.append(k.pattern_rect(0, 0, w, h, scale=0.5, opacity=0.16, color=k.on(bg), clip_rx=6))
    gid = k.uid("cg")
    o.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.10"/>'
             f'<stop offset="1" stop-color="#000000" stop-opacity="0.10"/></linearGradient>'
             f'<rect width="{w}" height="{h}" rx="6" fill="url(#{gid})"/>')
    o.append(k.logo("mono", w * 0.15, h * 0.17, w * 0.7, h * 0.66, color=k.on(bg)))
    return "".join(o)


def _card_back(k, c, w, h):
    o = [_paper(k, w, h, "#FFFFFF", 6)]
    o.append(f'<path d="M0,6 Q0,0 6,0 L10,0 L10,{h} L6,{h} Q0,{h} 0,{h-6} Z" fill="{k.brand_bg}"/>')
    o.append(k.logo("mark", w - 66, 18, 46, 46))
    o.append(_t(k, 30, 46, "Lucía Martín", 19, "700", c["hcol"], font=k.head_font))
    o.append(_t(k, 30, 63, "Responsable comercial", 9, fill="#6B6A66", ls=0.4))
    o.append(f'<rect x="30" y="76" width="34" height="2.5" rx="1" fill="{c["acc"]}"/>')
    lines = ["+34 600 123 456", f'lucia.martin@{c["domain"]}', c["web"], c["addr"]]
    for i, s in enumerate(lines):
        o.append(f'<circle cx="34" cy="{101+i*16}" r="2.4" fill="{c["acc"]}"/>')
        o.append(_t(k, 44, 104 + i * 16, s, 8.4 if i < 3 else 7.4, "700" if i == 0 else "400", "#33322F"))
    o.append(_t(k, 30, h - 12, "Primeegg Distribution SL", 6.4, "700", "#9A9893", ls=1))
    return "".join(o)


def _card(body, w, h):
    edge = f'<rect x="0" y="1.6" width="{w}" height="{h}" rx="6" fill="#000" opacity="0.14"/>'
    return edge + body


def render(k, W=1680, H=700):
    c = _ctx(k)
    aw, ah = 384, 543                                   # A4 1:1.414
    o = []
    o.append(_place(300, 352, aw, ah, -5.5, _letterhead(k, c, aw, ah), k))
    o.append(_place(535, 362, aw, ah, 2.5, _invoice(k, c, aw, ah), k, lift=1.3))
    ew, eh = 440, 220                                   # DL 220×110
    o.append(_place(965, 238, ew, eh, -5, _env_back(k, c, ew, eh), k))
    o.append(_place(1010, 470, ew, eh, 2, _env_front(k, c, ew, eh), k, lift=1.2))
    cw, ch = 300, 194                                   # 85×55
    o.append(_place(1438, 238, cw, ch, -7, _card(_card_front(k, c, cw, ch), cw, ch), k, lift=0.8))
    o.append(_place(1420, 470, cw, ch, 4, _card(_card_back(k, c, cw, ch), cw, ch), k, lift=1.0))
    return "".join(o)
