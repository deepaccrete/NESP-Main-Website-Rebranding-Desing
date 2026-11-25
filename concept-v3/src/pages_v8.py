# v8: map-first workspaces. A combined mini-grid hub from every open source, a developer site workspace and an investor
# opportunity workspace. Executed inside build_v8.py's namespace (after pages_v7), so developers()/investors() are redefined here.
import csv
MGJ = json.load(open(os.path.join(ROOT, "data", "minigrids.json")))
MGS = MGJ["sites"]; OSM = MGJ["osm"]; CAND = MGJ["candidates"]; MGC = MGJ["checks"]
MG_PULLED = datetime.date.fromisoformat(MGJ["pulled"]).strftime("%-d %B %Y")
UID_SLUG = {c["uid"]: c["slug"] for c in I3["communities"]}
SRC_L = {"platform": "SE4ALL platform layer", "eae": "REA data via Energy Access Explorer", "nep": "NEP project map (REA)"}
SRC_LIC = {"platform": "Licence not yet specified on the data portal",
           "eae": "© Rural Electrification Agency; extracts may be published if the source is acknowledged (as stated by Energy Access Explorer)",
           "nep": "No licence stated at source; republishing subject to REA's agreement",
           "osm": "© OpenStreetMap contributors, Open Database Licence (ODbL)"}
SRC_URL = {"platform": PORTAL, "eae": "https://www.energyaccessexplorer.org/", "nep": "https://nep.rea.gov.ng/", "osm": "https://www.openstreetmap.org/"}
STATUS_ORDER = ["Operational / commissioned", "Under construction / approved", "In evaluation", "Not operational", "Not stated"]
MG_KW = sum(s["kw"] or 0 for s in MGS); MG_CONN = sum(s["connections"] or 0 for s in MGS)
MG_STATES = len({s["state"] for s in MGS if s["state"]})
MG_DEVS = len({(s["developer"] or "").strip().lower() for s in MGS if s["developer"]})
BY_STATUS = {k: sum(1 for s in MGS if s["status"] == k) for k in STATUS_ORDER}
ONE_SRC = {k: sum(1 for s in MGS if s["sources"] == [k]) for k in SRC_L}
for s in MGS:
    s["n"] = len(s["source_ids"])
# ---- remap to the field survey (se4allWS:cluster_offgrid_survey is authoritative where a community was surveyed)
# Each survey record is linked to ONE off-grid cluster: the nearest within 2 km (survey -> cluster, not cluster -> survey,
# so a survey is never copied onto neighbouring clusters). Linked sites take the survey's cluster ID and building count;
# survey records with no off-grid cluster within 2 km become sites of their own. The off-grid layer's ID and count are kept.
import numpy as _np
from scipy.spatial import cKDTree as _KD
for c in CAND:
    c.pop("survey_uid", None); c["slug"] = None; c["sv_cid"] = None; c["sv_bld"] = None; c["sv_more"] = 0
    c["bld_layer"] = c["bld"]; c["bsrc"] = "layer"
_cos = math.cos(math.radians(9.0))
_ck = _KD(_np.array([[c["lon"] * _cos * 111.32, c["lat"] * 110.57] for c in CAND]))
_surv = sorted([x for x in I3["communities"] if x["lat"] is not None], key=lambda x: x["uid"])
SURVEY_ONLY = 0; SURVEY_LINKED = 0
for x in _surv:
    d, i = _ck.query([x["lon"] * _cos * 111.32, x["lat"] * 110.57])
    sv_cid = int(x["uid"].split("-")[0]); bld = x["bld"]
    if d <= 2.0:
        c = CAND[i]
        if c["slug"] is None or d < c.get("_svd", 99):
            if c["slug"] is not None: c["sv_more"] += 1
            c.update(slug=x["slug"], sv_cid=sv_cid, sv_bld=bld, _svd=d)
            if bld is not None: c["bld"] = int(bld); c["bsrc"] = "survey"
        else:
            c["sv_more"] += 1
        SURVEY_LINKED += 1
    else:
        mgd = min(((m["lat"] - x["lat"]) ** 2 + ((m["lon"] - x["lon"]) * math.cos(math.radians(x["lat"]))) ** 2, m["id"]) for m in MGS)
        CAND.append(dict(cid=None, state=x["state"], lat=x["lat"], lon=x["lon"], bld=int(bld) if bld is not None else 0, bld_layer=None, bsrc="survey",
                         mv_km=x.get("mv_km"), sub=x.get("sub_name"), sub_km=x.get("sub_km"), mg_id=mgd[1],
                         mg_km=None,
                         schools=x.get("schools"), health=x.get("health"), markets=None, slug=x["slug"], sv_cid=sv_cid, sv_bld=bld, sv_more=0,
                         nesp_name=x["name"], nesp_name_km=0.0))
        SURVEY_ONLY += 1
_mgi = {m["id"]: m for m in MGS}
for c in CAND:
    c.pop("_svd", None)
    if c["cid"] is None and c["mg_id"]:
        m = _mgi[c["mg_id"]]; c["mg_km"] = round(_hav(c["lat"], c["lon"], m["lat"], m["lon"]), 1)
CAND.sort(key=lambda c: -(c["bld"] or 0))
print("survey remap:", SURVEY_LINKED, "linked,", SURVEY_ONLY, "survey-only sites,", sum(1 for c in CAND if c["slug"]), "sites with a survey,", sum(1 for c in CAND if c["sv_more"]), "clusters with more than one survey")
TOP10_NONE = [s for s in inv["top10"] if not any(m["state"] == s for m in MGS)]
# DARES targets as published on nep.rea.gov.ng/dares.html (read 24 Nov 2026)
DARES = dict(minigrids=1225, offgrid=1100, interconnected=125, mw=465, usd_m=750, people_m=17.5)

# demo assumptions (editable on the pages; never presented as REA figures)
DEMO = dict(conn_per_bld=0.7, kwh_day=0.6, yield_=4.5, pr=0.75, capex_kwp=4000, grant_conn=150)

# ---------------------------------------------------------------- data files + open downloads
os.makedirs(os.path.join(OUT, "downloads"), exist_ok=True)
CCOLS = ["cid", "state", "lat", "lon", "bld", "mv_km", "sub_km", "sub", "mg_km", "mg_id", "schools", "health", "markets", "slug", "dre_name", "dre_lga", "dre_pop", "dre_conn", "dre_kwh_day", "dre_pv", "dre_rwi", "nesp_name", "sv_cid", "sv_bld", "sv_more", "bld_layer", "bsrc"]
DRE = MGC.get("dre") or {}
for c in CAND: c["lat"], c["lon"] = round(c["lat"], 5), round(c["lon"], 5)
mgdata = dict(sites=MGS, osm=OSM, ccols=CCOLS, cand=[[c.get(k) for k in CCOLS] for c in CAND], demo=DEMO, dares=DARES,
              srcl=SRC_L, statuses=STATUS_ORDER, apps=APPS,
              subs=[dict(name=x["name"], kv=x["kv"], lat=x["lat"], lon=x["lon"]) for v in X["states"].values() for x in v["substations"]])
open(os.path.join(OUT, "data", "mg-data.js"), "w").write("window.MG=" + json.dumps(mgdata, separators=(",", ":"), ensure_ascii=False) + ";")

def write_csv(path, header_note, cols, rows):
    with open(os.path.join(OUT, "downloads", path), "w", newline="", encoding="utf-8") as f:
        f.write("# " + header_note + "\n"); w = csv.writer(f); w.writerow([c[1] for c in cols])
        for r in rows: w.writerow(["" if r.get(c[0]) is None else (";".join(r[c[0]]) if isinstance(r.get(c[0]), list) else r[c[0]]) for c in cols])
def write_geojson(path, rows, props, note):
    fc = dict(type="FeatureCollection", note=note, features=[dict(type="Feature", geometry=dict(type="Point", coordinates=[r["lon"], r["lat"]]), properties={k: r.get(k) for k in props}) for r in rows])
    json.dump(fc, open(os.path.join(OUT, "downloads", path), "w"), ensure_ascii=False)
MG_COLS = [("id", "Site ID"), ("name", "Name"), ("project_title", "Project title (REA)"), ("developer", "Developer"), ("state", "State"), ("lga", "LGA"), ("kw", "Capacity kW"),
           ("connections", "Connections"), ("status", "Status (normalised)"), ("status_raw", "Status as published"), ("programme", "Programme"), ("system", "System"),
           ("sources", "Sources"), ("source_ids", "Source record IDs"), ("lat", "Latitude"), ("lon", "Longitude")]
MG_NOTE = (f"Nigeria mini-grids, combined from the SE4ALL platform layer, REA data published via Energy Access Explorer and the NEP project map; compiled {MG_PULLED}. "
           "Sources keep their own terms: SE4ALL (licence not yet specified), REA via EAE (extracts may be published with acknowledgement), NEP (no licence stated). Demo concept file.")
write_csv("nigeria-minigrids-combined.csv", MG_NOTE, MG_COLS, MGS)
write_geojson("nigeria-minigrids-combined.geojson", MGS, [c[0] for c in MG_COLS if c[0] not in ("lat", "lon")], MG_NOTE)
C_COLS = [("cid", "Cluster ID (cluster_offgrid_simple)"), ("nesp_name", "Nearest named town/village within 2 km (platform layer towns_villages)"), ("state", "State"), ("lat", "Latitude"), ("lon", "Longitude"), ("bld", "Buildings (survey count where surveyed)"), ("mv_km", "Distance to MV grid km (recalculated)"),
          ("sub", "Nearest substation"), ("sub_km", "Nearest substation km"), ("mg_id", "Nearest recorded mini-grid"), ("mg_km", "Nearest recorded mini-grid km"),
          ("schools", "Schools"), ("health", "Health centres"), ("markets", "Markets"),
          ("sv_cid", "Survey cluster ID (cluster_offgrid_survey)"), ("sv_bld", "Buildings, field survey"), ("bld_layer", "Buildings, off-grid layer"), ("bsrc", "Building count used (survey or layer)"),
          ("dre_name", "Name (World Bank DRE Atlas)"), ("dre_lga", "LGA (DRE Atlas)"), ("dre_pop", "Population (DRE Atlas)"), ("dre_conn", "Potential connections (DRE Atlas)"),
          ("dre_kwh_day", "Estimated demand kWh/day (DRE Atlas)"), ("dre_pv", "PV yield kWh/kWp/year (DRE Atlas)"), ("dre_rwi", "Relative wealth index (DRE Atlas)")]
C_NOTE = f"Off-grid settlements from se4allWS:cluster_offgrid_simple with distances recalculated against se4allWS:distribution_line_mv on {MG_PULLED}. Licence not yet specified on the data portal. DRE Atlas columns: World Bank Distributed Renewable Energy Atlas (VIDA), energydata.info, CC BY 4.0, matched to the nearest DRE settlement within 1 km."
write_csv("nigeria-offgrid-candidate-sites.csv", C_NOTE, C_COLS, CAND)
write_geojson("nigeria-offgrid-candidate-sites.geojson", CAND, [c[0] for c in C_COLS if c[0] not in ("lat", "lon")], C_NOTE)
O_NOTE = "Solar power plants up to 1 MW (or of unknown size) mapped on OpenStreetMap in Nigeria: possible mini-grids. © OpenStreetMap contributors, ODbL 1.0. Kept separate from the combined file because ODbL is share-alike."
write_geojson("osm-solar-plants-nigeria-odbl.geojson", OSM, ["osm", "name", "operator", "kw", "start", "state", "near_known_km"], O_NOTE)
DL = lambda f: f"downloads/{f}"

# ---------------------------------------------------------------- shared pieces
def assumptions_panel(extra=""):
    return f'''<details class="w-assume" id="w-assume"><summary>Indicative figures: demo assumptions <span class="a-pill mid">Demo only</span></summary>
<p class="sm">Sizing and cost figures on this page are worked out in your browser from the assumptions below. They show the logic only; they are not REA or programme figures. Change any value and every figure updates.</p>
<label class="chk" style="font-weight:600;margin:6px 0 10px"><input type="checkbox" data-k="use_wb" checked> Use World Bank DRE Atlas demand and connections where a settlement matched ({f0(DRE.get("matched", 0))} of {f0(len(CAND))} sites)</label>
<div class="w-agrid">
<label>Connections per building<input type="number" step="0.05" min="0" data-k="conn_per_bld" value="{DEMO['conn_per_bld']}"></label>
<label>Demand per connection (kWh/day)<input type="number" step="0.1" min="0" data-k="kwh_day" value="{DEMO['kwh_day']}"></label>
<label>Solar yield (kWh per kWp per day)<input type="number" step="0.1" min="0" data-k="yield_" value="{DEMO['yield_']}"></label>
<label>Performance ratio<input type="number" step="0.05" min="0" max="1" data-k="pr" value="{DEMO['pr']}"></label>
<label>Capital cost (US$ per kWp)<input type="number" step="50" min="0" data-k="capex_kwp" value="{DEMO['capex_kwp']}"></label>
<label>Grant per connection (US$)<input type="number" step="10" min="0" data-k="grant_conn" value="{DEMO['grant_conn']}"></label>
</div>
<p class="w-logic">connections = buildings × connections per building · daily demand = connections × demand per connection · PV size (kWp) = daily demand ÷ (yield × performance ratio) · capital cost = kWp × cost per kWp · grant = connections × grant per connection, capped at the capital cost</p>{extra}</details>'''

def ws_head(crumb, eyebrow, h1, lead):
    return f'''<section class="w-head"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb">{crumb}</nav><div class="w-headrow"><div><span class="a-kick">{eyebrow}</span><h1>{h1}</h1><p>{lead}</p></div>
<div class="w-strip" aria-live="polite"><div><b id="w-n1">—</b><span id="w-l1"></span></div><div><b id="w-n2">—</b><span id="w-l2"></span></div><div><b id="w-n3">—</b><span id="w-l3"></span></div></div></div></div></section>'''

def legend_status():
    return "".join(f'<span><i style="background:{c}"></i>{k}</span>' for k, c in zip(STATUS_ORDER, ["#065F46", "#1E4E79", "#E8A317", "#9F2A2A", "#94A3B8"]))

# ================================================================ MINI-GRID HUB
def minigrid_hub():
    srows = ""
    for k in ("platform", "eae", "nep"):
        n_in = MGC["by_source"][k]; n_sites = sum(1 for s in MGS if k in s["sources"])
        srows += (f'<tr><td><b>{SRC_L[k]}</b><br><a class="a-go" href="{SRC_URL[k]}" style="font-size:14px">{SRC_URL[k].split("//")[1].rstrip("/")}</a></td><td class="n">{n_in}</td><td class="n">{n_sites}</td>'
                  f'<td class="n">{ONE_SRC[k]}</td><td style="font-size:14px">{SRC_LIC[k]}</td></tr>')
    srows += (f'<tr><td><b>OpenStreetMap solar plants</b><br><span class="a-muted" style="font-size:14px">Possible mini-grids, shown separately</span></td><td class="n">{len(OSM)}</td><td class="n">—</td><td class="n">—</td><td style="font-size:14px">{SRC_LIC["osm"]}</td></tr>')
    sopt = '<option value="">All states</option>' + "".join(f'<option>{e(s)}</option>' for s in sorted({m["state"] for m in MGS if m["state"]}))
    stopt = '<option value="">Any status</option>' + "".join(f'<option>{e(s)}</option>' for s in STATUS_ORDER)
    devs = sorted({m["developer"] for m in MGS if m["developer"]}, key=str.lower)
    dopt = '<option value="">All developers</option>' + "".join(f'<option>{e(d)}</option>' for d in devs)
    body = ws_head('<a href="../index.html">Home</a> <span>/</span> <span>Mini-grids</span>', "Mini-grids in Nigeria · one open map",
                   "Every mini-grid we could find, in one place",
                   f"{len(MGS)} sites from three public sources, matched site by site. Filter, click a site to compare what each source says, and download everything.") + f'''
<section class="w-sec"><div class="wrap-wide"><div class="w-grid">
<form class="w-filters" id="h-f" onsubmit="return false"><h3>Filter</h3>
<label for="hq">Search</label><input id="hq" name="q" type="search" placeholder="Site, developer or LGA">
<label for="hs">State</label><select id="hs" name="state">{sopt}</select>
<label for="hst">Status</label><select id="hst" name="status">{stopt}</select>
<label for="hd">Developer</label><select id="hd" name="dev">{dopt}</select>
<fieldset class="w-src"><legend>Highlight by source</legend>
<label><input type="checkbox" name="src" value="platform" checked><i class="s-platform"></i>SE4ALL platform</label>
<label><input type="checkbox" name="src" value="eae" checked><i class="s-eae"></i>REA via Energy Access Explorer</label>
<label><input type="checkbox" name="src" value="nep" checked><i class="s-nep"></i>NEP project map</label>
<label class="w-only"><input type="checkbox" name="only"> Only sites a single source reports</label>
<label><input type="checkbox" name="osm"><i class="s-osm"></i>OpenStreetMap solar plants (possible)</label></fieldset>
<label for="hc">Colour sites by</label><select id="hc" name="colour"><option value="status">Status</option><option value="source">Number of sources</option></select>
<div class="w-dl"><b>Download</b><button type="button" class="btn btn-primary" data-dl="csv">This selection (CSV)</button><button type="button" class="btn btn-outline" data-dl="geojson">This selection (GeoJSON)</button>
<a href="../{DL("nigeria-minigrids-combined.csv")}" download>All {len(MGS)} sites, CSV</a><a href="../{DL("nigeria-minigrids-combined.geojson")}" download>All sites, GeoJSON</a><a href="../{DL("osm-solar-plants-nigeria-odbl.geojson")}" download>OSM solar plants (ODbL)</a></div></form>
<div class="w-mapwrap"><div class="w-map" id="h-map"></div><div class="w-legend" id="h-legend">{legend_status()}</div></div>
<aside class="w-detail" id="h-detail" aria-live="polite"><p class="a-muted">Click a site on the map to see what each source says about it.</p></aside>
</div></div></section>
<section class="sec field" style="padding-top:56px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Sources</span><h2>Where the {len(MGS)} sites come from</h2>
<p class="sub">Records from different sources are treated as one site when each is the other's nearest record within {MGJ["match_m"]/1000:.0f} km. {MGC["multi_source"]} sites are reported by more than one source.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Source</th><th class="n">Records</th><th class="n">Sites</th><th class="n">Only here</th><th>Terms of use</th></tr></thead><tbody>{srows}</tbody></table></div>
<div class="w-facts">
<div><b>{f0(MG_KW)} kW</b><span>recorded capacity ({MG_KW/1000:,.1f} MW) at {sum(1 for s in MGS if s["kw"])} sites with a value</span></div>
<div><b>{f0(MG_CONN)}</b><span>connections reported</span></div>
<div><b>{BY_STATUS["Operational / commissioned"]}</b><span>operational or commissioned · {BY_STATUS["Under construction / approved"]} under construction or approved · {BY_STATUS["In evaluation"]} in evaluation</span></div>
<div><b>{f0(DARES["minigrids"])}</b><span>new mini-grids targeted by DARES ({DARES["offgrid"]:,} off-grid, {DARES["interconnected"]} interconnected) for ${DARES["usd_m"]} million: <a class="a-go" href="https://nep.rea.gov.ng/dares.html">REA</a></span></div>
</div></div></section>
<section class="sec" id="notes"><div class="wrap"><div class="a-split"><div><h2 style="margin-bottom:14px">How this map is made</h2><ul class="a-notes">
<li>Compiled on {MG_PULLED} from the SE4ALL <code>minigrids</code> layer, the REA mini-grid file published by WRI's Energy Access Explorer (content dated 2021) and the NEP project map (list labelled April 2021). Statuses are normalised; the original wording is kept in the download.</li>
<li>When sources disagree (name, capacity, connections), the site panel shows each value. The combined record prefers the SE4ALL layer, then REA via EAE, then NEP.</li>
<li>OpenStreetMap solar plants up to 1 MW are shown as possible mini-grids only. They are not counted, and they are downloadable separately because the ODbL licence is share-alike.</li>
<li>Status dates differ by source and some are years old. Confirm current status with REA or the developer before relying on it.</li></ul></div>
<div><h2 style="margin-bottom:14px">Use it elsewhere</h2>{steps([("Developer workspace", "Find off-grid sites with no mini-grid nearby.", "../for/developers/index.html"), ("Investor workspace", "Build an indicative portfolio by area.", "../for/investors/index.html"), ("Programme projects", "Health facilities, universities and solar home systems.", "../projects/index.html")])}</div></div></div></section>'''
    body += '<script src="../data/mg-data.js"></script>'
    page("minigrids/index.html", "Mini-grids in Nigeria | Nigeria Electrification Atlas", "Nigeria's mini-grids from every open source, matched, mapped and downloadable.", body, "hub")

# ================================================================ DEVELOPER WORKSPACE
def developers():
    sopt = '<option value="">All of Nigeria</option>' + "".join(f'<option>{e(s)}</option>' for s in sorted(states))
    body = ws_head('<a href="../../index.html">Home</a> <span>/</span> <span>Mini-grid developers</span>', "Workspace for mini-grid developers",
                   "Find your next sites", "Every off-grid settlement in Nigeria with its distance to the grid, the nearest mini-grid and what the field teams found. Filter, click, download.") + f'''
<section class="w-sec"><div class="wrap-wide"><div class="w-grid">
<form class="w-filters" id="d-f" onsubmit="return false"><h3>Sites</h3>
<div class="w-modes" role="radiogroup" aria-label="Site type"><label><input type="radio" name="mode" value="offgrid" checked><span>Off-grid</span></label><label><input type="radio" name="mode" value="near"><span>Near grid</span></label><label><input type="radio" name="mode" value="all"><span>All</span></label></div>
<p class="w-hint" id="d-modehint"></p>
<label for="dq">Search by name or LGA</label><input id="dq" name="q" type="search" placeholder="e.g. Gembu, Sardauna">
<label for="ds">State</label><select id="ds" name="state">{sopt}</select>
<label for="db">Buildings</label><div class="w-two"><select id="db" name="bmin" aria-label="Minimum buildings"><option value="0">Any</option><option value="100" selected>100+</option><option value="300">300+</option><option value="500">500+</option><option value="1000">1,000+</option><option value="2000">2,000+</option></select>
<select name="bmax" aria-label="Maximum buildings"><option value="">no maximum</option><option value="500">up to 500</option><option value="1000">up to 1,000</option><option value="2000">up to 2,000</option><option value="5000">up to 5,000</option></select></div>
<label for="dm">No recorded mini-grid within</label><select id="dm" name="mgfree"><option value="0">Any distance</option><option value="2">2 km</option><option value="5" selected>5 km</option><option value="10">10 km</option><option value="20">20 km</option></select>
<label class="chk"><input type="checkbox" name="health"> Has a health centre</label><label class="chk"><input type="checkbox" name="school"> Has a school</label><label class="chk"><input type="checkbox" name="market"> Has a market</label>
<label class="chk"><input type="checkbox" name="surveyed"> Field-surveyed by NESP</label>
<fieldset class="w-src"><legend>Also show</legend><label><input type="checkbox" name="l_mg" checked><i class="s-mg"></i>Existing mini-grids</label><label><input type="checkbox" name="l_mv" checked><i class="s-mv"></i>MV grid (live)</label><label><input type="checkbox" name="l_sub"><i class="s-sub"></i>Substations</label></fieldset>
<div class="w-dl"><b>Download</b><button type="button" class="btn btn-primary" data-dl="csv">These sites (CSV)</button><button type="button" class="btn btn-outline" data-dl="geojson">These sites (GeoJSON)</button>
<a href="../../{DL("nigeria-offgrid-candidate-sites.csv")}" download>All {f0(len(CAND))} off-grid settlements, CSV</a><a id="d-webmap" href="{APPS}minigrid-offgrid" target="_blank" rel="noopener">Open in the off-grid webmap {EXT}</a></div></form>
<div class="w-mapwrap"><div class="w-map" id="d-map"></div><div class="w-legend"><span><i style="background:#B7791F"></i>Matching site</span><span><i style="background:#065F46"></i>Existing mini-grid</span><span><i class="sq"></i>Substation</span></div></div>
<aside class="w-detail" id="d-detail" aria-live="polite"><p class="a-muted">Click a site to see its facts, the nearest grid and mini-grid, and an indicative system size.</p></aside>
</div></div></section>
<section class="sec field" style="padding-top:48px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">The list</span><h2>Largest matching sites</h2><p class="sub">The 50 largest sites for your filters. Click a row to show it on the map.</p></div></div>
<div class="a-tbl"><table class="a-t" id="d-t"><thead><tr><th>Site</th><th>State</th><th class="n">Buildings</th><th class="n">To MV grid</th><th class="n">To nearest mini-grid</th><th>Services</th><th class="n">Indicative kWp</th></tr></thead><tbody></tbody></table></div>
{assumptions_panel()}</div></section>
<section class="sec" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How this workspace is made</h2><ul class="a-notes">
<li>Sites: the {f0(len(CAND))} settlements in SE4ALL's off-grid settlement layer (<code>cluster_offgrid_simple</code>). "Off-grid" means more than 5 km from the field-mapped MV grid; "near grid" means 5 km or less (interconnection or grid-extension candidates). Distances recalculated on {MG_PULLED}.</li>
<li>Nearest mini-grid uses the combined list of {len(MGS)} sites on the <a class="a-go" href="../../minigrids/index.html">mini-grid map</a>. Schools, health centres and markets are as recorded in the settlement layer.</li>
<li>"Field-surveyed" means a community in the NESP field survey lies within 2 km; its full record is one click away.</li>
<li>Settlement names, population and estimated demand come from the World Bank's <a class="a-go" href="https://energydata.info/dataset/nigeria-distributed-renewable-energy-dre">Distributed Renewable Energy Atlas for Nigeria</a> (VIDA; CC BY 4.0), matched to the nearest DRE settlement within 1 km ({f0(DRE.get("matched", 0))} of {f0(len(CAND))} sites). Where there is no match, demand comes from the demo assumptions.</li>
<li>Indicative kWp and costs are demo calculations from the assumptions above, not REA figures.</li></ul></div></section>'''
    body += '<script src="../../data/mg-data.js"></script>'
    page("for/developers/index.html", "Developer workspace | Nigeria Electrification Atlas", "Find, filter and download off-grid mini-grid sites in Nigeria.", body, "dev8")

# ================================================================ INVESTOR WORKSPACE
def investors():
    sopt = '<option value="">Choose a state…</option>' + "".join(f'<option>{e(s)}</option>' for s in sorted(states))
    body = ws_head('<a href="../../index.html">Home</a> <span>/</span> <span>Investors</span>', "Workspace for investors and financiers",
                   "Size an opportunity in a few clicks", "Pick an area on the map. The workspace counts the off-grid sites without a mini-grid, sorts them into bands and works out an indicative portfolio.") + f'''
<section class="w-sec"><div class="wrap-wide"><div class="w-grid">
<form class="w-filters" id="i-f" onsubmit="return false"><h3>Your area</h3>
<div class="w-modes" role="radiogroup" aria-label="Area"><label><input type="radio" name="area" value="state" checked><span>A state</span></label><label><input type="radio" name="area" value="circle"><span>A radius</span></label></div>
<div id="i-state-box"><label for="is">State</label><select id="is" name="state">{sopt}</select><p class="w-hint">Or click a state on the map.</p></div>
<div id="i-circle-box" hidden><label for="ir">Radius around the point you click</label><select id="ir" name="radius"><option>10</option><option selected>25</option><option>50</option><option>100</option></select><p class="w-hint">Click anywhere on the map to set the centre.</p></div>
<label for="ib">Smallest site to include</label><select id="ib" name="bmin"><option value="100">100+ buildings</option><option value="300" selected>300+ buildings</option><option value="500">500+ buildings</option><option value="1000">1,000+ buildings</option></select>
<label for="im">Treat as already served if a mini-grid is within</label><select id="im" name="served"><option value="2">2 km</option><option value="5" selected>5 km</option><option value="10">10 km</option></select>
<label for="ic">Colour states by</label><select id="ic" name="colour"><option value="gap">Off-grid buildings per recorded kW</option><option value="sites">Unserved off-grid sites</option></select>
<div class="w-dl"><b>Download</b><button type="button" class="btn btn-primary" data-dl="csv">Portfolio sites (CSV)</button><button type="button" class="btn btn-outline" data-dl="geojson">Portfolio sites (GeoJSON)</button><a href="../../minigrids/index.html">All mini-grids</a></div></form>
<div class="w-mapwrap"><div class="w-map" id="i-map"></div><div class="w-legend" id="i-legend"></div></div>
<aside class="w-detail" id="i-detail" aria-live="polite"><p class="a-muted">Choose a state or click the map to build an indicative portfolio.</p></aside>
</div></div></section>
<section class="sec field" style="padding-top:48px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Investment bands</span><h2>How sites are banded</h2><p class="sub">Physical indicators from the platform's data; the money figures in the portfolio come from the demo assumptions below.</p></div></div>
<div class="w-bands">
<div><b class="b-a">A · Field-verified</b><span>More than 5 km from the grid, not served, and a NESP field survey within 2 km.</span></div>
<div><b class="b-b">B · Large off-grid</b><span>More than 5 km from the grid, not served, 1,000+ buildings.</span></div>
<div><b class="b-c">C · Mid-size off-grid</b><span>More than 5 km from the grid, not served, below 1,000 buildings.</span></div>
<div><b class="b-d">D · Near grid</b><span>Within 5 km of the MV grid: interconnected mini-grid or grid extension, with the DisCo.</span></div>
<div><b class="b-s">Served</b><span>A recorded mini-grid already lies within the distance you choose.</span></div></div>
{assumptions_panel()}</div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">All states</span><h2>Where the unserved off-grid sites are</h2><p class="sub">Using your current filters. Click a column to re-sort or a state to load it.</p></div></div>
<div class="a-tbl"><table class="a-t" id="i-t"><thead><tr><th>State</th><th class="n">Unserved off-grid sites</th><th class="n">Buildings in them</th><th class="n">Recorded mini-grids</th><th class="n">Recorded kW</th><th class="n">Pipeline (evaluation or construction)</th><th class="n">Indicative capex (US$ m, demo)</th></tr></thead><tbody></tbody></table></div></div></section>
<section class="sec field" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How this workspace is made</h2><ul class="a-notes">
<li>Sites: SE4ALL off-grid settlements with distances recalculated against the field-mapped MV grid on {MG_PULLED}. Mini-grids: the combined list of {len(MGS)} sites from three public sources; see the <a class="a-go" href="../../minigrids/index.html">mini-grid map</a> for sources and terms.</li>
<li>"Off-grid buildings per recorded kW" compares the buildings in off-grid settlements with recorded mini-grid capacity in the state. Higher means more unmet demand per kW already built. Recorded capacity is incomplete, so treat it as a first screen.</li>
<li>For context, DARES targets {f0(DARES["minigrids"])} new mini-grids and ${DARES["usd_m"]} million of finance (<a class="a-go" href="https://nep.rea.gov.ng/dares.html">REA</a>).</li>
<li>Settlement names, population and estimated demand come from the World Bank's <a class="a-go" href="https://energydata.info/dataset/nigeria-distributed-renewable-energy-dre">Distributed Renewable Energy Atlas for Nigeria</a> (VIDA; CC BY 4.0), matched to the nearest DRE settlement within 1 km ({f0(DRE.get("matched", 0))} of {f0(len(CAND))} sites). Where there is no match, demand comes from the demo assumptions.</li>
<li>All money and kWp figures are demo calculations from the assumptions above. They show the method; they are not REA estimates.</li></ul></div></section>'''
    body += '<script src="../../data/mg-data.js"></script>'
    pdata = dict(stats={s: dict(off=d["offgrid_buildings"]) for s, d in states.items()})
    page("for/investors/index.html", "Investor workspace | Nigeria Electrification Atlas", "Indicative mini-grid portfolios by state or area, from Nigeria's open electrification data.", body, "inv8", pdata)

def minigrid_strip():
    return f'''<section class="sec" id="projects"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Mini-grids · open data</span><h2>Every mini-grid we could find, on one map</h2>
<p class="sub">Three public sources matched site by site, with {f0(len(CAND))} off-grid settlements to compare them against. Free to filter and download.</p></div><a class="link" href="minigrids/index.html">Open the mini-grid map {SVG_ARROW}</a></div>
<div class="a-pstrip">
<a class="a-pcell" href="minigrids/index.html"><b>{len(MGS)}</b><span>mini-grid sites</span><small>from {len(SRC_L)} sources · {MG_STATES} states</small></a>
<a class="a-pcell" href="minigrids/index.html"><b>{MG_KW/1000:,.1f} MW</b><span>recorded capacity</span><small>{f0(MG_CONN)} connections reported</small></a>
<a class="a-pcell" href="for/developers/index.html"><b>{f0(sum(1 for c in CAND if c["mv_km"] > 5 and c["mg_km"] > 5))}</b><span>off-grid settlements</span><small>more than 5 km from the grid and from any recorded mini-grid</small></a>
<a class="a-pcell" href="for/investors/index.html"><b>{f0(DARES["minigrids"])}</b><span>new mini-grids targeted</span><small>by DARES, ${DARES["usd_m"]} million (REA)</small></a>
</div><p class="a-next">Build an indicative portfolio in the <a class="a-go" href="for/investors/index.html">investor workspace</a>, or find sites in the <a class="a-go" href="for/developers/index.html">developer workspace</a>. Programme projects (health, universities, solar home systems) are on the <a class="a-go" href="projects/index.html">projects page</a>.</p></div></section>'''
