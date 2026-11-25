# v9: interactive field survey (icon profiles + statistics), two developer site finders (NESP data only vs World Bank DRE)
# and a comparison page. Executed inside build_v9.py's namespace after pages_v8.
from icons_sv import SV_ICONS
import statistics

def _tf(v): return 1 if str(v) == "True" else (0 if str(v) == "False" else None)
def _num(v):
    try:
        x = float(str(v).replace("%", "").replace(",", "").strip()); return None if x != x else (int(x) if x.is_integer() else round(x, 1))
    except (TypeError, ValueError): return None
def _acc(v): return {"all_year_round": "all", "dry_season_only": "dry", "dry_season": "dry", "never": "never"}.get(str(v))
def _net(v): return {"2G": "2G", "3G": "3G", "4G": "4G", "5G": "5G", "not_available": "none"}.get(str(v))
CROPS = ["millet", "guinea_corn", "groundnut", "maize", "rice", "beans", "pepper", "sweet_potatoes", "hibiscus_leaf", "sesame_seed", "cassava", "cashew", "yam", "cocoa"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_mgxy = [(m["lat"], m["lon"], m["name"] or m["id"]) for m in MGS]
SV_ROWS = []
for c in I3["communities"]:
    r = SURVEY.get(c["uid"], {})
    ready = c["grid"] == "no" and (c["bld"] or 0) >= N3["criteria"]["min_buildings"] and (c["bz_gen"] or 0) >= N3["criteria"]["min_business_genset_pct"] and c["all_year"] and (c["mobile_money"] or c["data_3g4g"])
    crops = []
    for k in ("crop_cultivated_primary", "crop_cultivated_secondary", "crop_cultivated_third", "crop_cultivated_fourth"):
        v = r.get(k)
        if v and str(v) not in ("None", "nan", "unknown") and str(v).lower() not in [x.lower() for x in crops]: crops.append(str(v).strip().lower())
    for k in CROPS:
        nm = k.replace("_", " ")
        if str(r.get(f"crop_cultivated_{k}")) == "True" and nm not in crops: crops.append(nm)
    mgk = mgn = None
    if c["lat"] is not None:
        best = min(_mgxy, key=lambda q: (q[0] - c["lat"]) ** 2 + ((q[1] - c["lon"]) * math.cos(math.radians(c["lat"]))) ** 2)
        mgk = round(_hav(c["lat"], c["lon"], best[0], best[1]), 1); mgn = best[2]
    crafts = sum(_num(r.get(k)) or 0 for k in ("count_craft_carpenter", "count_craft_welder", "count_craft_vulcanizer", "count_craft_car_repair", "count_craft_bike_repair", "count_craft_generator_repair", "count_craft_shoemaker", "count_craft_other"))
    inc = [str(r.get(k)).strip() for k in ("income_source_primary", "income_source_secondary", "income_source_third") if r.get(k) and str(r.get(k)) not in ("None", "nan", "unknown")]
    SV_ROWS.append(dict(
        id=c["slug"], u=c["uid"], n=c["name"], l=c["lga"], s=c["state"], la=c["lat"], lo=c["lon"], y=c["year"], d=str(r.get("survey_date") or "")[:10],
        g={"no": "no", "yes_connected_national_grid": "c", "yes_not_connected_national_grid": "nc"}.get(c["grid"]), nf=bool(c["never_functional"]),
        gy=_num(r.get("grid_year_built")), tr=_tf(r.get("grid_transformer_presence")), mgp=_tf(r.get("mini_grid_presence")),
        hh=_num(r.get("households_with_genset_percentage")), bz=_num(r.get("businesses_with_genset_percentage")),
        pe=_num(r.get("petrol_price_ngn_per_litre")), di=_num(r.get("diesel_price_ngn_per_litre")), ke=_num(r.get("kerosene_price_ngn_per_litre")), ps=_tf(r.get("petrol_station_in_community")),
        i1=inc[0] if inc else None, i2=inc[1] if len(inc) > 1 else None, i3=inc[2] if len(inc) > 2 else None,
        mi=_num(r.get("count_productive_use_grinding_mills")), op=_num(r.get("count_productive_use_oil_press")), sh=_num(r.get("count_commercial_shop_kiosk")),
        po=_num(r.get("count_commercial_pos_shop")), ph=_num(r.get("count_commercial_phone_charging")), cr=crafts,
        he=_num(r.get("count_health_facilities")), p1=_num(r.get("count_primary_schools")), p2=_num(r.get("count_secondary_schools")),
        mm=_tf(r.get("mobile_money_available")), ba=_tf(r.get("banks_available")),
        mtn=_net(r.get("network_mtn")), air=_net(r.get("network_airtel")), glo=_net(r.get("network_glo")), nm=_net(r.get("network_9mobile")),
        tk=_acc(r.get("accessibility_truck")), x4=_acc(r.get("accessibility_4x4_car")), sc=_acc(r.get("accessibility_saloon_car")), mb=_acc(r.get("accessibility_motorbike")),
        cp=crops, md=[d[:3].capitalize() for d in DAYS if str(r.get(f"market_{d}")) == "True"],
        b=c["bld"] if c["bld"] is not None else _num(r.get("building_count")), mv=c.get("mv_km"), sub=c.get("sub_name"), sk=c.get("sub_km"), mgn=mgn, mgk=mgk, rd=bool(ready)))
open(os.path.join(OUT, "data", "survey-data.js"), "w").write("window.SV=" + json.dumps(dict(rows=SV_ROWS, icons=SV_ICONS), separators=(",", ":"), ensure_ascii=False, allow_nan=False) + ";")
SV_LATEST = max(r["y"] for r in SV_ROWS)

# ---------------------------------------------------------------- the survey explorer (replaces communities_index)
def communities_index():
    sopt = '<option value="">All states</option>' + "".join(f'<option>{e(s)}</option>' for s in sorted({r["s"] for r in SV_ROWS if r["s"]}))
    years = sorted({r["y"] for r in SV_ROWS})
    yopt = '<option value="">All years</option>' + "".join(f'<option>{y}</option>' for y in years)
    body = ws_head('<a href="../index.html">Home</a> <span>/</span> <span>Field survey</span>', "Ground truth · NESP field survey",
                   f"Inside {len(SV_ROWS)} communities, as the field teams found them",
                   "Grid, generators, fuel prices, businesses, services, signal, roads and crops, about 100 facts per community. Filter, click any community, and compare.") + f'''
<section class="w-sec"><div class="wrap-wide"><div class="w-grid">
<form class="w-filters" id="sv-f" onsubmit="return false"><h3>Filter</h3>
<label for="svq">Search</label><input id="svq" name="q" type="search" placeholder="Community or LGA">
<label for="svs">State</label><select id="svs" name="state">{sopt}</select>
<label for="svg">Grid at survey</label><select id="svg" name="grid"><option value="">Any</option><option value="no">No grid</option><option value="nc">Grid present, not connected</option><option value="c">Connected</option><option value="nf">Grid that never worked</option></select>
<label for="svy">Survey year</label><select id="svy" name="year">{yopt}</select>
<fieldset class="w-src"><legend>Has</legend>
<label><input type="checkbox" name="health"><span class="sv-ic sm">{SV_ICONS["health"]}</span>Health facility</label>
<label><input type="checkbox" name="school"><span class="sv-ic sm">{SV_ICONS["school"]}</span>School</label>
<label><input type="checkbox" name="mill"><span class="sv-ic sm">{SV_ICONS["mill"]}</span>Grinding mill</label>
<label><input type="checkbox" name="mm"><span class="sv-ic sm">{SV_ICONS["money"]}</span>Mobile money</label>
<label><input type="checkbox" name="g34"><span class="sv-ic sm">{SV_ICONS["signal"]}</span>3G or 4G signal</label>
<label><input type="checkbox" name="truck"><span class="sv-ic sm">{SV_ICONS["truck"]}</span>Year-round truck access</label>
<label><input type="checkbox" name="ready"><span class="sv-ic sm">{SV_ICONS["sun"]}</span>Meets build-ready criteria</label></fieldset>
<label for="svc">Colour communities by</label><select id="svc" name="colour"><option value="grid">Grid at survey</option><option value="bz">Businesses on generators</option></select>
<div class="w-dl"><b>Download</b><button type="button" class="btn btn-primary" id="sv-csv">This selection (CSV)</button><a href="{PORTAL}" target="_blank" rel="noopener">Full layer on the data portal {EXT}</a></div></form>
<div class="w-mapwrap"><div class="w-map" id="sv-map"></div><div class="w-legend" id="sv-legend"></div></div>
<aside class="w-detail" id="sv-detail" aria-live="polite"></aside>
</div></div></section>
<section class="sec field" style="padding-top:48px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">The list</span><h2>Communities in this selection</h2><p class="sub">The 60 largest; the download has them all. Open any community for its full record.</p></div></div>
<div class="a-tbl"><table class="a-t" id="sv-t"><thead><tr><th>Community</th><th>State</th><th>Grid at survey</th><th class="n">Buildings</th><th class="n">Businesses on generators</th><th class="n">Health facilities</th><th class="n">Surveyed</th></tr></thead><tbody></tbody></table></div></div></section>
<section class="sec" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">About the survey</h2><ul class="a-notes">
<li>Source: <code>se4allWS:cluster_offgrid_survey</code> ({len(SV_ROWS)} communities; {", ".join(f"{y}: {sum(1 for r in SV_ROWS if r['y'] == y)}" for y in years)}). Shown as published; conditions may have changed since the visit.</li>
<li>Fuel prices are compared with the median of communities surveyed in the same year, because prices rose sharply between 2022 and 2026.</li>
<li>Nearest MV line, substation and mini-grid are recalculated against the current layers and the combined mini-grid list.</li>
<li>The grey tick on each generator bar marks the survey-wide median.</li></ul></div></section>'''
    body += '<script src="../data/survey-data.js"></script>'
    page("communities/index.html", "Field survey | Nigeria Electrification Atlas", f"Explore {len(SV_ROWS)} field-surveyed Nigerian communities: grid, generators, fuel, businesses, services and access.", body, "survey9")

# ---------------------------------------------------------------- community pages get the icon profile
SLUG_UID = {r["id"]: r for r in SV_ROWS}
_page_v8 = page
def page(path, title, desc, body, kind, pdata=None):
    if kind == "community":
        slug_ = path.split("/")[1]
        mark = '<section class="sec field" style="padding-top:56px">'
        if slug_ in SLUG_UID and mark in body:
            body = body.replace(mark, f'<section class="sec sv-psec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">At a glance</span><h2>What the field team found</h2></div></div><div id="sv-profile" class="sv-profile" data-id="{slug_}"></div></div></section>\n' + mark, 1)
            body += f'<script src="../../data/survey-data.js"></script>'
    return _page_v8(path, title, desc, body, kind, pdata)

# ---------------------------------------------------------------- developer site finders: NESP data only (main) and World Bank DRE
_developers_v8 = developers
def developers_wb():
    global page
    inner = page
    def moved(path, title, desc, body, kind, pdata=None):
        body = body.replace('"../../', '"../../../').replace("'../../", "'../../../")
        body = body.replace('<span class="a-kick">Workspace for mini-grid developers</span>', '<span class="a-kick">Site finder · with World Bank DRE Atlas data</span>')
        body = body.replace('<a href="../../../index.html">Home</a> <span>/</span> <span>Mini-grid developers</span>',
                            '<a href="../../../index.html">Home</a> <span>/</span> <a href="../index.html">Mini-grid developers</a> <span>/</span> <span>World Bank DRE version</span>')
        body += '<script src="../../../data/survey-data.js"></script>'
        pd = dict(pdata or {}); pd["variant"] = "wb"
        return inner("for/developers/world-bank/index.html", "Site finder with World Bank DRE data | Nigeria Electrification Atlas", desc, body + COMPARE_BAR("wb"), "dev8", pd)
    page = moved
    try: _developers_v8()
    finally: page = inner

def COMPARE_BAR(which, root="../../../"):
    other = ("world-bank/index.html", "World Bank DRE version") if which == "own" else ("../index.html", "NESP data version")
    cmpu = "compare/index.html" if which == "own" else "../compare/index.html"
    return f'''<div class="cmp-bar" role="note"><span><b>{"NESP data only" if which == "own" else "With World Bank DRE Atlas data"}</b> · Two versions of this site finder for the client to compare.</span><a href="{other[0]}">Switch to the {other[1]}</a><a href="{cmpu}">How they differ</a></div>'''

def developers():
    sopt = '<option value="">All of Nigeria</option>' + "".join(f'<option>{e(s)}</option>' for s in sorted(states))
    named = MGC["towns"]["named_candidates"]
    body = ws_head('<a href="../../index.html">Home</a> <span>/</span> <span>Mini-grid developers</span>', "Site finder · NESP data",
                   "Find your next site", "Every off-grid settlement on the platform with its distance to the grid and the nearest mini-grid, and, where our field teams visited, what they found. Filter, click, download.") + f'''
<section class="w-sec"><div class="wrap-wide"><div class="w-grid">
<form class="w-filters" id="d-f" onsubmit="return false"><h3>Sites</h3>
<div class="w-modes" role="radiogroup" aria-label="Site type"><label><input type="radio" name="mode" value="offgrid" checked><span>Off-grid</span></label><label><input type="radio" name="mode" value="near"><span>Near grid</span></label><label><input type="radio" name="mode" value="all"><span>All</span></label></div>
<p class="w-hint" id="d-modehint"></p>
<label for="dq">Search by place name</label><input id="dq" name="q" type="search" placeholder="Town, village or cluster ID">
<label for="ds">State</label><select id="ds" name="state">{sopt}</select>
<label for="db">Buildings</label><div class="w-two"><select id="db" name="bmin" aria-label="Minimum buildings"><option value="0">Any</option><option value="100" selected>100+</option><option value="300">300+</option><option value="500">500+</option><option value="1000">1,000+</option><option value="2000">2,000+</option></select>
<select name="bmax" aria-label="Maximum buildings"><option value="">no maximum</option><option value="500">up to 500</option><option value="1000">up to 1,000</option><option value="2000">up to 2,000</option><option value="5000">up to 5,000</option></select></div>
<label for="dm">No recorded mini-grid within</label><select id="dm" name="mgfree"><option value="0">Any distance</option><option value="2">2 km</option><option value="5" selected>5 km</option><option value="10">10 km</option><option value="20">20 km</option></select>
<label class="chk"><input type="checkbox" name="health"> Has a health centre</label><label class="chk"><input type="checkbox" name="school"> Has a school</label><label class="chk"><input type="checkbox" name="market"> Has a market</label>
<fieldset class="w-src"><legend>Field survey</legend>
<label><input type="checkbox" name="surveyed"><span class="sv-ic sm">{SV_ICONS["pin"]}</span>Field-surveyed only</label>
<label><input type="checkbox" name="sv_gen"><span class="sv-ic sm">{SV_ICONS["gen"]}</span>Half of businesses on generators</label>
<label><input type="checkbox" name="sv_pay"><span class="sv-ic sm">{SV_ICONS["money"]}</span>Mobile money available</label>
<label><input type="checkbox" name="sv_road"><span class="sv-ic sm">{SV_ICONS["truck"]}</span>Year-round truck or 4x4</label>
<label><input type="checkbox" name="sv_mill"><span class="sv-ic sm">{SV_ICONS["mill"]}</span>Grinding mill on site</label></fieldset>
<fieldset class="w-src"><legend>Also show</legend><label><input type="checkbox" name="l_mg" checked><i class="s-mg"></i>Existing mini-grids</label><label><input type="checkbox" name="l_mv" checked><i class="s-mv"></i>MV grid (live)</label><label><input type="checkbox" name="l_sub"><i class="s-sub"></i>Substations</label></fieldset>
<div class="w-dl"><b>Download</b><button type="button" class="btn btn-primary" data-dl="csv">These sites (CSV)</button><button type="button" class="btn btn-outline" data-dl="geojson">These sites (GeoJSON)</button>
<a href="../../{DL("nigeria-offgrid-candidate-sites.csv")}" download>All {f0(len(CAND))} off-grid settlements, CSV</a><a id="d-webmap" href="{APPS}minigrid-offgrid" target="_blank" rel="noopener">Open in the off-grid webmap {EXT}</a></div></form>
<div class="w-mapwrap"><div class="w-map" id="d-map"></div><div class="w-legend"><span><i style="background:#B7791F"></i>Matching site</span><span><i style="background:#D9480F"></i>Field-surveyed site</span><span><i style="background:#065F46"></i>Existing mini-grid</span><span><i class="sq"></i>Substation</span></div></div>
<aside class="w-detail" id="d-detail" aria-live="polite"><p class="a-muted">Click a site to see its facts and, where our teams visited, the field-survey profile.</p></aside>
</div></div></section>
<section class="sec field" style="padding-top:48px"><div class="wrap"><div class="sec-head"><div><span class="a-kick">The list</span><h2>Largest matching sites</h2><p class="sub">The 50 largest sites for your filters. Click a row to show it on the map.</p></div></div>
<div class="a-tbl"><table class="a-t" id="d-t"><thead><tr><th>Site</th><th>State</th><th class="n">Buildings</th><th class="n">To MV grid</th><th class="n">To nearest mini-grid</th><th>Services</th><th class="n">Indicative kWp</th></tr></thead><tbody></tbody></table></div>
{assumptions_panel().replace('<label class="chk" style="font-weight:600;margin:6px 0 10px"><input type="checkbox" data-k="use_wb" checked>', '<label class="chk" style="display:none"><input type="checkbox" data-k="use_wb">')}</div></section>
<section class="sec" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">How this site finder is made</h2><ul class="a-notes">
<li>Only the platform's own data: the {f0(len(CAND))} settlements in <code>cluster_offgrid_simple</code> (buildings, schools, health centres, markets), distances recalculated against <code>distribution_line_mv</code>, substations, place names from <code>towns_villages</code> ({f0(named)} sites have a named town or village within 2 km) and the NESP field survey (<code>cluster_offgrid_survey</code>, {len(SV_ROWS)} communities).</li>
<li>The field survey is authoritative where it exists: each survey record is linked to its nearest off-grid cluster within 2 km and that site shows the survey's cluster ID and building count (the off-grid layer's ID and count are shown alongside). {SURVEY_ONLY} surveyed communities with no off-grid cluster within 2 km are added as sites of their own.</li>
<li>Nearest mini-grid uses the combined list of {len(MGS)} sites on the <a class="a-go" href="../../minigrids/index.html">mini-grid map</a>.</li>
<li>Indicative kWp and costs are demo calculations from buildings and the assumptions above, not REA figures. A version that uses the World Bank's demand estimates is <a class="a-go" href="world-bank/index.html">here</a>.</li></ul></div></section>'''
    body += '<script src="../../data/mg-data.js"></script><script src="../../data/survey-data.js"></script>'
    page("for/developers/index.html", "Site finder | Nigeria Electrification Atlas", "Find off-grid mini-grid sites in Nigeria from the platform's own data and field survey.", body + COMPARE_BAR("own"), "dev8", dict(variant="own"))
    developers_wb()

# ---------------------------------------------------------------- comparison page
def compare_page():
    wb = MGC.get("dre") or {}; named = MGC["towns"]["named_candidates"]; sv_n = sum(1 for c in CAND if c.get("slug"))
    ex = sorted([c for c in CAND if c.get("dre_name") and c.get("nesp_name") and c.get("dre_kwh_day")], key=lambda c: -c["bld"])[:6]
    extr = "".join(f'<tr><td><b>{e(c["dre_name"])}</b><br><span class="a-muted">{e(c["dre_lga"] or "")}, {e(c["state"])}</span></td><td>{e(c["nesp_name"])}</td><td class="n">{f0(c["bld"])}</td><td class="n">{f0(c["dre_conn"])}</td><td class="n">{f0(c["dre_pop"])}</td><td class="n">{f0(c["dre_kwh_day"])}</td></tr>' for c in ex)
    rows = [
        ("Sites covered", f"{f0(len(CAND))} off-grid settlements", f"Same {f0(len(CAND))} settlements, {f0(wb.get('matched', 0))} matched to a World Bank settlement ({100*wb.get('matched', 0)/len(CAND):.0f}%)"),
        ("Place names", f"{f0(named)} sites ({100*named/len(CAND):.0f}%) from the platform's towns and villages layer", f"{f0(wb.get('matched', 0))} sites ({100*wb.get('matched', 0)/len(CAND):.0f}%) from the DRE Atlas (reverse geocoding)"),
        ("Size of a site", "Buildings counted in the SE4ALL settlement layer", "Also population and potential connections, modelled from building footprints (VIDA)"),
        ("Demand", "Not in the data: worked out from buildings and editable demo assumptions", "World Bank estimate of kWh per day for each settlement; costs still use demo assumptions"),
        ("Ground truth", f"{len(SV_ROWS)} field-surveyed communities (generators, fuel prices, businesses, services, signal, roads, crops); {f0(sv_n)} sites carry a survey, using the survey's cluster ID and building count", "None of its own; the field-survey link is kept where a survey exists"),
        ("Grid distance", "Recalculated against the field-mapped MV grid", "Same (the DRE Atlas uses transmission lines, so we keep the platform's MV distance)"),
        ("Freshness", "Settlement layer as on the portal; survey mostly 2022, some 2026", "DRE Atlas release of June 2025"),
        ("Terms of use", "Platform data: licence not yet specified", "CC BY 4.0: free to reuse with attribution to the World Bank"),
        ("Who maintains it", "NESP / REA, updated through the platform", "World Bank and VIDA, outside the platform's control"),
    ]
    tr = "".join(f'<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows)
    body = phero('<a href="../../../index.html">Home</a> <span>/</span> <a href="../index.html">Mini-grid developers</a> <span>/</span> <span>Compare</span>', "Site finder · two versions",
                 "NESP data or World Bank data: how the two site finders differ",
                 "Both versions show the same off-grid settlements, grid distances and mini-grids. They differ in names, demand and ground truth.",
                 '<div class="hero-cta" style="opacity:1;animation:none;margin-top:22px"><a class="btn btn-leaf" href="../index.html">Open the NESP data version</a><a class="btn btn-ghost" href="../world-bank/index.html">Open the World Bank version</a></div>') + f'''
<section class="sec"><div class="wrap"><div class="a-tbl"><table class="a-t cmp-t"><thead><tr><th></th><th>NESP data only</th><th>With World Bank DRE Atlas</th></tr></thead><tbody>{tr}</tbody></table></div></div></section>
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Same place, two sources</span><h2>How the numbers compare for large sites</h2><p class="sub">The six largest settlements that both sources name. Buildings come from the platform; connections, population and demand from the DRE Atlas.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>DRE Atlas name</th><th>Platform name</th><th class="n">Buildings (platform)</th><th class="n">Connections (DRE)</th><th class="n">Population (DRE)</th><th class="n">Demand kWh/day (DRE)</th></tr></thead><tbody>{extr}</tbody></table></div></div></section>
<section class="sec" id="notes"><div class="wrap"><div class="a-split"><div><h2 style="margin-bottom:14px">What is hard</h2><ul class="a-notes">
<li><b>Names.</b> The platform's settlement layer has no names, and the towns and villages layer names only {100*named/len(CAND):.0f}% of sites; the DRE Atlas names {100*wb.get('matched', 0)/len(CAND):.0f}%. Without names, developers cannot search for a place they already know.</li>
<li><b>Two definitions of a settlement.</b> The two sources draw settlement boundaries differently, so building counts and connections disagree, sometimes by a lot. Records are matched to the nearest settlement within 1 km; {f0(len(CAND) - wb.get('matched', 0))} sites have no match.</li>
<li><b>Demand is modelled either way.</b> The DRE Atlas estimates demand from buildings with its own assumptions; it is consistent across Nigeria but not field-verified.</li>
<li><b>The survey covers few sites.</b> {len(SV_ROWS)} communities were surveyed, mostly in 2022, in 20 states; only {f0(sv_n)} of {f0(len(CAND))} sites ({100*sv_n/len(CAND):.0f}%) carry one.</li>
<li><b>Two ID systems.</b> The survey layer numbers its clusters separately from the off-grid settlement layer (no shared ID), so surveys are linked by location, and building counts differ for some 2026 surveys (e.g. Burari: 1,347 surveyed, 1,447 in the off-grid layer).</li>
<li><b>Data ownership.</b> The World Bank data is CC BY 4.0 and can be reused with attribution, but REA cannot correct or update it. The platform's own data still has no licence set.</li></ul></div>
<div><h2 style="margin-bottom:14px">A possible way forward</h2><ul class="a-notes"><li>Use the DRE Atlas for names, population and first-cut demand, and the platform for grid distance, mini-grids and field survey, as one site finder.</li><li>Add place names to the platform's settlement layer at source.</li><li>Prioritise new field surveys in large unserved sites, so ground truth grows where developers look.</li></ul></div></div></div></section>'''
    page("for/developers/compare/index.html", "Site finder: two versions compared | Nigeria Electrification Atlas", "NESP data vs World Bank DRE Atlas site finders.", body, "compare")
