#!/usr/bin/env python3
"""Брендбуки: brandbooks/PE-xx.yy/{PE-xx.yy_Brandbook.html, PE-xx.yy_Brandbook_Figma.svg}.
Источники: logobooks/<код>/ (логотип, палитра, шрифты), brandbooks/<код>/{brand.json, pattern.svg}, tools/mockups/*.py.
Запуск: python3 tools/build_brandbooks.py [PE-01.05 ...] [--no-figma]"""
import sys, importlib, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_logobooks as LBk
from build_logobooks import Book, T, para, wrap, esc, mix, W, H, M, TODAY, html_page, figma_svg, measure
from brandkit import BrandKit, lum
from chrome_util import bake_for_figma

ROOT = Path(__file__).resolve().parent.parent
BB = ROOT / "brandbooks"
SCENES = ["icons", "pack_retail", "pack_horeca", "pack_powder", "logistics", "stationery", "uniform",
          "digital_web", "digital_social"]


def load_scene(name):
    try:
        return importlib.import_module(f"mockups.{name}")
    except Exception as e:
        print("  нет сцены", name, "—", e)
        return None


class Brandbook(Book):
    kind = "БРЕНДБУК"

    def __init__(self, code):
        super().__init__(ROOT / "logobooks" / code)
        self.k = BrandKit(code)
        self.b = self.k.b
        self.palette = self.k.palette
        self.text_font = self.k.text_font
        self.head_font = self.k.head_font

    def card(self, x, y, w, h, fill="#FFFFFF"):
        return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="{fill}" stroke="{self.line}"/>'

    def label(self, x, y, s, fill=None):
        return T(x, y, s.upper(), 17, 700, fill or self.accent, ls=3)

    # ------------------------------------------------------------ слайды
    def s_cover(self):
        k = self.k
        c = f'<rect width="{W}" height="{H}" fill="{k.brand_bg}"/>'
        c += k.pattern_rect(W * 0.5, 0, W * 0.5, H, 1.4, 0.35, k.on(k.brand_bg), 0)
        c += f'<rect x="{W*0.56:.0f}" y="{H/2-230:.0f}" width="{W*0.38:.0f}" height="460" rx="24" fill="#FFFFFF"/>'
        c += k.logo("primary", W * 0.56 + 50, H / 2 - 200, W * 0.38 - 100, 400)
        on = k.on(k.brand_bg)
        sub = mix(k.brand_bg, on, 0.7)
        c += T(M, 120, f"PRIMEEGG · {self.code}", 18, 600, sub, ls=3)
        c += T(M, 330, "БРЕНДБУК", 22, 700, sub, ls=6)
        tl = wrap(self.d["name"], 820, 80, 0.62)
        for j, l in enumerate(tl[:2]):
            c += T(M, 430 + j * 92, l, 80, 600, on, self.head_font)
        dy = (min(2, len(tl)) - 1) * 92
        p, _ = para(M, 520 + dy, self.k.t("taglines.es", ""), 760, 34, 1.35, fill=on, family=self.head_font, italic=True)
        c += p
        c += T(M, H - 150, "Primeegg Distribution SL", 24, 600, on)
        c += T(M, H - 114, f"Фирменный стиль · версия 1.0 · {TODAY}", 21, 400, sub)
        return c

    def s_platform(self):
        b = self.b
        c = self.label(M, 280, "Суть бренда")
        ess = wrap(b.get("essence", ""), 900, 76, 0.6)
        for j, l in enumerate(ess[:2]):
            c += T(M, 380 + j * 88, l, 76, 600, self.ink, self.head_font)
        y = 400 + len(ess[:2]) * 88
        cols = [("Миссия", b.get("mission", "")), ("Видение", b.get("vision", "")), ("Позиционирование", b.get("positioning", ""))]
        cw = (W - 2 * M - 2 * 40) / 3
        for i, (h, txt) in enumerate(cols):
            x = M + i * (cw + 40)
            c += f'<line x1="{x:.1f}" y1="{y:.0f}" x2="{x+cw:.1f}" y2="{y:.0f}" stroke="{self.ink}" stroke-width="2"/>'
            c += self.label(x, y + 50, h)
            p, _ = para(x, y + 100, txt, cw - 10, 25, 1.5, fill=self.ink)
            c += p
        return self.frame(self.n, self.total, "Платформа бренда", c)

    def s_values(self):
        vals = self.b.get("values", [])[:4]
        cw = (W - 2 * M - 3 * 28) / 4
        c = ""
        for i, v in enumerate(vals):
            x = M + i * (cw + 28)
            c += self.card(x, 250, cw, 640)
            c += T(x + 36, 330, f"{i+1:02d}", 22, 700, self.accent, ls=2)
            nl = wrap(v["name"], cw - 72, 44, 0.6)
            for j, l in enumerate(nl[:2]):
                c += T(x + 36, 430 + j * 52, l, 44, 600, self.ink, self.head_font)
            p, _ = para(x + 36, 470 + len(nl[:2]) * 52, v.get("text", ""), cw - 72, 23, 1.5, fill=self.muted)
            c += p
        return self.frame(self.n, self.total, "Ценности", c)

    def s_audience(self):
        aud = self.b.get("audience", [])[:3]
        cw = (W - 2 * M - 2 * 32) / 3
        c = ""
        for i, a in enumerate(aud):
            x = M + i * (cw + 32)
            fill = [self.k.brand_bg, "#FFFFFF", "#FFFFFF"][i] if i == 0 else "#FFFFFF"
            dark = i == 0
            ink = self.k.on(fill) if dark else self.ink
            mut = mix(fill, ink, 0.75) if dark else self.muted
            c += self.card(x, 250, cw, 650, fill)
            c += T(x + 40, 320, f"СЕГМЕНТ {i+1}", 17, 700, mut if dark else self.accent, ls=3)
            nl = wrap(a.get("segment", ""), cw - 80, 40, 0.6)
            for j, l in enumerate(nl[:2]):
                c += T(x + 40, 400 + j * 48, l, 40, 600, ink, self.head_font)
            y = 440 + len(nl[:2]) * 48
            c += T(x + 40, y, "ЧТО ВАЖНО", 16, 700, mut, ls=2.5)
            p, y = para(x + 40, y + 40, a.get("need", ""), cw - 80, 22, 1.5, fill=ink)
            c += p
            c += T(x + 40, y + 34, "ЧТО МЫ ГОВОРИМ", 16, 700, mut, ls=2.5)
            p, _ = para(x + 40, y + 74, a.get("message", ""), cw - 80, 22, 1.5, fill=ink, italic=True)
            c += p
        return self.frame(self.n, self.total, "Аудитория", c)

    def s_voice(self):
        b = self.b
        tone = b.get("tone", {})
        c = self.label(M, 280, "Характер")
        x = M
        for adj in b.get("personality", [])[:5]:
            w = len(adj) * 15 + 56
            c += f'<rect x="{x}" y="306" width="{w}" height="52" rx="26" fill="{mix(self.accent, "#FFFFFF", 0.88)}"/>'
            c += T(x + w / 2, 340, adj, 24, 600, self.ink, anchor="middle")
            x += w + 14
        c += self.label(M, 440, "Принципы голоса")
        y = 490
        for pr in tone.get("principles", [])[:3]:
            c += T(M, y, pr["name"], 28, 600, self.ink, self.head_font)
            p, y2 = para(M, y + 38, pr.get("text", ""), 760, 22, 1.45, fill=self.muted)
            c += p
            y = y2 + 30
        bx = 1000
        bw = W - M - bx
        c += self.card(bx, 250, bw, 330)
        c += self.label(bx + 36, 300, "Так говорим", "#1E8E4E")
        yy = 350
        for s in tone.get("do", [])[:3]:
            p, yy = para(bx + 36, yy, "«" + s + "»", bw - 72, 22, 1.4, fill=self.ink)
            c += p; yy += 18
        c += self.card(bx, 610, bw, 300)
        c += self.label(bx + 36, 660, "Так не говорим", "#C0392B")
        yy = 710
        for s in tone.get("dont", [])[:3]:
            p, yy = para(bx + 36, yy, "«" + s + "»", bw - 72, 22, 1.4, fill=self.muted)
            c += p; yy += 18
        return self.frame(self.n, self.total, "Характер и голос", c)

    def s_taglines(self):
        k = self.k
        c = f'<rect x="{M}" y="250" width="{W-2*M}" height="360" rx="16" fill="{k.brand_bg}"/>'
        c += k.pattern_rect(W - M - 520, 250, 520, 360, 1, 0.25, k.on(k.brand_bg), 16)
        on = k.on(k.brand_bg)
        c += T(M + 56, 320, "ГЛАВНЫЙ СЛОГАН · ES", 17, 700, mix(k.brand_bg, on, 0.7), ls=3)
        tl = wrap(k.t("taglines.es", ""), 1100, 64, 0.55)
        for j, l in enumerate(tl[:2]):
            c += T(M + 56, 420 + j * 76, l, 64, 600, on, self.head_font)
        c += T(M, 680, "EN", 17, 700, self.accent, ls=3) + T(M + 70, 680, k.t("taglines.en", ""), 26, 500, self.ink, self.head_font, italic=True)
        c += T(M, 730, "RU", 17, 700, self.accent, ls=3) + T(M + 70, 730, k.t("taglines.ru", ""), 26, 500, self.ink, self.head_font, italic=True)
        c += self.label(1000, 680, "Заголовки для коммуникаций")
        y = 730
        for h in self.b.get("headlines_es", [])[:3]:
            p, y = para(1000, y, h, W - M - 1000, 28, 1.3, fill=self.ink, family=self.head_font)
            c += p; y += 18
        return self.frame(self.n, self.total, "Слоганы и заголовки", c)

    def s_logo(self):
        c = self.card(M, 250, 1040, 640)
        c += self.k.logo("primary", M + 120, 300, 800, 540)
        x = 1200
        c += self.card(x, 250, W - M - x, 300)
        c += self.k.logo("horizontal", x + 30, 280, W - M - x - 60, 240)
        c += self.card(x, 580, (W - M - x - 20) / 2, 310)
        c += self.k.logo("mark", x + 40, 620, (W - M - x - 20) / 2 - 80, 230)
        x2 = x + (W - M - x - 20) / 2 + 20
        c += self.card(x2, 580, (W - M - x - 20) / 2, 310, self.k.dark)
        c += self.k.logo("mono", x2 + 30, 620, (W - M - x - 20) / 2 - 60, 230, color="#FFFFFF")
        c += T(M, 950, f"Полные правила использования логотипа — в логобуке {self.code}.", 23, 400, self.muted)
        return self.frame(self.n, self.total, "Логотип", c)

    def s_colors(self):
        props = self.b.get("color_proportions") or [{"hex": p["hex"], "pct": 100 // len(self.palette)} for p in self.palette]
        tot = sum(p["pct"] for p in props) or 100
        x, bw = M, W - 2 * M
        c = self.label(M, 280, "Пропорции цвета в коммуникациях")
        cid = self.k.uid("bar")
        c += f'<clipPath id="{cid}"><rect x="{M}" y="310" width="{bw}" height="300" rx="16"/></clipPath><g clip-path="url(#{cid})">'
        for p in props:
            w = bw * p["pct"] / tot
            c += f'<rect x="{x:.1f}" y="310" width="{w+0.5:.1f}" height="300" fill="{p["hex"]}"/>'
            if w > 90:
                c += T(x + 24, 580, f'{p["pct"]}%', 34, 700, self.k.on(p["hex"]))
            x += w
        c += "</g>"
        c += f'<rect x="{M}" y="310" width="{bw}" height="300" rx="16" fill="none" stroke="{self.line}"/>'
        pal = self.palette[:5]
        cw = (bw - (len(pal) - 1) * 24) / len(pal)
        for i, p in enumerate(pal):
            xx = M + i * (cw + 24)
            c += f'<rect x="{xx:.1f}" y="660" width="56" height="56" rx="28" fill="{p["hex"]}" stroke="{self.line}"/>'
            nm = wrap(p.get("name", ""), cw - 76, 22, 0.6)
            c += T(xx + 72, 684, nm[0] if nm else "", 22, 600, self.ink)
            c += T(xx + 72, 712, p["hex"], 19, 500, self.muted)
            rl = wrap(p.get("role", ""), cw, 18, 0.58)
            for j, l in enumerate(rl[:2]):
                c += T(xx, 760 + j * 26, l, 18, 400, self.muted)
        p, _ = para(M, 870, "Основной цвет держит узнаваемость, акцент — только для выделения (цена, новинка, кнопка). "
                            "Нейтральные цвета дают воздух и работают фоном для продукта.", W - 2 * M, 22, 1.5, fill=self.muted)
        return self.frame(self.n, self.total, "Цвет", c + p)

    def s_type(self):
        k = self.k
        c = self.card(M, 250, W - 2 * M, 660)
        rows = [("H1 · 72 / 80", "Huevos frescos de granja", 72, 600, self.head_font),
                ("H2 · 44 / 52", "Distribución diaria para hostelería", 44, 600, self.head_font),
                ("Лид · 28 / 40", "Seleccionamos, clasificamos y entregamos en menos de 24 horas.", 28, 400, self.text_font),
                ("Текст · 18 / 28", "Trabajamos con granjas de Castilla y Andalucía. Cada lote se controla y se etiqueta con su código de trazabilidad.", 20, 400, self.text_font),
                ("Подпись · 13 / 18", "CATEGORÍA A · TALLA L · LOTE 2611 · CONSUMIR ANTES DE 24.12.2026", 15, 600, self.text_font)]
        y = 360
        for lab, txt, size, wt, fam in rows:
            c += T(M + 48, y - size * 0.25, lab, 16, 600, self.muted, ls=1.5)
            c += T(M + 330, y, txt, size, wt, self.ink, fam, ls=1.5 if size == 15 else 0)
            y += max(size * 1.35, 60) + 34
        f = self.d.get("fonts", [])
        names = " · ".join(dict.fromkeys(x["family"] for x in f))
        c += T(M, 960, f"Шрифты: {names}. Все — Google Fonts, свободная лицензия.", 22, 400, self.muted)
        return self.frame(self.n, self.total, "Типографическая иерархия", c)

    def s_pattern(self):
        k = self.k
        c = k.pattern_rect(M, 250, 760, 640, 1.2, 1, None, 16, k.light)
        c += f'<rect x="{M}" y="250" width="760" height="640" rx="16" fill="none" stroke="{self.line}"/>'
        c += k.pattern_rect(M + 790, 250, 400, 305, 0.8, 0.4, k.on(k.brand_bg), 16, k.brand_bg)
        c += k.pattern_rect(M + 790, 585, 400, 305, 0.8, 1, k.dark, 16, "#FFFFFF")
        c += f'<rect x="{M+790}" y="585" width="400" height="305" rx="16" fill="none" stroke="{self.line}"/>'
        rx = M + 1230
        c += self.label(rx, 290, self.k.t("pattern.name", "Фирменный паттерн"))
        p, y = para(rx, 340, self.k.t("pattern.text", ""), W - M - rx, 23, 1.5, fill=self.ink)
        c += p
        p, _ = para(rx, y + 30, "Паттерн — фон, а не герой: под логотипом и текстом на нём всегда есть спокойная плашка. "
                                "Масштаб — не мельче, чем 1/12 ширины носителя.", W - M - rx, 20, 1.5, fill=self.muted)
        return self.frame(self.n, self.total, "Графический элемент", c + p)

    def s_photo(self):
        k = self.k
        scenes = self.b.get("photo", {}).get("scenes", [])[:3]
        cw = (W - 2 * M - 2 * 28) / 3
        c = ""
        tones = [k.primary, k.accent, k.dark]
        for i, s in enumerate(scenes):
            x = M + i * (cw + 28)
            gid = k.uid("ph")
            base = tones[i % 3]
            c += (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(base, "#FFFFFF", 0.35)}"/>'
                  f'<stop offset="1" stop-color="{mix(base, "#000000", 0.25)}"/></linearGradient>')
            c += f'<rect x="{x:.1f}" y="250" width="{cw:.1f}" height="420" rx="16" fill="url(#{gid})"/>'
            # условная композиция: горизонт + яйца
            cx, cy = x + cw / 2, 520
            c += f'<ellipse cx="{cx:.1f}" cy="{cy+70}" rx="{cw*0.36:.1f}" ry="22" fill="#000" opacity="0.18"/>'
            for dx, sc in ((-70, 0.9), (0, 1.15), (70, 0.9)):
                ex, eh = cx + dx * 1.3, 120 * sc
                c += (f'<path transform="translate({ex - 46*sc:.1f},{cy + 70 - eh:.1f}) scale({0.92*sc:.3f})" '
                      f'd="M50 0 C78 0 100 45 100 80 C100 110 78 130 50 130 C22 130 0 110 0 80 C0 45 22 0 50 0 Z" '
                      f'fill="{["#F4EEE3", "#E8C49A", "#F4EEE3"][int(dx/70)+1]}"/>')
            c += T(x + 28, 290, "ФОТО", 15, 700, "#FFFFFF", ls=3, extra=' opacity="0.8"')
            c += T(x, 720, s.get("title", ""), 28, 600, self.ink, self.head_font)
            p, _ = para(x, 760, s.get("hint", ""), cw, 20, 1.45, fill=self.muted)
            c += p
        pr = self.b.get("photo", {}).get("principles", [])
        y = 880
        txt = "  ·  ".join(pr[:3])
        p, _ = para(M, y, txt, W - 2 * M, 20, 1.45, fill=self.ink)
        return self.frame(self.n, self.total, "Фотостиль", c + p)

    def s_scene(self, mod):
        c = mod.render(self.k, 1680, 700)
        c = f'<g transform="translate({M},235)">{c}</g>'
        c += T(M, 985, getattr(mod, "CAPTION", ""), 21, 400, self.muted)
        return self.frame(self.n, self.total, getattr(mod, "TITLE", ""), c)

    def s_end(self):
        k = self.k
        c = f'<rect width="{W}" height="{H}" fill="{k.dark}"/>'
        c += k.pattern_rect(0, 0, W, H, 1.6, 0.12, "#FFFFFF", 0)
        c += k.logo("inverse", W / 2 - 400, 220, 800, 480)
        on = "#FFFFFF"
        c += T(W / 2, 790, k.t("taglines.es", ""), 34, 500, on, self.head_font, anchor="middle", italic=True)
        ct = k.t("contacts", {}) or {}
        line = "  ·  ".join(v for v in (ct.get("web"), ct.get("email"), ct.get("phone")) if v)
        c += T(W / 2, 880, line, 22, 500, mix(k.dark, on, 0.75), anchor="middle")
        c += T(W / 2, 920, f"Primeegg Distribution SL · Брендбук {self.code} · версия 1.0 · {TODAY}", 18, 400,
               mix(k.dark, on, 0.55), anchor="middle")
        return c

    def slides(self):
        plan = [("Обложка", self.s_cover), ("Платформа бренда", self.s_platform), ("Ценности", self.s_values),
                ("Аудитория", self.s_audience), ("Характер и голос", self.s_voice), ("Слоганы", self.s_taglines),
                ("Логотип", self.s_logo), ("Цвет", self.s_colors), ("Типографика", self.s_type),
                ("Графический элемент", self.s_pattern), ("Фотостиль", self.s_photo)]
        for sc in SCENES:
            mod = load_scene(sc)
            if mod:
                plan.append((getattr(mod, "TITLE", sc), (lambda m: (lambda: self.s_scene(m)))(mod)))
        plan.append(("Финал", self.s_end))
        self.total = len(plan)
        out = []
        for i, (name, fn) in enumerate(plan, 1):
            self.n = i
            try:
                out.append((f"{i:02d} {name}", fn()))
            except Exception as e:
                print(f"  ! {self.code} слайд «{name}»: {e}")
        return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    figma = "--no-figma" not in sys.argv
    codes = args or sorted(p.name for p in BB.glob("PE-*") if (p / "brand.json").exists())
    books = [Brandbook(c) for c in codes]
    measure(books)
    for b in books:
        slides = b.slides()
        out_dir = BB / b.code
        out_dir.mkdir(exist_ok=True)
        page = html_page(b, slides).replace("— логобук</title>", "— брендбук</title>").replace("Все логобуки", "Все брендбуки")
        (out_dir / f"{b.code}_Brandbook.html").write_text(page)
        if figma:
            fs = figma_svg(b, slides).replace("ЛОГОБУК", "БРЕНДБУК", 1)
            (out_dir / f"{b.code}_Brandbook_Figma.svg").write_text(bake_for_figma(fs))
        print("OK", b.code, len(slides), "слайдов")


if __name__ == "__main__":
    main()
