"""BrandKit — единый доступ к фирменному стилю одного концепта для мокапов и слайдов брендбука.

    from brandkit import BrandKit
    k = BrandKit("PE-01.05")
    k.logo("mark", x, y, w, h)              # SVG-фрагмент компонента логотипа, вписанного в бокс
    k.logo("mono", x, y, w, h, color="#fff") # одноцветная версия в нужном цвете
    k.pattern_rect(x, y, w, h, scale=1, opacity=1, color=None, clip_rx=0)  # фирменный паттерн в прямоугольнике
    k.uid("box")                             # уникальный id для clipPath/gradient
    k.primary, k.accent, k.dark, k.light, k.ink, k.paper   # цвета (#RRGGBB)
    k.head_font, k.text_font, k.logo_font     # font-family строки с fallback
    k.t("tagline_es", "Huevos frescos de granja")           # текст из brand.json с запасным значением
    k.palette                                  # список цветов логобука [{role,name,hex,...}]
    k.on(color) -> "#FFFFFF" или k.ink: читаемый цвет текста на фоне color

Все размеры — в пикселях SVG. Мокапы рисуются в своих координатах 0..W, 0..H и возвращают фрагмент без <svg>."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VB = {"primary": (400, 300), "horizontal": (640, 200), "vertical": (400, 400), "mark": (200, 200),
      "wordmark": (640, 160), "mono": (400, 300), "inverse": (400, 300), "pattern": None}


def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#" + "".join(f"{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02X}" for i in (0, 2, 4))


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def pick_font(fonts, role_word, idx, fallback):
    """Шрифт по роли ('Заголовки', 'Текст'...), иначе по позиции."""
    for x in fonts:
        r = x.get("role", "").lower()
        if r.startswith(role_word) or (role_word != "логотип" and role_word in r):
            return x["family"]
    return fonts[idx]["family"] if len(fonts) > idx else fallback


class BrandKit:
    _n = 0

    def __init__(self, code):
        self.code = code
        self.lb_dir = ROOT / "logobooks" / code
        self.bb_dir = ROOT / "brandbooks" / code
        self.d = json.loads((self.lb_dir / "data.json").read_text())
        bj = self.bb_dir / "brand.json"
        self.b = json.loads(bj.read_text()) if bj.exists() else {}
        self.name = self.d["name"]
        self.comp = {k: (self.lb_dir / f"{k}.svg").read_text() for k in VB if (self.lb_dir / f"{k}.svg").exists()}
        pt = self.bb_dir / "pattern.svg"
        self.pattern_src = pt.read_text() if pt.exists() else None
        self.palette = self.d["palette"]
        pal = self.palette
        self.primary = pal[0]["hex"]
        acc = [c for c in pal[1:] if "акцент" in c.get("role", "").lower()]
        self.accent = (acc[0] if acc else (pal[1] if len(pal) > 1 else pal[0]))["hex"]
        by = sorted(pal, key=lambda c: lum(c["hex"]))
        self.ink = by[0]["hex"] if lum(by[0]["hex"]) < 0.06 else "#1C1B19"
        self.light = by[-1]["hex"] if lum(by[-1]["hex"]) > 0.75 else "#F6F2EA"
        self.dark = self.d.get("dark_bg", self.ink)
        self.brand_bg = self.d.get("brand_bg", self.primary)
        self.paper = "#FBFAF7"
        f = self.d.get("fonts", [])
        self.logo_font = pick_font(f, "логотип", 0, "Inter") + ", sans-serif"
        self.head_font = pick_font(f, "заголов", 1, "Fraunces") + ", Georgia, serif"
        self.text_font = pick_font(f, "текст", 2, "Inter") + ", Helvetica, Arial, sans-serif"

    # ------------------------------------------------------------ utils
    def uid(self, p="u"):
        BrandKit._n += 1
        return f"{self.code.replace('.', '').replace('-', '')}{p}{BrandKit._n}"

    def t(self, key, default=""):
        cur = self.b
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return default
        return cur if cur not in (None, "") else default

    def on(self, bg):
        return "#FFFFFF" if contrast("#FFFFFF", bg) >= contrast(self.ink, bg) else self.ink

    def _body(self, src):
        m = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S)
        body = re.sub(r"<title>.*?</title>", "", m.group(1), flags=re.S)
        pre = self.uid("c")
        for x in sorted(set(re.findall(r'\bid="([^"]+)"', body)), key=len, reverse=True):
            body = body.replace(f'id="{x}"', f'id="{pre}-{x}"').replace(f"#{x})", f"#{pre}-{x})") \
                       .replace(f'href="#{x}"', f'href="#{pre}-{x}"')
        return body

    # ------------------------------------------------------------ logo
    def logo(self, key, x, y, w, h, color=None, align="center", opacity=None):
        """Вписывает компонент логотипа в бокс (x,y,w,h) с сохранением пропорций.
        align: center | left | right (по горизонтали; по вертикали всегда центр)."""
        if key not in self.comp:
            key = "primary"
        vw, vh = VB[key]
        body = self._body(self.comp[key])
        if color:
            body = body.replace("currentColor", color)
        s = min(w / vw, h / vh)
        ox = {"left": x, "right": x + w - vw * s}.get(align, x + (w - vw * s) / 2)
        oy = y + (h - vh * s) / 2
        op = f' opacity="{opacity}"' if opacity is not None else ""
        return f'<g transform="translate({ox:.2f},{oy:.2f}) scale({s:.4f})"{op}>{body}</g>'

    # ------------------------------------------------------------ pattern
    def pattern_rect(self, x, y, w, h, scale=1.0, opacity=1.0, color=None, clip_rx=0, bg=None):
        """Заливает прямоугольник фирменным паттерном (копии тайла, без <pattern> — совместимо с Figma)."""
        cid = self.uid("pc")
        out = f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{clip_rx}"/></clipPath>'
        out += f'<g clip-path="url(#{cid})">'
        if bg:
            out += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>'
        if self.pattern_src:
            m = re.search(r'viewBox="([\d.\s-]+)"', self.pattern_src)
            _, _, tw, th = (float(v) for v in m.group(1).split())
            body = re.search(r"<svg[^>]*>(.*)</svg>", self.pattern_src, re.S).group(1)
            body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)
            if color:
                body = re.sub(r'(fill|stroke)="(?!none)[^"]+"', lambda mm: f'{mm.group(1)}="{color}"', body)
            sw, sh = tw * scale, th * scale
            nx, ny = int(w // sw) + 2, int(h // sh) + 2
            if nx * ny > 900:                      # защита от гигантских файлов
                k = (nx * ny / 900) ** 0.5
                scale *= k; sw, sh = tw * scale, th * scale
                nx, ny = int(w // sw) + 2, int(h // sh) + 2
            out += f'<g opacity="{opacity}">'
            for j in range(ny):
                for i in range(nx):
                    out += f'<g transform="translate({x + i*sw:.1f},{y + j*sh:.1f}) scale({scale:.4f})">{body}</g>'
            out += "</g>"
        out += "</g>"
        return out


def all_codes():
    return sorted(p.name for p in (ROOT / "logobooks").glob("PE-*") if (p / "data.json").exists())
