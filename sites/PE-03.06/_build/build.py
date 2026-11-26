import re, json, sys, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import art
from strings import ES, UK

SITE = Path("/Users/arturkasian/Project Egg/sites/PE-03.06")
A = SITE / "assets"
TPL = (Path(__file__).parent / "template.html").read_text()

def inner(svg):
    return re.sub(r'^\s*<svg[^>]*>|</svg>\s*$', '', svg.strip())

def svgfile(name, **attrs):
    s = (A / name).read_text().strip()
    extra = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in attrs.items())
    return s.replace("<svg ", f"<svg {extra} ", 1)

def uri(svg):
    svg = re.sub(r'>\s+<', '><', svg.strip()).replace('"', "'")
    return urllib.parse.quote(svg, safe=" =:/;,'-.()")

pat = (A / "pattern.svg").read_text()
pat_cal = pat.replace("#C8553D", "#F4ECDC").replace("#F2A541", "#F4ECDC")
pat_cob = pat.replace("#C8553D", "#1F4E9C").replace("#F2A541", "#1F4E9C")

SCENES = {"retail": "scene-pack_retail.svg", "horeca": "scene-pack_horeca.svg",
          "powder": "scene-pack_powder.svg", "log": "scene-logistics.svg"}
sprite = ['<svg width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">']
for k, f in SCENES.items():
    sprite.append(f'<symbol id="sc-{k}" viewBox="0 0 1680 700">{inner((A/f).read_text())}</symbol>')
sprite.append('</svg>')
sprite = "".join(sprite)

def crop(sym, vb, label):
    return (f'<svg viewBox="{vb}" role="img" aria-label="{label}" style="width:100%;height:auto">'
            f'<use href="#sc-{sym}" width="1680" height="700"/></svg>')

PROV = ["A Coruña","Álava","Albacete","Alicante","Almería","Asturias","Ávila","Badajoz","Baleares","Barcelona","Burgos","Cáceres","Cádiz","Cantabria","Castellón","Ceuta","Ciudad Real","Córdoba","Cuenca","Girona","Granada","Guadalajara","Gipuzkoa","Huelva","Huesca","Jaén","La Rioja","Las Palmas","León","Lleida","Lugo","Madrid","Málaga","Melilla","Murcia","Navarra","Ourense","Palencia","Pontevedra","Salamanca","Santa Cruz de Tenerife","Segovia","Sevilla","Soria","Tarragona","Teruel","Toledo","Valencia","Valladolid","Bizkaia","Zamora","Zaragoza"]

def build(t, fname):
    uk = t["lang"] == "uk"
    other = ("index.html", "es", "ES") if uk else ("uk.html", "uk", "UA")
    def lsw(tag, extra=""):
        es_cur = '' if uk else ' aria-current="true"'
        uk_cur = ' aria-current="true"' if uk else ''
        return (f'<{tag} class="lang" aria-label="{t["lang_aria"]}"{extra}><a href="index.html" hreflang="es" lang="es"{es_cur}>ES</a>'
                f'<span aria-hidden="true">|</span><a href="uk.html" hreflang="uk" lang="uk"{uk_cur}>UA</a></{tag}>')
    days = "".join(f'<li class="{"on" if i in (0,3) else ""}"><span>{d}</span>{"<small>"+t["deliv"]+"</small>" if i in (0,3) else ""}</li>'
                   for i, d in enumerate(t["days"]))
    days = days.replace(' class=""', '')
    egg_ico = lambda col: f'<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M12 3.5c3.4 0 6 5.2 6 9.6 0 4-2.7 7.4-6 7.4s-6-3.4-6-7.4c0-4.4 2.6-9.6 6-9.6z" fill="{col}"/></svg>'
    fonts_es = "family=DM+Serif+Display:ital@0;1&family=Josefin+Sans:wght@400;600;700"
    fonts_uk = fonts_es + "&family=Playfair+Display:ital,wght@0,400;0,500;1,400&family=Montserrat:wght@400;500;600"
    R = {
        "fonts": fonts_uk if uk else fonts_es,
        "f_head": "'Playfair Display', Georgia, serif" if uk else "'DM Serif Display', Georgia, serif",
        "f_body": "'Montserrat', 'Helvetica Neue', Arial, sans-serif" if uk else "'Josefin Sans', 'Helvetica Neue', Arial, sans-serif",
        "hw": "500" if uk else "400", "body_size": "1rem" if uk else "1.125rem", "body_size_m": "1rem" if uk else "1.0625rem",
        "favicon": uri((A/"logo-mark.svg").read_text()),
        "pat_color": uri(pat), "flower": uri(art.petal()), "pat_cal": uri(pat_cal), "pat_cob": uri(pat_cob),
        "sprite": sprite,
        "logo_h": svgfile("logo-horizontal.svg", role="img", aria_label="Primeegg").replace('viewBox="0 0 640 200"', 'viewBox="60 18 528 164"'),
        "logo_primary": svgfile("logo-primary.svg", role="img", aria_label="Primeegg — Huevos de granja · España 2026").replace('viewBox="0 0 400 300"', 'viewBox="56 26 288 248"'),
        "logo_inverse": svgfile("logo-inverse.svg", role="img", aria_label="Primeegg").replace('viewBox="0 0 400 300"', 'viewBox="56 26 288 248"'),
        "logo_mark": svgfile("logo-mark.svg", aria_hidden="true"), "logo_mark2": svgfile("logo-mark.svg", aria_hidden="true"),
        "lang_sw": lsw("nav"), "lang_sw_ftr": lsw("div", ' role="group"'),
        "regions": "".join(f"<li>{r}</li>" for r in t["regions"]),
        "sc_retail12": crop("retail", "570 160 630 440", t["retail_aria"]),
        "sc_bag": crop("powder", "285 55 420 600", t["bag_aria"]),
        "sc_pouch": crop("powder", "780 185 330 470", t["pouch_aria"]),
        "sc_tray": crop("horeca", "225 80 570 540", t["tray_aria"]),
        "sc_truck": crop("log", "70 90 1090 560", t["truck_aria"]),
        "sc_pallet": crop("log", "1210 240 400 410", t["pallet_aria"]),
        "sizes": art.egg_sizes(t), "map": art.spain_map(t), "stamped": art.stamped_egg(t["stamped_aria"]),
        "d_tortilla": art.tortilla(t["tortilla_aria"]), "d_flan": art.flan(t["flan_aria"]), "d_mayo": art.mayonesa(t["mayo_aria"]),
        "days": days, "egg_ico_ind": egg_ico("#0E2140"), "egg_ico_cal": egg_ico("#F4ECDC"),
        "provinces": "".join(f"<option>{p}</option>" for p in PROV),
        "msgs": json.dumps(t["msgs"], ensure_ascii=False),
    }
    for n in art.ICONS:
        R["i_" + n] = art.icon(n)
    out = TPL
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: R[m.group(1)], out)
    def sub(m):
        k = m.group(1)
        if k not in t: raise KeyError(k)
        return t[k]
    out = re.sub(r"\[\[(\w+)\]\]", sub, out)
    (SITE / fname).write_text(out)
    print(fname, len(out)//1024, "KB")

build(ES, "index.html")
build(UK, "uk.html")
