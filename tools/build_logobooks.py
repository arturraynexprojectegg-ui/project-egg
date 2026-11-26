#!/usr/bin/env python3
"""Собирает логобуки из logobooks/PE-xx.yy/{data.json, *.svg}.
Выход в каждой папке:
  PE-xx.yy_Logobook.html       — страница (слайды 1920×1080 inline SVG, адаптивно)
  PE-xx.yy_Logobook_Figma.svg  — все слайды одним SVG для импорта в Figma (текст запечён)
Запуск: python3 tools/build_logobooks.py [PE-01.05 ...] [--no-figma]"""
import json, re, sys, html, colorsys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chrome_util import chrome_eval, bake_for_figma, fonts_href, used_families

ROOT = Path(__file__).resolve().parent.parent
LB = ROOT / "logobooks"
W, H, M = 1920, 1080, 120
GAPY = 120                     # расстояние между слайдами на Figma-борде
FIG_COLS = 3
TEXT = "Inter, Helvetica, Arial, sans-serif"
VB = {"primary": (400, 300), "horizontal": (640, 200), "vertical": (400, 400), "mark": (200, 200),
      "wordmark": (640, 160), "mono": (400, 300), "inverse": (400, 300)}
TODAY = date.today().strftime("%d.%m.%Y")


# ---------------------------------------------------------------- helpers
def esc(s): return html.escape(str(s), quote=True)


def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02X}" for i in (0, 2, 4))


def wrap(text, width, size, k=0.53):
    maxc = max(8, int(width / (size * k)))
    out, cur = [], ""
    for w in str(text).split():
        if cur and len(cur) + 1 + len(w) > maxc:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out


def T(x, y, s, size=24, weight=400, fill="#000", family=TEXT, anchor="start", ls=0, italic=False, extra=""):
    st = ' font-style="italic"' if italic else ""
    lsa = f' letter-spacing="{ls}"' if ls else ""
    an = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{esc(family)}" font-size="{size}" font-weight="{weight}"'
            f' fill="{fill}"{an}{lsa}{st}{extra}>{esc(s)}</text>')


def para(x, y, text, width, size=24, lh=1.5, **kw):
    lines = wrap(text, width, size)
    return "".join(T(x, y + i * size * lh, l, size, **kw) for i, l in enumerate(lines)), y + len(lines) * size * lh


class Book:
    def __init__(self, folder: Path):
        self.dir = folder
        self.d = json.loads((folder / "data.json").read_text())
        self.code = self.d["code"]
        self.comp = {}
        for k in VB:
            p = folder / f"{k}.svg"
            if p.exists():
                self.comp[k] = p.read_text()
        self.uid = 0
        pal = self.d["palette"]
        by_l = sorted(pal, key=lambda c: lum(c["hex"]))
        self.ink = by_l[0]["hex"] if lum(by_l[0]["hex"]) < 0.08 else "#1C1B19"
        self.paper = "#FBFAF7"
        self.accent = pal[0]["hex"]
        if lum(self.accent) > 0.6:          # слишком светлый акцент для текста
            self.accent = next((c["hex"] for c in pal if lum(c["hex"]) < 0.35), self.ink)
        self.muted = mix(self.ink, self.paper, 0.45)
        self.line = mix(self.ink, self.paper, 0.85)
        self.tint = mix(self.accent, "#FFFFFF", 0.9)
        f = self.d.get("fonts", [])
        from brandkit import pick_font
        self.head_font = pick_font(f, "заголов", 1, "Fraunces") + ", Georgia, serif"
        self.measure = {}

    # вставка компонента в бокс с сохранением пропорций
    def place(self, key, bx, by, bw, bh, color=None, align="center", extra_tf=""):
        src = self.comp.get(key) or self.comp["primary"]
        vw, vh = VB[key] if key in self.comp else VB["primary"]
        m = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S)
        body = re.sub(r"<title>.*?</title>", "", m.group(1), flags=re.S)
        self.uid += 1
        pre = f"{self.code.replace('.', '')}u{self.uid}"
        for x in sorted(set(re.findall(r'\bid="([^"]+)"', body)), key=len, reverse=True):
            body = body.replace(f'id="{x}"', f'id="{pre}-{x}"').replace(f"#{x})", f"#{pre}-{x})") \
                       .replace(f'href="#{x}"', f'href="#{pre}-{x}"')
        if color:
            body = body.replace("currentColor", color)
        s = min(bw / vw, bh / vh)
        ox = bx + (bw - vw * s) / 2 if align == "center" else bx
        oy = by + (bh - vh * s) / 2
        return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({s:.4f}){extra_tf}">{body}</g>', (ox, oy, s)

    # общий каркас слайда
    def frame(self, n, total, title, content, bg=None, dark=False):
        bg = bg or self.paper
        ink = "#FFFFFF" if dark else self.ink
        mut = mix(bg, "#FFFFFF", 0.55) if dark else self.muted
        head = (T(M, 92, f"PRIMEEGG · {getattr(self, 'kind', 'ЛОГОБУК')} · {self.code}", 18, 600, mut, ls=3) +
                T(W - M, 92, f"{n:02d} / {total:02d}", 18, 600, mut, anchor="end", ls=2) +
                (T(M, 196, title, 60, 600, ink, self.head_font) if title else "") +
                T(M, H - 64, self.d["name"], 18, 500, mut) +
                T(W - M, H - 64, f"Primeegg Distribution SL · {TODAY}", 18, 500, mut, anchor="end"))
        return f'<rect width="{W}" height="{H}" fill="{bg}"/>{head}{content}'

    # ------------------------------------------------------------ слайды
    def s_cover(self):
        d = self.d
        c = f'<rect x="{W*0.52:.0f}" y="0" width="{W*0.48:.0f}" height="{H}" fill="#FFFFFF"/>'
        c += f'<rect x="{W*0.52:.0f}" y="0" width="6" height="{H}" fill="{self.accent}"/>'
        logo, _ = self.place("primary", W * 0.52 + 80, 200, W * 0.48 - 160, H - 400)
        c += logo
        c += T(M, 300, "ЛОГОБУК", 22, 700, self.accent, ls=6)
        tl = wrap(d["name"], 780, 72, 0.62)
        for j, l in enumerate(tl[:2]):
            c += T(M, 400 + j * 84, l, 72, 600, self.ink, self.head_font)
        dy = (min(2, len(tl)) - 1) * 84
        c += T(M, 460 + dy, d.get("name_en", ""), 30, 400, self.muted, self.head_font, italic=True)
        p, yy = para(M, 560 + dy, d.get("tagline", ""), 780, 30, 1.45, fill=self.ink)
        c += p
        c += f'<line x1="{M}" y1="{H-210}" x2="{W*0.52-M:.0f}" y2="{H-210}" stroke="{self.line}" stroke-width="2"/>'
        c += T(M, H - 160, "Primeegg Distribution SL", 24, 600, self.ink)
        c += T(M, H - 124, f"Концепт {self.code} · версия 1.0 · {TODAY}", 22, 400, self.muted)
        return c

    def s_concept(self):
        d = self.d
        c, y = "", 300
        for ptxt in d.get("story", []):
            p, y = para(M, y, ptxt, 820, 26, 1.55, fill=self.ink)
            c += p; y += 30
        # правая колонка: знак + элементы
        bx = 1080
        c += f'<rect x="{bx}" y="250" width="{W-M-bx}" height="320" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
        logo, _ = self.place("mark", bx + 40, 275, W - M - bx - 80, 270)
        c += logo
        ey = 630
        c += T(bx, ey, "ЭЛЕМЕНТЫ ЗНАКА", 18, 700, self.accent, ls=3)
        ey += 46
        nw, mw = 250, W - M - bx - 270
        for e in d.get("elements", [])[:4]:
            nl = wrap(e["element"], nw, 23, 0.62)
            ml = wrap(e["meaning"], mw, 21)
            for j, l in enumerate(nl):
                c += T(bx, ey + j * 30, l, 23, 600, self.ink)
            for j, l in enumerate(ml):
                c += T(bx + 270, ey + j * 30, l, 21, 400, self.muted)
            ey += max(len(nl), len(ml)) * 30 + 22
        return self.frame(2, self.total, "Концепция", c)

    def s_primary(self):
        c = f'<rect x="{M}" y="250" width="{W-2*M}" height="640" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
        logo, _ = self.place("primary", M + 200, 280, W - 2 * M - 400, 580)
        c += logo
        c += T(M, 950, "Основная версия логотипа. Используется по умолчанию на всех носителях, где позволяет место и фон.",
               24, 400, self.muted)
        return self.frame(3, self.total, "Основной логотип", c)

    def s_versions(self):
        tiles = [("horizontal", "Горизонтальная", "Шапка сайта, накладные, борт фургона"),
                 ("vertical", "Вертикальная", "Упаковка, стенды, квадратные форматы"),
                 ("mark", "Знак", "Иконка, фавикон, штамп на яйце, соцсети"),
                 ("wordmark", "Надпись", "Узкие форматы, текстовые упоминания")]
        c, gap = "", 40
        tw, th = (W - 2 * M - gap) / 2, 250
        for i, (k, name, use) in enumerate(tiles):
            x = M + (i % 2) * (tw + gap)
            y = 240 + (i // 2) * (th + 110)
            c += f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
            logo, _ = self.place(k, x + 40, y + 24, tw - 80, th - 48)
            c += logo
            c += T(x, y + th + 40, name, 26, 600, self.ink) + T(x + 260, y + th + 40, use, 21, 400, self.muted)
        return self.frame(4, self.total, "Версии логотипа", c)

    def s_clear(self):
        mb = self.measure.get("primary")
        u = float(self.d.get("clear_space", {}).get("unit", 20))
        bx, by, bw, bh = (mb["x"], mb["y"], mb["width"], mb["height"]) if mb else (24, 24, 352, 252)
        # масштаб: логотип+поля по центру области
        area = (M, 250, 1060, 680)
        tot_w, tot_h = bw + 2 * u, bh + 2 * u
        s = min((area[2] - 80) / tot_w, (area[3] - 80) / tot_h)
        ox = area[0] + (area[2] - tot_w * s) / 2 - (bx - u) * s
        oy = area[1] + (area[3] - tot_h * s) / 2 - (by - u) * s
        X = lambda v: ox + v * s
        Y = lambda v: oy + v * s
        c = f'<rect x="{area[0]}" y="{area[1]}" width="{area[2]}" height="{area[3]}" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
        c += (f'<rect x="{X(bx-u):.1f}" y="{Y(by-u):.1f}" width="{tot_w*s:.1f}" height="{tot_h*s:.1f}" fill="{self.tint}" '
              f'stroke="{self.accent}" stroke-width="2" stroke-dasharray="10 8"/>')
        c += (f'<rect x="{X(bx):.1f}" y="{Y(by):.1f}" width="{bw*s:.1f}" height="{bh*s:.1f}" fill="#FFFFFF" '
              f'stroke="{self.accent}" stroke-width="1.5"/>')
        m = re.search(r"<svg[^>]*>(.*)</svg>", self.comp["primary"], re.S)
        logo, _ = self.place("primary", 0, 0, 400, 300)
        c += f'<g transform="translate({ox:.2f},{oy:.2f}) scale({s:.4f})">{logo}</g>'
        # модули x по углам
        us = u * s
        for (cx, cy) in [(X(bx - u), Y(by - u)), (X(bx + bw), Y(by - u)), (X(bx - u), Y(by + bh)), (X(bx + bw), Y(by + bh))]:
            c += f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{us:.1f}" height="{us:.1f}" fill="{self.accent}" fill-opacity="0.18" stroke="{self.accent}" stroke-width="1.5"/>'
            c += T(cx + us / 2, cy + us / 2 + min(26, us * 0.45) * 0.36, "x", min(26, us * 0.45), 600, self.accent, anchor="middle")
        rx = 1260
        c += T(rx, 300, "ОХРАННОЕ ПОЛЕ", 18, 700, self.accent, ls=3)
        p, y = para(rx, 350, f"Минимальное свободное пространство вокруг логотипа равно 1x, где x — "
                              f"{self.d.get('clear_space', {}).get('unit_name', 'модуль')}.", W - M - rx, 26, 1.5, fill=self.ink)
        c += p
        p, y = para(rx, y + 24, "В охранное поле не заходят текст, края носителя, другие логотипы и активные элементы фона. "
                                "При увеличении логотипа поле масштабируется пропорционально.", W - M - rx, 22, 1.5, fill=self.muted)
        c += p
        return self.frame(5, self.total, "Охранное поле", c)

    def s_minsize(self):
        ms = self.d.get("min_size", {})
        c = f'<rect x="{M}" y="250" width="1000" height="660" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
        c += T(M + 48, 310, "ОСНОВНОЙ ЛОГОТИП", 18, 700, self.accent, ls=3)
        mn = ms.get("screen_px", 80)
        k = min(1.0, max(0.0, ((1000 - 96 - 120) / mn - 4) / 5.6))
        sizes = [mn * (1 + k * f) for f in (2.6, 1.8, 1.2)] + [mn]
        x = M + 48
        for i, wpx in enumerate(sizes):
            hpx = wpx * 0.75
            logo, _ = self.place("primary", x, 560 - hpx / 2, wpx, hpx)
            c += logo
            c += T(x + wpx / 2, 790, f"{int(wpx)} px" if i < 3 else f"мин. {int(wpx)} px", 20, 600 if i == 3 else 400,
                   self.ink if i == 3 else self.muted, anchor="middle")
            x += wpx + 40
        c += T(M + 48, 860, f"Печать: ширина не менее {ms.get('print_mm', 20)} мм. Экран: не менее {ms.get('screen_px', 80)} px.",
               22, 500, self.ink)
        rx = 1180
        c += f'<rect x="{rx}" y="250" width="{W-M-rx}" height="660" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
        c += T(rx + 48, 310, "ЗНАК", 18, 700, self.accent, ls=3)
        x = rx + 48
        for px in (128, 64, 32, 24, 16):
            logo, _ = self.place("mark", x, 560 - px / 2, px, px)
            c += logo
            c += T(x + px / 2, 790, f"{px}", 20, 400, self.muted, anchor="middle")
            x += px + 36
        c += T(rx + 48, 860, f"Минимум для знака: {ms.get('mark_px', 16)} px (фавикон).", 22, 500, self.ink)
        return self.frame(6, self.total, "Минимальный размер", c)

    def s_palette(self):
        pal = self.d["palette"][:5]
        n = len(pal)
        gap = 24
        cw = (W - 2 * M - (n - 1) * gap) / n
        c = ""
        for i, p in enumerate(pal):
            x = M + i * (cw + gap)
            c += f'<rect x="{x:.1f}" y="250" width="{cw:.1f}" height="400" rx="16" fill="{p["hex"]}" stroke="{self.line}"/>'
            rl = wrap(p.get("role", "").upper(), cw, 15, 0.92)[:2]
            for j, l in enumerate(rl):
                c += T(x, 694 + j * 22, l, 15, 700, self.accent, ls=2)
            y0 = 694 + len(rl) * 22 + 22
            nm = wrap(p.get("name", ""), cw, 26, 0.6)
            for j, l in enumerate(nm[:2]):
                c += T(x, y0 + j * 32, l, 26, 600, self.ink)
            y = y0 + min(2, len(nm)) * 32 + 12
            for lab, key in (("HEX", "hex"), ("RGB", "rgb"), ("CMYK", "cmyk"), ("PANTONE", "pantone")):
                c += T(x, y, lab, 16, 600, self.muted, ls=1.5) + T(x + 104, y, p.get(key, "—"), 19, 500, self.ink)
                y += 32
        return self.frame(7, self.total, "Фирменные цвета", c)

    def s_colorways(self):
        a = self.d["palette"][0]["hex"]
        dark = self.d.get("dark_bg", "#151515")
        brand = self.d.get("brand_bg", a)
        tiles = [("primary", "#FFFFFF", None, "Цветная на светлом фоне"),
                 ("inverse", dark, None, "Цветная на тёмном фоне"),
                 ("mono", "#FFFFFF", "#111111", "Одноцветная чёрная"),
                 ("mono", dark, "#FFFFFF", "Одноцветная белая на тёмном"),
                 ("mono", brand, "#FFFFFF", "Белая на фирменном цвете"),
                 ("mono", mix(a, "#FFFFFF", 0.88), a, "Фирменный цвет на светлом")]
        tw, th, gx, gy = (W - 2 * M - 2 * 32) / 3, 270, 32, 82
        c = ""
        for i, (k, bg, col, lab) in enumerate(tiles):
            x = M + (i % 3) * (tw + gx)
            y = 240 + (i // 3) * (th + gy)
            c += f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14" fill="{bg}" stroke="{self.line}"/>'
            logo, _ = self.place(k, x + 30, y + 20, tw - 60, th - 40, color=col)
            c += logo
            c += T(x, y + th + 38, lab, 22, 500, self.ink)
        return self.frame(8, self.total, "Цветовые версии", c)

    def s_type(self):
        fonts = self.d.get("fonts", [])[:3]
        n = max(1, len(fonts))
        gap = 40
        cw = (W - 2 * M - (n - 1) * gap) / n
        c = ""
        for i, f in enumerate(fonts):
            x = M + i * (cw + gap)
            fam = f["family"] + ", sans-serif"
            wt = re.findall(r"\d{3}", str(f.get("weights", "400")))
            w0 = wt[-1] if wt else "400"
            c += f'<rect x="{x:.1f}" y="250" width="{cw:.1f}" height="660" rx="16" fill="#FFFFFF" stroke="{self.line}"/>'
            c += T(x + 40, 310, f.get("role", "").upper(), 18, 700, self.accent, ls=3)
            c += T(x + 40, 520, "Aa", 190, w0, self.ink, fam)
            c += T(x + 40, 610, f["family"], 40, w0, self.ink, fam)
            c += T(x + 40, 656, "Начертания: " + str(f.get("weights", "")), 20, 500, self.muted)
            c += T(x + 40, 730, "Huevos frescos de granja", 28, wt[0] if wt else 400, self.ink, fam)
            c += T(x + 40, 772, "ABCDEFGHIJ abcdefghij 0123456789", 22, wt[0] if wt else 400, self.muted, fam)
            p, _ = para(x + 40, 840, f.get("note", ""), cw - 80, 19, 1.45, fill=self.muted)
            c += p
        return self.frame(9, self.total, "Типографика", c)

    def s_misuse(self):
        a = self.d["palette"][0]["hex"]
        tw, th, gx, gy = (W - 2 * M - 2 * 32) / 3, 270, 32, 82
        items = []
        # 1 растяжение
        items.append(("Не растягивать и не сжимать", "#FFFFFF", ("primary", None, "stretch")))
        items.append(("Не поворачивать", "#FFFFFF", ("primary", None, "rotate")))
        items.append(("Не перекрашивать в чужие цвета", "#FFFFFF", ("mono", "#C13BD6", None)))
        items.append(("Не ставить на фон с низким контрастом", mix(a, "#FFFFFF", 0.25), ("mono", mix(a, "#FFFFFF", 0.05), None)))
        items.append(("Не размещать на пёстром фоне", "busy", ("primary", None, None)))
        items.append(("Не обрезать и не выводить за край", "#FFFFFF", ("primary", None, "crop")))
        c = ""
        for i, (lab, bg, (k, col, tf)) in enumerate(items):
            x = M + (i % 3) * (tw + gx)
            y = 240 + (i // 3) * (th + gy)
            self.uid += 1
            cid = f"{self.code.replace('.', '')}clip{self.uid}"
            c += f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14"/></clipPath>'
            c += f'<g clip-path="url(#{cid})">'
            if bg == "busy":
                c += f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" fill="#FFFFFF"/>'
                cols = [p["hex"] for p in self.d["palette"]] + ["#E8D5B0", "#9BB7D4"]
                for j in range(14):
                    c += (f'<rect x="{x + j * tw / 14:.1f}" y="{y}" width="{tw / 14 + 1:.1f}" height="{th}" '
                          f'fill="{cols[j % len(cols)]}" opacity="0.55" transform="skewX(-20)"/>')
            else:
                c += f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" fill="{bg}"/>'
            bx, by, bw, bh = x + 40, y + 30, tw - 80, th - 60
            if tf == "stretch":
                logo, _ = self.place(k, 0, 0, 400, 300, col)
                c += f'<g transform="translate({bx + bw/2:.1f},{by + bh/2:.1f}) scale({bh/300*1.55:.4f},{bh/300*0.72:.4f}) translate(-200,-150)">{logo}</g>'
            elif tf == "rotate":
                logo, _ = self.place(k, bx, by, bw, bh, col)
                c += f'<g transform="rotate(-14 {bx + bw/2:.1f} {by + bh/2:.1f})">{logo}</g>'
            elif tf == "crop":
                logo, _ = self.place(k, bx + bw * 0.45, by + bh * 0.25, bw * 1.1, bh * 1.1, col)
                c += logo
            else:
                logo, _ = self.place(k, bx, by, bw, bh, col)
                c += logo
            c += "</g>"
            c += f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" rx="14" fill="none" stroke="{self.line}"/>'
            # значок запрета
            cx, cy = x + tw - 34, y + 34
            c += (f'<circle cx="{cx:.1f}" cy="{cy}" r="18" fill="#D93025"/>'
                  f'<path d="M{cx-7:.1f} {cy-7} L{cx+7:.1f} {cy+7} M{cx+7:.1f} {cy-7} L{cx-7:.1f} {cy+7}" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>')
            c += T(x, y + th + 38, lab, 22, 500, self.ink)
        return self.frame(10, self.total, "Недопустимое использование", c)

    def s_icons(self):
        c = ""
        # иконка приложения
        x0 = M
        c += T(x0, 290, "ИКОНКА ПРИЛОЖЕНИЯ", 18, 700, self.accent, ls=3)
        c += f'<rect x="{x0}" y="330" width="300" height="300" rx="66" fill="#FFFFFF" stroke="{self.line}" stroke-width="2"/>'
        logo, _ = self.place("mark", x0 + 40, 370, 220, 220)
        c += logo
        c += f'<rect x="{x0+340}" y="430" width="200" height="200" rx="44" fill="#FFFFFF" stroke="{self.line}" stroke-width="2"/>'
        logo, _ = self.place("mark", x0 + 366, 456, 148, 148)
        c += logo
        c += T(x0, 690, "Скругление 22% от стороны, знак занимает ~75% площади.", 21, 400, self.muted)
        # аватар
        x1 = 820
        c += T(x1, 290, "АВАТАР СОЦСЕТЕЙ", 18, 700, self.accent, ls=3)
        c += f'<circle cx="{x1+150}" cy="480" r="150" fill="#FFFFFF" stroke="{self.line}" stroke-width="2"/>'
        logo, _ = self.place("mark", x1 + 45, 375, 210, 210)
        c += logo
        c += T(x1, 690, "Круглая маска: знак вписан с полем 15%.", 21, 400, self.muted)
        # фавикон во вкладке
        x2 = 1260
        c += T(x2, 290, "ФАВИКОН", 18, 700, self.accent, ls=3)
        c += f'<rect x="{x2}" y="330" width="540" height="64" rx="14" fill="#E9E6E0"/>'
        c += f'<rect x="{x2+12}" y="342" width="300" height="52" rx="10" fill="#FFFFFF"/>'
        logo, _ = self.place("mark", x2 + 26, 356, 24, 24)
        c += logo
        c += T(x2 + 62, 375, "Primeegg — Distribución", 18, 500, "#333")
        for j, px in enumerate((64, 32, 16)):
            xx = x2 + j * 130
            c += f'<rect x="{xx}" y="450" width="110" height="110" rx="10" fill="#FFFFFF" stroke="{self.line}"/>'
            logo, _ = self.place("mark", xx + 55 - px / 2, 505 - px / 2, px, px)
            c += logo
            c += T(xx + 55, 590, f"{px}×{px}", 18, 500, self.muted, anchor="middle")
        c += T(x2, 690, "SVG + PNG 16, 32, 48, 180 (apple-touch), 512 px.", 21, 400, self.muted)
        c += f'<line x1="{M}" y1="780" x2="{W-M}" y2="780" stroke="{self.line}" stroke-width="2"/>'
        p, _ = para(M, 840, "Знак работает самостоятельно там, где название уже прочитано из контекста: иконки, фавиконы, "
                            "штамп на скорлупе, пломбы и наклейки на таре. В остальных случаях используется полный логотип.",
                    W - 2 * M, 24, 1.5, fill=self.ink)
        return self.frame(11, self.total, "Знак в цифровой среде", c + p)

    def s_end(self):
        dark = self.d.get("dark_bg", "#151515")
        c = f'<rect width="{W}" height="{H}" fill="{dark}"/>'
        logo, _ = self.place("inverse", W / 2 - 420, 240, 840, 520)
        c += logo
        c += T(W / 2, 860, "Primeegg Distribution SL", 28, 600, "#FFFFFF", anchor="middle")
        c += T(W / 2, 904, f"Логобук {self.code} · {self.d['name']} · версия 1.0 · {TODAY}", 20, 400,
               mix(dark, "#FFFFFF", 0.6), anchor="middle")
        return c

    def slides(self):
        fns = [("01 Обложка", self.s_cover), ("02 Концепция", self.s_concept), ("03 Основной логотип", self.s_primary),
               ("04 Версии", self.s_versions), ("05 Охранное поле", self.s_clear), ("06 Минимальный размер", self.s_minsize),
               ("07 Цвета", self.s_palette), ("08 Цветовые версии", self.s_colorways), ("09 Типографика", self.s_type),
               ("10 Недопустимое использование", self.s_misuse), ("11 Знак в цифровой среде", self.s_icons),
               ("12 Финал", self.s_end)]
        self.total = len(fns)
        out = []
        for name, fn in fns:
            body = fn()
            if name.startswith("01"):
                body = f'<rect width="{W}" height="{H}" fill="{self.paper}"/>' + body + \
                       T(M, 92, f"PRIMEEGG · {self.code}", 18, 600, self.muted, ls=3)
            out.append((name, body))
        return out


# ---------------------------------------------------------------- измерения
def measure(books):
    parts = []
    for b in books:
        m = re.search(r"<svg[^>]*>(.*)</svg>", b.comp["primary"], re.S)
        parts.append(f'<svg data-code="{b.code}" viewBox="0 0 400 300" width="400" height="300"><g>{m.group(1)}</g></svg>')
    js = ("const r={};for(const s of document.querySelectorAll('svg[data-code]')){const bb=s.querySelector('g').getBBox();"
          "r[s.dataset.code]={x:bb.x,y:bb.y,width:bb.width,height:bb.height};}return JSON.stringify(r);")
    res = json.loads(chrome_eval("".join(parts), js))
    for b in books:
        b.measure["primary"] = res.get(b.code)


# ---------------------------------------------------------------- вывод
def html_page(b, slides):
    fam = used_families("".join(s for _, s in slides) + " Inter")
    nav = "".join(f'<a href="#s{i+1:02d}">{esc(n[3:])}</a>' for i, (n, _) in enumerate(slides))
    secs = "".join(f'<section id="s{i+1:02d}" aria-label="{esc(n)}"><svg xmlns="http://www.w3.org/2000/svg" '
                   f'viewBox="0 0 {W} {H}" role="img">{body}</svg></section>' for i, (n, body) in enumerate(slides))
    return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(b.d["name"])} — логобук</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts_href(fam)}">
<style>
:root{{color-scheme:light;--bg:#ECE9E3;--ink:#1C1B19;--muted:#6B665D;--line:#D8D3CA;--acc:{b.accent}}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#161512;--ink:#F1EDE6;--muted:#A39C90;--line:#2E2B26;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}}
body::before{{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}}
header{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
  padding-block:10px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;gap:16px;align-items:center}}
header .home{{white-space:nowrap;font-size:13px;color:var(--muted);text-decoration:none}}
header b{{white-space:nowrap;font-size:14px}} header b span{{color:var(--acc)}}
nav{{display:flex;gap:6px;overflow-x:auto;min-width:0}}
nav a{{white-space:nowrap;color:var(--ink);text-decoration:none;font-size:13px;padding:5px 10px;border:1px solid var(--line);border-radius:99px}}
nav a:hover,nav a:focus-visible{{border-color:var(--acc);outline:none}}
main{{max-width:1600px;margin:auto;padding-block:24px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:24px}}
section{{scroll-margin-top:72px}}
section svg{{display:block;width:100%;height:auto;max-width:100%;border-radius:10px;box-shadow:0 1px 3px #0002}}
</style></head><body>
<header><a class="home" href="../index.html">← Все логобуки</a><b><span>{esc(b.code)}</span> {esc(b.d["name"])}</b><nav>{nav}</nav></header>
<main>{secs}</main></body></html>'''


def figma_svg(b, slides):
    cols = FIG_COLS
    rows = (len(slides) + cols - 1) // cols
    BW = cols * W + (cols - 1) * GAPY + 2 * GAPY
    BH = rows * H + (rows - 1) * GAPY + 2 * GAPY + 160
    g = []
    g.append(T(GAPY, 110, f"PRIMEEGG · ЛОГОБУК {b.code} · {b.d['name']}", 48, 600, "#1C1B19", "Inter, sans-serif"))
    for i, (n, body) in enumerate(slides):
        x = GAPY + (i % cols) * (W + GAPY)
        y = GAPY + 160 + (i // cols) * (H + GAPY)
        g.append(f'<g id="{esc(b.code)} {esc(n)}" transform="translate({x},{y})">'
                 f'<clipPath id="fc{i}"><rect width="{W}" height="{H}"/></clipPath><g clip-path="url(#fc{i})">{body}</g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{BW}" height="{BH}" '
            f'viewBox="0 0 {BW} {BH}"><rect width="{BW}" height="{BH}" fill="#E4E0D8"/>' + "".join(g) + "</svg>")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    figma = "--no-figma" not in sys.argv
    dirs = [LB / a for a in args] if args else sorted(p for p in LB.glob("PE-*") if (p / "data.json").exists())
    books = []
    for d in dirs:
        try:
            books.append(Book(d))
        except Exception as e:
            print("SKIP", d.name, e)
    measure(books)
    for b in books:
        slides = b.slides()
        (b.dir / f"{b.code}_Logobook.html").write_text(html_page(b, slides))
        if figma:
            (b.dir / f"{b.code}_Logobook_Figma.svg").write_text(bake_for_figma(figma_svg(b, slides)))
        print("OK", b.code, b.d["name"])


if __name__ == "__main__":
    main()
