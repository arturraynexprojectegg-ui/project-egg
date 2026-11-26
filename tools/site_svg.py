#!/usr/bin/env python3
"""Сайт (HTML) -> SVG для Figma: точный растровый фон + редактируемый текст + исходный вектор.

  python3 tools/site_svg.py <site.html> <out.svg> [width=1440]

Слои в SVG:
  1. «Фон» — скриншот страницы, где спрятан весь текст и вся инлайн-SVG-графика
     (остаются плашки, градиенты, рамки, тени, декоративные псевдоэлементы).
  2. «Графика» — все инлайн-SVG страницы (логотипы, мокапы, карты, иконки) векторами, со стилями, перенесёнными в атрибуты.
  3. «Текст» — каждый видимый фрагмент текста отдельной строкой <text> с реальным шрифтом, кеглем, весом и цветом.
Мобильная ширина (<500) рендерится в iframe — headless Chrome не умеет окно уже 500 px."""
import base64, io, json, re, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chrome_util import CHROME
from PIL import Image

src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
args = [a for a in sys.argv[3:] if not a.startswith("--")]
W = int(args[0]) if args else 1440
VH = 900 if W > 600 else 800
CHUNK = 6000
tmp = Path(tempfile.mkdtemp())

base = src.read_text()
base = re.sub(r"(-?\d*\.?\d+)(d|s|l)?vh\b", lambda m: f"{float(m.group(1)) * VH / 100:.2f}px", base)
FREEZE = ("<style>*,*::before,*::after{animation-duration:0.001s!important;animation-delay:0s!important;animation-iteration-count:1!important;"
          "transition-duration:0s!important;transition-delay:0s!important;scroll-behavior:auto!important}"
          "</style>")
base = base.replace("</head>", FREEZE + "</head>", 1)
(page_v := tmp / "v.html").write_text(base)

HIDE_JS = r"""
(function(){
 const all=[...document.querySelectorAll('body *')];
 const rules=[]; let n=0;
 for(const el of all){
   if(el.closest('svg')) continue;
   const cs=getComputedStyle(el);
   for(const s of ['Top','Right','Bottom','Left']) el.style.setProperty('border-'+s.toLowerCase()+'-color',cs['border'+s+'Color'],'important');
   el.style.setProperty('outline-color',cs.outlineColor,'important');
   el.style.setProperty('text-decoration-color','transparent','important');
   el.style.setProperty('background-color',cs.backgroundColor,'important');
   el.style.setProperty('box-shadow',cs.boxShadow,'important');
   for(const p of ['::before','::after','::marker']){
     const ps=getComputedStyle(el,p);
     if(ps.content && ps.content!=='none' && ps.content!=='normal'){
       el.dataset.pk=el.dataset.pk||(++n);
       rules.push(`[data-pk="${el.dataset.pk}"]${p}{color:${ps.color}!important;-webkit-text-fill-color:${ps.color}!important;`+
         `border-color:${ps.borderTopColor}!important;background-color:${ps.backgroundColor}!important}`);
     }
   }
 }
 const st=document.createElement('style');
 st.textContent='body *:not(svg):not(svg *){color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important}'+
   'input::placeholder,textarea::placeholder{color:transparent!important;-webkit-text-fill-color:transparent!important}'+
   'svg{visibility:hidden!important}'+rules.join('');
 document.head.appendChild(st);
})();
"""
(page_h := tmp / "h.html").write_text(base.replace("</body>", f"<script>window.addEventListener('load',()=>setTimeout(()=>{{{HIDE_JS}}},800));</script></body>", 1))

# ------------------------------------------------------------------ сериализатор (работает в iframe)
SER_JS = r"""
async function serialize(win){
 const d=win.document; await d.fonts.ready; await new Promise(r=>setTimeout(r,1500)); await d.fonts.ready;
 const H=Math.ceil(Math.max(d.documentElement.scrollHeight,d.body.scrollHeight));
 const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
 const cvs=d.createElement('canvas').getContext('2d');
 const parseC=c=>{const m=c.match(/rgba?\(([^)]+)\)/); if(!m) return null; const p=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
   const a=p.length>3?p[3]:1; if(a===0) return null; return {hex:'#'+p.slice(0,3).map(v=>Math.round(v).toString(16).padStart(2,'0')).join(''),a}};
 const opac=el=>{let o=1; for(let e=el;e&&e.nodeType===1;e=e.parentElement){o*=parseFloat(win.getComputedStyle(e).opacity)} return o};
 const visible=el=>{for(let e=el;e&&e.nodeType===1;e=e.parentElement){const cs=win.getComputedStyle(e); if(cs.display==='none'||cs.visibility==='hidden'||cs.contentVisibility==='hidden') return false} return true};
 const fam=f=>f.split(',')[0].replace(/["']/g,'').trim();
 const out=[]; const svgs=[];
 // ---------- текст
 const tw=d.createTreeWalker(d.body,NodeFilter.SHOW_TEXT);
 const range=d.createRange();
 let node;
 while(node=tw.nextNode()){
   const p=node.parentElement; if(!p||p.closest('svg,script,style,noscript,template,select,option,textarea')) continue;
   if(!node.data.trim()) continue; if(!visible(p)) continue;
   const cs=win.getComputedStyle(p); const col=parseC(cs.webkitTextFillColor&&cs.webkitTextFillColor!=='currentcolor'?cs.webkitTextFillColor:cs.color)||parseC(cs.color);
   if(!col) continue;
   const o=opac(p)*col.a; if(o<0.02) continue;
   const font=`${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`; cvs.font=font;
   const asc=cvs.measureText('Hg').fontBoundingBoxAscent;
   const tt=cs.textTransform; const ls=parseFloat(cs.letterSpacing)||0;
   const txt=node.data; let line=null; const lines=[];
   for(let i=0;i<txt.length;i++){
     range.setStart(node,i); range.setEnd(node,i+1);
     const rs=range.getClientRects(); if(!rs.length) continue; const r=rs[0]; if(r.width===0&&!/\s/.test(txt[i])) continue;
     const top=Math.round(r.top);
     if(!line||Math.abs(top-line.top)>2){ line={top,x:r.left,y:r.top,ch:''}; lines.push(line); }
     line.ch+=txt[i];
   }
   for(const L of lines){
     let s=cs.whiteSpace.startsWith('pre')?L.ch:L.ch.replace(/\s+/g,' ');
     if(tt==='uppercase') s=s.toUpperCase(); else if(tt==='lowercase') s=s.toLowerCase();
     else if(tt==='capitalize') s=s.replace(/(^|\s)(\S)/g,(m,a,b)=>a+b.toUpperCase());
     const lead=s.match(/^\s*/)[0].length; let x=L.x; if(lead){ s=s.trimStart(); x+=lead*parseFloat(cs.fontSize)*0.25; }
     s=s.trimEnd(); if(!s) continue;
     const sx=win.scrollX, sy=win.scrollY;
     out.push(`<text x="${(x+sx).toFixed(1)}" y="${(L.y+sy+asc).toFixed(1)}" font-family="${esc(fam(cs.fontFamily))}" font-size="${parseFloat(cs.fontSize).toFixed(1)}" font-weight="${cs.fontWeight}"`+
       (cs.fontStyle==='italic'?' font-style="italic"':'')+(ls?` letter-spacing="${ls.toFixed(2)}"`:'')+` fill="${col.hex}"`+(o<0.999?` fill-opacity="${o.toFixed(3)}"`:'')+` xml:space="preserve">${esc(s)}</text>`);
   }
 }
 // ---------- плейсхолдеры и значения полей
 for(const el of d.querySelectorAll('input,textarea,select')){
   if(!visible(el)) continue; const r=el.getBoundingClientRect(); if(!r.width) continue;
   let s='', cs=win.getComputedStyle(el), color=cs.color;
   if(el.tagName==='SELECT'){ s=el.options[el.selectedIndex]?.text||''; }
   else if(['checkbox','radio','hidden','submit','button','range','color','file'].includes(el.type)) continue;
   else if(el.value){ s=el.value } else if(el.placeholder){ s=el.placeholder; color=win.getComputedStyle(el,'::placeholder').color }
   const c=parseC(color); if(!s||!c) continue;
   const pl=parseFloat(cs.paddingLeft)+parseFloat(cs.borderLeftWidth); cvs.font=`${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
   const asc=cvs.measureText('Hg').fontBoundingBoxAscent, dsc=cvs.measureText('Hg').fontBoundingBoxDescent;
   const y=el.tagName==='TEXTAREA'? r.top+parseFloat(cs.paddingTop)+parseFloat(cs.borderTopWidth)+asc : r.top+(r.height-(asc+dsc))/2+asc;
   out.push(`<text x="${(r.left+pl+win.scrollX).toFixed(1)}" y="${(y+win.scrollY).toFixed(1)}" font-family="${esc(fam(cs.fontFamily))}" font-size="${parseFloat(cs.fontSize).toFixed(1)}" font-weight="${cs.fontWeight}" fill="${c.hex}"`+(c.a<1?` fill-opacity="${c.a}"`:'')+`>${esc(s)}</text>`);
 }
 // ---------- инлайн-SVG
 const PROPS=['fill','fill-opacity','fill-rule','stroke','stroke-width','stroke-opacity','stroke-dasharray','stroke-dashoffset','stroke-linecap','stroke-linejoin','opacity','font-family','font-size','font-weight','font-style','letter-spacing','text-anchor','dominant-baseline','visibility','display','stop-color','stop-opacity','clip-rule'];
 let sid=0;
 function copyStyles(o,c){
   if(o.nodeType!==1) return;
   const cs=win.getComputedStyle(o);
   for(const p of PROPS){ let v=cs.getPropertyValue(p); if(!v) continue;
     if(p==='font-family') v=fam(v);
     if((p==='fill'||p==='stroke'||p==='stop-color')){ if(v.startsWith('url(')) v=v.replace(/url\("?[^#]*#([^")]+)"?\)/,'url(#$1)'); else {const pc=parseC(v); if(v==='none'){} else if(pc){ v=pc.hex; if(pc.a<1&&p!=='stop-color') c.setAttribute(p+'-opacity',pc.a); if(pc.a<1&&p==='stop-color') c.setAttribute('stop-opacity',pc.a);} else if(v.includes('rgba(0, 0, 0, 0)')) v='none'; } }
     if(p==='display'&&v!=='none') continue; if(p==='visibility'&&v!=='hidden') continue;
     c.setAttribute(p,v);
   }
   c.removeAttribute('class'); c.removeAttribute('style');
   const oc=[...o.childNodes], cc=[...c.childNodes];
   for(let i=0;i<oc.length;i++) if(cc[i]) copyStyles(oc[i],cc[i]);
 }
 function expandUse(root, orig){
   // <use href="#id"> -> копия цели (symbol -> вложенный svg)
   const uses=[...root.querySelectorAll('use')];
   for(const u of uses){
     const href=u.getAttribute('href')||u.getAttribute('xlink:href'); if(!href||!href.startsWith('#')) continue;
     const t=d.getElementById(href.slice(1)); if(!t) continue;
     const clone=t.cloneNode(true); copyStyles(t,clone);
     let rep;
     if(t.tagName.toLowerCase()==='symbol'){
       rep=d.createElementNS('http://www.w3.org/2000/svg','svg');
       for(const a of ['viewBox','preserveAspectRatio']) if(t.getAttribute(a)) rep.setAttribute(a,t.getAttribute(a));
       for(const a of ['x','y','width','height']) if(u.getAttribute(a)) rep.setAttribute(a,u.getAttribute(a));
       while(clone.firstChild) rep.appendChild(clone.firstChild);
     } else { rep=d.createElementNS('http://www.w3.org/2000/svg','g'); rep.appendChild(clone);
       const x=u.getAttribute('x')||0, y=u.getAttribute('y')||0; if(x||y) rep.setAttribute('transform',`translate(${x},${y})`); }
     for(const a of ['transform','fill','stroke','opacity','color']) if(u.getAttribute(a)&&a!=='transform') rep.setAttribute(a,u.getAttribute(a));
     if(u.getAttribute('transform')) rep.setAttribute('transform',(u.getAttribute('transform')+' '+(rep.getAttribute('transform')||'')).trim());
     u.replaceWith(rep);
     expandUse(rep);
   }
 }
 for(const s of d.querySelectorAll('svg')){
   if(s.parentElement&&s.parentElement.closest('svg')) continue; if(!visible(s)) continue;
   const r=s.getBoundingClientRect(); if(r.width<1||r.height<1) continue;
   if(r.bottom+win.scrollY<0||r.top>H) continue;
   const o=opac(s); if(o<0.02) continue;
   const c=s.cloneNode(true); copyStyles(s,c); expandUse(c);
   sid++; const pre='g'+sid+'-';
   const all=[c,...c.querySelectorAll('*')];
   const ids={}; for(const e of all){ const id=e.getAttribute('id'); if(id){ ids[id]=pre+id; e.setAttribute('id',pre+id);} }
   for(const e of all){ for(const a of [...e.attributes]){ if(a.value.includes('url(#')||a.name==='href'||a.name==='xlink:href'){
     e.setAttribute(a.name,a.value.replace(/#([\w\-:.]+)/g,(m,id)=>ids[id]?('#'+ids[id]):m)); } } }
   for(const e of c.querySelectorAll('script,title,desc')) e.remove();
   c.setAttribute('x',(r.left+win.scrollX).toFixed(2)); c.setAttribute('y',(r.top+win.scrollY).toFixed(2));
   c.setAttribute('width',r.width.toFixed(2)); c.setAttribute('height',r.height.toFixed(2));
   if(!c.getAttribute('viewBox')) c.setAttribute('viewBox',`0 0 ${r.width} ${r.height}`);
   c.setAttribute('overflow','hidden');
   for(const a of ['class','style','role','aria-hidden','aria-label','focusable','data-pk']) c.removeAttribute(a);
   const ser=new XMLSerializer().serializeToString(c);
   svgs.push(o<0.999?`<g opacity="${o.toFixed(3)}">${ser}</g>`:ser);
 }
 return JSON.stringify({H, text:out.join('\n'), svgs:svgs.join('\n')});
}
"""


def run_dump(html, size):
    f = tmp / "w.html"; f.write_text(html)
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", f"--window-size={size[0]},{size[1]}",
                           "--virtual-time-budget=40000", "--dump-dom", f.as_uri()], capture_output=True, text=True, timeout=300).stdout


wrapper = f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0}}iframe{{border:0;display:block}}</style></head>
<body><iframe id="f" src="{page_v.as_uri()}" width="{W}" height="{VH}" scrolling="no"></iframe>
<script>{SER_JS}
const f=document.getElementById('f');
f.addEventListener('load',async()=>{{
  const w=f.contentWindow; await w.document.fonts.ready; await new Promise(r=>setTimeout(r,1200));
  const H=Math.ceil(Math.max(w.document.documentElement.scrollHeight,w.document.body.scrollHeight)); f.height=H;
  await new Promise(r=>setTimeout(r,800));
  let res; try{{res=await serialize(w)}}catch(e){{res='ERROR '+e.stack}}
  const t=document.createElement('textarea'); t.id='OUT'; t.textContent=res; document.body.appendChild(t);
}});
</script></body></html>"""
dom = run_dump(wrapper, (max(W, 500), VH))
import html as H_
m = re.search(r'<textarea id="OUT">(.*?)</textarea>', dom, re.S)
if not m:
    sys.exit("сериализатор не вернул результат")
raw = H_.unescape(m.group(1))
if raw.startswith("ERROR"):
    sys.exit(raw)
res = json.loads(raw)
Hpx = res["H"]

# ------------------------------------------------------------------ фон: скриншоты кусками
tiles = []
for y0 in range(0, Hpx, CHUNK):
    ch = min(CHUNK, Hpx - y0)
    shot = f"""<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;overflow:hidden}}
#c{{width:{W}px;height:{ch}px;overflow:hidden;position:relative}}iframe{{border:0;display:block;position:absolute;left:0;top:{-y0}px}}</style></head>
<body><div id="c"><iframe src="{page_h.as_uri()}" width="{W}" height="{Hpx}" scrolling="no"></iframe></div></body></html>"""
    f = tmp / f"s{y0}.html"; f.write_text(shot)
    png = tmp / f"s{y0}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={max(W, 500)},{ch}", "--virtual-time-budget=40000", f"--screenshot={png}", f.as_uri()],
                   capture_output=True, timeout=300)
    im = Image.open(png).convert("RGB").crop((0, 0, W, ch))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88, optimize=True)
    tiles.append(f'<image x="0" y="{y0}" width="{W}" height="{ch}" preserveAspectRatio="none" '
                 f'href="data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode()}"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{Hpx}" viewBox="0 0 {W} {Hpx}">\n'
       f'<g id="Фон">{"".join(tiles)}</g>\n<g id="Графика">{res["svgs"]}</g>\n<g id="Текст">{res["text"]}</g>\n</svg>\n')
out.write_text(svg)
print(f"{out.name}: {W}×{Hpx}, текстовых строк {res['text'].count('<text')}, svg {res['svgs'].count('<svg') }, {out.stat().st_size // 1024} KB")
