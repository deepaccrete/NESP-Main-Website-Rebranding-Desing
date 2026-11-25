# -*- coding: utf-8 -*-
"""State profiles v2 (map-first). Rewrites site/states/<slug>/index.html in place.
Keeps each page's v3 header/footer; replaces <main>. Originals are kept in _backup/states-before-redesign/.
Run from anywhere:  python3 concept-v3/src/make_state_pages.py"""
import os, re, json, html, shutil, datetime, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from clean_footer import fix as clean_footer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site"); BAK = os.path.join(os.path.dirname(ROOT), "_backup", "states-before-redesign")
s = open(os.path.join(SITE, "data", "atlas-data.js"), encoding="utf-8").read()
A = json.loads(s[s.index("=") + 1:].rstrip().rstrip(";"))
S2 = json.load(open(os.path.join(ROOT, "data", "states.json")))
NAT = json.load(open(os.path.join(ROOT, "data", "national.json")))
X = json.load(open(os.path.join(ROOT, "data", "extras.json")))
PULLED = datetime.date.fromisoformat(S2["pulled"]).strftime("%-d %B %Y")
APPS = "https://apps.nigeriase4all.gov.ng/"; PORTAL = "https://data.nigeriase4all.gov.ng/"
e = lambda x: html.escape(str(x), quote=True)
f0 = lambda n: "—" if n is None else f"{n:,.0f}"
slug = lambda t: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", t.lower()))
STATES = sorted(A["states"])
nb = NAT["bands"]; ntot = sum(b["buildings"] for b in nb); nat_far = 100 * sum(b["buildings"] for b in nb if b["lo"] >= 5) / ntot
BAND_C = ["#065F46", "#A3D376", "#E8A317", "#D97706", "#9A3412"]

def unserved(c): return c.get("never_functional") or c.get("grid") in ("no", "yes_not_connected_national_grid")

SVG = lambda b: f'<svg viewBox="0 0 24 24">{b}</svg>'
SW_POLY = lambda c: SVG(f'<path d="M4 7l7-4 9 5-2 11-10 2z" fill="{c}" fill-opacity=".55" stroke="{c}" stroke-width="1.5"/>')
SW_LINE = lambda c, w: SVG(f'<path d="M2 18C8 6 14 18 22 6" fill="none" stroke="{c}" stroke-width="{w}"/>')
DOT = lambda c: f'<i style="background:{c}"></i>'

def main_html(name):
    d = A["states"][name]; b2 = S2["states"][name]; x = X["states"][name]
    comm = [c for c in A["communities"] if c["state"] == name]
    uns = [c for c in comm if unserved(c)]
    fleet = [g for g in A["fleet"] if g["state"] == name]
    nep = [p for p in A["nep"] if p["state"] == name]
    nepmg = [p for p in nep if p["kind"] == "minigrid"]
    disco = ", ".join(f'{q["name"]} ({q["code"]})' for q in d["disco"]) or "—"
    codes = ", ".join(q["code"] for q in d["disco"]) or "the DisCo"
    sh5 = 100 * d["buildings_over_5km"] / d["buildings"] if d["buildings"] else 0
    surveyed = bool(comm)
    opts = "".join(f'<option value="{e(t)}"{" selected" if t == name else ""}>{e(t)}</option>' for t in STATES)
    mg_total = len(fleet) + sum(1 for p in nepmg if not p.get("in_se4all_layer"))
    mg_kw = sum(g["kw"] or 0 for g in fleet) + sum(p["capacity_kw"] or 0 for p in nepmg if not p.get("in_se4all_layer"))

    hero = f'''<section class="phero sp-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../../index.html">Home</a> <span>/</span> <a href="../index.html">State governments</a> <span>/</span> <span>{e(name)}</span></nav>
<div class="sp-top"><div><div class="eyebrow">State profile</div><h1>{e(name)}</h1><p class="lead">{e(disco)}. #{d["rank_offgrid"]} of 37 states for off-grid demand.</p></div>
<form class="a-pickhero" data-state-go><label for="sp-state">Switch state</label><select id="sp-state">{opts}</select><button class="btn btn-primary" type="submit">Go</button></form></div>
<div class="sp-kpis">
<div class="sp-kpi"><div class="k">Off-grid demand</div><b>{f0(d["offgrid_buildings"])}</b><span>buildings in off-grid settlements</span></div>
<div class="sp-kpi"><div class="k">Far from the grid</div><b>{f0(d["buildings_over_5km"])}</b><span>buildings more than 5 km away ({sh5:.0f}% of the state)</span></div>
<div class="sp-kpi"><div class="k">Surveyed, no working grid</div><b>{f"{len(uns)} of {len(comm)}" if surveyed else "—"}</b><span>{"field-surveyed communities" if surveyed else "no field survey yet in this state"}</span></div>
<div class="sp-kpi"><div class="k">Mini-grids recorded</div><b>{mg_total}</b><span>{f0(mg_kw)} kW · {len(fleet)} platform, {len(nepmg)} NEP</span></div>
</div><p class="a-stamp">Calculated from the platform's public data on {PULLED}. <a href="#about">About these figures</a></p></div></section>'''

    if surveyed:
        listpane = f'''<div class="sp-chips"><button data-cf="prio" aria-pressed="true">No working grid ({len(uns)})</button><button data-cf="clinic" aria-pressed="false">Clinic without grid ({sum(1 for c in uns if (c["health"] or 0) > 0)})</button><button data-cf="broken" aria-pressed="false">Grid never worked ({sum(1 for c in comm if c["never_functional"])})</button><button data-cf="all" aria-pressed="false">All ({len(comm)})</button></div>
<input class="sp-search" id="sp-q" type="search" placeholder="Search community or LGA" aria-label="Search surveyed communities"><div class="sp-count" id="sp-count"></div><ul class="sp-list" id="sp-list"></ul>'''
    else:
        listpane = f'<p class="sp-empty"><b>No field survey yet in {e(name)}.</b><br>You can still click any settlement on the map to see its size, distance to the grid and the nearest substation and mini-grid.</p><p class="sp-empty" style="margin-top:10px"><a class="a-go" href="../../communities/index.html">See the surveyed states</a></p>'
    layers = f'''<div class="sp-lg"><h4>Demand</h4>
<label><input type="checkbox" data-lay="offgrid"><span class="sp-sw">{SW_POLY("#C2410C")}</span>Off-grid settlements<small>SE4ALL</small></label>
<label><input type="checkbox" data-lay="settle"><span class="sp-sw">{SW_POLY("#64748B")}</span>All settlement clusters<small>heavy</small></label>
<h4>Grid</h4>
<label><input type="checkbox" data-lay="mv"><span class="sp-sw">{SW_LINE("#2563EB", 2)}</span>MV grid (11/33 kV)</label>
<label><input type="checkbox" data-lay="hv"><span class="sp-sw">{SW_LINE("#7F1D1D", 3.5)}</span>HV lines (132/330 kV)</label>
<label><input type="checkbox" data-lay="subs"><span class="sp-sw" data-sw="subs"></span>Substations<small>{len(x["substations"])}</small></label>
<label><input type="checkbox" data-lay="planned"><span class="sp-sw" data-sw="planned"></span>Planned substations<small>{len(x["planned_substations"])}</small></label>
<label><input type="checkbox" data-lay="plants"><span class="sp-sw" data-sw="plants"></span>Power plants<small>{len(x["plants"])}</small></label>
<h4>Supply already in place</h4>
<label><input type="checkbox" data-lay="mg"><span class="sp-sw" data-sw="mg"></span>Mini-grids (platform)<small>{len(fleet)}</small></label>
<div class="sp-key"><span>{DOT("#047857")}Operational</span><span>{DOT("#B91C1C")}Not operational</span><span>{DOT("#1E4E79")}Under construction</span></div>
<label><input type="checkbox" data-lay="nep"><span class="sp-sw" data-sw="nep"></span>NEP projects<small>{len(nep)}</small></label>
<div class="sp-key"><span>{DOT("#7C3AED")}Mini-grid</span><span>{DOT("#BE185D")}Health</span><span>{DOT("#1D4ED8")}Education</span></div>
<h4>Field survey</h4>
<label><input type="checkbox" data-lay="survey"><span class="sp-sw">{SVG('<circle cx="12" cy="12" r="7" fill="#D97706" stroke="#fff" stroke-width="2"/>')}</span>Surveyed communities<small>{len(comm)}</small></label>
<div class="sp-key"><span>{DOT("#D97706")}No grid</span><span>{DOT("#B91C1C")}Grid never worked</span><span>{DOT("#6D28D9")}Not connected</span><span>{DOT("#1E4E79")}Connected</span></div>
<p class="sp-empty" style="font-size:12.5px;margin-top:12px">Lines and settlements are drawn live from the platform's GeoServer. Circle size shows community size.</p></div>'''
    mapsec = f'''<section class="sp-mapsec" id="map"><div class="sp-mapwrap">
<div class="sp-mapbox"><div class="sp-map" id="sp-map" role="region" aria-label="Map of {e(name)}"></div>
<div class="sp-ctl tl"><div class="sp-seg" role="group" aria-label="Basemap"><button type="button" data-base="streets">Streets</button><button type="button" data-base="satellite">Satellite</button><button type="button" data-base="plain">Plain</button></div><button class="sp-btn" type="button" id="sp-home">Reset view</button><button class="sp-btn" type="button" id="sp-fs">Full screen</button></div>
<div class="sp-ctl bl"><span class="sp-hint">Click a settlement, community or asset for details</span></div><div class="sp-busy" id="sp-busy">Looking up the settlement…</div></div>
<aside class="sp-side" aria-label="Map panel"><div class="sp-tabs" role="tablist"><button type="button" role="tab" data-tab="list" aria-selected="true">Communities</button><button type="button" role="tab" data-tab="layers" aria-selected="false">Layers</button><button type="button" role="tab" data-tab="det" aria-selected="false">Details</button></div>
<div class="sp-pane" id="sp-p-list">{listpane}</div><div class="sp-pane" id="sp-p-layers" hidden>{layers}</div>
<div class="sp-pane" id="sp-p-det" hidden><p class="sp-empty">Click anything on the map: a settlement, a surveyed community, a substation or a mini-grid.</p></div></aside>
</div></section>'''

    nf, pnc = d["never_functional"], d["present_not_connected"]
    cl = [c for c in uns if (c["health"] or 0) > 0]; sc = [c for c in uns if (c["schools"] or 0) > 0]
    no_survey = lambda k: f'<div class="sp-card"><span class="k">{k}</span><b class="big">—</b><p>No field survey yet in {e(name)}, so grid condition and facilities are not known community by community.</p><div class="go"><a href="mailto:contact.nigeriase4all@gmail.com?subject=Field%20survey%20for%20{e(name)}">Request a survey</a></div></div>'
    cards = f'''<div class="sp-card"><span class="k">Off-grid mini-grids and solar</span><b class="big">{f0(d["buildings_over_5km"])}<small>buildings</small></b>
<p>in {f0(d["clusters_over_5km"])} settlements more than 5 km from the MV grid, where grid extension is least likely soon. {f0(d["offgrid_clusters"])} settlements are on the SE4ALL off-grid list.</p>
<div class="go"><a href="../../for/developers/index.html#state={e(name)}">Shortlist sites in the Site finder →</a></div></div>'''
    if surveyed:
        cards += f'''<div class="sp-card red"><span class="k">Fix the grid</span><b class="big">{nf + pnc}<small>communities</small></b>
<p>surveyed where the grid has never worked ({nf}) or is in place but not connected ({pnc}). Rehabilitation or connection work with {e(codes)}.</p>
<div class="go"><button type="button" data-show="broken">Show them on the map →</button></div></div>
<div class="sp-card amber"><span class="k">Clinics and schools</span><b class="big">{len(cl)}<small>communities</small></b>
<p>without working grid have a health facility ({f0(sum(c["health"] for c in cl))} facilities); {len(sc)} have schools ({f0(sum(c["schools"] for c in sc))}). Anchor loads for a mini-grid, or stand-alone solar.</p>
<div class="go"><button type="button" data-show="clinic">Show them on the map →</button></div></div>'''
    else:
        cards += no_survey("Fix the grid") + no_survey("Clinics and schools")
    bands = b2["bands"]; tot = d["buildings"] or 1
    blab = lambda b: f"{b['lo']}–{b['hi']} km" if b["hi"] else f"{b['lo']}+ km"
    stack = "".join(f'<i style="width:{100*b["buildings"]/tot:.2f}%;background:{c}" title="{blab(b)}: {100*b["buildings"]/tot:.1f}%"></i>' for b, c in zip(bands, BAND_C))
    stackl = "".join(f'<span><i style="background:{c}"></i>{blab(b)}<b>{100*b["buildings"]/tot:.1f}%</b>{f0(b["buildings"])} bldgs</span>' for b, c in zip(bands, BAND_C))
    near = 100 * bands[0]["buildings"] / tot
    route = ("Most buildings are close to the grid, so supply quality and connections matter more than new lines; off-grid options suit the remote fringe."
             if near >= 50 else "A large share of buildings is far from the grid: off-grid mini-grids and solar home systems are the main route to access.")
    act = f'''<section class="sec" style="padding-top:64px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Where to act</span><h2>Electrification priorities for {e(name)}</h2></div></div>
<div class="sp-act">{cards}</div>
<div class="sp-dist"><h3>How far buildings are from the grid</h3><p>{near:.0f}% of {e(name)}'s {f0(d["buildings"])} buildings are within 1 km of the mapped MV grid and {sh5:.0f}% are more than 5 km away (Nigeria: {nat_far:.0f}%). {route}</p>
<div class="sp-stack" role="img" aria-label="Share of buildings by distance to the grid">{stack}</div><div class="sp-stack-l">{stackl}</div></div></div></section>'''

    prio = ""
    if surveyed:
        prio = f'''<section class="sec field"><div class="wrap"><div class="sp-tbar"><div><span class="a-kick">Ground truth</span><h2 style="margin:8px 0 4px">Priority communities</h2>
<p class="sub" style="margin:0">Surveyed communities without working grid: those with a clinic first, then by size. Click a row to see it on the map.</p></div>
<button class="btn btn-outline" type="button" id="sp-csv">Download all {len(comm)} as CSV</button></div>
<div class="sp-twrap"><table class="sp-t"><thead><tr><th>#</th><th>Community</th><th>Grid at survey</th><th class="n">Buildings</th><th class="n">Clinics / schools</th><th class="n">Businesses on generators</th><th class="n">To MV grid</th><th class="n">Surveyed</th></tr></thead><tbody id="sp-tbody"></tbody></table></div>
<button class="btn btn-outline sp-more" type="button" id="sp-tmore">Show all</button></div></section>'''

    rows = [(g["community"] or "Mini-grid", f'{f0(g["kw"])} kW · {g["status"] or "—"}{" · " + g["condition"] if g["condition"] and g["status"] != "Under Construction" else ""}') for g in sorted(fleet, key=lambda g: -(g["kw"] or 0))]
    rows += [((p["name"] or "NEP mini-grid").strip().title(), f'{f0(p["capacity_kw"])} kW · {f0(p["customers"])} customers · NEP') for p in nepmg if not p.get("in_se4all_layer")]
    mglist = ('<ul class="sp-rows">' + "".join(f"<li><span>{e(a)}</span><span>{e(b)}</span></li>" for a, b in rows[:8]) + "</ul>" + (f'<p class="sp-empty" style="margin-top:8px">+ {len(rows)-8} more on the map.</p>' if len(rows) > 8 else "")) if rows else f'<p class="sp-empty">No mini-grid is recorded in {e(name)} in the platform layer or the NEP map.</p>'
    hcount = sum(1 for p in nep if p["kind"] == "health"); ecount = sum(1 for p in nep if p["kind"] == "education")
    subs = "".join(f'<span>{e(t["name"])}</span>' for t in sorted(x["substations"], key=lambda t: (-(t["kv"] or 0), t["name"])))
    plan = "".join(f'<span class="p">{e(t["name"])} · planned</span>' for t in x["planned_substations"])
    plants = "".join(f'<span>{e(t["name"])} · {e(t["kind"])}</span>' for t in x["plants"])
    inplace = f'''<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Already in place</span><h2>Supply and grid in {e(name)}</h2></div></div><div class="sp-two">
<div class="sp-box"><h3>Off-grid supply</h3><div class="sp-mini"><div><b>{mg_total}</b><span>mini-grids ({f0(mg_kw)} kW)</span></div><div><b>{f0(d.get("shs_connections"))}</b><span>solar home systems (NEP)</span></div><div><b>{hcount + ecount}</b><span>NEP health and education sites</span></div></div>{mglist}
<p style="margin-top:14px"><a class="a-go" href="../../projects/index.html">All electrification projects</a> · <a class="a-go" href="https://minigridmonitor.nigeriase4all.gov.ng/">Mini-grid monitor</a></p></div>
<div class="sp-box"><h3>Grid backbone</h3><div class="sp-mini"><div><b>{f0(d["mv_km"])}</b><span>km of MV grid mapped</span></div><div><b>{f0(d["hv_km"])}</b><span>km of HV lines</span></div><div><b>{len(x["substations"])}</b><span>substations ({len(x["planned_substations"])} planned)</span></div></div>
<div class="sp-pills">{subs}{plan}{plants or ""}</div>{"" if subs or plan else '<p class="sp-empty">No substation recorded in this state.</p>'}
<p style="margin-top:14px">Distribution company: {e(disco)}. <a class="a-go" href="{APPS}power-sector" target="_blank" rel="noopener">Power sector webmap</a></p></div>
</div></div></section>'''

    about = f'''<section class="sec" id="about" style="padding-top:0"><div class="wrap"><details class="sp-about"><summary>About these figures and the data behind them</summary><div class="in"><ul class="a-notes">
<li>Calculated on {PULLED} from the Nigeria SE4ALL public data portal (<a class="a-go" href="{PORTAL}">data.nigeriase4all.gov.ng</a>), run by the Rural Electrification Agency. The map's lines and settlements, and the click-for-details lookup, are read live from that portal's GeoServer.</li>
<li>Distance to grid is recalculated for every settlement against the current field-mapped MV layer (about 50 m accuracy). Line lengths are clipped to the state boundary.</li>
<li>"No working grid" means a surveyed community with no grid, grid that has never worked, or grid present but not connected. Survey years run from 2019 to 2026.</li>
<li>Mini-grids: the platform layer plus NEP mini-grids (REA project map, list labelled April 2021) that are not already in it. Substations and plants are de-duplicated by name.</li>
<li>Layers: <code>cluster_all_simple_new</code>, <code>cluster_offgrid_simple</code>, <code>cluster_offgrid_survey</code>, <code>distribution_line_mv</code>, <code>existing_lines_high_voltage</code>, <code>substations_currently_installed</code>, <code>minigrids</code>, <code>disco_coverage</code>. Dataset licences are not yet specified on the portal.</li>
</ul><p style="margin-top:10px"><a class="a-go" href="{PORTAL}">Download from the data portal</a></p></div></details></div></section>'''
    return hero + mapsec + act + prio + inplace + about

import hashlib
VER = {k: hashlib.md5(open(os.path.join(HERE, "assets", k, "state." + k), "rb").read()).hexdigest()[:6] + format(int(datetime.datetime.now().timestamp()) % 4096, "03x") for k in ("css", "js")}
n = 0
for name in STATES:
    sl = slug(name); path = os.path.join(SITE, "states", sl, "index.html"); bk = os.path.join(BAK, sl, "index.html")
    if not os.path.exists(bk): os.makedirs(os.path.dirname(bk), exist_ok=True); shutil.copy(path, bk)
    doc = open(bk, encoding="utf-8").read()
    a = doc.index('<main id="main">') + len('<main id="main">'); b = doc.index("</main>")
    doc = doc[:a] + main_html(name) + doc[b:]
    doc = re.sub(r'window\.PAGE=\{.*?\};</script>', lambda m: "window.PAGE=" + json.dumps(dict(root="../../", kind="stateprofile", state=name, infra=X["states"][name])) + ";</script>", doc, count=1, flags=re.S)
    if "state.css" not in doc: doc = doc.replace('<link rel="stylesheet" href="../../assets/css/v9.css">', '<link rel="stylesheet" href="../../assets/css/v9.css">\n<link rel="stylesheet" href="../../assets/css/state.css">', 1)
    if "state.js" not in doc: doc = doc.replace('<script src="../../assets/js/v9.js"></script>', '<script src="../../assets/js/v9.js"></script><script src="../../assets/js/state.js"></script>', 1)
    doc = re.sub(r'state\.(css|js)(\?v=[0-9a-f]+)?"', lambda m: f'state.{m.group(1)}?v={VER[m.group(1)]}"', doc)
    assert "state.css" in doc and "state.js" in doc and '"kind": "stateprofile"' in doc, name
    doc = clean_footer(doc)
    open(path, "w", encoding="utf-8").write(doc); n += 1
for f, sub in (("state.css", "css"), ("state.js", "js")):
    src = os.path.join(HERE, "assets", sub, f)
    if os.path.exists(src): shutil.copy(src, os.path.join(SITE, "assets", sub, f))
print("rebuilt", n, "state pages")
