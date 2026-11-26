#!/usr/bin/env python3
"""Собирает logos/board-raw.svg — презентационный борд всех концептов для Figma.
Затем figma_safe.sh прогоняет его через Chrome: textPath -> отдельные буквы."""
import json, re, html, sys
from pathlib import Path
from datetime import date

UK = "--uk" in sys.argv
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

ROOT = Path(__file__).parent
STYLES = [
    ("01-minimal", "Минимализм и геометрия", "Minimal & Geometric",
     "Чистые геометрические знаки, негативное пространство, 1–2 цвета. Максимальная читаемость в малом размере."),
    ("02-farm-craft", "Фермерский крафт", "Farm Craft & Vintage",
     "Штампы, бейджи и эмблемы хозяйства. Рассчитаны на однотонную печать на картоне и таре."),
    ("03-mediterranean", "Средиземноморье", "Mediterranean / Spain",
     "Азулежу, андалузские арки, солнце-желток, терракота и кобальт. Испанское происхождение как ценность."),
    ("04-premium", "Премиум", "Premium & Gourmet",
     "Монограммы, контрастные антиквы, золото и бордо. Позиционирование для haute cuisine и деликатесного ретейла."),
    ("05-corporate-b2b", "Корпоративный B2B", "Corporate B2B / Logistics",
     "Маршруты, пины, тара и сети поставок. Надёжный поставщик для оптовиков и HoReCa."),
    ("06-friendly-retail", "Дружелюбный ретейл", "Friendly Retail",
     "Округлые формы, маскоты и сочные цвета. Заметность на полке супермаркета."),
    ("07-wordmark", "Типографика", "Wordmark & Lettering",
     "Логотип как слово: буквы-яйца, лигатура «ee», кастомные детали. Без отдельного знака."),
    ("08-eco-organic", "Эко / органика", "Eco & Organic",
     "Линейная иллюстрация, свободный выгул, природа. Основа для линеек Bio / Camperas."),
]

STYLES_UK = {
    "01-minimal": ("Мінімалізм і геометрія", "Чисті геометричні знаки, негативний простір, 1–2 кольори. Максимальна читабельність у малому розмірі."),
    "02-farm-craft": ("Фермерський крафт", "Штампи, бейджі й емблеми господарства. Розраховані на одноколірний друк на картоні й тарі."),
    "03-mediterranean": ("Середземномор’я", "Азулежу, андалузькі арки, сонце-жовток, теракота й кобальт. Іспанське походження як цінність."),
    "04-premium": ("Преміум", "Монограми, контрастні антикви, золото й бордо. Позиціювання для haute cuisine та делікатесного ретейлу."),
    "05-corporate-b2b": ("Корпоративний B2B", "Маршрути, піни, тара й мережі постачання. Надійний постачальник для гуртовиків і HoReCa."),
    "06-friendly-retail": ("Дружній ретейл", "Округлі форми, маскоти й соковиті кольори. Помітність на полиці супермаркету."),
    "07-wordmark": ("Типографіка", "Логотип як слово: літери-яйця, лігатура «ee», кастомні деталі. Без окремого знака."),
    "08-eco-organic": ("Еко / органіка", "Лінійна ілюстрація, вільний вигул, природа. Основа для лінійок Bio / Camperas."),
}
if UK:
    STYLES = [(f, STYLES_UK[f][0], en, STYLES_UK[f][1]) for f, ru, en, d in STYLES]
TX = {
    "eyebrow": "PRIMEEGG DISTRIBUTION SL · BRAND IDENTITY",
    "h1": "Пошук стилю логотипа" if UK else "Поиск стиля логотипа",
    "sub": ("Етап 01 · Logo exploration · {n} концептів у 8 стилістичних напрямах" if UK
            else "Этап 01 · Logo exploration · {n} концептов в 8 стилистических направлениях"),
    "scope": ("Яйця · Яєчний порошок · Ovoproductos · B2B / HoReCa / Retail" if UK
              else "Яйца · Яичный порошок · Ovoproductos · B2B / HoReCa / Retail"),
    "count": "{n} концептів · {a} — {b}" if UK else "{n} концептов · {a} — {b}",
    "foot": ("Концепти в роботі. Шрифти: Google Fonts. Кольори орієнтовні, фінальну палітру зафіксовано в логобуці." if UK
             else "Концепты в работе. Шрифты: Google Fonts. Цвета ориентировочные, финальная палитра фиксируется в логобуке."),
}
META = "meta.uk.json" if UK else "meta.json"

CW, ART_H, LABEL_H = 400, 300, 128      # карточка
GAP, MX = 32, 120                        # отступы
COLS = 10
SEC_HEAD = 150
W = MX * 2 + COLS * CW + (COLS - 1) * GAP

INK, MUTED, LINE, CARD, BG, ACC = "#1D1B18", "#6F685E", "#E2DBCF", "#FFFFFF", "#F3EFE8", "#D99A00"
SANS = "Inter, Helvetica, Arial, sans-serif"
SERIF = ("Playfair Display, Georgia, serif" if UK else "Fraunces, Georgia, serif")


def esc(s): return html.escape(s, quote=True)


def wrap(text, width_px, size):
    """Простой перенос по словам; средняя ширина символа Inter ≈ 0.53 em."""
    maxc = int(width_px / (size * 0.53))
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > maxc and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    if len(lines) > 3:
        lines = lines[:3]; lines[2] = lines[2].rstrip(".,;: ") + "…"
    return lines


def inner(svg, prefix):
    svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg)
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    m = re.search(r"<svg[^>]*>(.*)</svg>", svg, flags=re.S)
    body = m.group(1)
    ids = set(re.findall(r'\bid="([^"]+)"', body))
    for x in sorted(ids, key=len, reverse=True):
        p = f"{prefix}-{x}"
        body = body.replace(f'id="{x}"', f'id="{p}"').replace(f"#{x})", f"#{p})") \
                   .replace(f'href="#{x}"', f'href="#{p}"')
    return body.strip()


out, y = [], 0
# --- шапка борда
y = 120
total = sum(len(json.loads((ROOT / f / META).read_text())) for f, *_ in STYLES)
out.append(f'''<g id="Header">
  <text x="{MX}" y="{y}" font-family="{SANS}" font-size="20" font-weight="600" letter-spacing="4" fill="{ACC}">PRIMEEGG DISTRIBUTION SL · BRAND IDENTITY</text>
  <text x="{MX}" y="{y+92}" font-family="{SERIF}" font-size="84" font-weight="700" fill="{INK}">{TX["h1"]}</text>
  <text x="{MX}" y="{y+150}" font-family="{SANS}" font-size="26" font-weight="400" fill="{MUTED}">{TX["sub"].format(n=total)}</text>
  <text x="{W-MX}" y="{y}" text-anchor="end" font-family="{SANS}" font-size="20" font-weight="500" fill="{MUTED}">{date.today().strftime("%d.%m.%Y")} · v1.0</text>
  <text x="{W-MX}" y="{y+32}" text-anchor="end" font-family="{SANS}" font-size="20" font-weight="500" fill="{MUTED}">{TX["scope"]}</text>
  <line x1="{MX}" y1="{y+200}" x2="{W-MX}" y2="{y+200}" stroke="{INK}" stroke-width="2"/>
</g>''')
y += 280

for si, (folder, ru, en, desc) in enumerate(STYLES, 1):
    meta = json.loads((ROOT / folder / META).read_text())
    sec = [f'<g id="Section-{si:02d}">']
    sec.append(f'''<text x="{MX}" y="{y+48}" font-family="{SERIF}" font-size="48" font-weight="700" fill="{ACC}">{si:02d}</text>
<text x="{MX+80}" y="{y+48}" font-family="{SERIF}" font-size="48" font-weight="600" fill="{INK}">{esc(ru)}</text>
<text x="{MX+80}" y="{y+88}" font-family="{SANS}" font-size="20" font-weight="600" letter-spacing="3" fill="{MUTED}">{esc(en.upper())}</text>
<text x="{W-MX}" y="{y+48}" text-anchor="end" font-family="{SANS}" font-size="22" font-weight="400" fill="{MUTED}">{esc(desc)}</text>
<text x="{W-MX}" y="{y+88}" text-anchor="end" font-family="{SANS}" font-size="20" font-weight="600" fill="{INK}">{TX["count"].format(n=len(meta), a=f"PE-{si:02d}.01", b=f"PE-{si:02d}.{len(meta):02d}")}</text>''')
    y0 = y + SEC_HEAD
    for i, m in enumerate(meta):
        x = MX + (i % COLS) * (CW + GAP)
        yy = y0 + (i // COLS) * (ART_H + LABEL_H + GAP)
        code = f"PE-{si:02d}.{i+1:02d}"
        body = inner((ROOT / folder / m["file"]).read_text(), f"L{si:02d}{i+1:02d}")
        colors = m.get("colors", [])[:6]
        sw = "".join(f'<rect x="{CW-24-k*22}" y="{ART_H+22}" width="16" height="16" rx="8" fill="{esc(c)}" stroke="#00000022"/>'
                     for k, c in enumerate(reversed(colors)))
        lines = wrap(m.get("concept", ""), CW - 40, 15)
        concept = "".join(f'<text x="20" y="{ART_H+88+k*20}" font-family="{SANS}" font-size="15" font-weight="400" fill="{MUTED}">{esc(l)}</text>'
                          for k, l in enumerate(lines))
        sec.append(f'''<g id="{code}" transform="translate({x},{yy})">
  <rect width="{CW}" height="{ART_H+LABEL_H}" rx="12" fill="{CARD}" stroke="{LINE}"/>
  <rect y="{ART_H}" width="{CW}" height="1" fill="{LINE}"/>
  <g id="{code}-logo">{body}</g>
  <text x="20" y="{ART_H+36}" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="1.5" fill="{ACC}">{code}</text>
  <text x="20" y="{ART_H+62}" font-family="{SANS}" font-size="19" font-weight="600" fill="{INK}">{esc(m.get("title",""))}</text>
  {sw}{concept}
</g>''')
    rows = (len(meta) + COLS - 1) // COLS
    y = y0 + rows * (ART_H + LABEL_H + GAP) - GAP + 110
    sec.append("</g>")
    out.append("\n".join(sec))

H = y + 40
out.append(f'<text x="{MX}" y="{H-60}" font-family="{SANS}" font-size="18" fill="{MUTED}">{TX["foot"]}</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n<rect id="Background" width="{W}" height="{H}" fill="{BG}"/>\n'
       + "\n".join(out) + "\n</svg>\n")
from chrome_util import bake_for_figma
out = ROOT / ("Primeegg_Logo-Exploration_v1_UA.svg" if UK else "Primeegg_Logo-Exploration_v1.svg")
out.write_text(bake_for_figma(svg))
print(f"{out.name} {W}x{H}, {total} logos")
