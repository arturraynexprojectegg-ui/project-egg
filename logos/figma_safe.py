#!/usr/bin/env python3
"""board-raw.svg -> board-figma.svg.
Figma при импорте SVG не понимает textPath и textLength. Скрипт открывает борд в headless Chrome
с настоящими Google Fonts и запекает:
  * textPath  -> отдельные <text> на каждую букву с translate+rotate;
  * textLength -> обычный текст + transform scale по X (или letter-spacing), как рисует браузер."""
import html, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ("Fraunces:ital,wght@0,300..900;1,300..900|Playfair+Display:ital,wght@0,400..900;1,400..900|DM+Serif+Display"
         "|Cormorant+Garamond:ital,wght@0,300..700;1,300..700|Libre+Baskerville:ital,wght@0,400;0,700;1,400|Abril+Fatface"
         "|Lora:ital,wght@0,400..700;1,400..700|Montserrat:wght@300..900|Manrope:wght@300..800|Space+Grotesk:wght@300..700"
         "|Syne:wght@400..800|Bricolage+Grotesque:wght@300..800|Outfit:wght@300..900|Archivo+Black|Josefin+Sans:wght@300..700"
         "|Bebas+Neue|Oswald:wght@300..700|Inter:wght@300..900|Fredoka:wght@300..700|Baloo+2:wght@400..800|Nunito:wght@300..900"
         "|Quicksand:wght@300..700|Pacifico|Lobster|Caveat:wght@400..700|Yellowtail|Rye")
fam = "&".join("family=" + f for f in FONTS.split("|"))

JS = r"""
(async () => {
  const svg = document.querySelector('svg');
  svg.getBBox();
  await document.fonts.ready;
  await new Promise(r => setTimeout(r, 1500));
  await document.fonts.ready;
  const NS = 'http://www.w3.org/2000/svg';
  const SKIP = new Set(['x','y','dx','dy','text-anchor','textLength','lengthAdjust','startOffset','href','xlink:href','id','rotate']);
  let nPath = 0, nLen = 0;
  // 1) textPath -> буквы
  for (const tp of [...svg.querySelectorAll('textPath')]) {
    const t = tp.closest('text');
    const g = document.createElementNS(NS, 'g');
    const attrs = {};
    for (const a of t.attributes) if (!SKIP.has(a.name)) attrs[a.name] = a.value;
    for (const a of tp.attributes) if (!SKIP.has(a.name)) attrs[a.name] = a.value;
    for (const a of t.attributes) if (a.name === 'transform') g.setAttribute('transform', a.value);
    delete attrs.transform;
    const n = t.getNumberOfChars(), str = t.textContent;
    for (let i = 0; i < n; i++) {
      const ch = str[i]; if (!ch || !ch.trim()) continue;
      let p, r; try { p = t.getStartPositionOfChar(i); r = t.getRotationOfChar(i); } catch (e) { continue; }
      const c = document.createElementNS(NS, 'text');
      for (const k in attrs) c.setAttribute(k, attrs[k]);
      c.setAttribute('x', 0); c.setAttribute('y', 0);
      c.setAttribute('transform', `translate(${p.x.toFixed(2)} ${p.y.toFixed(2)}) rotate(${r.toFixed(2)})`);
      c.textContent = ch; g.appendChild(c);
    }
    t.replaceWith(g); nPath++;
  }
  // 2) textLength -> scale / letter-spacing
  for (const t of [...svg.querySelectorAll('text[textLength]')]) {
    const target = parseFloat(t.getAttribute('textLength'));
    const mode = t.getAttribute('lengthAdjust') || 'spacing';
    t.removeAttribute('textLength'); t.removeAttribute('lengthAdjust');
    const nat = t.getComputedTextLength();
    if (!nat || Math.abs(nat - target) < 0.5) { nLen++; continue; }
    if (mode === 'spacingAndGlyphs') {
      const bb = t.getBBox(), anc = t.getAttribute('text-anchor') || 'start';
      const ox = anc === 'middle' ? bb.x + bb.width / 2 : anc === 'end' ? bb.x + bb.width : bb.x;
      const s = target / nat, prev = t.getAttribute('transform') || '';
      t.setAttribute('transform', `${prev} translate(${ox.toFixed(2)} 0) scale(${s.toFixed(4)} 1) translate(${(-ox).toFixed(2)} 0)`.trim());
    } else {
      const n = t.getNumberOfChars();
      const ls = parseFloat(t.getAttribute('letter-spacing') || '0') + (target - nat) / Math.max(1, n - 1);
      t.setAttribute('letter-spacing', ls.toFixed(2));
    }
    nLen++;
  }
  const out = document.createElement('textarea'); out.id = 'OUT';
  out.textContent = new XMLSerializer().serializeToString(svg);
  document.body.appendChild(out);
  document.title = `DONE ${nPath} ${nLen}`;
})();
"""

raw = (ROOT / "board-raw.svg").read_text()
page = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" '
        f'href="https://fonts.googleapis.com/css2?{fam}&display=block"></head><body>{raw}<script>{JS}</script></body></html>')
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
    f.write(page); tmp = f.name
dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=30000",
                      "--dump-dom", "file://" + tmp], capture_output=True, text=True, timeout=180).stdout
m = re.search(r'<textarea id="OUT">(.*?)</textarea>', dom, re.S)
if not m:
    sys.exit("Chrome не вернул результат")
svg = html.unescape(m.group(1))
t = re.search(r"<title>(DONE[^<]*)</title>", dom)
(ROOT / "Primeegg_Logo-Exploration_v1.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n")
print("board-figma.svg OK;", t.group(1) if t else "", f"{len(svg)//1024} KB")
