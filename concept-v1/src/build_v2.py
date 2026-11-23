# -*- coding: utf-8 -*-
"""Concept v2 generator: home, states index, 37 state profiles. Figures come only from ../data (GeoNode ETL)."""
import os, sys, json, re, shutil, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "nesp-website-source"))
from content import POSTS, ORIG, UP, ST  # blog metadata transcribed from the live site

DATA = os.path.join(ROOT, "data"); OUT = os.path.join(ROOT, "site")
states = json.load(open(os.path.join(DATA, "states.json"))); S = states["states"]
nat = json.load(open(os.path.join(DATA, "national.json")))
finder = json.load(open(os.path.join(DATA, "finder.json")))
geo = json.load(open(os.path.join(DATA, "states.geojson")))
for f in geo["features"]:
    f["properties"] = {"state": f["properties"]["state"]}
PULLED = datetime.date.fromisoformat(states["pulled"]).strftime("%-d %B %Y")
SHOW = "Nasarawa"

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "assets")); os.makedirs(os.path.join(OUT, "data"))
for f in ("site.css", "site.js"): shutil.copy(os.path.join(HERE, "assets", f), os.path.join(OUT, "assets", f))
# data as JS so pages also work from file://
lite = {k: {kk: vv for kk, vv in v.items() if kk not in ("survey", "minigrids", "bands")} for k, v in S.items()}
open(os.path.join(OUT, "data", "se4all-data.js"), "w").write(
    "window.SE4ALL=" + json.dumps(dict(pulled=states["pulled"], states=lite, finder=finder, geo=geo), separators=(",", ":")) + ";")

e = lambda s: html.escape(str(s), quote=True)
fmt = lambda n: "—" if n is None else f"{n:,.0f}"
slug = lambda s: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))
pct = lambda a, b: (100 * a / b) if b else 0
POST_URL = lambda p: ORIG + "/blog-post/" + p["date"].replace("-", "/") + "/" + p["slug"]
LIVE = dict(blog=ORIG + "/blog", about=ORIG + "/about", power=ORIG + "/power-sector")
APPS = "https://apps.nigeriase4all.gov.ng/"
WFS_CAP = "https://data.nigeriase4all.gov.ng/geoserver/ows?service=WFS&version=2.0.0&request=GetCapabilities"
LEAF = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">'
LEAFJS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>'
RAMP = ["#F6EBD6", "#EBCB91", "#D9A445", "#B9770E", "#7A4E07"]

def page(path, title, body, desc, cur="", page_data=None, leaflet=False):
    depth = path.count("/"); root = "../" * depth
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    pd = dict(root=root); pd.update(page_data or {})
    nav = [("Map", root + "index.html#map", "map"), ("States", root + "states/index.html", "states"), ("Site-finder", root + "index.html#finder", "finder"),
           ("Data", "https://data.nigeriase4all.gov.ng/", "data"), ("Stories", LIVE["blog"], "stories"), ("About", LIVE["about"], "about")]
    navh = "".join(f'<a href="{u}"{" aria-current=page" if k == cur else ""}>{t}</a>' for t, u, k in nav)
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="icon" href="{ORIG}/assets/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600&family=Source+Sans+3:wght@400;500;600;700&family=Source+Code+Pro:wght@400&display=swap" rel="stylesheet">
{LEAF if leaflet else ""}<link rel="stylesheet" href="{root}assets/site.css"></head><body>
<header class="top"><div class="wrap">
<a class="id" href="{root}index.html"><img src="{ORIG}/assets/logo-5-blitz.png" alt="SE4ALL logo"><span><b>Nigeria SE4ALL</b><small>Federal Ministry of Power · NESP</small></span></a>
<nav aria-label="Primary">{navh}</nav><button class="menu-btn" aria-expanded="false">Menu</button>
<a href="https://www.power.gov.ng/" class="fmpl" aria-label="Federal Ministry of Power"><img class="fmp" src="{ORIG}/assets/fmp_logo_no_text.png" alt="FMP"></a>
</div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap"><div class="g">
<div><h4>Nigeria SE4ALL</h4><p>An initiative of the Federal Ministry of Power, in partnership with the Nigerian Energy Support Programme (NESP).</p>
<div class="logos"><img src="{ORIG}/assets/logo-1-eu.png" alt="European Union"><img src="{ORIG}/assets/logo-4-ger-coop.png" alt="German Cooperation"><img src="{ORIG}/assets/logo-3-giz.png" alt="GIZ"></div></div>
<div><h4>Explore</h4><ul><li><a href="{root}states/index.html">States</a></li><li><a href="{root}index.html#finder">Site-finder</a></li><li><a href="{APPS}minigrid-offgrid">Off-grid webmap</a></li><li><a href="{APPS}power-sector">Power sector webmap</a></li><li><a href="{APPS}shs">Solar home systems webmap</a></li></ul></div>
<div><h4>Data</h4><ul><li><a href="https://data.nigeriase4all.gov.ng/">Data portal (GeoNode)</a></li><li><a href="{WFS_CAP}">WFS endpoint</a></li><li><a href="https://minigridmonitor.nigeriase4all.gov.ng/">Mini-grid monitor</a></li><li><a href="https://learning.nigeriase4all.gov.ng/">Learning platform</a></li></ul></div>
<div><h4>Office</h4><p>Federal Ministry of Power<br>POWER HOUSE 14, Zambezi Crescent Maitama<br>Abuja, Nigeria</p><p style="margin-top:10px"><a href="mailto:contact.nigeriase4all@gmail.com">contact.nigeriase4all@gmail.com</a><br><a href="http://www.power.gov.ng">www.power.gov.ng</a></p></div>
</div><div class="bot"><span>© 2021 All Rights Reserved by nigeriase4all.gov.ng</span><span><a href="{ORIG}/terms-of-service">Terms of Service</a> · <a href="{ORIG}/privacy-policy">Privacy Policy</a> · <a href="{ORIG}/accreditation">Accreditation</a></span></div></div></footer>
<script>window.PAGE={json.dumps(pd, separators=(",", ":"))};</script>
<script src="{root}data/se4all-data.js"></script>{LEAFJS if leaflet else ""}<script src="{root}assets/site.js"></script></body></html>'''
    open(full, "w", encoding="utf-8").write(doc)

def state_options(selected=""):
    return "".join(f'<option value="{e(s)}"{" selected" if s == selected else ""}>{e(s)}</option>' for s in sorted(S))

def legend_ramp():
    return ('<h4>Buildings &gt;5 km from mapped MV grid</h4><div class="ramp">' + "".join(f'<i style="background:{c}"></i>' for c in RAMP) +
            '</div><div class="ramp-l"><span>0%</span><span>10</span><span>20</span><span>30</span><span>40%+</span></div>'
            '<div class="key"><i></i> Mapped MV grid (GeoServer)</div>')

# ------------------------------------------------------------------ HOME
def home():
    p = "index.html"
    ds = finder["D"]; ns = finder["N"]
    dopt = "".join(f'<option value="{d}"{" selected" if d == 10 else ""}>{d}</option>' for d in ds)
    nopt = "".join(f'<option value="{n}"{" selected" if n == 500 else ""}>{n:,}</option>' for n in ns)
    surv_dates = sorted(x["date"] for s in S.values() for x in s["survey"] if x.get("date"))
    stories = "".join(f'<a class="story" href="{POST_URL(x)}"><span class="d">{x["date"]}</span><span><h3>{e(x["title"])}</h3><span class="muted small">{e(x["author"])}</span></span><span class="t">{" · ".join(t.replace(" Sector","") for t in x["tags"])}</span></a>' for x in POSTS[:5])
    body = f'''
<section class="hero" id="map">
<div class="copy">
<span class="kicker">Electrification data · Nigeria</span>
<h1>Where Nigeria's settlements are, and how far they are from the grid.</h1>
<p class="muted">Nigeria SE4ALL is the Federal Ministry of Power's open electrification data platform, developed with the Nigerian Energy Support Programme. The headline figures below are calculated directly from its public data layers.</p>
<div class="facts">
<div><b>{fmt(nat["clusters"])}</b><span>settlement clusters mapped</span></div>
<div><b>{nat["buildings"]/1e6:.1f}M</b><span>buildings in those settlements</span></div>
<div><b>{fmt(nat["mv_km"])}</b><span>km of medium-voltage grid mapped</span></div>
<div><b>{fmt(nat["surveyed"])}</b><span>settlements surveyed in the field</span></div>
</div>
<form class="picker" data-state-go><label for="pick">Open a state profile</label><div class="row"><select id="pick"><option value="">Choose a state…</option>{state_options()}</select><button class="btn" type="submit">Go</button></div></form>
<p class="small muted">Figures pulled from <a href="https://data.nigeriase4all.gov.ng/">data.nigeriase4all.gov.ng</a> on {PULLED}.</p>
</div>
<div class="mapbox"><div id="nat-map" aria-label="Map of Nigeria: share of buildings more than 5 km from the mapped grid, by state"></div>
<div class="map-ui hoverbox" aria-live="polite"></div><div class="map-ui legend">{legend_ramp()}</div></div>
</section>

<section class="finder" id="finder"><div class="wrap">
<div><span class="kicker">Site-finder</span><h2>Find candidate settlements for off-grid electrification</h2>
<form class="sentence" onsubmit="return false">In <select name="state" aria-label="State"><option value="">all of Nigeria</option>{state_options()}</select>,
show settlements at least <select name="dist" aria-label="Minimum distance to grid in km">{dopt}</select> km from the mapped grid
with at least <select name="bldg" aria-label="Minimum number of buildings">{nopt}</select> buildings.</form></div>
<div class="result"><b id="f-clusters">—</b><span>settlement clusters match</span><b id="f-buildings" style="font-size:26px;margin-top:12px">—</b><span>buildings in those settlements</span><br>
<a class="btn" id="f-go" href="{APPS}minigrid-offgrid">Open the off-grid webmap</a>
<p class="note">Counts come from the SE4ALL settlement-cluster layer ({fmt(nat["clusters"])} clusters). Distance is to the grid recorded in that layer.</p></div>
</div></section>

<section class="sec white"><div class="wrap">
<div class="sec-h"><div><span class="kicker">Start from what you do</span><h2>Paths through the platform</h2></div><p class="lede">The same national data serves very different jobs. Pick yours.</p></div>
<div class="paths">
<div class="path"><h3>Mini-grid developer</h3><p>Shortlist sites by distance to grid and settlement size, then check field-survey data for the communities.</p><div class="go"><a class="arrow" href="#finder">Site-finder</a><a class="arrow" href="{APPS}minigrid-offgrid">Off-grid webmap</a><a class="arrow" href="{APPS}minigrid-interconnected">Interconnected webmap</a></div></div>
<div class="path"><h3>Investor</h3><p>Compare states on the size of the unserved market and the mini-grids already operating.</p><div class="go"><a class="arrow" href="states/index.html">Compare states</a><a class="arrow" href="https://minigridmonitor.nigeriase4all.gov.ng/">Mini-grid monitor</a><a class="arrow" href="https://greenenergyinvestment.com.ng">Green Energy Investment</a></div></div>
<div class="path"><h3>Government planner</h3><p>See each state's settlements, grid and generation assets in one profile, and national progress toward 30:30:30.</p><div class="go"><a class="arrow" href="states/{slug(SHOW)}/index.html">Example: {SHOW}</a><a class="arrow" href="{LIVE["power"]}">30:30:30 targets</a><a class="arrow" href="{APPS}power-sector">Power sector webmap</a></div></div>
<div class="path"><h3>Researcher or data user</h3><p>Download the layers or query them directly from GeoServer in QGIS or your own code.</p><div class="go"><a class="arrow" href="https://data.nigeriase4all.gov.ng/">Data portal</a><a class="arrow" href="{WFS_CAP}">WFS endpoint</a></div></div>
<div class="path"><h3>Student or mapper</h3><p>Learn GIS and OpenStreetMap, and contribute buildings to the national base data at a mapathon.</p><div class="go"><a class="arrow" href="https://learning.nigeriase4all.gov.ng/">Learning platform</a><a class="arrow" href="{POST_URL([x for x in POSTS if x["slug"]=="nigeria-se4-all-mapathon"][0])}">About mapathons</a></div></div>
</div></div></section>

<section class="sec"><div class="wrap">
<div class="sec-h"><div><span class="kicker">How the data is made</span><h2>From satellite to field survey</h2></div><p class="lede">The platform combines remote mapping, field visits and vehicle-mounted mapping, then publishes the result as open layers.</p></div>
<div class="method">
<div class="step"><div class="ph"><img src="{UP}05_Mapathon_image_1_7f67e75c90.jpg" alt="Mapathon participants" loading="lazy"></div><b class="num">75,000+</b><h3>Remote mapping</h3><p>Buildings mapped in off-grid areas of Kogi, Yobe and Imo through SE4ALL mapathons on OpenStreetMap.</p><a class="arrow small" href="{POST_URL([x for x in POSTS if x["slug"]=="nigeria-se4-all-mapathon"][0])}">Mapathons</a></div>
<div class="step"><div class="ph"><img src="{UP}Offgrid_settlement_survey_map_new_8c945e48f0.png" alt="Map of surveyed off-grid settlements" loading="lazy"></div><b class="num">{fmt(nat["surveyed"])}</b><h3>Field survey</h3><p>Settlements visited and published with grid status, income sources and services. Most were surveyed in 2022; new surveys are still being added (latest: {datetime.date.fromisoformat(surv_dates[-1]).strftime("%-d %b %Y")}).</p><a class="arrow small" href="{POST_URL(POSTS[0])}">Survey method</a></div>
<div class="step"><div class="ph"><img src="{UP}MM_Picture_1_a90ca4d78d.jpg" alt="Vehicle-mounted mobile mapping device" loading="lazy"></div><b class="num">~4,000</b><h3>Mobile mapping</h3><p>Poles tracked along about 250 km of road in Nasarawa in May 2022, with earlier missions in the FCT and Sokoto.</p><a class="arrow small" href="{POST_URL([x for x in POSTS if x["slug"].startswith("innovative")][0])}">Mobile mapping</a></div>
<div class="step"><div class="ph"><img src="{UP}Medium_Voltage_grid_datasets_cadd5e1403.png" alt="Medium-voltage grid layer on the webmap" loading="lazy"></div><b class="num">28</b><h3>Open publication</h3><p>Layers published on the GeoNode data portal, viewable in the webmaps and queryable through WMS and WFS.</p><a class="arrow small" href="https://data.nigeriase4all.gov.ng/">Data portal</a></div>
</div></div></section>

<section class="sec white"><div class="wrap">
<div class="sec-h"><div><span class="kicker">From the field</span><h2>Stories</h2></div><p class="lede">Methods, walkthroughs and field notes from the team. <a class="arrow" href="{LIVE["blog"]}">All stories</a></p></div>
<div class="stories">{stories}</div></div></section>

<section class="sec"><div class="wrap">
<div class="sec-h"><div><span class="kicker">Ecosystem</span><h2>Related platforms</h2></div><p class="lede">Nigeria SE4ALL is one part of the country's electrification data landscape.</p></div>
<div class="eco">
<a class="ext" href="https://data.nigeriase4all.gov.ng/"><b>Data portal</b><span>SE4ALL GeoNode: all layers</span></a>
<a class="ext" href="https://minigridmonitor.nigeriase4all.gov.ng/"><b>Mini-grid monitor</b><span>Operational mini-grid data</span></a>
<a class="ext" href="https://learning.nigeriase4all.gov.ng/"><b>Learning platform</b><span>Courses and training</span></a>
<a class="ext" href="https://www.power.gov.ng/"><b>Federal Ministry of Power</b><span>Policy and programmes</span></a>
<a class="ext" href="https://rea.gov.ng/"><b>Rural Electrification Agency</b><span>Rural access programmes</span></a>
<a class="ext" href="https://nerc.gov.ng/"><b>NERC</b><span>Electricity regulator</span></a>
<a class="ext" href="https://grid3.gov.ng/"><b>GRID3 Nigeria</b><span>Settlements, markets, facilities</span></a>
<a class="ext" href="https://greenenergyinvestment.com.ng"><b>Green Energy Investment</b><span>One-stop investment platform</span></a>
</div></div></section>'''
    page(p, "Nigeria SE4ALL: electrification data for every state", body, "Open electrification data for Nigeria: settlements, grid, mini-grids and field surveys for every state.", "map", leaflet=True)

# ------------------------------------------------------------------ STATES INDEX
def states_index():
    p = "states/index.html"
    rows = ""
    for s in sorted(S.values(), key=lambda v: -v["buildings_over_5km"]):
        sh = pct(s["buildings_over_5km"], s["buildings"]); mv = s["mv_km"] if s["mv_km"] >= 50 else None
        rows += (f'<tr><td><a class="arrow" style="font-weight:500" href="{slug(s["state"])}/index.html">{e(s["state"])}</a></td>'
                 f'<td class="n">{fmt(s["clusters"])}</td><td class="n">{fmt(s["buildings"])}</td>'
                 f'<td class="n" data-v="{sh:.2f}">{sh:.1f}%</td><td class="n">{fmt(s["buildings_over_5km"])}</td>'
                 f'<td class="n" data-v="{mv if mv else -1}">{fmt(mv) if mv else "<span class=na-note>not mapped</span>"}</td>'
                 f'<td class="n">{len(s["minigrids"])}</td><td class="n">{s["surveyed"]}</td><td>{", ".join(d["code"] for d in s["disco"])}</td></tr>')
    body = f'''<div class="wrap"><div class="crumb"><a href="../index.html">Home</a> / States</div>
<div class="state-h"><div><span class="kicker">State profiles</span><h1>Compare Nigeria's 36 states and the FCT</h1></div><div class="meta">Calculated from GeoNode layers<br>Pulled {PULLED}</div></div></div>
<section style="background:#fff;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)"><div class="hero" style="grid-template-columns:1fr;border:0"><div class="mapbox" style="min-height:520px"><div id="nat-map"></div><div class="map-ui hoverbox"></div><div class="map-ui legend">{legend_ramp()}</div></div></div></section>
<section class="sec"><div class="wrap">
<p class="lede" style="margin-bottom:20px">Sorted by buildings more than 5 km from the mapped grid. Click a column to re-sort.</p>
<div class="tbl"><table class="t" data-sort><thead><tr><th>State</th><th data-n>Settlements</th><th data-n>Buildings</th><th data-n>&gt;5 km share</th><th data-n>Buildings &gt;5 km</th><th data-n>MV grid km</th><th data-n>Mini-grids</th><th data-n>Surveyed</th><th>DisCo</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="flag" style="margin-top:18px">"Not mapped" means GeoNode holds less than 50 km of MV grid for the state. In these states, distance-to-grid figures depend on the grid recorded in the settlement layer, so they should be read with care until the grid data is completed.</div>
</div></section>'''
    page(p, "State profiles | Nigeria SE4ALL", body, "Compare settlements, grid and mini-grids across Nigeria's 36 states and the FCT.", "states", leaflet=True)

# ------------------------------------------------------------------ STATE PROFILE
GRID_L = {"no": ("No grid", "no"), "yes_connected_national_grid": ("Connected to national grid", "yes"), "yes_not_connected_national_grid": ("Grid present, not connected", "")}
FUNC_L = {"everything_functional": "Functional", "never_functional": "Never functional", "partially_functional": "Partly functional", "not_functional_anymore": "No longer functional"}

def state_page(name):
    s = S[name]; sl = slug(name); p = f"states/{sl}/index.html"
    mv_ok = s["mv_km"] >= 50
    sh = pct(s["buildings_over_5km"], s["buildings"])
    mg = s["minigrids"]; kw = sum(x["kw"] or 0 for x in mg)
    nb = nat["bands"]; ntot = sum(b["buildings"] for b in nb)
    bars = ""
    for b, n in zip(s["bands"], nb):
        lab = f'{b["lo"]}–{b["hi"]} km' if b["hi"] else f'{b["lo"]}+ km'
        v = pct(b["buildings"], s["buildings"]); nv = pct(n["buildings"], ntot)
        bars += f'<div class="row"><span>{lab}</span><span class="track"><span class="fill{" near" if b["lo"] < 5 else ""}" style="width:{v:.1f}%"></span><span class="nat" style="left:{nv:.1f}%" title="Nigeria: {nv:.1f}%"></span></span><span class="v">{v:.1f}% · {fmt(b["buildings"])}</span></div>'
    # mini-grids
    if mg:
        mrows = "".join(f'<tr><td>{e(x["community"] or "—")}</td><td>{e(x["lga"] or "—")}</td><td class="n">{fmt(x["kw"])}</td><td class="n">{fmt(x["connections"])}</td><td>{e(x["system"] or "—")}</td><td>{e(x["status"] or "—")}{" · " + e(x["condition"]) if x["condition"] else ""}</td><td>{e(x["programme"] or "—")}</td></tr>' for x in mg)
        mtable = f'<div class="tbl"><table class="t" data-sort><thead><tr><th>Community</th><th>LGA</th><th data-n>kW</th><th data-n>Connections</th><th>System</th><th>Status</th><th>Programme</th></tr></thead><tbody>{mrows}</tbody></table></div>'
    else:
        mtable = '<p class="muted">No mini-grids for this state are recorded in the SE4ALL mini-grid layer. Check the <a class="ext" href="https://minigridmonitor.nigeriase4all.gov.ng/">mini-grid monitor</a> for operational data.</p>'
    # survey
    sv = s["survey"]
    if sv:
        srows = ""
        for x in sorted(sv, key=lambda r: (r["lga"] or "", r["community"] or "")):
            gl, gc = GRID_L.get(x["grid"], ((x["grid"] or "—").replace("_", " "), ""))
            srows += f'<tr data-f="{"no" if x["grid"] == "no" else "grid"}"><td>{e(x["community"] or "—")}</td><td>{e(x["lga"] or "—")}</td><td><span class="chip {gc}">{gl}</span></td><td>{FUNC_L.get(x["functionality"], "—") if x["functionality"] else "—"}</td><td>{e((x["income"] or "—").capitalize())}</td><td class="n" data-v="{x["date"] or ""}">{x["date"] or "—"}</td></tr>'
        nog = sum(1 for x in sv if x["grid"] == "no")
        stable = f'''<p class="lede" style="margin-bottom:16px"><span class="num">{nog}</span> of <span class="num">{len(sv)}</span> surveyed communities had no grid presence at the time of survey.</p>
<div class="filters" data-for="svt"><button data-f="all" aria-pressed="true">All ({len(sv)})</button><button data-f="no" aria-pressed="false">No grid ({nog})</button><button data-f="grid" aria-pressed="false">Grid present ({len(sv)-nog})</button></div>
<div class="tbl"><table class="t" id="svt" data-sort><thead><tr><th>Community</th><th>LGA</th><th>Grid at survey</th><th>Grid functionality</th><th>Primary income</th><th data-n>Survey date</th></tr></thead><tbody>{srows}</tbody></table></div>'''
    else:
        stable = '<p class="muted">No communities in this state are in the published field-survey layer.</p>'
    # related stories: posts that mention the state by name
    rel = [x for x in POSTS if re.search(r"\b" + re.escape(name) + r"\b", x["body"])]
    relh = "".join(f'<a class="story" href="{POST_URL(x)}"><span class="d">{x["date"]}</span><span><h3>{e(x["title"])}</h3></span><span class="t">mentions {e(name)}</span></a>' for x in rel)
    kpi = lambda v, l, src, na=False: f'<div class="kpi{" na" if na else ""}"><b>{v}</b><span>{l}</span><small>{src}</small></div>'
    disco = ", ".join(f'{d["name"]} ({d["code"]})' for d in s["disco"]) or "—"
    body = f'''<div class="wrap"><div class="crumb"><a href="../../index.html">Home</a> / <a href="../index.html">States</a> / {e(name)}</div>
<div class="state-h"><div><span class="kicker">State profile</span><h1>{e(name)}</h1><p class="muted">Distribution company: {e(disco)}</p></div>
<div class="meta">Calculated from Nigeria SE4ALL GeoNode layers<br>Pulled {PULLED} · <a href="#notes">Data notes</a></div></div>
<div class="kpis">
{kpi(fmt(s["clusters"]), "settlement clusters", "cluster_all_simple_new")}
{kpi(fmt(s["buildings"]), "buildings in settlements", "cluster_all_simple_new")}
{kpi(fmt(s["buildings_over_5km"]), f"buildings &gt;5 km from mapped grid ({sh:.1f}%)", "grid_dist_km &gt; 5")}
{kpi(fmt(s["offgrid_clusters"]), f"SE4ALL off-grid settlements · {fmt(s['offgrid_buildings'])} buildings", "cluster_offgrid_simple")}
{kpi(fmt(s["mv_km"]) if mv_ok else "Not mapped", "km of MV grid mapped", "distribution_line_mv", not mv_ok)}
{kpi(fmt(s["hv_km"]), "km of HV transmission lines", "existing_lines_high_voltage")}
{kpi(fmt(s["substations"]), "substations installed", "substations_currently_installed")}
{kpi(str(len(mg)) + (f' · {kw:,.0f} kW' if kw else ''), "mini-grids recorded", "minigrids")}
{kpi(fmt(s["surveyed"]), "communities surveyed in the field", "cluster_offgrid_survey")}
{kpi(fmt(s["markets"]), "markets (GRID3)", "grid3_market_edited")}
</div></div>

<section class="sec" id="map"><div class="wrap"><div class="split">
<div><h2 style="margin-bottom:14px">Map</h2><div class="state-map"><div class="map" id="state-map"></div>
<div class="map-ui layers"><b class="small">Layers</b>
<label><input type="checkbox" data-layer="settle"> Settlement clusters</label>
<label><input type="checkbox" data-layer="offgrid"> SE4ALL off-grid settlements</label>
<label><input type="checkbox" data-layer="mv"> MV grid</label>
<label><input type="checkbox" data-layer="hv"> HV lines</label>
<label><input type="checkbox" data-layer="subs"> Substations</label>
<label><input type="checkbox" data-layer="mg"> <i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#0E5A3A"></i> Mini-grids</label>
<label><input type="checkbox" data-layer="survey"> <i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#B9770E"></i> Surveyed: no grid</label></div></div>
<p class="small muted" style="margin-top:8px">Lines and settlements are drawn live from the SE4ALL GeoServer. Blue survey points had grid present at the time of survey.</p></div>
<div><h2 style="margin-bottom:6px">Distance to the grid</h2><p class="muted" style="margin-bottom:18px">Share of {e(name)}'s {fmt(s["buildings"])} buildings by distance from the mapped grid. The black tick marks Nigeria as a whole.</p>
<div class="bars">{bars}</div>
<div class="flag" style="margin-top:22px">{fmt(s["clusters_over_5km"])} settlement clusters ({fmt(s["buildings_over_5km"])} buildings) in {e(name)} are more than 5 km from the mapped grid. <a class="arrow" href="../../index.html#finder">Filter them in the site-finder</a></div>
{"" if mv_ok else '<div class="flag" style="margin-top:12px">GeoNode holds little or no MV grid for this state, so distances may be overstated.</div>'}
<div style="margin-top:22px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="{APPS}minigrid-offgrid">Off-grid webmap</a><a class="btn line" href="{APPS}power-sector">Power sector webmap</a></div>
</div></div></div></section>

<section class="sec white"><div class="wrap"><div class="sec-h"><div><span class="kicker">Generation</span><h2>Mini-grids</h2></div><p class="lede">Mini-grids recorded for {e(name)} in the SE4ALL mini-grid layer.</p></div>{mtable}</div></section>
<section class="sec"><div class="wrap"><div class="sec-h"><div><span class="kicker">Ground truth</span><h2>Surveyed communities</h2></div><p class="lede">Communities visited by the SE4ALL field teams, with what they found on the ground.</p></div>{stable}</div></section>
{f'<section class="sec white"><div class="wrap"><div class="sec-h"><div><span class="kicker">From the field</span><h2>Stories about {e(name)}</h2></div><p class="lede">Articles that mention {e(name)}.</p></div><div class="stories">{relh}</div></div></section>' if rel else ''}
<section class="sec" id="notes"><div class="wrap"><div class="split">
<div><h2 style="margin-bottom:14px">Layers used</h2><ul class="layers-used">
<li><span>se4allWS:cluster_all_simple_new</span><span>settlements, buildings, distance</span></li>
<li><span>se4allWS:cluster_offgrid_simple</span><span>off-grid settlements</span></li>
<li><span>se4allWS:cluster_offgrid_survey</span><span>field survey</span></li>
<li><span>se4allWS:distribution_line_mv</span><span>MV grid</span></li>
<li><span>geonode:existing_lines_high_voltage</span><span>HV lines</span></li>
<li><span>geonode:substations_currently_installed</span><span>substations</span></li>
<li><span>se4allWS:minigrids</span><span>mini-grids</span></li>
<li><span>se4allWS:disco_coverage</span><span>DisCo areas</span></li>
<li><span>se4allWS:grid3_market_edited</span><span>markets (GRID3)</span></li></ul>
<p style="margin-top:14px"><a class="arrow" href="https://data.nigeriase4all.gov.ng/">Download from the data portal</a></p></div>
<div><h2 style="margin-bottom:14px">Data notes</h2><ul class="notes">
<li>Figures are calculated from the public GeoNode layers (planned refresh: nightly). Last pull: {PULLED}.</li>
<li>Line lengths are measured after clipping to the state boundary. The MV layer combines SE4ALL field data, DisCo grid data (KAECO, KEDCO) and 2025 field work orders.</li>
<li>"Distance to the grid" is the distance recorded for each settlement cluster in the SE4ALL settlement layer. It may not yet reflect MV lines added in later field work, so it can overstate distances where new grid data has been collected.</li>
<li>Field-survey records are shown as published. Survey dates for {e(name)}: {(min(x["date"] for x in sv if x["date"]) + " to " + max(x["date"] for x in sv if x["date"])) if sv else "none"}.</li>
<li>Dataset licences are not yet specified on the data portal.</li></ul></div></div></div></section>'''
    page(p, f"{name} state profile | Nigeria SE4ALL", body, f"Settlements, grid, mini-grids and surveyed communities in {name}, calculated from Nigeria SE4ALL open data.", "states",
         dict(state=name, minigrids=mg, survey=[x for x in sv if x["lat"] is not None]), leaflet=True)

home(); states_index()
for n in S: state_page(n)
print("built", sum(1 for _, _, fs in os.walk(OUT) for f in fs if f.endswith(".html")), "pages")
