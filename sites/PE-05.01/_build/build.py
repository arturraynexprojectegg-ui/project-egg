import re, json, os, sys, urllib.parse, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from strings import ES, UK
SITE = "/Users/arturkasian/Project Egg/sites/PE-05.01"
A = SITE + "/assets/"
TPL = open(os.path.join(HERE, "template.html")).read()

def inline(fname, vb, suf, label, cls=""):
    s = open(A + fname).read()
    s = re.sub(r'<\?xml[^>]*>', '', s).strip()
    s = re.sub(r'<svg([^>]*?)viewBox="[^"]*"', lambda m: '<svg%s viewBox="%s"' % (m.group(1), vb), s, 1)
    attrs = ' role="img" aria-label="%s" preserveAspectRatio="xMidYMid meet"%s' % (label, (' class="%s"' % cls) if cls else '')
    s = s.replace('<svg', '<svg' + attrs, 1)
    if suf:
        s = re.sub(r'id="([^"]+)"', lambda m: 'id="%s%s"' % (m.group(1), suf), s)
        s = re.sub(r'url\(#([^)]+)\)', lambda m: 'url(#%s%s)' % (m.group(1), suf), s)
        s = re.sub(r'href="#([^"]+)"', lambda m: 'href="#%s%s"' % (m.group(1), suf), s)
    return s

def ico(d):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % d

ICONS = {
 "ico_check": ico('<path d="m5 12.5 4.2 4.2L19 7"/>'),
 "ico_user": ico('<circle cx="12" cy="8" r="3.6"/><path d="M4.5 20c1.2-3.8 4-5.6 7.5-5.6s6.3 1.8 7.5 5.6"/>'),
 "ico_tray": ico('<rect x="3" y="6" width="18" height="12" rx="1.5"/><circle cx="7.5" cy="10" r="1.5"/><circle cx="12" cy="10" r="1.5"/><circle cx="16.5" cy="10" r="1.5"/><circle cx="7.5" cy="14.2" r="1.5"/><circle cx="12" cy="14.2" r="1.5"/><circle cx="16.5" cy="14.2" r="1.5"/>'),
 "ico_clock": ico('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
 "ico_person": ico('<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19c.9-3.2 3-4.8 5.5-4.8s4.6 1.6 5.5 4.8"/><path d="M16 5.5c1.6.4 2.7 1.7 2.7 3.2s-1.1 2.8-2.7 3.2M17.5 14.6c1.6.6 2.6 2 3 4.4"/>'),
 "ico_cal": ico('<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/><path d="m8.5 14.5 2.2 2.2 4.6-4.6"/>'),
 "ico_snow": ico('<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/><path d="m9.5 4.5 2.5 2 2.5-2M9.5 19.5l2.5-2 2.5 2"/>'),
 "ico_box": ico('<path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5 12 12l8.5-4.5M12 12v9"/>'),
 "ico_temp": ico('<path d="M14 14.5V5a2 2 0 1 0-4 0v9.5a4 4 0 1 0 4 0Z"/><path d="M12 9v7"/>'),
 "ico_search": ico('<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5"/><path d="M10.5 7.5v6M7.5 10.5h6"/>'),
 "ico_doc": ico('<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 15.5h6M9 8.5h2"/>'),
 "ico_seal": ico('<circle cx="12" cy="10" r="6"/><path d="m8.5 15-1.5 6 5-2.5 5 2.5-1.5-6"/><path d="m9.6 10 1.6 1.6 3.2-3.2"/>'),
}
def egg(h):
    return '<svg viewBox="0 0 40 50" style="height:%dpx;margin-top:%dpx" aria-hidden="true"><path d="M20 3C10 3 4 18 4 29c0 10 7 18 16 18s16-8 16-18C36 18 30 3 20 3Z" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>' % (h, 26 - h)
ICONS.update(egg_s=egg(16), egg_m=egg(19), egg_l=egg(22), egg_xl=egg(26))

PIN = 'M50 130 C78 130 100 85 100 50 C100 20 78 0 50 0 C22 0 0 20 0 50 C0 85 22 130 50 130 Z'

P = [
 ("C","A Coruña",0,0,"z48"),("LU","Lugo",1,0,"z48"),("O","Asturias",2,0,"z48"),("S","Cantabria",3,0,"z24"),("BI","Bizkaia",4,0,"z24"),("SS","Gipuzkoa",5,0,"z48"),
 ("PO","Pontevedra",0,1,"z48"),("OU","Ourense",1,1,"z48"),("LE","León",2,1,"z24"),("P","Palencia",3,1,"z24"),("BU","Burgos",4,1,"z24"),("VI","Álava",5,1,"z24"),("NA","Navarra",6,1,"z24"),("HU","Huesca",7,1,"z48"),("L","Lleida",8,1,"z48"),("GI","Girona",9,1,"z48"),
 ("ZA","Zamora",1,2,"z24"),("VA","Valladolid",2,2,"z24"),("SG","Segovia",3,2,"z24"),("SO","Soria",4,2,"z24"),("LO","La Rioja",5,2,"z24"),("Z","Zaragoza",6,2,"z24"),("T","Tarragona",7,2,"z24"),("B","Barcelona",8,2,"z24"),
 ("SA","Salamanca",1,3,"z24"),("AV","Ávila",2,3,"z24"),("M","Madrid",3,3,"z24"),("GU","Guadalajara",4,3,"z24"),("TE","Teruel",5,3,"z48"),("CS","Castellón",6,3,"z24"),
 ("CC","Cáceres",1,4,"z24"),("TO","Toledo",2,4,"z24"),("CU","Cuenca",3,4,"z24"),("AB","Albacete",4,4,"z24"),("V","Valencia",5,4,"z24"),("PM","Illes Balears",7,4,"z48"),
 ("BA","Badajoz",1,5,"z24"),("CR","Ciudad Real",2,5,"z24"),("J","Jaén",3,5,"z24"),("MU","Murcia",4,5,"z24"),("A","Alicante",5,5,"z24"),
 ("H","Huelva",0,6,"z48"),("SE","Sevilla",1,6,"z24"),("CO","Córdoba",2,6,"z24"),("GR","Granada",3,6,"z24"),("AL","Almería",4,6,"z48"),
 ("CA","Cádiz",1,7,"z48"),("MA","Málaga",2,7,"z24"),
 ("CE","Ceuta",1,8,"z72"),("ML","Melilla",3,8,"z72"),("GC","Las Palmas",6,8,"z72"),("TF","S. C. de Tenerife",7,8,"z72"),
]

def map_svg(L):
    st, ts, ox, oy = 56, 50, 4, 4
    W, H = 10*st, 9*st + 8
    o = ['<svg id="spain" viewBox="0 0 %d %d" role="group" aria-label="%s">' % (W, H, L["map_aria"])]
    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="none" stroke="#7D9AB0" stroke-opacity=".5" stroke-dasharray="2 4"/>' % (ox+6*st-6, oy+8*st-6, 2*st+6, st+6))
    o.append('<text class="lbl" x="%d" y="%d">%s</text>' % (ox+8*st+8, oy+8*st+30, L["canarias"]))
    o.append('<text class="lbl" x="%d" y="%d">%s</text>' % (ox+7*st, oy+4*st+68, L["baleares"]))
    o.append('<text class="lbl" x="%d" y="%d">%s</text>' % (ox+6*st+8, oy+30, L["fr"]))
    o.append('<text class="lbl" x="%d" y="%d">%s</text>' % (ox+6*st, oy+6*st+30, L["med"]))
    o.append('<text class="lbl" transform="translate(%d %d) rotate(-90)" text-anchor="middle">PORTUGAL</text>' % (ox+30, oy+4*st+28))
    for k, n, c, r, z in P:
        x, y = ox + c*st, oy + r*st
        zl = z[1:] + " " + L["u_h"]
        o.append('<g class="tile %s" data-k="%s" tabindex="0" role="button" aria-label="%s — %s"><rect x="%d" y="%d" width="%d" height="%d" rx="4"/><text x="%g" y="%d" text-anchor="middle">%s</text></g>' % (z, k, n, zl, x, y, ts, ts, x+ts/2, y+30, k))
    mx, my = ox + 3*st + ts - 4, oy + 3*st + 6
    o.append('<g aria-hidden="true" style="pointer-events:none" transform="translate(%g %g) scale(.17) translate(-50 -130)"><path d="%s" fill="#F2B705" stroke="#0A2A40" stroke-width="12"/><circle cx="50" cy="50" r="18" fill="#0A2A40"/></g>' % (mx, my, PIN))
    o.append('</svg>')
    return "".join(o)

def hero_svg(L):
    o = ['<svg viewBox="0 0 640 450" role="img" aria-label="%s">' % L["hero_aria"], '<rect width="640" height="450" fill="#0A2A40"/>']
    rnd = random.Random(7)
    for gx in range(0, 640, 80):
        for gy in range(0, 450, 70):
            if rnd.random() < .55:
                o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="#0E3352"/>' % (gx+8, gy+8, 64 - rnd.choice([0, 22]), 54 - rnd.choice([0, 20])))
    for gx in range(0, 641, 80):
        o.append('<line x1="%d" y1="0" x2="%d" y2="450" stroke="#B9CCDA" stroke-opacity=".07"/>' % (gx, gx))
    for gy in range(0, 451, 70):
        o.append('<line x1="0" y1="%d" x2="640" y2="%d" stroke="#B9CCDA" stroke-opacity=".07"/>' % (gy, gy))
    o.append('<path d="M-20 300 C160 250 300 330 660 120" fill="none" stroke="#B9CCDA" stroke-opacity=".12" stroke-width="10"/>')
    o.append('<path d="M120 -10 C150 160 90 300 140 460" fill="none" stroke="#B9CCDA" stroke-opacity=".09" stroke-width="7"/>')
    route = "M82 392 H196 Q212 392 212 376 V292 Q212 276 228 276 H356 Q372 276 372 260 V180 Q372 164 388 164 H520"
    o.append('<path d="%s" fill="none" stroke="#4F7FA3" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round"/>' % route)
    o.append('<path class="route-draw" pathLength="1" d="%s" fill="none" stroke="#F2B705" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>' % route)
    o.append('<g><rect x="34" y="368" width="48" height="48" rx="4" fill="#F7F3EA"/><path d="M42 406v-17l16-9 16 9v17" fill="none" stroke="#0B3C5D" stroke-width="3" stroke-linejoin="round"/><rect x="52" y="394" width="12" height="12" fill="#0B3C5D"/></g>')
    o.append('<text x="34" y="354" font-family="Inter,sans-serif" font-size="11.5" font-weight="600" letter-spacing="1" fill="#B9CCDA">%s</text>' % L["h_wh"])
    o.append('<text x="34" y="438" font-family="Montserrat,sans-serif" font-size="13" font-weight="700" fill="#FFFFFF">04:55</text>')
    stops = [(212, 334, 226, 338, "05:31"), (292, 276, 276, 260, "05:58"), (372, 218, 386, 222, "06:20")]
    for i, (x, y, tx, ty, t) in enumerate(stops):
        o.append('<g class="stop" style="animation-delay:%.2fs;transform-origin:%dpx %dpx"><circle cx="%d" cy="%d" r="8" fill="#0A2A40" stroke="#FFFFFF" stroke-width="3"/><text x="%d" y="%d" font-family="Montserrat,sans-serif" font-size="12" font-weight="700" fill="#FFFFFF">%s</text></g>' % (0.7 + i*0.4, x, y, x, y, tx, ty, t))
    o.append('<g><rect x="292" y="84" width="180" height="48" rx="4" fill="#FFFFFF"/><text x="306" y="103" font-family="Inter,sans-serif" font-size="10.5" font-weight="600" letter-spacing="1" fill="#4B5F6E">%s</text><text x="306" y="122" font-family="Montserrat,sans-serif" font-size="14" font-weight="800" fill="#0A2A40">%s</text></g>' % (L["h_dest"], L["h_dest2"]))
    o.append('<ellipse class="pin-shadow" cx="520" cy="171" rx="22" ry="5" fill="#000" fill-opacity=".45"/>')
    o.append('<g class="pin-land"><g transform="translate(490 82) scale(.6)"><path d="%s" fill="#F7F3EA"/><circle cx="50" cy="50" r="24" fill="#F2B705"/><circle cx="50" cy="50" r="8" fill="#0A2A40"/></g></g>' % PIN)
    o.append('<text x="24" y="36" font-family="Montserrat,sans-serif" font-size="13" font-weight="700" letter-spacing="1.2" fill="#FFFFFF">%s</text>' % L["h_route"])
    o.append('<text x="24" y="56" font-family="Inter,sans-serif" font-size="12" fill="#B9CCDA">%s</text>' % L["h_route2"])
    o.append('<g><circle cx="612" cy="32" r="4" fill="#3ED17E"/><text x="602" y="36" text-anchor="end" font-family="Inter,sans-serif" font-size="11.5" font-weight="600" letter-spacing="1" fill="#B9CCDA">%s</text></g>' % L["h_live"])
    o.append('<g opacity=".7"><path d="M560 420h56M560 415v5M616 415v5" stroke="#B9CCDA" stroke-width="1.5"/><text x="588" y="410" text-anchor="middle" font-family="Inter,sans-serif" font-size="10.5" fill="#B9CCDA">%s</text>' % L["km"] + '</g>')
    o.append('</svg>')
    return "".join(o)

def sched(L):
    out = []
    for i, d in enumerate(L["days"]):
        slots = L["slots"].get(i, [])
        inner = "".join('<span class="slot%s">%s<small>%s</small></span>' % (" y" if y else "", t, s) for t, s, y in slots) or '<span style="color:var(--muted-2);font-size:13px">—</span>'
        out.append('<div class="day"><b>%s</b>%s</div>' % (d, inner))
    return "".join(out)

def build(L, fname):
    pat = open(A + "pattern.svg").read().replace('#D9A000', '#F2B705')
    v = dict(L); v.update(ICONS)
    v["pattern_uri"] = urllib.parse.quote(pat, safe='')
    v["logo_horizontal"] = inline("logo-horizontal.svg", "84 16 460 140", "", "Primeegg Distribution")
    v["logo_inverse"] = inline("logo-inverse.svg", "40 88 322 112", "", "Primeegg Distribution")
    v["svg_retail"] = inline("scene-pack_retail.svg", "40 110 1600 500", "_r", L["alt_retail"])
    v["svg_powder"] = inline("scene-pack_powder.svg", "250 40 1240 620", "_p", L["alt_powder"])
    v["svg_tray"] = inline("scene-pack_horeca.svg", "190 40 590 600", "_h", L["alt_tray"])
    v["svg_truck"] = inline("scene-logistics.svg", "70 110 1080 540", "_t", L["alt_truck"])
    v["map_svg"] = map_svg(L); v["hero_svg"] = hero_svg(L); v["sched"] = sched(L)
    key = lambda x: x.replace("Á", "A").replace("Ó", "O").replace("S. C.", "Santa C")
    v["prov_opts"] = "".join('<option>%s</option>' % n for n in sorted([p[1] for p in P], key=key))
    v["vol_opts"] = "".join('<option>%s</option>' % o for o in L["vol"])
    v["start_opts"] = "".join('<option>%s</option>' % o for o in L["start"])
    v["faq"] = "".join('<details><summary>%s</summary><p>%s</p></details>' % qa for qa in L["faqs"])
    v["js_i18n"] = json.dumps(L["js"], ensure_ascii=False)
    v["js_prov"] = json.dumps({p[0]: {"n": p[1], "z": p[4]} for p in P}, ensure_ascii=False)
    n24 = sum(1 for p in P if p[4] == "z24") - 1
    def rep(m):
        return str(v[m.group(1)]).replace("{n24}", str(n24))
    s = re.sub(r'\{\{([a-zA-Z0-9_]+)\}\}', rep, TPL)
    open(os.path.join(SITE, fname), "w").write(s)
    print(fname, len(s), "n24(+Madrid)", n24)

build(ES, "index.html")
build(UK, "uk.html")
