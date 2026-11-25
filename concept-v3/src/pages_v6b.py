# v6 pages and homepage sections. Executed inside build_v6.py's namespace.
DC = NAT2["distance_check"]
SURV = I3["communities"]
COMM_BY_UID = {c["uid"]: c for c in SURV}
surveyed_states = sorted({c["state"] for c in SURV if c["state"]})
no_survey_states = sorted(s for s in states if s not in surveyed_states)

def nice(v):
    if v is None: return None
    if isinstance(v, bool) or str(v) in ("True", "False"): return "Yes" if str(v) == "True" else "No"
    s = str(v).strip()
    if s in ("", "nan", "None", "null"): return None
    if s.endswith(".0") and s[:-2].lstrip("-").isdigit(): s = s[:-2]
    return s.replace("_", " ").replace("yes connected national grid", "yes, connected to national grid").replace("yes not connected national grid", "yes, not connected to national grid")

GROUPS = [
    ("Energy today", [("grid_presence", "Grid at survey"), ("grid_voltage", "Grid voltage"), ("grid_functionality", "Grid functionality"), ("grid_year_built", "Grid built"),
                      ("grid_transformer_presence", "Transformer present"), ("mini_grid_presence", "Mini-grid present"), ("mini_grid_status", "Mini-grid status"),
                      ("households_with_genset_percentage", "Households with generators"), ("households_genset_size_avg_kva", "Household generator size (kVA)"),
                      ("businesses_with_genset_percentage", "Businesses with generators"), ("businesses_genset_size_avg_kva", "Business generator size (kVA)"),
                      ("petrol_price_ngn_per_litre", "Petrol (₦/litre)"), ("diesel_price_ngn_per_litre", "Diesel (₦/litre)"), ("kerosene_price_ngn_per_litre", "Kerosene (₦/litre)"),
                      ("petrol_station_in_community", "Petrol station in community"), ("distance_to_nearest_petrol_station_km", "Nearest petrol station (km)")]),
    ("Economy and productive use", [("income_source_primary", "Main income"), ("income_source_secondary", "Second income"), ("income_source_third", "Third income"),
                      ("count_productive_use_grinding_mills", "Grinding mills"), ("count_productive_use_oil_press", "Oil presses"), ("name_productive_use_other", "Other productive use"),
                      ("count_commercial_shop_kiosk", "Shops and kiosks"), ("count_commercial_barber_beauty_salon", "Barbers and salons"), ("count_commercial_tailor_dressmaker", "Tailors"),
                      ("count_commercial_phone_charging", "Phone charging"), ("count_commercial_pos_shop", "POS shops"), ("count_commercial_tea_shop", "Tea shops"),
                      ("count_craft_welder", "Welders"), ("count_craft_carpenter", "Carpenters"), ("count_craft_generator_repair", "Generator repairers"), ("count_craft_vulcanizer", "Vulcanisers")]),
    ("Services and finance", [("count_health_facilities", "Health facilities"), ("count_primary_schools", "Primary schools"), ("count_secondary_schools", "Secondary schools"),
                      ("banks_available", "Bank"), ("mobile_money_available", "Mobile money")]),
    ("Connectivity and access", [("network_mtn", "MTN"), ("network_airtel", "Airtel"), ("network_glo", "Glo"), ("network_9mobile", "9mobile"),
                      ("accessibility_truck", "Truck access"), ("accessibility_4x4_car", "4x4 access"), ("accessibility_saloon_car", "Saloon car access"),
                      ("accessibility_motorbike", "Motorbike access"), ("accessibility_public_transport", "Public transport")]),
    ("Agriculture", [("crop_cultivated_primary", "Main crop"), ("crop_cultivated_secondary", "Second crop"), ("crop_cultivated_third", "Third crop"), ("crop_cultivated_fourth", "Fourth crop")]),
]
MARKET_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# ------------------------------------------------------------------ homepage sections (inserted before the briefings)
def usp_sections():
    top = sorted([c for c in SURV if c["grid"] == "no" and (c["bld"] or 0) >= N3["criteria"]["min_buildings"] and (c["bz_gen"] or 0) >= N3["criteria"]["min_business_genset_pct"] and c["all_year"] and (c["mobile_money"] or c["data_3g4g"])],
                 key=lambda c: -(c["bld"] or 0))[:3]
    feat = "".join(f'<a class="a-feat" href="communities/{c["slug"]}/index.html"><span class="a-pill ok">Build-ready</span><b>{e(c["name"])}</b><span>{e(c["lga"] or "")}, {e(c["state"])}</span>'
                   f'<span class="a-feat-n">{f0(c["bld"])} buildings · {int(c["bz_gen"])}% of businesses on generators · {c.get("mv_km", "—")} km to MV line</span></a>' for c in top)
    usp = lambda k, n, t, d, href, link, cls="": f'<a class="a-usp {cls}" href="{href}"><span class="a-usp-ic">{USP_ICONS[k]}</span><span class="a-usp-n">{n}</span><h3>{t}</h3><p>{d}</p><span class="a-go">{link}</span></a>'
    return f'''
<section class="sec" id="why"><div class="wrap">
<div class="sec-head"><div><span class="a-kick">Why this platform</span><h2>What makes it different</h2><p class="sub">Other sources map buildings from satellites. This platform went to the communities, mapped the grid on the ground, and turns both into answers.</p></div></div>
<div class="a-usps">
{usp("survey", f'{sv["total"]}', "Field-verified demand data", "Teams visited each community and recorded about 100 facts: who runs generators, what fuel costs, which mills, shops and clinics are there, and whether mobile money and 3G work.", "communities/index.html", "Explore the field survey", "a-usp-hero")}
{usp("grid", f'{f0(NAT2["mv_km"])} km', "A field-mapped grid, measured against every settlement", f"Medium-voltage lines from field surveys, mobile mapping, DisCo data and 2025 work orders. All {f0(NAT2['clusters'])} settlements are re-measured against it every night; {f0(DC['moved_closer'] + DC['moved_further'])} changed side of the 5 km line.", "#explore", "Explore by state")}
{usp("answers", "5", "Answers for your role", "Briefings for developers, investors, state governments, researchers and learners, and a profile for every state.", "#briefings", "Who are you?")}
{usp("open", "28", "Open, and honest about quality", "Every layer free through download, WMS and WFS, with a public data-health check that reports duplicates, missing licences and broken links.", "data-health/index.html", "See the data health check")}
{usp("skills", "4", "A pipeline of skills", "Free courses and mapathons where 280+ participants have mapped 75,000+ buildings for the national base data.", "for/learners/index.html", "Start learning")}
</div></div></section>

<section class="sec field" id="survey"><div class="wrap">
<div class="a-survey">
<div><span class="a-kick">Inside the field survey</span><h2>What {sv["total"]} communities told our field teams</h2>
<p class="sub">Every surveyed community has its own page with the full record, its nearest grid line and substation, and a printable site brief.</p>
<ul class="a-cats">
<li><b>Energy today</b><span>Grid presence and condition, generators, fuel prices</span></li>
<li><b>Economy</b><span>Income sources, grinding mills, oil presses, shops, crafts, market days</span></li>
<li><b>Services</b><span>Health facilities, schools, banks and mobile money</span></li>
<li><b>Access</b><span>Road access by vehicle and season, mobile network coverage</span></li></ul>
<div class="hero-cta" style="opacity:1;animation:none;margin-top:22px"><a class="btn btn-primary" href="communities/index.html">Browse all {sv["total"]} communities</a></div></div>
<div class="a-findings">
{card("Already paying for power", pc(dev["share_business_genset50"]), "of communities", "without grid have at least half of their businesses on generators.", "field survey", "good")}
{card("Fuel price to beat", f"₦{f0(fuel26['petrol'])}", "/ litre", f"median petrol price in 2026 surveys, against ₦{f0(fuel22['petrol'])} in 2022.", "field survey", "warn", f'<p class="a-note">2026: {fuel26["n"]} communities in {", ".join(fuel26["states"])}.</p>')}
{card("Productive demand", f0(dev["mills"]), "grinding mills", f"and {f0(dev['presses'])} oil presses in communities without grid.", "field survey")}
{card("Clinics without grid", f0(hl["no_grid_with_health"]), "communities", f"without grid have at least one health facility ({f0(hl['facilities'])} in total).", "field survey", "alert")}
</div></div>
<h3 class="a-h3" style="margin-top:34px">Build-ready communities with the largest markets</h3><div class="a-feats">{feat}</div>
</div></section>
'''

# ------------------------------------------------------------------ survey explorer
def communities_index():
    sopt = '<option value="">All states</option>' + "".join(f'<option value="{e(s)}">{e(s)} ({sum(1 for c in SURV if c["state"] == s)})</option>' for s in surveyed_states)
    body = phero('<a href="../index.html">Home</a> <span>/</span> <span>Field survey</span>', "Field-verified demand data",
                 f"{sv['total']} communities, surveyed on the ground",
                 f"Search and filter every community the field teams visited, in {len(surveyed_states)} states. Open one for its full record and a printable site brief.") + f'''
<section class="sec" style="padding-top:56px"><div class="wrap">
<form class="a-cfilters" id="a-cf" onsubmit="return false">
<input type="search" name="q" placeholder="Search community or LGA" aria-label="Search community or LGA">
<select name="state" aria-label="State">{sopt}</select>
<select name="grid" aria-label="Grid status"><option value="">Any grid status</option><option value="no">No grid at survey</option><option value="grid">Grid present</option><option value="broken">Grid that never worked</option></select>
<label class="chk"><input type="checkbox" name="clinic"> Has a health facility</label>
<label class="chk"><input type="checkbox" name="ready"> Build-ready</label>
<span class="a-ccount"><b id="a-cc">—</b> communities</span>
<button type="button" class="btn btn-outline" id="a-ccsv">Download CSV</button></form>
<div class="a-dmap" id="a-comm-map"></div>
<div class="a-tbl"><table class="a-t" id="a-ct"><thead><tr><th>Community</th><th>State</th><th class="n">Buildings</th><th>Grid at survey</th><th class="n">Nearest MV line</th><th class="n">Businesses on generators</th><th class="n">Health facilities</th><th class="n">Surveyed</th></tr></thead><tbody></tbody></table></div>
<p style="margin-top:14px"><button type="button" class="btn btn-outline" id="a-cmore"></button></p>
</div></section>
<section class="sec field" id="notes"><div class="wrap"><h2 style="margin-bottom:14px">About the survey</h2><ul class="a-notes">
<li>Source: field-survey layer <code>cluster_offgrid_survey</code> ({sv["total"]} communities; {", ".join(f"{y}: {n}" for y, n in sv["by_year"].items())}). Records are shown as surveyed; conditions may have changed since.</li>
<li>Not yet surveyed: {len(no_survey_states)} states ({", ".join(no_survey_states)}).</li>
<li>Nearest MV line and substation are recalculated against the current grid and de-duplicated substation layers. Pulled {PULLED}.</li></ul></div></section>'''
    page("communities/index.html", "Field survey explorer | Nigeria Electrification Atlas", f"Search {sv['total']} field-surveyed communities in Nigeria.", body, "communities", dict(criteria=N3["criteria"]))

# ------------------------------------------------------------------ one page per surveyed community (printable site brief)
def community_pages():
    for c in SURV:
        r = SURVEY.get(c["uid"], {})
        name = c["name"] or "Surveyed community"; date = str(r.get("survey_date") or "")[:10]
        gl = {"no": "No grid", "yes_connected_national_grid": "Connected to national grid", "yes_not_connected_national_grid": "Grid present, not connected"}.get(c["grid"], nice(c["grid"]) or "—")
        ready = c["grid"] == "no" and (c["bld"] or 0) >= N3["criteria"]["min_buildings"] and (c["bz_gen"] or 0) >= N3["criteria"]["min_business_genset_pct"] and c["all_year"] and (c["mobile_money"] or c["data_3g4g"])
        tables = ""
        for title, fields in GROUPS:
            rows = "".join(f'<tr><th>{lab}</th><td>{e(v)}</td></tr>' for k, lab in fields if (v := nice(r.get(k))) is not None)
            if title == "Economy and productive use":
                days = [d.capitalize() for d in MARKET_DAYS if str(r.get(f"market_{d}")) == "True"]
                if days: rows += f'<tr><th>Market days</th><td>{", ".join(days)}</td></tr>'
            if title == "Agriculture":
                other = [nice(r.get(k)) for k in ("crop_cultivated_other_1", "crop_cultivated_other_2", "crop_cultivated_other_3") if nice(r.get(k))]
                if other: rows += f'<tr><th>Other crops</th><td>{e(", ".join(other))}</td></tr>'
            if rows: tables += f'<div class="a-fact"><h3 class="a-h3">{title}</h3><table class="a-kv">{rows}</table></div>'
        mail = f"mailto:{EMAIL}?subject=" + html.escape(f"Correction: {name} ({c['uid']})").replace(" ", "%20")
        extra = (f'<div class="hero-cta" style="opacity:1;animation:none;margin-top:22px"><button class="btn btn-leaf" type="button" onclick="window.print()">Print or save as PDF</button>'
                 f'<a class="btn btn-ghost" href="{mail}">Report a correction</a></div>')
        kpi = lambda v, l, src: f'<div class="a-kpi"><b>{v}</b><span>{l}</span><small>{src}</small></div>'
        body = phero(f'<a href="../../index.html">Home</a> <span>/</span> <a href="../index.html">Field survey</a> <span>/</span> <a href="../../states/{slug(c["state"])}/index.html">{e(c["state"])}</a> <span>/</span> <span>{e(name)}</span>',
                     "Surveyed community" + (" · build-ready" if ready else ""), e(name), f"{e(c['lga'] or '—')} LGA, {e(c['state'])} · surveyed {date}", extra) + f'''
<section class="sec" style="padding-top:56px"><div class="wrap">
<div class="a-kpis">
{kpi(f0(c["bld"]), "buildings in the settlement", "field survey")}{kpi(gl, "grid at survey", "field survey")}
{kpi((str(c["mv_km"]) + " km") if c.get("mv_km") is not None else "—", "to the nearest MV line", "recalculated, distribution_line_mv")}
{kpi((str(c["sub_km"]) + " km") if c.get("sub_km") is not None else "—", "to " + e(c.get("sub_name") or "the nearest substation"), "installed substations, de-duplicated")}
{kpi((str(int(c["bz_gen"])) + "%") if c["bz_gen"] is not None else "—", "of businesses run generators", "field survey")}
</div></div></section>
<section class="sec field" style="padding-top:56px"><div class="wrap"><div class="a-split">
<div>{tables}</div>
<div><div class="a-smap a-cmap"><div class="a-map" id="a-one-map"></div></div><p class="sm a-muted" style="margin-top:8px">The community (amber), medium-voltage grid (live from GeoServer) and the nearest installed substation (blue).</p>
<div class="a-flag" style="margin-top:18px">{f"Nearest recorded mini-grid: {e(c['mg_name'])}, {c['mg_km']} km away ({e(c['mg_src'])}). " if c.get("mg_km") is not None else ""}{"Meets the developer build-ready criteria. " if ready else ""}Recorded as surveyed on {date}; conditions may have changed. Seen something out of date? <a class="a-go" href="{mail}">Report a correction</a></div>
<p style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-primary" href="../../states/{slug(c["state"])}/index.html">{e(c["state"])} state profile</a><a class="btn btn-outline" href="{APPS}minigrid-offgrid" target="_blank" rel="noopener">Off-grid webmap</a></p></div>
</div></div></section>
<section class="sec" id="notes"><div class="wrap"><ul class="a-notes"><li>Source: <code>cluster_offgrid_survey</code>, record {e(c["uid"])}. Nearest MV line and substation recalculated on {PULLED}.</li><li>Dataset licence not yet specified on the data portal.</li></ul></div></section>'''
        sub = None
        if c.get("sub_name"):
            sub = next((x for x in X["states"].get(c["state"], {}).get("substations", []) if x["name"] == c["sub_name"]), None)
            if sub is None:
                sub = next((x for st in X["states"].values() for x in st["substations"] if x["name"] == c["sub_name"]), None)
        page(f"communities/{c['slug']}/index.html", f"{name}, {c['state']} | Field survey | Nigeria Electrification Atlas",
             f"Field survey record for {name}, {c['lga']} LGA, {c['state']}: grid, generators, fuel prices, businesses and services.", body, "community",
             dict(point=[c["lat"], c["lon"]] if c["lat"] is not None else None, name=name, sub=sub))

# ------------------------------------------------------------------ data health
def data_health():
    L = HEALTH["layers"]
    dup_layers = [r for r in L if r["duplicates"]]
    lic_set = sum(1 for r in L if r["licence"] not in ("not_specified", None, ""))
    broken = {k: v for k, v in HEALTH["links"].items() if v["status"] != 200}
    def dup_cell(r):
        if r["duplicates"]:
            return f'<span class="a-pill bad">{f0(r["duplicates"])} ({100 * r["duplicates"] / r["features"]:.0f}%)</span>'
        return '<span class="a-pill ok">None</span>' if r["checked"] else '<span class="a-pill">Not checked (size)</span>'
    def lic_cell(r):
        return '<span class="a-pill mid">Not specified</span>' if r["licence"] == "not_specified" else e(r["licence"])
    def link_cell(v):
        if v["status"] == 200: return '<span class="a-pill ok">OK</span>'
        return f'<span class="a-pill bad">{v["status"] if isinstance(v["status"], int) else "Unreachable"}</span>'
    rows = "".join(f'<tr><td><a class="a-go" href="{r["page"]}" target="_blank" rel="noopener">{e(r["title"])}</a><br><code class="a-code">{e(r["layer"])}</code></td>'
                   f'<td class="n" data-v="{r["features"]}">{f0(r["features"])}</td><td class="n" data-v="{r["duplicates"] if r["duplicates"] is not None else -1}">{dup_cell(r)}</td>'
                   f'<td>{lic_cell(r)}</td><td class="n">{r["last_updated"]}</td></tr>' for r in L)
    lrows = "".join(f'<tr><td>{e(k)}</td><td><a class="a-go" href="{v["url"]}" style="word-break:break-all">{e(v["url"])}</a></td><td>{link_cell(v)}</td></tr>' for k, v in HEALTH["links"].items())
    body = phero('<a href="../index.html">Home</a> <span>/</span> <span>Data health</span>', "Open, and honest about quality", "Data health",
                 "How reliable is each layer? We check the data every night and publish what we find, including what still needs fixing at source.") + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Settlement distances", f0(DC["settlements"]), "re-measured", f"against the field-mapped MV grid. {f0(DC['moved_closer'])} turned out to be within 5 km and {f0(DC['moved_further'])} further than recorded.", "fixed on this site", "good")}
{card("Duplicated layers", f"{len(dup_layers)} of {len(L)}", "layers", f"contain exact duplicate rows ({f0(sum(r['duplicates'] for r in dup_layers))} in total), including substations, power plants, towns and transmission lines. This site removes them before counting.", "fixed on this site; needs a fix at source", "warn")}
{card("Licences", f"{lic_set} of {len(L)}", "layers licensed", "No layer has a licence set yet, so reuse terms are unclear until the data owners choose one.", "needs the data owner", "alert")}
{card("Survey coverage", f"{len(surveyed_states)} of 37", "states", f"have field-surveyed communities. Not yet covered: {', '.join(no_survey_states[:6])}{' and others' if len(no_survey_states) > 6 else ''}.", "field-survey layer")}
{card("Mini-grid records", f0(inv["fleet_n"]), "sites", f"in the mini-grid layer. The NEP project map lists {len(NEP_NEW)} more; a data-sharing agreement with REA would keep the two in step.", "needs a data-sharing agreement", "warn")}
{card("Broken links", f0(len(broken)), "of " + str(len(HEALTH["links"])), "key links checked. " + ("; ".join(broken.keys()) if broken else "All working."), "link check, " + HEALTH["checked_on"], "alert" if broken else "good")}
</div></div></section>
{nep_health_section()}
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Every layer</span><h2>Layer-by-layer check</h2><p class="sub">Exact duplicates ignore ID columns. Layers above 30,000 features are not checked for duplicates yet.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Layer</th><th class="n">Features</th><th class="n">Exact duplicates</th><th>Licence</th><th class="n">Last updated</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Links</span><h2>Key links</h2></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Link</th><th>Address</th><th>Status</th></tr></thead><tbody>{lrows}</tbody></table></div></div></section>
<section class="sec field"><div class="wrap"><div class="a-split">
<div><h2 style="margin-bottom:14px">Fixed automatically on this site</h2><ul class="a-notes"><li>Duplicate substations, power plants and other repeated rows are removed before counting.</li><li>Every settlement's distance to grid is recalculated against the current field-mapped MV layer.</li><li>Survey communities get their nearest MV line and substation.</li><li>Every figure shows its source layer and the date it was pulled.</li></ul></div>
<div><h2 style="margin-bottom:14px">Needs the data owners</h2><ul class="a-notes"><li>Remove duplicates at source and block repeat imports.</li><li>Add created and updated dates to every record.</li><li>Choose a licence for every layer.</li><li>Align the webmaps and the data portal on one source of truth.</li><li>Complete the mini-grid layer with programme data; extend the survey to the remaining states.</li></ul>
<p style="margin-top:14px"><a class="a-go" href="mailto:{EMAIL}?subject=Data%20quality">Report a data issue</a></p></div></div></div></section>'''
    page("data-health/index.html", "Data health | Nigeria Electrification Atlas", "Layer-by-layer data-quality check for the Nigeria SE4ALL data portal.", body, "health")
