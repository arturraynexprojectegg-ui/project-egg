"""Утилиты: запуск headless Chrome с Google Fonts и получение результата JS."""
import html, re, subprocess, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT_FAMILIES = [
    "Fraunces:ital,wght@0,300..900;1,300..900", "Playfair+Display:ital,wght@0,400..900;1,400..900", "DM+Serif+Display:ital@0;1",
    "Cormorant+Garamond:ital,wght@0,300..700;1,300..700", "Libre+Baskerville:ital,wght@0,400;0,700;1,400", "Abril+Fatface",
    "Lora:ital,wght@0,400..700;1,400..700", "Montserrat:ital,wght@0,300..900;1,300..900", "Manrope:wght@300..800",
    "Space+Grotesk:wght@300..700", "Syne:wght@400..800", "Bricolage+Grotesque:wght@300..800", "Outfit:wght@300..900",
    "Archivo+Black", "Josefin+Sans:ital,wght@0,300..700;1,300..700", "Bebas+Neue", "Oswald:wght@300..700",
    "Inter:wght@300..900", "Fredoka:wght@300..700", "Baloo+2:wght@400..800", "Nunito:ital,wght@0,300..900;1,300..900",
    "Quicksand:wght@300..700", "Pacifico", "Lobster", "Caveat:wght@400..700", "Yellowtail", "Rye",
]


def fonts_href(families=None, display="swap"):
    fams = families or FONT_FAMILIES
    return "https://fonts.googleapis.com/css2?" + "&".join("family=" + f for f in fams) + f"&display={display}"


def used_families(svg_text):
    """Возвращает подмножество FONT_FAMILIES, реально упомянутых в тексте."""
    out = []
    for f in FONT_FAMILIES:
        name = f.split(":")[0].replace("+", " ")
        if name in svg_text:
            out.append(f)
    return out


def chrome_eval(body_html, js_async_body, timeout=240):
    """Открывает страницу с body_html и всеми шрифтами, выполняет JS (тело async-функции,
    должно вернуть строку) и возвращает эту строку."""
    js = ("(async()=>{await document.fonts.ready;await new Promise(r=>setTimeout(r,1200));await document.fonts.ready;"
          "let __r;try{__r=await (async()=>{" + js_async_body + "})();}catch(e){__r='ERROR '+e.stack}"
          "const o=document.createElement('textarea');o.id='OUT';o.textContent=__r;document.body.appendChild(o);})();")
    page = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts_href(display="block")}">'
            f'</head><body>{body_html}<script>{js}</script></body></html>')
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(page); tmp = f.name
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=40000",
                          "--dump-dom", "file://" + tmp], capture_output=True, text=True, timeout=timeout).stdout
    m = re.search(r'<textarea id="OUT">(.*?)</textarea>', dom, re.S)
    if not m:
        raise RuntimeError("Chrome не вернул результат")
    res = html.unescape(m.group(1))
    if res.startswith("ERROR"):
        raise RuntimeError(res)
    return res


BAKE_JS = r"""
const NS='http://www.w3.org/2000/svg';
const SKIP=new Set(['x','y','dx','dy','text-anchor','textLength','lengthAdjust','startOffset','href','xlink:href','id','rotate']);
const svg=document.querySelector('svg'); let nP=0,nL=0;
for(const tp of [...svg.querySelectorAll('textPath')]){
  const t=tp.closest('text'); const g=document.createElementNS(NS,'g'); const at={};
  for(const a of t.attributes) if(!SKIP.has(a.name)) at[a.name]=a.value;
  for(const a of tp.attributes) if(!SKIP.has(a.name)) at[a.name]=a.value;
  if(at.transform){g.setAttribute('transform',at.transform); delete at.transform;}
  const n=t.getNumberOfChars(), s=t.textContent;
  for(let i=0;i<n;i++){const ch=s[i]; if(!ch||!ch.trim()) continue; let p,r;
    try{p=t.getStartPositionOfChar(i); r=t.getRotationOfChar(i);}catch(e){continue}
    const c=document.createElementNS(NS,'text'); for(const k in at) c.setAttribute(k,at[k]);
    c.setAttribute('x',0); c.setAttribute('y',0);
    c.setAttribute('transform',`translate(${p.x.toFixed(2)} ${p.y.toFixed(2)}) rotate(${r.toFixed(2)})`);
    c.textContent=ch; g.appendChild(c);}
  t.replaceWith(g); nP++;
}
for(const t of [...svg.querySelectorAll('text[textLength]')]){
  const target=parseFloat(t.getAttribute('textLength')); const mode=t.getAttribute('lengthAdjust')||'spacing';
  t.removeAttribute('textLength'); t.removeAttribute('lengthAdjust');
  const nat=t.getComputedTextLength(); if(!nat||Math.abs(nat-target)<0.5){nL++;continue}
  if(mode==='spacingAndGlyphs'){const bb=t.getBBox(), anc=t.getAttribute('text-anchor')||'start';
    const ox=anc==='middle'?bb.x+bb.width/2:anc==='end'?bb.x+bb.width:bb.x; const sc=target/nat;
    t.setAttribute('transform',`${t.getAttribute('transform')||''} translate(${ox.toFixed(2)} 0) scale(${sc.toFixed(4)} 1) translate(${(-ox).toFixed(2)} 0)`.trim());
  } else { const n=t.getNumberOfChars();
    t.setAttribute('letter-spacing',(parseFloat(t.getAttribute('letter-spacing')||'0')+(target-nat)/Math.max(1,n-1)).toFixed(2)); }
  nL++;
}
return new XMLSerializer().serializeToString(svg);
"""


def bake_for_figma(svg_text):
    """textPath и textLength -> обычный текст, как его рисует браузер."""
    svg_text = re.sub(r"<\?xml[^>]*\?>", "", svg_text)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + chrome_eval(svg_text, BAKE_JS) + "\n"
