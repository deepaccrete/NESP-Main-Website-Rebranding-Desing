# v7 pages: electrification projects from the Nigeria Electrification Project map (REA). Executed inside build_v7.py's namespace.
NEP_CAVEAT = ("Source: the project map on <a class=\"a-go\" href=\"https://nep.rea.gov.ng/\">nep.rea.gov.ng</a> (Rural Electrification Agency, Nigeria Electrification Project), "
              f"read on {NEP_PULLED}. The mini-grid list is labelled April 2021 at source. No licence is stated on that site; republishing is subject to REA's agreement.")
YES, NOTYET = '<span class="a-pill ok">Yes</span>', '<span class="a-pill mid">Not yet</span>'
DEVL = lambda p: f'<br><span class="a-muted">{e(p["developer"])}</span>' if p["developer"] else ""
kw = lambda v: "—" if not v else (f"{v/1000:,.1f} MW" if v >= 1000 else f"{v:,.0f} kW")

def projects_strip():
    return f'''<section class="sec" id="projects"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Projects on the ground</span><h2>What has already been built</h2>
<p class="sub">Projects from the Nigeria Electrification Project, mapped alongside the platform's own data.</p></div><a class="link" href="projects/index.html">All projects {SVG_ARROW}</a></div>
<div class="a-pstrip">
<a class="a-pcell" href="projects/index.html#minigrid"><b>{NS["minigrids"]}</b><span>solar hybrid mini-grids</span><small>{kw(NS["minigrid_kw"])} · {f0(NS["minigrid_customers"])} customers · {NS["minigrid_developers"]} developers</small></a>
<a class="a-pcell" href="projects/index.html#shs"><b>{f0(NS["shs_connections"])}</b><span>solar home system connections</span><small>across all {NS["shs_states"]} states and the FCT</small></a>
<a class="a-pcell" href="projects/index.html#health"><b>{NS["health"]}</b><span>health facilities on solar</span><small>COVID-19 intervention</small></a>
<a class="a-pcell" href="projects/index.html#education"><b>{NS["education"]}</b><span>universities</span><small>Energizing Education Programme</small></a>
</div><p class="a-next">{len(NEP_NEW)} of the {NS["minigrids"]} mini-grids are not yet in the platform's own mini-grid layer, which takes the combined count to {ALL_MG_N}. Source: REA, nep.rea.gov.ng; mini-grid list labelled April 2021.</p></div></section>'''

def projects_page():
    ph = lambda arr: sum(1 for p in NEP_E if p["source_array"] == arr)
    devs = sorted(DEVS.items(), key=lambda kv: -kv[1]["n"])
    dtr = "".join(f'<tr><td><b>{e(k)}</b></td><td class="n" data-v="{r["n"]}">{r["n"]}</td><td class="n" data-v="{r["kw"]}">{f0(r["kw"])}</td><td class="n" data-v="{r["cust"]}">{f0(r["cust"])}</td><td>{e(", ".join(sorted(x for x in r["states"] if x)))}</td></tr>' for k, r in devs)
    smax = max(s["connections"] or 0 for s in SHS)
    shtr = "".join(f'<tr><td><a class="a-go" style="font-weight:600" href="../states/{slug(s["state"])}/index.html">{e(s["state"])}</a></td><td class="n" data-v="{s["connections"] or 0}"><span class="a-bar">{f0(s["connections"])}<i style="width:{110*(s["connections"] or 0)/smax:.0f}px"></i></span></td>'
                   f'<td class="n" data-v="{states[s["state"]]["offgrid_buildings"]}">{f0(states[s["state"]]["offgrid_buildings"])}</td></tr>' for s in sorted(SHS, key=lambda s: -(s["connections"] or 0)) if s["state"] in states)
    etr = ""
    for p in sorted(NEP_E, key=lambda p: (p["source_array"], -(p["capacity_kw"] or 0), p["name"] or "")):
        st = p["status"] or "Not stated"; cls = "ok" if st.startswith("100%") else ("mid" if "%" in st or "Evaluation" in st else "")
        etr += (f'<tr><td><b>{e(p["name"])}</b>{DEVL(p)}</td><td>{PHASE[p["source_array"]]}</td><td>{e(p["state"] or "—")}</td>'
                f'<td class="n" data-v="{p["capacity_kw"] or 0}">{f0(p["capacity_kw"]) if p["capacity_kw"] else "—"}</td><td class="n" data-v="{p["grant"] or 0}">{f0(p["grant"]) if p["grant"] else "—"}</td><td><span class="a-pill {cls}">{e(st)}</span></td></tr>')
    sopt = '<option value="">All states</option>' + "".join(f'<option value="{e(s)}">{e(s)}</option>' for s in sorted(states))
    dopt = '<option value="">All developers</option>' + "".join(f'<option value="{e(k)}">{e(k)} ({r["n"]})</option>' for k, r in sorted(DEVS.items()))
    mism = [p for p in NEP_ALL if p["state_mismatch"]]
    mtr = "".join(f'<li><b>{e(p["name"])}</b> ({KIND_L[p["kind"]].lower()}): listed as {e(p["stated_state"])}, plotted in {e(p["state"])}.</li>' for p in mism)
    body = phero('<a href="../index.html">Home</a> <span>/</span> <span>Projects</span>', "Electrification projects · Nigeria Electrification Project",
                 "What has been built, and where",
                 f"{NS['minigrids']} solar hybrid mini-grids, {NS['health']} health facilities and {NS['education']} universities from the Rural Electrification Agency's project map, plus {f0(NS['shs_connections'])} solar home system connections. All on one map, checked against the platform's own data.") + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Mini-grids", NS["minigrids"], "sites", f"{kw(NS['minigrid_kw'])} serving {f0(NS['minigrid_customers'])} customers in {NS['minigrid_states']} states, built by {NS['minigrid_developers']} developers under the Performance-Based Grant.", "NEP project map (list labelled April 2021)", "good", '<a class="a-go" href="#minigrid">Developers and sites</a>')}
{card("New to the platform", len(NEP_NEW), f"of {NS['minigrids']}", f"NEP mini-grids are not in the platform's own mini-grid layer ({NS['overlap_with_se4all']} are, within 1 km). Together the two sources record {ALL_MG_N} mini-grids.", "NEP map compared with the SE4ALL mini-grid layer", "warn")}
{card("Solar home systems", f0(NS["shs_connections"]), "connections", f"reported across all {NS['shs_states']} states and the FCT. Largest: {', '.join(s['state'] for s in sorted(SHS, key=lambda s: -(s['connections'] or 0))[:3])}.", "NEP project map, totals by state", "", '<a class="a-go" href="#shs">By state</a>')}
{card("Health facilities", NS["health"], "facilities", "solar-powered under the COVID-19 intervention; all are listed at source as completed and operational.", "NEP project map", "", '<a class="a-go" href="#health">On the map</a>')}
{card("Universities", NS["education"], "campuses", f"in the Energizing Education Programme: {ph('eep1')} in phase I with capacity, grant and progress published; {ph('eep2')} in phase II under evaluation; {ph('eep3')} in phase III listed by name.", "NEP project map", "", '<a class="a-go" href="#education">Phase details</a>')}
{card("Location checks", NS["checks"]["state_mismatch"], "records", f"are plotted in a different state from the one they are listed in, and {NS['checks']['duplicate_points']} records share a point with another. Shown here as published and flagged.", "boundary check on this site", "alert", '<a class="a-go" href="#notes">See which</a>')}
</div></div></section>
<section class="sec field" id="map"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Explore</span><h2>Every project on one map</h2><p class="sub">Filter by programme, state or developer. The map, count and list update together.</p></div></div>
<div class="a-tool"><form class="a-panel" id="a-pf" onsubmit="return false"><h3>Filter projects</h3>
<label for="pq">Search by name or LGA</label><input id="pq" name="q" type="search" placeholder="e.g. Kano, hospital, MG">
<label for="pk">Programme</label><select id="pk" name="kind"><option value="">All programmes</option><option value="minigrid">Mini-grids (Performance-Based Grant)</option><option value="health">Health facilities (COVID-19 intervention)</option><option value="education">Universities (Energizing Education)</option></select>
<label for="ps">State</label><select id="ps" name="state">{sopt}</select>
<label for="pd">Mini-grid developer</label><select id="pd" name="dev">{dopt}</select>
<label class="chk"><input type="checkbox" name="newonly"> Only mini-grids not yet in the platform's layer</label>
<label class="chk"><input type="checkbox" name="shs"> Show solar home systems by state</label>
<div class="a-count"><b id="a-pc">—</b><span>projects match</span></div><button type="button" class="btn btn-primary" id="a-pcsv" style="margin-top:14px">Download list (CSV)</button>
<div class="a-pkey"><span><i style="background:#065F46"></i>Mini-grid</span><span><i style="background:#9F2A2A"></i>Health facility</span><span><i style="background:#1E4E79"></i>University</span><span><i class="ring"></i>Solar home systems</span></div></form>
<div><div class="a-dmap tall" id="a-proj-map"></div><div class="a-tbl"><table class="a-t" id="a-pt"><thead><tr><th>Project</th><th>Programme</th><th>State</th><th>Developer</th><th class="n">Capacity</th><th class="n">Customers</th><th>Status at source</th></tr></thead><tbody></tbody></table></div>
<p style="margin-top:14px"><button type="button" class="btn btn-outline" id="a-pmore"></button></p></div></div></div></section>
<section class="sec" id="minigrid"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Mini-grids</span><h2>Who built them</h2><p class="sub">{NS["minigrid_developers"]} developers, {NS["minigrids"]} sites. Click a column to re-sort.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Developer</th><th class="n">Sites</th><th class="n">kW</th><th class="n">Customers</th><th>States</th></tr></thead><tbody>{dtr}</tbody></table></div></div></section>
<section class="sec field" id="shs"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Solar home systems</span><h2>Connections by state</h2><p class="sub">Reported totals per state, set against off-grid buildings from the platform's settlement data.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>State</th><th class="n">SHS connections</th><th class="n">Off-grid buildings</th></tr></thead><tbody>{shtr}</tbody></table></div></div></section>
<section class="sec" id="education"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Energizing Education Programme</span><h2>Universities</h2><p class="sub">Phase I projects carry capacity, grant and progress at source; later phases are listed by name and status only.</p></div></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Project</th><th>Phase</th><th>State</th><th class="n">Installed kW</th><th class="n">Grant (as published)</th><th>Progress at source</th></tr></thead><tbody>{etr}</tbody></table></div>
<p class="a-note" style="margin-top:12px">Installed kW is the source's figure for the whole hybrid system and can exceed the headline solar size in the project title. The source does not state the grant currency.</p></div></section>
<section class="sec field" id="health"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Health facilities</span><h2>Solar for health under the COVID-19 intervention</h2><p class="sub">{NS["health"]} facilities, switch the programme filter above to see them alone. System sizes are not shown: every record carries the same value at source.</p></div></div>
{steps([("Show health facilities on the map", "Filters the map and list above.", "#map"), ("State profiles", "Projects, grid and surveyed communities for each state.", "../states/index.html"), ("Field survey", "Health facilities in communities without grid.", "../communities/index.html")])}</div></section>
<section class="sec" id="notes"><div class="wrap"><div class="a-split">
<div><h2 style="margin-bottom:14px">How this page is made</h2><ul class="a-notes">
<li>{NEP_CAVEAT}</li>
<li>Project records are read from the data the NEP map publishes. They are not changed here, only checked: each point is placed in a state by its coordinates, and NEP mini-grids within 1 km of a site in the SE4ALL mini-grid layer are counted once.</li>
<li>Health facility system sizes are withheld because all {NS["health"]} records carry the same placeholder value. Phase II and III "grant" fields hold row numbers rather than amounts and are withheld too.</li>
<li>Solar home system figures are state totals with one point per state, not individual installations.</li></ul></div>
<div><h2 style="margin-bottom:14px">Records flagged for REA</h2><ul class="a-notes">{mtr}<li>{NS["checks"]["duplicate_points"]} records share exact coordinates with another record of the same programme.</li></ul>
<p style="margin-top:14px"><a class="a-go" href="mailto:{EMAIL}?subject=Project%20data%20correction">Report a correction</a> · <a class="a-go" href="../data-health/index.html">Data health</a></p></div></div></div></section>'''
    body = body.replace(f"Calculated from the platform's public data on {PULLED}.", f"Read from the NEP project map on {NEP_PULLED}; compared with the platform's data of {PULLED}.", 1)
    page("projects/index.html", "Electrification projects | Nigeria Electrification Atlas",
         "Mini-grids, solar home systems, health facilities and universities from the Nigeria Electrification Project, on one map.", body, "projects")

def state_projects(name):
    d = states[name]; mg = [p for p in NEP_MG if p["state"] == name]; hs = [p for p in NEP_H if p["state"] == name]; ed = [p for p in NEP_E if p["state"] == name]
    if not (mg or hs or ed or d["shs_connections"]):
        return ""
    mtr = "".join(f'<tr><td><b>{e(p["name"] or "—")}</b><br><span class="a-muted">{e(p["lga"] or "")}</span></td><td>{e(p["developer"] or "—")}</td><td class="n" data-v="{p["capacity_kw"] or 0}">{f0(p["capacity_kw"])}</td><td class="n" data-v="{p["customers"] or 0}">{f0(p["customers"])}</td><td>{YES if p["in_se4all_layer"] else NOTYET}</td></tr>' for p in sorted(mg, key=lambda p: -(p["capacity_kw"] or 0)))
    mtab = (f'<h3 class="a-h3">NEP mini-grids ({len(mg)} · {kw(d["nep_kw"])} · {f0(d["nep_customers"])} customers)</h3><div class="a-tbl"><table class="a-t"><thead><tr><th>Site</th><th>Developer</th><th class="n">kW</th><th class="n">Customers</th><th>In platform layer</th></tr></thead><tbody>{mtr}</tbody></table></div>') if mg else '<p class="a-muted">No NEP mini-grid is listed in this state.</p>'
    other = "".join(f'<li><b>{e(p["name"])}</b> · {"health facility, " + e(p["status"] or "") if p["kind"] == "health" else PHASE[p["source_array"]] + (", " + e(p["status"]) if p["status"] else "")}</li>' for p in hs + ed)
    shs_t = f'<div class="a-kpis" style="grid-template-columns:1fr;margin-bottom:18px"><div class="a-kpi"><b>{f0(d["shs_connections"])}</b><span>solar home system connections</span><small>NEP, state total</small></div></div>' if d["shs_connections"] else ""
    return f'''<section class="sec field" id="projects"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Projects on the ground</span><h2>NEP projects in {e(name)}</h2>
<p class="sub">From the Nigeria Electrification Project map (REA). Switch on "NEP projects" in the map above.</p></div><a class="link" href="../../projects/index.html">All projects {SVG_ARROW}</a></div>
<div class="a-split"><div>{mtab}</div><div>{shs_t}<h3 class="a-h3">Health facilities and universities</h3>{f'<ul class="a-notes">{other}</ul>' if other else '<p class="a-muted">None listed in this state.</p>'}</div></div>
<p class="a-note" style="margin-top:16px">{NEP_CAVEAT}</p></div></section>'''

def nep_health_section():
    mism = [p for p in NEP_ALL if p["state_mismatch"]]
    rows = "".join(f'<tr><td>{e(p["name"])}</td><td>{KIND_L[p["kind"]]}</td><td>{e(p["stated_state"])}</td><td>{e(p["state"])}</td></tr>' for p in mism)
    return f'''<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">External source</span><h2>Nigeria Electrification Project map</h2><p class="sub">Checks on the project records shown on the <a class="a-go" href="../projects/index.html">projects page</a>, read from nep.rea.gov.ng on {NEP_PULLED}.</p></div></div>
<div class="a-cards">
{card("Snapshot age", "April 2021", "", "is the label the source gives its mini-grid list. Newer programme data from REA would bring it up to date.", "NEP project map", "warn")}
{card("Placed in another state", NS["checks"]["state_mismatch"], "records", "are plotted outside the state they are listed in.", "boundary check", "alert")}
{card("Placeholder values", NS["health"], "health records", "all carry the same system size (50), so sizes are not shown.", "value check", "alert")}
{card("Overlap with platform", NS["overlap_with_se4all"], f"of {NS['minigrids']}", f"NEP mini-grids are already in the SE4ALL mini-grid layer ({NS['se4all_layer']} sites); the rest are counted as new.", "1 km match", "")}
{card("Licence", "None", "stated", "on nep.rea.gov.ng. Republishing on this platform needs REA's agreement.", "needs the data owner", "alert")}
{card("Duplicate points", NS["checks"]["duplicate_points"], "records", "share exact coordinates with another record of the same programme.", "coordinate check", "warn")}
</div><div class="a-tbl" style="margin-top:22px"><table class="a-t"><thead><tr><th>Record</th><th>Programme</th><th>Listed in</th><th>Plotted in</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'''
