# -*- coding: utf-8 -*-
"""v4: the client's new design (their HTML + site.css) carrying the v2.1 information architecture and the stakeholder briefings.
Every text replacement is checked (must) so a design change upstream fails loudly instead of silently."""
import os, re, json, shutil, html, datetime, sys
from shapely.geometry import shape, Point

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DESIGN = os.environ.get("DESIGN", "/tmp/claude-0/newdesign")     # downloaded design (index.html + assets/)
V2 = os.path.join(ROOT, "data")
V3 = os.path.join(ROOT, "data")
SURVEY = json.load(open(os.path.join(ROOT, "data", "survey_full.json"))); HEALTH = json.load(open(os.path.join(ROOT, "data", "data_health.json")))
X = json.load(open(os.path.join(ROOT, "data", "extras.json")))
sys.path.insert(0, HERE); from icons import ROLE_ICONS, WEBMAP_ICONS, USP_ICONS, CHEVRON, EXT
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "nesp-website-source")); from content import POSTS
OUT = os.environ.get("OUT", os.path.join(ROOT, "site"))
ORIG = "https://nigeriase4all.gov.ng"; APPS = "https://apps.nigeriase4all.gov.ng/"; PORTAL = "https://data.nigeriase4all.gov.ng/"
OSIP = "https://deepaccrete.github.io/NESP-OSIP-HTML/homepage.html"
EMAIL = "contact.nigeriase4all@gmail.com"
WFS_CAP = PORTAL + "geoserver/ows?service=WFS&version=2.0.0&request=GetCapabilities"

# ---------------------------------------------------------------- data
v2 = json.load(open(os.path.join(V2, "states.json"))); S2 = v2["states"]
NAT2 = json.load(open(os.path.join(V2, "national.json"))); FIND = json.load(open(os.path.join(V2, "finder.json")))
I3 = json.load(open(os.path.join(V3, "insights.json"))); N3 = I3["national"]; S3 = I3["states"]
geo = json.load(open(os.path.join(V2, "states.geojson")))
for f in geo["features"]: f["properties"] = {"state": f["properties"]["state"]}
shapes = [(f["properties"]["state"], shape(f["geometry"])) for f in geo["features"]]
def state_of(lat, lon):
    if lat is None: return None
    p = Point(lon, lat)
    for s, g in shapes:
        if g.contains(p): return s
    return min(shapes, key=lambda x: x[1].distance(p))[0]   # coastal points just outside the simplified boundary
fleet = I3["fleet"]
for g in fleet: g["state"] = state_of(g["lat"], g["lon"])
PULLED = datetime.date.fromisoformat(v2["pulled"]).strftime("%-d %B %Y")
states = {}
for s, a in S2.items():
    b = S3[s]
    states[s] = dict(state=s, buildings=a["buildings"], buildings_over_5km=a["buildings_over_5km"], clusters=a["clusters"], clusters_over_5km=a["clusters_over_5km"],
                     offgrid_buildings=a["offgrid_buildings"], offgrid_clusters=a["offgrid_clusters"], mv_km=a["mv_km"], hv_km=a["hv_km"], substations=a["substations"],
                     markets=a["markets"], surveyed=a["surveyed"], disco=a["disco"], bands=a["bands"],
                     minigrids=sum(1 for g in fleet if g["state"] == s), minigrid_kw=sum((g["kw"] or 0) for g in fleet if g["state"] == s),
                     **{k: b[k] for k in ("rank_offgrid", "rank_over_5km", "under_grid_buildings", "surveyed_no_grid", "no_grid_with_health", "no_grid_health_facilities",
                                          "no_grid_with_school", "no_grid_schools", "never_functional", "present_not_connected", "ready_sites")})
for c in I3["communities"]:
    c.update(X["communities"].get(c["uid"], {}))
    c["slug"] = (re.sub(r"[^a-z0-9]+", "-", (c["name"] or "community").lower()).strip("-")[:40] + "-" + c["uid"]).lower()
for s, d in states.items():
    x = X["states"][s]; d["substations"] = len(x["substations"]); d["planned_substations"] = len(x["planned_substations"]); d["plants"] = len(x["plants"])
XN = X["national"]
lite = {s: {k: v for k, v in d.items() if k != "bands"} for s, d in states.items()}
dev, inv, sv, hl = N3["developer"], N3["investor"], N3["survey"], N3["health"]
fuel22, fuel26 = dev["fuel"]["2022"], dev["fuel"]["2026"]
off_total = sum(d["offgrid_buildings"] for d in states.values())

# ---------------------------------------------------------------- output skeleton
if os.path.exists(OUT): shutil.rmtree(OUT)
shutil.copytree(os.path.join(DESIGN, "assets"), os.path.join(OUT, "assets"), ignore=shutil.ignore_patterns("[[]photo[]].jpg"))
os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True); os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
shutil.copy(os.path.join(HERE, "assets", "css", "v6.css"), os.path.join(OUT, "assets", "css", "v6.css"))
shutil.copy(os.path.join(HERE, "assets", "js", "v6.js"), os.path.join(OUT, "assets", "js", "v6.js"))
open(os.path.join(OUT, "data", "atlas-data.js"), "w").write("window.ATLAS=" + json.dumps(dict(states=lite, finder=FIND, geo=geo, communities=I3["communities"], fleet=fleet, national=N3), separators=(",", ":")) + ";")

SRC = open(os.path.join(DESIGN, "index.html"), encoding="utf-8").read()
def must(s, old, new, count=1, regex=False):
    n = len(re.findall(old, s, flags=re.S)) if regex else s.count(old)
    if n < 1 or (count and n != count): raise SystemExit(f"replacement failed ({n} matches): {old[:90]!r}")
    return re.sub(old, new, s, flags=re.S) if regex else s.replace(old, new)
e = lambda x: html.escape(str(x), quote=True)
f0 = lambda n: "—" if n is None else f"{n:,.0f}"
pc = lambda x: f"{round(100 * x)}%"
slug = lambda s: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))
POST_URL = lambda p: ORIG + "/blog-post/" + p["date"].replace("-", "/") + "/" + p["slug"]
post = lambda sl: [p for p in POSTS if p["slug"] == sl][0]
SVG_ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
STATE_OPTS = "".join(f'<option value="{e(s)}">{e(s)}</option>' for s in sorted(states))

# ---------------------------------------------------------------- shared chrome (header + footer), from the design
head_end = SRC.index("</head>"); body_start = SRC.index("<body"); body_open_end = SRC.index(">", body_start) + 1
HEAD = SRC[:head_end]
HEAD = must(HEAD, "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap")
HEAD = must(HEAD, '<link rel="stylesheet" href="assets/css/site.css">',
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">\n<link rel="stylesheet" href="assets/css/site.css">\n<link rel="stylesheet" href="assets/css/v6.css">')
hdr_s = SRC.index('<header class="hdr"'); mnav_e = SRC.index("</div>", SRC.index('<div class="mnav"')); mnav_e = SRC.index("</div>", SRC.index('class="btn btn-primary" href="#tools" style="margin-top:12px', mnav_e)) + 6
CHROME_TOP = SRC[hdr_s:mnav_e]
ft_s = SRC.index("<footer"); ft_e = SRC.index("</footer>") + len("</footer>")
FOOTER = SRC[ft_s:ft_e]

ROLES = [("developer", "for/developers/index.html", "Mini-grid developers", "Build-ready communities and site criteria"),
         ("investor", "for/investors/index.html", "Investors and financiers", "Market by state, recorded fleet, grid backbone"),
         ("state", "states/index.html", "State governments", "Profiles for the 36 states and the FCT"),
         ("researcher", "for/researchers/index.html", "Researchers and data users", "Catalogue, downloads, WMS/WFS and data notes"),
         ("learner", "for/learners/index.html", "Students and GIS careers", "Free courses, mapathons and a learning path")]
WEBMAPS = [("offgrid", APPS + "minigrid-offgrid?buildings_max=2000&buildings_min=100&grid_dist_max=40&grid_dist_min=5", "Off-grid mini-grids", "Unelectrified settlements far from the grid"),
           ("interconnected", APPS + "minigrid-interconnected?buildings_max=2000&buildings_min=100&grid_dist_max=5&grid_dist_min=0", "Interconnected mini-grids", "Grid-connected communities with weak supply"),
           ("power", APPS + "power-sector?grid_buffer=3", "Power sector", "DisCo areas, substations, MV and HV grid"),
           ("shs", APPS + "shs?market_dist=10&grid_dist_max=40&grid_dist_min=0", "Solar home systems", "Markets and the customer base around them")]
ROLE_MENU = "".join(f'<a role="menuitem" href="{{R}}{u}"><span class="dd-ic a-ic-{k}">{ROLE_ICONS[k]}</span><span><b>{t}</b><small>{d}</small></span></a>' for k, u, t, d in ROLES)
MAP_MENU = "".join(f'<a role="menuitem" href="{u}" target="_blank" rel="noopener"><span class="dd-ic a-ic-{k}">{WEBMAP_ICONS[k]}</span><span><b>{t} {EXT}</b><small>{d}</small></span></a>' for k, u, t, d in WEBMAPS)
ics = []
CHROME_TOP = must(CHROME_TOP, r'(<div class="dd-menu" id="dd-menu" role="menu">).*?(<a class="dd-foot")', lambda m: m.group(1) + ROLE_MENU + m.group(2), regex=True)
CHROME_TOP = must(CHROME_TOP, r'<a class="dd-foot" href="#tools">Open the full map', '<a class="dd-foot" href="{R}index.html#briefings">See every briefing', regex=True)
CHROME_TOP = must(CHROME_TOP, r'(aria-controls="dd-menu">)Explore(\s*<svg)', r'\1Who are you?\2', regex=True)
CHROME_TOP = must(CHROME_TOP, '<a href="#data">Data</a><a href="blog.html">Blog</a><a href="about.html">About</a>',
                  f'<a href="{{R}}communities/index.html">Field survey</a><a href="{{R}}index.html#data">Data</a><a href="{ORIG}/blog">Blog</a><a href="{ORIG}/about">About</a>', count=2)
CHROME_TOP = must(CHROME_TOP, r'<a href="mini-grids.html">Mini-grids</a><a href="power-sector.html">Power sector</a><a href="solar-home-systems.html">Solar home systems</a>',
                  "".join(f'<a href="{{R}}{u}">{t}</a>' for k, u, t, d in ROLES))
CHROME_TOP = must(CHROME_TOP, r'<div class="mnav-h">Explore</div>', '<div class="mnav-h">Who are you?</div>', regex=True)
CHROME_TOP = must(CHROME_TOP, r'<button class="icon-btn" aria-label="Search">.*?</button>\s*', "", regex=True)
CHROME_TOP = must(CHROME_TOP, r'<a class="btn btn-primary" href="#tools">Open the map</a>',
    f'<div class="dd a-dd2" id="dd2"><button class="btn btn-primary a-dd2-btn" aria-haspopup="true" aria-expanded="false" aria-controls="dd2-menu">Explore webmaps {CHEVRON}</button>'
    f'<div class="dd-menu" id="dd2-menu" role="menu">{MAP_MENU}<a class="dd-foot" href="{{R}}index.html#tools">About the webmaps</a></div></div>', regex=True)
CHROME_TOP = must(CHROME_TOP, r'<a class="btn btn-primary" href="#tools" style="margin-top:12px;justify-content:center">Open the map</a>',
    '<div class="mnav-group"><div class="mnav-h">Explore webmaps</div>' + "".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for k, u, t, d in WEBMAPS) + '</div>', regex=True)
CHROME_TOP = must(CHROME_TOP, '<a class="brand" href="#"', '<a class="brand" href="{R}index.html"')
CHROME_TOP = CHROME_TOP.replace('src="assets/', 'src="{R}assets/')

FOOTER = must(FOOTER, "[contact@rea.gov.ng]", f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
FOOTER = must(FOOTER, r'<div class="socials">.*?</div>\s*', "", regex=True)
FOOTER = must(FOOTER, r'<a href="#" style="color:var\(--green\);font-weight:600">rea.gov.ng</a>', '<a href="https://rea.gov.ng/" style="color:var(--green);font-weight:600">rea.gov.ng</a>', regex=True)
FOOTER = must(FOOTER, r'<a href="#" style="color:var\(--green\);font-weight:600">power.gov.ng</a>', '<a href="https://www.power.gov.ng/" style="color:var(--green);font-weight:600">power.gov.ng</a>', regex=True)
FOOTER = must(FOOTER, r'<div class="fcol">\s*<h4>Platform</h4>.*?</div>\s*<div class="fcol">\s*<h4>Explore</h4>.*?</div>\s*<div class="fcol">\s*<h4>Resources</h4>.*?</div>\s*<div class="fcol">\s*<h4>About</h4>.*?</div>',
    f'<div class="fcol"><h4>Briefings</h4><a href="{{R}}for/developers/index.html">Mini-grid developers</a><a href="{{R}}for/investors/index.html">Investors</a><a href="{{R}}states/index.html">State governments</a></div>'
    f'<div class="fcol"><h4>Platform</h4><a href="{{R}}communities/index.html">Field survey explorer</a><a href="{{R}}data-health/index.html">Data health</a><a href="{{R}}index.html#explore">Map by state</a><a href="{{R}}index.html#finder">Site-finder</a><a href="{{R}}index.html#tools">Webmaps</a><a href="{{R}}index.html#data">Data downloads</a></div>'
    f'<div class="fcol"><h4>Resources</h4><a href="https://learning.nigeriase4all.gov.ng/" target="_blank" rel="noopener">Learning platform</a><a href="{ORIG}/blog">Blog</a><a href="{PORTAL}documents/29/download">How to download data</a><a href="{PORTAL}documents/28/download">How to use WMS/WFS</a></div>'
    f'<div class="fcol"><h4>About</h4><a href="{ORIG}/about">About the platform</a><a href="mailto:{EMAIL}?subject=Data%20request">Request or share data</a><a href="https://rea.gov.ng/">Rural Electrification Agency</a><a href="https://www.power.gov.ng/">Federal Ministry of Power</a><a href="{ORIG}/accreditation">Accreditation</a><a href="mailto:{EMAIL}">Contact</a></div>', regex=True)
FOOTER = must(FOOTER, r'<span><a href="accreditation.html">Accreditation</a>.*?</span>\s*</div>',
              f'<span><a href="{ORIG}/accreditation">Accreditation</a><a href="{ORIG}/terms-of-service">Terms of service</a><a href="{ORIG}/privacy-policy">Privacy</a></span></div>', regex=True)
FOOTER = FOOTER.replace('src="assets/', 'src="{R}assets/')

LEAF_JS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>'
def page(path, title, desc, body, kind, pdata=None):
    R = "../" * path.count("/")
    head = HEAD.replace('href="assets/', f'href="{R}assets/')
    head = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{e(desc)}">', head)
    pd = dict(root=R, kind=kind); pd.update(pdata or {})
    doc = (head + "</head>\n<body>\n" + CHROME_TOP.replace("{R}", R) + "\n<main id=\"main\">" + body + "</main>\n" + FOOTER.replace("{R}", R) +
           f'\n<script>window.PAGE={json.dumps(pd)};</script><script src="{R}data/atlas-data.js"></script>{LEAF_JS}<script src="{R}assets/js/v6.js"></script>\n</body></html>')
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True); open(full, "w", encoding="utf-8").write(doc)

def phero(crumbs, eyebrow, h1, lead, extra=""):
    return f'''<section class="phero"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1>
<p class="lead">{lead}</p>{extra}<p class="a-stamp">Calculated from the platform's public data on {PULLED}. <a href="#notes">How these figures are made</a></p></div></section>'''

def card(k, big, small, text, src, cls="", act=""):
    return f'<div class="a-card {cls}"><div class="a-k">{k}</div><div class="a-big">{big}{f"<small>{small}</small>" if small else ""}</div><p>{text}</p>{act}<div class="a-src">Source: {src}</div></div>'

def steps(items):
    return '<div class="a-steps">' + "".join(f'<a class="a-stepl" href="{u}"{" target=_blank rel=noopener" if u.startswith("http") else ""}><b>{t}</b><span>{d}</span></a>' for t, d, u in items) + "</div>"

def legend():
    return ('<h4>Buildings more than 5 km from mapped MV grid</h4><div class="a-ramp">' + "".join(f'<i style="background:{c}"></i>' for c in ["#F6EBD6", "#EBCB91", "#D9A445", "#B9770E", "#7A4E07"]) +
            '</div><div class="a-ramp-l"><span>0%</span><span>10</span><span>20</span><span>30</span><span>40%+</span></div><div class="a-key"><i></i> MV grid (live from GeoServer)</div>')

# ================================================================ HOME: the design page, re-organised
def home():
    s = SRC[body_open_end:SRC.index("</body>")]
    s = s.replace(s[s.index('<header class="hdr"'):s.index('<header class="hdr"') + len(SRC[hdr_s:mnav_e])], CHROME_TOP.replace("{R}", ""))
    s = s.replace(SRC[ft_s:ft_e], FOOTER.replace("{R}", ""))
    # hero CTAs
    s = must(s, '<a class="btn btn-leaf" href="#tools">Explore the map', '<a class="btn btn-leaf" href="#survey">Inside the field survey')
    s = must(s, '''const words = "Planning Nigeria's electrification from the ground up.".split(' ');''', '''const words = "Ground truth for Nigeria's electrification, open to everyone.".split(' ');''')
    s = must(s, 'const hlWords = new Set([1, 2]);', 'const hlWords = new Set([0, 1]);')
    # the design's own menu: a click right after hover-open used to close it again
    s = must(s, "ddBtn.addEventListener('click', e => { e.stopPropagation(); setDD(!dd.classList.contains('open')); });",
             "let ddHover = 0; ddBtn.addEventListener('click', e => { e.stopPropagation(); setDD(Date.now() - ddHover < 500 ? true : !dd.classList.contains('open')); });")
    s = must(s, "dd.addEventListener('mouseenter', () => setDD(true));", "dd.addEventListener('mouseenter', () => { ddHover = Date.now(); setDD(true); });")
    s = must(s, r'<div class="eyebrow">Rural Electrification Agency · Nigeria</div>', '<div class="eyebrow">Field-verified electrification data · Nigeria</div>', regex=True)
    s = must(s, r'<p class="lead">Nigeria Electrification Atlas is the Rural Electrification Agency.*?</p>',
             f'<p class="lead">{sv["total"]} communities surveyed on the ground, {f0(NAT2["mv_km"])} km of field-mapped grid, and every one of Nigeria\'s {f0(NAT2["clusters"])} settlements measured against it. Choose who you are and get answers, not just layers.</p>', regex=True)
    s = must(s, '<a class="btn btn-ghost" href="about.html">About the platform</a>', '<a class="btn btn-ghost" href="#briefings">Who are you?</a>')
    s = must(s, r'<div class="l">states with the medium-voltage grid mapped</div>\s*<div class="s">11 kV and 33 kV · NESP field mapping</div>',
             f'<div class="l">states with a field-mapped medium-voltage grid</div><div class="s">{f0(NAT2["mv_km"])} km · 11 and 33 kV</div>', regex=True)
    # KPI strip: authentic figures
    s = must(s, r'<span data-count="700">700</span></div>\s*<div class="l">rural settlements surveyed on site</div>\s*<div class="s">NESP settlement surveys</div>',
             f'<span data-count="{sv["total"]}">{sv["total"]}</span></div><div class="l">communities surveyed on the ground</div><div class="s">About 100 facts each · 2019–2026</div>', regex=True)
    s = must(s, r'<span data-count="3.2" data-dec="1">3.2</span>M<sup>\+</sup></div>\s*<div class="l">off-grid buildings mapped</div>\s*<div class="s">Building footprints</div>',
             f'<span data-count="{NAT2["clusters"]}">{f0(NAT2["clusters"])}</span></div><div class="l">settlements measured against the current grid</div><div class="s">Recalculated nightly</div>', regex=True)
    s = must(s, r'<span data-count="13">13</span></div>\s*<div class="l">open datasets to download</div>\s*<div class="s">Creative Commons licence</div>',
             '<span data-count="28">28</span></div><div class="l">data layers on the open portal</div><div class="s">Download, WMS and WFS</div>', regex=True)
    # ---- new sections after the KPI strip: briefings, explore by state, site-finder
    dopt = "".join(f'<option value="{d}"{" selected" if d == 10 else ""}>{d}</option>' for d in FIND["D"])
    nopt = "".join(f'<option value="{n}"{" selected" if n == 500 else ""}>{n:,}</option>' for n in FIND["N"])
    NEW = f'''
<section class="sec" id="briefings"><div class="wrap">
<div class="sec-head"><div><span class="a-kick">Who are you?</span><h2>What the data says for your role</h2><p class="sub">Each briefing leads with the answers, then the lists and maps behind them. No searching through layers.</p></div></div>
<div class="a-roles a-roles5">
<a class="a-role" href="for/developers/index.html"><span class="a-role-h"><span class="a-ic a-ic-developer">{ROLE_ICONS["developer"]}</span><span class="who">Mini-grid developers</span></span><span class="a-big">{dev["ready"]}</span><h3>build-ready communities</h3>
<p>Surveyed, no grid, {N3["criteria"]["min_buildings"]}+ buildings, businesses already paying for generators, year-round access, and mobile money or 3G/4G.</p><span class="a-go">Open the developer briefing</span></a>
<a class="a-role" href="for/investors/index.html"><span class="a-role-h"><span class="a-ic a-ic-investor">{ROLE_ICONS["investor"]}</span><span class="who">Investors and financiers</span></span><span class="a-big">{pc(inv["top5_share"])}</span><h3>of off-grid buildings are in five states</h3>
<p>{", ".join(inv["top5"][:-1])} and {inv["top5"][-1]}. Four of the ten largest off-grid markets have no mini-grid recorded on the platform.</p><span class="a-go">Open the investor briefing</span></a>
<div class="a-role"><span class="a-role-h"><span class="a-ic a-ic-state">{ROLE_ICONS["state"]}</span><span class="who">State governments</span></span><span class="a-big">37</span><h3>state profiles</h3>
<p>Off-grid demand, clinics without grid power, grid that never worked, substations and build-ready sites for each state.</p>
<label for="home-state" style="font-weight:600;font-size:15px">Open the profile for</label><select id="home-state" data-state-go><option value="">Choose a state…</option>{STATE_OPTS}</select>
<a class="a-go" href="states/index.html">Compare all states</a></div>
<a class="a-role a-role-wide" href="for/researchers/index.html"><span class="a-role-h"><span class="a-ic a-ic-researcher">{ROLE_ICONS["researcher"]}</span><span class="who">Researchers and data users</span></span><span class="a-big">28</span><h3>open data layers</h3>
<p>Download as shapefile, GeoJSON or CSV, or query them live through WMS and WFS. A full catalogue with feature counts, direct links and data-quality notes.</p><span class="a-go">Open the data briefing</span></a>
<a class="a-role a-role-wide a-role-learn" href="for/learners/index.html"><span class="a-role-h"><span class="a-ic a-ic-learner">{ROLE_ICONS["learner"]}</span><span class="who">Students and GIS careers</span></span><span class="a-big">4</span><h3>free courses, and a community to join</h3>
<p>Want a career in GIS? Start with free courses from an introduction to QGIS, then join the mapathons where 280+ participants have mapped 75,000+ buildings.</p><span class="a-go">Start your learning path</span></a>
</div>
<p class="a-next">Next briefings in preparation: REA and Federal Ministry of Power · DisCos · Health and education programmes.</p>
</div></section>

<section class="sec field" id="explore"><div class="wrap"><div class="a-explore">
<div class="a-copy"><span class="a-kick">Explore by state</span><h2>Where Nigeria's settlements are, and how far they are from the grid</h2>
<div class="a-figs"><div><b>454,267</b><span>settlement clusters mapped</span></div><div><b>{NAT2["buildings"]/1e6:.1f}M</b><span>buildings in those settlements</span></div>
<div><b>{f0(NAT2["mv_km"])} km</b><span>of medium-voltage grid mapped</span></div><div><b>{f0(N3["investor"]["fleet_n"])}</b><span>mini-grids recorded</span></div></div>
<form class="a-pick" data-state-go><label for="pick">Open a state profile</label><div class="row"><select id="pick"><option value="">Choose a state…</option>{STATE_OPTS}</select><button class="btn btn-primary" type="submit">Go</button></div></form>
<p class="sm">Hover a state for its figures; click for the full profile. Calculated from <a class="a-go" href="{PORTAL}">the data portal</a> on {PULLED}.</p></div>
<div class="a-mapbox"><div class="a-map" id="a-nat-map" aria-label="Map of Nigeria by state"></div><div class="a-mapui a-hover" aria-live="polite"></div><div class="a-mapui a-legend">{legend()}</div></div>
</div></div></section>

<section class="sec" id="finder" style="padding-top:0;background:var(--field)"><div class="wrap"><div class="a-finder">
<div><span class="a-kick">Site-finder</span><h2>Find candidate settlements for off-grid electrification</h2>
<form class="a-sentence" id="a-finder" onsubmit="return false">In <select name="state" aria-label="State"><option value="">all of Nigeria</option>{STATE_OPTS}</select>,
show settlements at least <select name="dist" aria-label="Minimum distance to grid in km">{dopt}</select> km from the mapped grid with at least <select name="bldg" aria-label="Minimum buildings">{nopt}</select> buildings.</form></div>
<div class="a-result"><b id="f-c">—</b><span>settlement clusters match</span><b id="f-b" style="font-size:26px;margin-top:12px">—</b><span>buildings in those settlements</span>
<div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-leaf" id="f-go" href="{APPS}minigrid-offgrid" target="_blank" rel="noopener">Open in the off-grid webmap</a><span id="f-sp"></span></div>
<p class="fine">The webmap opens with the same distance and size filters. Distances are recalculated against the field-mapped MV grid.</p></div>
</div></div></section>
'''
    i = s.index('<section class="sec what" id="about">'); s = s[:i] + usp_sections() + NEW + s[i:]
    # ---- "About" (ownership claims) -> How the data is made (v2.1)
    a0 = s.index('<section class="sec what" id="about">'); a1 = s.index("</section>", a0) + len("</section>")
    METHOD = f'''<section class="sec" id="about"><div class="wrap">
<div class="sec-head"><div><span class="a-kick">How the data is made</span><h2>From satellite to field survey</h2><p class="sub">Remote mapping, field visits and vehicle-mounted mapping, published as open layers.</p></div><a class="link" href="{ORIG}/about">About the platform {SVG_ARROW}</a></div>
<div class="a-method">
<div class="a-step"><div class="a-ph"><img src="assets/img/blog-mapathon.jpg" alt="Volunteers mapping buildings at a mapathon" loading="lazy"></div><div class="a-bd"><b class="a-num">75,000+</b><h3>Remote mapping</h3><p>Buildings mapped in off-grid areas of Kogi, Yobe and Imo through mapathons on OpenStreetMap.</p><a class="a-go" href="{POST_URL(post("nigeria-se4-all-mapathon"))}">Mapathons</a></div></div>
<div class="a-step"><div class="a-ph"><img src="assets/img/blog-offgrid-survey.jpg" alt="Map of surveyed off-grid settlements" loading="lazy" style="object-fit:contain;background:#fff"></div><div class="a-bd"><b class="a-num">{sv["total"]}</b><h3>Field survey</h3><p>Communities visited and published with grid status, generators, fuel prices, businesses and services. New surveys are still being added.</p><a class="a-go" href="{POST_URL(post("the-nigeria-se-4-all-off-grid-settlements-survey"))}">Survey method</a></div></div>
<div class="a-step"><div class="a-ph"><img src="assets/img/blog-mobile-mapping.jpg" alt="Mobile mapping device on a vehicle" loading="lazy"></div><div class="a-bd"><b class="a-num">~4,000</b><h3>Mobile mapping</h3><p>Poles tracked along about 250 km of road in Nasarawa in May 2022, with earlier missions in the FCT and Sokoto.</p><a class="a-go" href="{POST_URL(post("innovative-geospatial-data-collection-on-electrical-infrastructure-with-mobile-mapping-technology"))}">Mobile mapping</a></div></div>
<div class="a-step"><div class="a-ph"><img src="assets/Medium_Voltage_grid_datasets_cadd5e1403.png" alt="MV grid on the webmap" loading="lazy"></div><div class="a-bd"><b class="a-num">28</b><h3>Open publication</h3><p>Layers published on the data portal, shown in the webmaps and queryable through WMS and WFS.</p><a class="a-go" href="{PORTAL}">Data portal</a></div></div>
</div></div></section>'''
    s = s[:a0] + s[a1:]          # the USP section now carries "how the data is made"
    o0 = s.index('<section class="osip"'); o1 = s.index("</section>", o0) + len("</section>")
    s = s[:o0] + s[o1:]          # OSIP removed from the homepage (kept in the briefings' next steps)
    # ---- webmaps: drop unverified "Last updated" dates
    s = must(s, r'<span\s+class="meta">\s*Last\s+updated\s+[A-Za-z]{3}\s+\d{4}\s*</span>', "", count=4, regex=True)
    # ---- data section: verified facts only
    s = must(s, "Everything on the webmaps is published on our geodata portal", "Everything on the webmaps is published on the geodata portal")
    s = must(s, r'<p class="sub" style="margin-bottom:28px">Each dataset carries.*?</p>',
             f'<p class="sub" style="margin-bottom:28px">Download each layer as a shapefile, GeoJSON, CSV or Excel file, or stream it into QGIS and your own tools through WMS and WFS. Guides: <a class="a-go" href="{PORTAL}documents/29/download">how to download geodata</a> · <a class="a-go" href="{PORTAL}documents/28/download">how to use WMS/WFS</a>.</p>', regex=True)
    s = must(s, r'<div><b>CC BY 4.0</b><span>Open licence</span></div>\s*<div><b>SHP · GeoJSON · KML</b><span>Download formats</span></div>',
             '<div><b>28 layers</b><span>On the open portal</span></div><div><b>SHP · GeoJSON · CSV</b><span>Download formats</span></div>', regex=True)
    s = must(s, r'<div class="by-sector"><span>Or browse data by sector</span>.*?</div>',
             '<div class="by-sector"><span>Or start from a briefing</span><a href="for/developers/index.html"><i></i>Developers</a><a class="ps" href="for/investors/index.html"><i></i>Investors</a><a class="shs" href="states/index.html"><i></i>State governments</a></div>', regex=True)
    s = must(s, '<a href="about.html#data-requests">Request or contribute data</a>', f'<a href="mailto:{EMAIL}?subject=Data%20request">Request or contribute data</a>')
    s = must(s, "<span>3.2M+ off-grid buildings</span>", f"<span>{off_total/1e6:.1f}M+ buildings in off-grid settlements</span>")
    # ---- blog: real links; replace the report card (its PDF no longer exists on the portal)
    s = must(s, '<a class="post" href="blog.html"', "<a class=\"post\" href=\"@@POST@@\"", count=3)
    for p in ["the-nigeria-se-4-all-off-grid-settlements-survey", "innovative-geospatial-data-collection-on-electrical-infrastructure-with-mobile-mapping-technology", "power-sector-analytics-explorer"]:
        s = s.replace("@@POST@@", POST_URL(post(p)), 1)
    s = must(s, r'<a class="post report" href="#">.*?</a>',
             lambda m: f'<a class="post" href="{POST_URL(post("off-grid-mini-grids-explorer"))}"><div class="img"><img src="assets/minigrid_with_nav_2da30ad4df.webp" alt="Off-grid mini-grid explorer webmap" loading="lazy"></div><div class="b"><span class="chip"><i></i>Mini-grids</span><h3>Exploring mini-grid potential and selecting sites for off-grid mini-grids</h3><span class="by">Emmanuel Jolaiya · 16 Aug 2022</span></div></a>', regex=True)
    s = must(s, '<a class="link" href="blog.html">View the blog', f'<a class="link" href="{ORIG}/blog">View the blog')
    # ---- learning: verified course list instead of unverified lesson counts/certificate
    s = must(s, r"The Nigeria Electrification Atlas Learning Platform is a free online learning system.*?when you finish\.",
             "The Learning Platform offers free, expert-led video courses that turn the data platform into skills, from an introduction to the project to QGIS and data-driven project planning.", regex=True)
    s = must(s, r'<h3>What\'s inside</h3>\s*<ul>.*?</ul>',
             '<h3>Courses on the platform</h3><ul>' + "".join(f'<li><span class="hic">{SVG_ARROW}</span><div><b>{t}</b><small>{d}</small></div></li>' for t, d in [
                 ("Nigeria SE4ALL introduction course", "The project and its activities. Self-paced."), ("QGIS training", "Fundamental components and capabilities of QGIS. Self-paced."),
                 ("Project development", "Data-driven project planning for the private sector. Self-paced."), ("Mapathon introduction", "The basics of OpenStreetMap for gathering ground-truth data.")]) + "</ul>", regex=True)
    s = must(s, r"<h3>Start learning — it's free</h3>\s*<p>.*?</p>", "<h3>Start learning — it's free</h3><p>Register on the Learning Platform and work through the courses at your own pace.</p>", regex=True)
    s = must(s, r'<span><svg[^>]*>.*?</svg>\s*Certificate on completion</span>', "<span>4 courses</span>", regex=True)
    s = must(s, r'<span class="cta-note">19 lessons · ~2 hours total</span>', '<span class="cta-note">4 courses · free registration</span>', regex=True)
    # ---- testimonials: real contact
    s = must(s, "mailto:[contact@rea.gov.ng]?subject=My%20platform%20story", f"mailto:{EMAIL}?subject=My%20platform%20story")
    # ---- partners: only organisations named on the platform
    s = must(s, r'<div class="plogo">Federal Ministry of Education</div>.*?<div class="plogo">AfDB</div>',
             '<div class="plogo">Nigerian Electricity Regulatory Commission (NERC)</div><div class="plogo">Transmission Company of Nigeria (TCN)</div><div class="plogo">INTEGRATION environment &amp; energy</div><div class="plogo">Reiner Lemoine Institut</div>', regex=True)
    s = must(s, "The platform is delivered with federal ministries, regulators and development partners.", "Delivered with the Federal Ministry of Power, the Rural Electrification Agency, sector institutions and development partners.")
    s = must(s, 'href="#tools">Open the map</a></div>', 'href="#tools">Explore webmaps</a></div>')
    # head
    head = re.sub(r"<title>.*?</title>", "<title>Nigeria Electrification Atlas: evidence for every stakeholder</title>", HEAD, flags=re.S)
    leaf = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>'
    s = s.replace("</body>", "")
    doc = head + "</head>\n" + SRC[body_start:body_open_end] + s + f'\n<script>window.PAGE={json.dumps(dict(root="", kind="home"))};</script><script src="data/atlas-data.js"></script>{leaf}<script src="assets/js/v6.js"></script>\n</body></html>'
    for bad in ["[contact@", "CC BY", "19 lessons", "Last updated", "blog.html", "about.html", "mini-grids.html", "Federal Ministry of Education", "ground up", "os-card", "osip-wind"]:
        if bad in re.sub(r"<script.*?</script>", "", doc, flags=re.S): raise SystemExit(f"unverified/placeholder text left on home: {bad}")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)

# ================================================================ STATES INDEX (state governments)
def states_index():
    p = "states/index.html"
    rows = ""
    for d in sorted(states.values(), key=lambda v: -v["offgrid_buildings"]):
        sh = d["buildings_over_5km"] / d["buildings"]
        rows += (f'<tr><td><a class="a-go" style="font-weight:600" href="{slug(d["state"])}/index.html">{e(d["state"])}</a></td><td class="n" data-v="{d["offgrid_buildings"]}">{f0(d["offgrid_buildings"])}</td>'
                 f'<td class="n" data-v="{sh:.4f}">{pc(sh)}</td><td class="n" data-v="{d["mv_km"]}">{f0(d["mv_km"])}</td><td class="n" data-v="{d["minigrids"]}">{d["minigrids"]}</td>'
                 f'<td class="n" data-v="{d["surveyed"]}">{d["surveyed"]}</td><td class="n" data-v="{d["no_grid_with_health"]}">{d["no_grid_with_health"]}</td><td class="n" data-v="{d["never_functional"]}">{d["never_functional"]}</td>'
                 f'<td class="n" data-v="{d["ready_sites"]}">{d["ready_sites"]}</td><td>{", ".join(x["code"] for x in d["disco"])}</td></tr>')
    pick = f'<form class="a-pickhero" data-state-go><label for="sp">State</label><select id="sp"><option value="">Choose your state…</option>{STATE_OPTS}</select><button class="btn btn-primary" type="submit">Open profile</button></form>'
    body = phero('<a href="../index.html">Home</a> <span>/</span> <span>State governments</span>', "Briefing for state governments", "Your state's electrification picture, from the ground up",
                 'Under the Electricity Act 2023 states can regulate their own electricity markets, and <a href="https://nerc.gov.ng/media/15-states-have-transitioned-to-regulating-their-state-electricity-markets/" style="color:#fff;text-decoration:underline">NERC reports that 15 states have already done so</a>. Each profile sets out the state\'s gap and where to start.', pick) + f'''
<section class="sec"><div class="wrap"><div class="a-explore" style="grid-template-columns:1fr"><div class="a-mapbox"><div class="a-map" id="a-nat-map"></div><div class="a-mapui a-hover"></div><div class="a-mapui a-legend">{legend()}</div></div></div></div></section>
<section class="sec field" style="padding-top:64px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Compare states</span><h2>All 36 states and the FCT</h2><p class="sub">Sorted by off-grid buildings. Click a column to re-sort, or a state for its profile.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>State</th><th class="n">Off-grid buildings</th><th class="n">Share &gt;5 km from grid</th><th class="n">MV grid km</th><th class="n">Mini-grids</th><th class="n">Surveyed</th><th class="n">Clinics without grid</th><th class="n">Grid never worked</th><th class="n">Build-ready</th><th>DisCo</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="sec" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How these figures are made</h2><ul class="a-notes">
<li>Settlement and building figures: SE4ALL settlement and off-grid layers, summed by state. Distances are recalculated for every settlement against the field-mapped MV grid (<code>distribution_line_mv</code>).</li>
<li>MV grid: <code>distribution_line_mv</code>, clipped to state boundaries. Clinics, grid condition and build-ready sites: field-survey layer.</li>
<li>Calculated from the public data portal on {PULLED}; planned refresh: nightly.</li></ul></div></section>'''
    page(p, "State profiles | Nigeria Electrification Atlas", "Electrification profiles for Nigeria's 36 states and the FCT.", body, "states")

# ================================================================ STATE PROFILE (v2.1 layout + briefing answers)
def infra_section(name):
    x = X["states"][name]
    kv = " · ".join(f"{n} at {k} kV" for k, n in sorted(((k, sum(1 for s in x["substations"] if s["kv"] == k)) for k in {s["kv"] for s in x["substations"] if s["kv"]}), key=lambda t: -t[0]))
    subs = "".join(f'<tr><td>{e(s["name"])}</td><td class="n">{s["kv"] or "—"} kV</td></tr>' for s in sorted(x["substations"], key=lambda s: (-(s["kv"] or 0), s["name"])))
    plan = "".join(f'<tr><td>{e(s["name"])}</td><td class="n">{s["kv"] or "—"} kV</td></tr>' for s in x["planned_substations"])
    plants = "".join(f'<tr><td>{e(p["name"])}</td><td>{e(p["kind"])}</td><td><span class="a-pill {"ok" if p["status"] == "Existing" else "mid"}">{p["status"]}</span></td></tr>' for p in x["plants"])
    hv = "".join(f'<tr><td>{e(l["name"])}</td><td>{e(l["volt"] or "—")}</td><td class="n" data-v="{l["km"]}">{l["km"]:,.1f}</td></tr>' for l in x["hv_lines"])
    tbl = lambda head, rows, empty: f'<div class="a-tbl"><table class="a-t"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>' if rows else f'<p class="a-muted">{empty}</p>'
    return f'''<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Grid and generation</span><h2>Infrastructure in {e(name)}</h2>
<p class="sub">{len(x["substations"])} installed substation{"s" if len(x["substations"]) != 1 else ""}{(" (" + kv + ")") if kv else ""}, {len(x["planned_substations"])} planned, {len(x["plants"])} power plant{"s" if len(x["plants"]) != 1 else ""} and {len(x["hv_lines"])} HV line section{"s" if len(x["hv_lines"]) != 1 else ""}. Switch them on in the map above.</p></div></div>
<div class="a-split"><div><h3 class="a-h3">Installed substations</h3>{tbl('<th>Substation</th><th class="n">Voltage</th>', subs, "No installed substation recorded in this state.")}
<h3 class="a-h3">Planned substations</h3>{tbl('<th>Substation</th><th class="n">Voltage</th>', plan, "No planned substation recorded in this state.")}</div>
<div><h3 class="a-h3">Power plants</h3>{tbl('<th>Plant</th><th>Type</th><th>Status</th>', plants, "No power plant recorded in this state.")}
<h3 class="a-h3">High-voltage lines</h3>{tbl('<th>Line</th><th>Voltage</th><th class="n">km in state</th>', hv, "No HV line recorded in this state.")}</div></div>
<p class="a-note" style="margin-top:16px">The source substation and power-plant layers list each asset twice; figures here are de-duplicated by name.</p></div></section>'''

NF = ' <span class="a-pill bad">Never functional</span>'
GRID_L = {"no": ("No grid", "mid"), "yes_connected_national_grid": ("Connected to national grid", "ok"), "yes_not_connected_national_grid": ("Grid present, not connected", "")}
def state_page(name):
    d = states[name]; p = f"states/{slug(name)}/index.html"
    comm = [c for c in I3["communities"] if c["state"] == name]
    nog = [c for c in comm if c["grid"] == "no"]
    mg = [g for g in fleet if g["state"] == name]
    sh = d["buildings_over_5km"] / d["buildings"]
    nb = NAT2["bands"]; ntot = sum(b["buildings"] for b in nb)
    blab = lambda b: f"{b['lo']}–{b['hi']} km" if b["hi"] else f"{b['lo']}+ km"
    bars = "".join(f'<div class="row"><span>{blab(b)}</span><span class="track"><span class="fill{" near" if b["lo"] < 5 else ""}" style="width:{100*b["buildings"]/d["buildings"]:.1f}%"></span><span class="nat" style="left:{100*n["buildings"]/ntot:.1f}%"></span></span><span class="v">{100*b["buildings"]/d["buildings"]:.1f}% · {f0(b["buildings"])}</span></div>' for b, n in zip(d["bands"], nb))
    kpi = lambda v, l, src: f'<div class="a-kpi"><b>{v}</b><span>{l}</span><small>{src}</small></div>'
    disco = ", ".join(f'{x["name"]} ({x["code"]})' for x in d["disco"]) or "—"
    # survey table
    if comm:
        tr = ""
        for c in sorted(comm, key=lambda r: (r["lga"] or "", r["name"] or "")):
            gl, gc = GRID_L.get(c["grid"], ((c["grid"] or "—").replace("_", " "), ""))
            tags = ["nogrid" if c["grid"] == "no" else "grid"] + (["clinic"] if c["grid"] == "no" and (c["health"] or 0) > 0 else []) + (["broken"] if c["never_functional"] else [])
            tr += (f'<tr data-f="{" ".join(tags)}"><td><b>{e(c["name"])}</b></td><td>{e(c["lga"] or "—")}</td><td><span class="a-pill {gc}">{gl}</span>{NF if c["never_functional"] else ""}</td>'
                   f'<td class="n" data-v="{c["bld"] or 0}">{f0(c["bld"])}</td><td class="n" data-v="{c["bz_gen"] or 0}">{(str(int(c["bz_gen"])) + "%") if c["bz_gen"] is not None else "—"}</td><td class="n" data-v="{c["health"] or 0}">{f0(c["health"])}</td><td class="n" data-v="{c["schools"] or 0}">{f0(c["schools"])}</td><td class="n" data-v="{c.get('mv_km', '')}">{(str(c['mv_km']) + " km") if c.get('mv_km') is not None else "—"}</td><td class="n" data-v="{c.get('sub_km', '')}">{(str(c['sub_km']) + " km") if c.get('sub_km') is not None else "—"}<br><span class="a-muted" style="font-size:12.5px">{e(c.get('sub_name') or '')}</span></td><td class="n">{c["year"]}</td></tr>')
        clin = sum(1 for c in nog if (c["health"] or 0) > 0); brk = sum(1 for c in comm if c["never_functional"])
        survey = f'''<div class="a-filters" data-for="svt"><button data-f="all" aria-pressed="true">All ({len(comm)})</button><button data-f="nogrid" aria-pressed="false">No grid ({len(nog)})</button><button data-f="clinic" aria-pressed="false">Clinics without grid ({clin})</button><button data-f="broken" aria-pressed="false">Grid never worked ({brk})</button><button data-f="grid" aria-pressed="false">Grid present ({len(comm)-len(nog)})</button></div>
<div class="a-tbl"><table class="a-t" id="svt"><thead><tr><th>Community</th><th>LGA</th><th>Grid at survey</th><th class="n">Buildings</th><th class="n">Businesses on generators</th><th class="n">Health facilities</th><th class="n">Schools</th><th class="n">Nearest MV line</th><th class="n">Nearest substation</th><th class="n">Surveyed</th></tr></thead><tbody>{tr}</tbody></table></div>'''
    else:
        survey = '<p class="a-muted">No communities in this state are in the published field-survey layer yet.</p>'
    if mg:
        mtr = "".join(f'<tr><td><b>{e(g["community"] or "—")}</b><br><span class="a-muted">{e(g["lga"] or "")}</span></td><td class="n">{f0(g["kw"])}</td><td class="n">{f0(g["conn"])}</td><td>{e(g["system"] or "—")}</td><td><span class="a-pill {"mid" if g["status"] == "Under Construction" else ("ok" if g["operational"] else "bad")}">{e(g["status"] or "—")}{(" · " + e(g["condition"])) if g["condition"] and g["status"] != "Under Construction" else ""}</span></td><td>{e(g["programme"] or "—")}</td></tr>' for g in mg)
        mtab = f'<div class="a-tbl"><table class="a-t"><thead><tr><th>Community</th><th class="n">kW</th><th class="n">Connections</th><th>System</th><th>Status</th><th>Programme</th></tr></thead><tbody>{mtr}</tbody></table></div>'
    else:
        mtab = f'<p class="a-muted">No mini-grids for this state are recorded in the platform\'s mini-grid layer. Check the <a class="a-go" href="https://minigridmonitor.nigeriase4all.gov.ng/">mini-grid monitor</a>.</p>'
    rel = [x for x in POSTS if re.search(r"\b" + re.escape(name) + r"\b", x["body"])]
    relh = "".join(f'<a class="a-stepl" href="{POST_URL(x)}"><b>{e(x["title"])}</b><span>{x["date_label"]} · mentions {e(name)}</span></a>' for x in rel)
    pick = f'<form class="a-pickhero" data-state-go><label for="sp">Switch state</label><select id="sp">{STATE_OPTS.replace(f">{e(name)}<", f" selected>{e(name)}<")}</select><button class="btn btn-primary" type="submit">Go</button></form>'
    body = phero(f'<a href="../../index.html">Home</a> <span>/</span> <a href="../index.html">State governments</a> <span>/</span> <span>{e(name)}</span>', "State profile", e(name),
                 f"Distribution company: {e(disco)}. Ranked #{d['rank_offgrid']} of 37 for off-grid demand.", pick) + f'''
<section class="sec" style="padding-bottom:40px"><div class="wrap">
<div class="a-cards">
{card("Off-grid demand", f0(d["offgrid_buildings"]), "buildings", f"in settlements classed as off-grid; #{d['rank_offgrid']} of 37 nationally.", "off-grid settlement layer", "good")}
{card("Far from the grid", f0(d["buildings_over_5km"]), "buildings", f"more than 5 km from the mapped grid: {pc(sh)} of all buildings in {e(name)}.", "settlement layer", "warn", f'<a class="a-go" href="../../index.html#finder">Filter them in the site-finder</a>')}
{card("Clinics without grid power", f0(d["no_grid_with_health"]), "communities", (f"surveyed without grid have a health facility ({f0(d['no_grid_health_facilities'])} facilities); {f0(d['no_grid_with_school'])} have schools." if d["surveyed"] else "No field-survey data yet for this state."), "field-survey layer", "alert")}
{card("Grid that never worked", f0(d["never_functional"]), "communities", ("have grid infrastructure in place that has never been functional: rehabilitation candidates." if d["surveyed"] else "No field-survey data yet for this state."), "field-survey layer", "alert")}
{card("Under-served near the grid", f0(d["under_grid_buildings"]), "buildings", f"within 1 km of the grid: connection or interconnected mini-grid candidates with {e(', '.join(x['code'] for x in d['disco']) or 'the DisCo')}.", "settlement layer")}
{card("Build-ready sites", f0(d["ready_sites"]), "communities", f"meet the developer build-ready criteria. {len(mg)} mini-grid{'s' if len(mg)!=1 else ''} recorded ({f0(d['minigrid_kw'])} kW).", "field-survey and mini-grid layers", "", '<a class="a-go" href="../../for/developers/index.html">See the developer briefing</a>')}
</div></div></section>
<section class="sec field" style="padding-top:56px"><div class="wrap">
<div class="a-kpis">
{kpi(f0(d["clusters"]), "settlement clusters", "cluster_all_simple_new")}{kpi(f0(d["buildings"]), "buildings in settlements", "cluster_all_simple_new")}{kpi(f0(d["offgrid_clusters"]), "SE4ALL off-grid settlements", "cluster_offgrid_simple")}
{kpi(f0(d["mv_km"]), "km of MV grid mapped", "distribution_line_mv")}{kpi(f0(d["hv_km"]), "km of HV lines", "existing_lines_high_voltage")}{kpi(f0(d["substations"]), "substations installed (unique)", "substations_currently_installed")}
{kpi(len(mg), "mini-grids recorded", "minigrids")}{kpi(f0(d["surveyed"]), "communities surveyed", "cluster_offgrid_survey")}{kpi(f0(d["markets"]), "markets (GRID3)", "grid3_market_edited")}{kpi(f0(d["present_not_connected"]), "surveyed: grid present, not connected", "cluster_offgrid_survey")}
</div></div></section>
<section class="sec" id="map" style="padding-top:64px"><div class="wrap"><div class="a-split">
<div><h2 style="margin-bottom:14px">Map</h2><div class="a-smap"><div class="a-map" id="a-state-map"></div>
<div class="a-mapui a-layers"><b style="font-size:13.5px">Layers</b><label><input type="checkbox" data-layer="settle"> Settlement clusters</label><label><input type="checkbox" data-layer="offgrid"> Off-grid settlements</label><label><input type="checkbox" data-layer="mv"> MV grid</label><label><input type="checkbox" data-layer="hv"> HV lines</label><label><input type="checkbox" data-layer="subs"> Substations</label><label><input type="checkbox" data-layer="planned"> Planned substations</label><label><input type="checkbox" data-layer="plants"> Power plants</label><label><input type="checkbox" data-layer="mg"> Mini-grids</label><label><input type="checkbox" data-layer="survey"> Surveyed communities</label></div></div>
<p class="sm a-muted" style="margin-top:8px">Surveyed communities: amber, no grid · red, grid that never worked · blue, grid present. Lines and settlements are drawn live from GeoServer.</p></div>
<div><h2 style="margin-bottom:6px">Distance to the grid</h2><p class="a-muted" style="margin-bottom:18px">Share of {e(name)}'s {f0(d["buildings"])} buildings by distance from the mapped grid. The black tick marks Nigeria as a whole.</p>
<div class="a-bars">{bars}</div>
<div class="a-flag" style="margin-top:20px">{f0(d["clusters_over_5km"])} settlement clusters ({f0(d["buildings_over_5km"])} buildings) are more than 5 km from the field-mapped grid, recalculated against the current MV layer.</div>
<div style="margin-top:20px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-primary" href="{APPS}minigrid-offgrid" target="_blank" rel="noopener">Off-grid webmap</a><a class="btn btn-outline" href="{APPS}power-sector" target="_blank" rel="noopener">Power sector webmap</a></div></div>
</div></div></section>
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Ground truth</span><h2>Surveyed communities</h2><p class="sub">What the field teams found, community by community. Use the filters for clinics without grid or grid that never worked.</p></div></div>{survey}</div></section>
{infra_section(name)}
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Generation</span><h2>Mini-grids</h2><p class="sub">Recorded for {e(name)} in the platform's mini-grid layer.</p></div></div>{mtab}</div></section>
{f'<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">From the field</span><h2>Stories about {e(name)}</h2></div></div><div class="a-steps">{relh}</div></div></section>' if rel else ''}
<section class="sec" id="notes"><div class="wrap"><div class="a-split">
<div><h2 style="margin-bottom:14px">Layers used</h2><ul class="a-layers-used"><li><span>se4allWS:cluster_all_simple_new</span><span>settlements</span></li><li><span>se4allWS:cluster_offgrid_simple</span><span>off-grid settlements</span></li><li><span>se4allWS:cluster_offgrid_survey</span><span>field survey</span></li><li><span>se4allWS:distribution_line_mv</span><span>MV grid</span></li><li><span>geonode:existing_lines_high_voltage</span><span>HV lines</span></li><li><span>geonode:substations_currently_installed</span><span>substations</span></li><li><span>se4allWS:minigrids</span><span>mini-grids</span></li><li><span>se4allWS:disco_coverage</span><span>DisCo areas</span></li><li><span>se4allWS:grid3_market_edited</span><span>markets</span></li></ul>
<p style="margin-top:14px"><a class="a-go" href="{PORTAL}">Download from the data portal</a></p></div>
<div><h2 style="margin-bottom:14px">How these figures are made</h2><ul class="a-notes"><li>Calculated from the public data portal on {PULLED}; planned refresh: nightly.</li><li>Line lengths are clipped to the state boundary. The MV layer combines SE4ALL field data, DisCo grid data (KAECO, KEDCO) and 2025 field work orders.</li><li>Distance to grid is recalculated for every settlement against the current MV layer (accurate to about 50 m).</li><li>Survey records are shown as published (survey years 2019 to 2026). Dataset licences are not yet specified on the portal.</li></ul></div>
</div></div></section>'''
    page(p, f"{name} state profile | Nigeria Electrification Atlas", f"Settlements, grid, mini-grids and surveyed communities in {name}.", body, "state", dict(state=name, infra=X["states"][name]))

# ================================================================ DEVELOPERS
def developers():
    c = N3["criteria"]; top_ready = ", ".join(f"{s} ({n})" for s, n in sorted(dev["ready_by_state"].items(), key=lambda x: -x[1])[:4])
    sopt = '<option value="">All states</option>' + "".join(f'<option value="{e(s)}">{e(s)} ({n})</option>' for s, n in sorted(dev["ready_by_state"].items()))
    body = phero('<a href="../../index.html">Home</a> <span>/</span> <span>Mini-grid developers</span>', "Briefing for mini-grid developers", "Where you can build, and where people already pay for power",
                 "Ranked from field-surveyed communities: settlement size, existing generator use, productive demand, road access and payment options.") + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Build-ready communities", dev["ready"], "communities", f"meet all build-ready criteria. Most are in {top_ready}.", "field-survey layer", "good", '<a class="a-go" href="#sites">See the list</a>')}
{card("Already paying for power", pc(dev["share_business_genset50"]), "of communities", f"without grid have at least half of their businesses on generators ({pc(dev['share_household_genset50'])} for households).", "field-survey layer")}
{card("Productive demand", f0(dev["mills"]), "grinding mills", f"and {f0(dev['presses'])} oil presses in the {f0(sv['no_grid'])} surveyed communities without grid.", "field-survey layer")}
{card("Fuel price to beat", f"₦{f0(fuel26['petrol'])}", "/ litre petrol", f"median in 2026 surveys (diesel ₦{f0(fuel26['diesel'])}), against ₦{f0(fuel22['petrol'])} petrol and ₦{f0(fuel22['diesel'])} diesel in 2022.", "field-survey layer", "warn", f'<p class="a-note">2026 figure from {fuel26["n"]} communities in {", ".join(fuel26["states"])}.</p>')}
{card("Payments and metering", pc(dev["share_3g4g"]), "have 3G/4G", f"of surveyed communities without grid; {pc(dev['share_mobile_money'])} have mobile money and {pc(dev['share_all_year'])} year-round truck or 4x4 access.", "field-survey layer")}
{card("Typical size", f0(dev["no_grid_median_buildings"]), "buildings", f"median for a surveyed community without grid. Recorded mini-grids have a median of {f0(inv['fleet_median_kw'])} kW.", "field-survey and mini-grid layers")}
</div></div></section>
<section class="sec field" id="sites"><div class="wrap">
<div class="sec-head"><div><span class="a-kick">Ranked list</span><h2>Build-ready communities</h2><p class="sub">Change a criterion and the count, map and list update immediately.</p></div></div>
<div class="a-tool"><form class="a-panel" id="a-criteria"><h3>Criteria</h3><p class="sub" style="font-size:14.5px">Surveyed communities with no grid at the time of survey.</p>
<label for="state">State</label><select name="state" id="state">{sopt}</select>
<label for="minb">At least this many buildings</label><select name="minb" id="minb"><option>100</option><option selected>200</option><option>500</option><option>1000</option></select>
<label for="ming">Businesses running generators</label><select name="ming" id="ming"><option value="0">Any share</option><option value="25">25% or more</option><option value="50" selected>50% or more</option><option value="75">75% or more</option></select>
<label for="mvd">Distance to nearest MV line</label><select name="mvd" id="mvd"><option value="any" selected>Any distance</option><option value="gt5">More than 5 km (off-grid)</option><option value="gt10">More than 10 km</option><option value="lt5">Within 5 km (grid extension or interconnection)</option></select>
<label class="chk"><input type="checkbox" name="road" checked> Year-round truck or 4x4 access</label><label class="chk"><input type="checkbox" name="pay" checked> Mobile money or 3G/4G available</label>
<div class="a-count"><b id="a-ready-count">—</b><span>communities match</span></div><button type="button" class="btn btn-primary" id="a-ready-csv" style="margin-top:14px">Download list (CSV)</button></form>
<div><div class="a-dmap" id="a-dev-map"></div><div class="a-tbl"><table class="a-t" id="a-ready"><thead><tr><th>Community</th><th>State</th><th class="n">Buildings</th><th class="n">Businesses on generators</th><th class="n">Grinding mills</th><th class="n">Oil presses</th><th class="n">Health facilities</th><th class="n">Nearest MV line</th><th class="n">Nearest substation</th><th>Payments</th><th class="n">Surveyed</th></tr></thead><tbody></tbody></table></div>
<p style="margin-top:14px"><button type="button" class="btn btn-outline" id="a-ready-more"></button></p></div></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Next steps</span><h2>Take a site further</h2></div></div>
{steps([("Off-grid webmap", "Check settlement clusters and the grid around a site.", APPS + "minigrid-offgrid"), ("Interconnected webmap", "Grid-connected communities with poor supply.", APPS + "minigrid-interconnected"), ("Licensing and finance on OSIP", "Regulatory pathways, incentives and financing.", OSIP)])}</div></section>
<section class="sec field" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How these figures are made</h2><ul class="a-notes">
<li>Build-ready criteria (proposed, to be agreed with REA/NESP): no grid at survey; at least {c["min_buildings"]} buildings; at least {c["min_business_genset_pct"]}% of businesses with generators; year-round truck or 4x4 access; mobile money or 3G/4G.</li>
<li>Nearest MV line and substation are recalculated for every surveyed community against the current <code>distribution_line_mv</code> layer and the de-duplicated substation layer.</li>
<li>Source: field-survey layer ({sv["total"]} communities; {", ".join(f"{y}: {n}" for y, n in sv["by_year"].items())}). Conditions may have changed since the survey.</li>
<li>Calculated from the public data portal on {PULLED}; planned refresh: nightly.</li></ul></div></section>'''
    page("for/developers/index.html", "Developer briefing | Nigeria Electrification Atlas", "Build-ready communities for mini-grid developers.", body, "developer")

# ================================================================ INVESTORS
def investors():
    rows = sorted(states.values(), key=lambda s: -s["offgrid_buildings"]); mx = rows[0]["offgrid_buildings"]; trs = ""
    for d in rows:
        kwp = d["minigrid_kw"] / d["offgrid_buildings"] * 1e5 if d["offgrid_buildings"] else 0; sh = d["buildings_over_5km"] / d["buildings"]
        trs += (f'<tr><td><a class="a-go" style="font-weight:600" href="../../states/{slug(d["state"])}/index.html">{e(d["state"])}</a></td><td class="n" data-v="{d["offgrid_buildings"]}"><span class="a-bar">{f0(d["offgrid_buildings"])}<i style="width:{80*d["offgrid_buildings"]/mx:.0f}px"></i></span></td>'
                f'<td class="n" data-v="{sh:.4f}">{pc(sh)}</td><td class="n" data-v="{d["minigrids"]}">{d["minigrids"]}</td><td class="n" data-v="{d["minigrid_kw"]}">{f0(d["minigrid_kw"]) if d["minigrid_kw"] else "—"}</td>'
                f'<td class="n" data-v="{kwp:.2f}">{kwp:,.0f}</td><td class="n" data-v="{d["substations"]}">{d["substations"]}</td><td class="n" data-v="{d["ready_sites"]}">{d["ready_sites"] or "—"}</td><td>{", ".join(x["code"] for x in d["disco"])}</td></tr>')
    ftr = "".join(f'<tr><td><b>{e(g["community"] or "—")}</b><br><span class="a-muted">{e(g["lga"] or "")}{", " + e(g["state"]) if g["state"] else ""}</span></td><td class="n" data-v="{g["kw"] or 0}">{f0(g["kw"])}</td><td class="n" data-v="{g["conn"] or 0}">{f0(g["conn"])}</td><td>{e(g["system"] or "—")}</td><td><span class="a-pill {"mid" if g["status"] == "Under Construction" else ("ok" if g["operational"] else "bad")}">{e(g["status"] or "—")}{(" · " + e(g["condition"])) if g["condition"] and g["status"] != "Under Construction" else ""}</span></td><td>{e(g["programme"] or "—")}</td></tr>' for g in sorted(fleet, key=lambda g: -(g["kw"] or 0)))
    body = phero('<a href="../../index.html">Home</a> <span>/</span> <span>Investors</span>', "Briefing for investors and financiers", "Where the off-grid market is, and what is already built",
                 "Market size by state from the national settlement data, set against the mini-grids recorded on the platform.") + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Market concentration", pc(inv["top5_share"]), "in five states", f"of all off-grid buildings are in {', '.join(inv['top5'])}.", "off-grid settlement layer", "good")}
{card("Apparent white space", f"{len(inv['top10_no_minigrid'])} of 10", "largest markets", f"have no mini-grid recorded on the platform: {', '.join(inv['top10_no_minigrid'])}.", "mini-grid layer", "warn", '<p class="a-note">The mini-grid layer is incomplete; confirm against REA programme data.</p>')}
{card("Recorded fleet", f0(inv["fleet_kw"]), "kW", f"across {inv['fleet_n']} mini-grids (median {f0(inv['fleet_median_kw'])} kW): {', '.join(f'{v} {k.lower()}' for k, v in inv['systems'].items())}.", "mini-grid layer")}
{card("Operating risk", f0(inv["fleet_non_operational"]), f"of {inv['fleet_n']}", "recorded mini-grids are marked non-operational: asset performance matters as much as new build.", "mini-grid layer", "alert")}
{card("Customers per kW", f"{inv['conn_per_kw']:.1f}", "connections / kW", f"across recorded mini-grids with connection data ({f0(inv['fleet_conn'])} connections).", "mini-grid layer")}
{card("Grid backbone", f0(XN["substations"]), "substations", f"installed ({' · '.join(f'{n} at {k} kV' for k, n in XN['substations_by_kv'].items())}), with {XN['planned_substations']} planned. {sum(r[2] for r in XN['plants'] if r[1] == 'Existing')} power plants recorded.", "substation and power-plant layers (de-duplicated)", "", f'<p class="a-note">The source layers list each substation and plant twice ({XN["source_substation_points"]} substation points).</p>')}
</div></div></section>
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Market by state</span><h2>Off-grid demand against recorded supply</h2><p class="sub">Sorted by off-grid buildings. Click a column to re-sort, or a state for its profile.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>State</th><th class="n">Off-grid buildings</th><th class="n">Share &gt;5 km</th><th class="n">Mini-grids</th><th class="n">kW</th><th class="n">kW per 100k off-grid bldgs</th><th class="n">Substations</th><th class="n">Build-ready sites</th><th>DisCo</th></tr></thead><tbody>{trs}</tbody></table></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Recorded fleet</span><h2>Mini-grids on the platform</h2><p class="sub">Green: operational · red: non-operational · blue: under construction. Circle size shows capacity.</p></div></div>
<div class="a-dmap tall" id="a-inv-map"></div><div class="a-tbl"><table class="a-t"><thead><tr><th>Community</th><th class="n">kW</th><th class="n">Connections</th><th>System</th><th>Status</th><th>Programme</th></tr></thead><tbody>{ftr}</tbody></table></div></div></section>
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Next steps</span><h2>From market view to investment</h2></div></div>
{steps([("Invest through OSIP", "Opportunities, incentives, licensing and financing.", OSIP), ("Mini-grid monitor", "Operational data reported by mini-grids.", "https://minigridmonitor.nigeriase4all.gov.ng/"), ("Build-ready sites", "Field-surveyed communities that meet developer criteria.", "../developers/index.html")])}</div></section>
<section class="sec" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How these figures are made</h2><ul class="a-notes">
<li>Off-grid buildings: SE4ALL off-grid settlement layer, summed by state. "&gt;5 km" uses distances recalculated against the field-mapped MV grid.</li>
<li>Mini-grids: the platform's mini-grid layer ({inv["fleet_n"]} sites), assigned to states by location. It does not yet include all programme mini-grids.</li>
<li>Calculated from the public data portal on {PULLED}; planned refresh: nightly.</li></ul></div></section>'''
    page("for/investors/index.html", "Investor briefing | Nigeria Electrification Atlas", "Off-grid market by state against recorded mini-grid supply.", body, "investor")

exec(open(os.path.join(HERE, "pages_v5.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "pages_v6.py"), encoding="utf-8").read())
home(); states_index(); developers(); investors(); researchers(); learners(); communities_index(); community_pages(); data_health()
for n in states: state_page(n)
print("built", sum(1 for _, _, fs in os.walk(OUT) for f in fs if f.endswith(".html")), "pages")
