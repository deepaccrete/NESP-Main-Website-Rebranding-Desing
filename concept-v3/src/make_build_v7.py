# build_v7.py = build_v6.py + checked patches: NEP projects (REA) as a projects page, state sections, investor white space,
# homepage strip, nearest mini-grid for surveyed communities and data-health checks. Also writes pages_v6b.py, v7.js and v7.css.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def patcher(name):
    box = {"s": open(os.path.join(HERE, name), encoding="utf-8").read()}
    def P(old, new, count=1):
        n = box["s"].count(old)
        if n != count: sys.exit(f"{name}: patch failed ({n}x): {old[:110]!r}")
        box["s"] = box["s"].replace(old, new)
    return box, P

# ================================================================ build_v6.py -> build_v7.py
b, P = patcher("build_v6.py")
P('off_total = sum(d["offgrid_buildings"] for d in states.values())',
  'off_total = sum(d["offgrid_buildings"] for d in states.values())\nexec(open(os.path.join(HERE, "nep_data.py"), encoding="utf-8").read())\nlite = {s: {k: v for k, v in d.items() if k != "bands"} for s, d in states.items()}')
P('communities=I3["communities"], fleet=fleet, national=N3)', 'communities=I3["communities"], fleet=fleet, national=N3, nep=NEP_LITE, shs=SHS)')
P('"v6.css"', '"v7.css"', count=2); P('"v6.js"', '"v7.js"', count=2)
P('assets/css/v6.css', 'assets/css/v7.css'); P('assets/js/v6.js', 'assets/js/v7.js', count=2)
# header + footer
P('''f'<a href="{{R}}communities/index.html">Field survey</a><a href="{{R}}index.html#data">Data</a>''',
  '''f'<a href="{{R}}projects/index.html">Projects</a><a href="{{R}}communities/index.html">Field survey</a><a href="{{R}}index.html#data">Data</a>''')
P('''<a href="{{R}}communities/index.html">Field survey explorer</a><a href="{{R}}data-health/index.html">Data health</a>''',
  '''<a href="{{R}}projects/index.html">Electrification projects</a><a href="{{R}}communities/index.html">Field survey explorer</a><a href="{{R}}data-health/index.html">Data health</a>''')
# home
P('''Four of the ten largest off-grid markets have no mini-grid recorded on the platform.</p>''',
  '''{len(TOP10_NONE)} of the ten largest off-grid markets have no mini-grid recorded in either the platform or the NEP project map.</p>''')
P('''<div><b>{f0(N3["investor"]["fleet_n"])}</b><span>mini-grids recorded</span></div>''',
  '''<div><b>{f0(ALL_MG_N)}</b><span>mini-grids recorded (platform and NEP)</span></div>''')
P('s = s[:i] + usp_sections() + NEW + s[i:]', 's = s[:i] + usp_sections() + NEW + projects_strip() + s[i:]')
# state profile
P('''<label><input type="checkbox" data-layer="mg"> Mini-grids</label>''', '''<label><input type="checkbox" data-layer="mg"> Mini-grids (platform)</label><label><input type="checkbox" data-layer="nep"> NEP projects</label>''')
P('''Recorded for {e(name)} in the platform's mini-grid layer.</p></div></div>{mtab}</div></section>''',
  '''Recorded for {e(name)} in the platform's mini-grid layer.</p></div></div>{mtab}</div></section>\n{state_projects(name)}''')
# investors
P('''{card("Apparent white space", f"{len(inv['top10_no_minigrid'])} of 10", "largest markets", f"have no mini-grid recorded on the platform: {', '.join(inv['top10_no_minigrid'])}.", "mini-grid layer", "warn", '<p class="a-note">The mini-grid layer is incomplete; confirm against REA programme data.</p>')}''',
  '''{card("Apparent white space", f"{len(TOP10_NONE)} of 10", "largest markets", f"have no mini-grid in either the platform's layer or the NEP project map: {', '.join(TOP10_NONE)}." + (f" {', '.join(TOP10_NEP_ONLY)} {'has' if len(TOP10_NEP_ONLY) == 1 else 'have'} NEP sites only." if TOP10_NEP_ONLY else ""), "mini-grid layer and NEP project map", "warn", '<p class="a-note">The NEP mini-grid list is labelled April 2021; confirm against current REA programme data.</p>')}''')
P('''{card("Customers per kW", f"{inv['conn_per_kw']:.1f}", "connections / kW", f"across recorded mini-grids with connection data ({f0(inv['fleet_conn'])} connections).", "mini-grid layer")}''',
  '''{card("Programme mini-grids", f0(NS["minigrids"]), "NEP sites", f"{f0(NS['minigrid_kw'])} kW for {f0(NS['minigrid_customers'])} customers ({NS['minigrid_customers']/NS['minigrid_kw']:.1f} per kW, against {inv['conn_per_kw']:.1f} in the platform's layer), from {NS['minigrid_developers']} developers. {len(NEP_NEW)} are new to the platform.", "NEP project map (REA)", "good", '<a class="a-go" href="../../projects/index.html">All projects</a>')}''')
P('''<th class="n">Mini-grids</th><th class="n">kW</th><th class="n">kW per 100k off-grid bldgs</th>''',
  '''<th class="n">Mini-grids (platform)</th><th class="n">kW</th><th class="n">NEP mini-grids</th><th class="n">NEP kW</th><th class="n">kW per 100k off-grid bldgs</th>''')
P('''<td class="n" data-v="{d["minigrid_kw"]}">{f0(d["minigrid_kw"]) if d["minigrid_kw"] else "—"}</td>'
                f'<td class="n" data-v="{kwp:.2f}">''',
  '''<td class="n" data-v="{d["minigrid_kw"]}">{f0(d["minigrid_kw"]) if d["minigrid_kw"] else "—"}</td>'
                f'<td class="n" data-v="{d["nep_minigrids"]}">{d["nep_minigrids"] or "—"}</td><td class="n" data-v="{d["nep_kw"]}">{f0(d["nep_kw"]) if d["nep_kw"] else "—"}</td>'
                f'<td class="n" data-v="{kwp:.2f}">''')
P('''kwp = d["minigrid_kw"] / d["offgrid_buildings"] * 1e5 if d["offgrid_buildings"] else 0;''',
  '''kwp = (d["minigrid_kw"] + sum(p["capacity_kw"] or 0 for p in NEP_NEW if p["state"] == d["state"])) / d["offgrid_buildings"] * 1e5 if d["offgrid_buildings"] else 0;''')
P('''<h2>Mini-grids on the platform</h2><p class="sub">Green: operational · red: non-operational · blue: under construction. Circle size shows capacity.</p>''',
  '''<h2>Mini-grids on the platform and the NEP map</h2><p class="sub">Platform layer: green operational · red non-operational · blue under construction. Purple: NEP mini-grids not in the platform layer. Circle size shows capacity.</p>''')
P('''It does not yet include all programme mini-grids.</li>''',
  '''NEP mini-grids from <a class="a-go" href="https://nep.rea.gov.ng/">nep.rea.gov.ng</a> (list labelled April 2021) within 1 km of a platform site are counted once. "kW per 100k" uses both sources.</li>''')
# pages
P('exec(open(os.path.join(HERE, "pages_v6.py"), encoding="utf-8").read())',
  'exec(open(os.path.join(HERE, "pages_v6b.py"), encoding="utf-8").read())\nexec(open(os.path.join(HERE, "pages_v7.py"), encoding="utf-8").read())')
P('communities_index(); community_pages(); data_health()', 'communities_index(); community_pages(); data_health(); projects_page()')
open(os.path.join(HERE, "build_v7.py"), "w", encoding="utf-8").write(b["s"])

# ================================================================ pages_v6.py -> pages_v6b.py
b, P = patcher("pages_v6.py")
P('''{card("Mini-grid records", f0(inv["fleet_n"]), "sites", "in the mini-grid layer, fewer than are known to operate in Nigeria. Programme data from REA would complete it.", "needs a data-sharing agreement", "warn")}''',
  '''{card("Mini-grid records", f0(inv["fleet_n"]), "sites", f"in the mini-grid layer. The NEP project map lists {len(NEP_NEW)} more; a data-sharing agreement with REA would keep the two in step.", "needs a data-sharing agreement", "warn")}''')
P('''<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Every layer</span>''',
  '''{nep_health_section()}\n<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Every layer</span>''')
P('''<div class="a-flag" style="margin-top:18px">{"Meets the developer build-ready criteria. " if ready else ""}''',
  '''<div class="a-flag" style="margin-top:18px">{f"Nearest recorded mini-grid: {e(c['mg_name'])}, {c['mg_km']} km away ({e(c['mg_src'])}). " if c.get("mg_km") is not None else ""}{"Meets the developer build-ready criteria. " if ready else ""}''')
open(os.path.join(HERE, "pages_v6b.py"), "w", encoding="utf-8").write(b["s"])

# ================================================================ v6.js -> v7.js
b, P = patcher("assets/js/v6.js")
NEPDOT = '''function nepDot(p) { var c = { minigrid: "#065F46", health: "#9F2A2A", education: "#1E4E79" }[p.kind];
    var h = "<b>" + esc(p.name || "Project") + "</b><br>" + esc(p.short) + (p.lga ? " · " + esc(p.lga) : "") + (p.state ? ", " + esc(p.state) : "") +
      (p.developer ? "<br>" + esc(p.developer) : "") + (p.capacity_kw ? "<br>" + fmt(p.capacity_kw) + " kW" : "") + (p.customers ? " · " + fmt(p.customers) + " customers" : "") +
      (p.status ? "<br>" + esc(p.status) : "") + (p.kind === "minigrid" ? "<br><small>" + (p.in_se4all_layer ? "Also in the platform's mini-grid layer" : "Not yet in the platform's mini-grid layer") + "</small>" : "") +
      (p.state_mismatch ? "<br><small>Listed at source in " + esc(p.stated_state) + "</small>" : "") + "<br><small>Source: NEP project map (REA)</small>";
    return dot(p, p.kind === "minigrid" ? 4 + Math.min(9, Math.sqrt(p.capacity_kw || 1) / 2) : 5, c, h); }
  function dot('''
P('  function dot(', '  ' + NEPDOT)
P('''      survey: L.layerGroup(cs.map(function (c) {''',
  '''      nep: L.layerGroup((A.nep || []).filter(function (p) { return p.state === P.state && p.lat != null; }).map(nepDot)),
      survey: L.layerGroup(cs.map(function (c) {''')
P('''["settle", "mv", "hv", "subs", "mg", "survey"].forEach''', '''["settle", "mv", "hv", "subs", "mg", "nep", "survey"].forEach''')
P('''        "<b>" + esc(g.community || "Mini-grid") + "</b><br>" + esc(g.lga || "") + "<br>" + fmt(g.kw) + " kW · " + esc(g.system || "") + "<br>" + esc(g.status || "") + (g.condition ? " · " + esc(g.condition) : "") + (g.programme ? "<br>" + esc(g.programme) : "")).addTo(im); });''',
  '''        "<b>" + esc(g.community || "Mini-grid") + "</b><br>" + esc(g.lga || "") + "<br>" + fmt(g.kw) + " kW · " + esc(g.system || "") + "<br>" + esc(g.status || "") + (g.condition ? " · " + esc(g.condition) : "") + (g.programme ? "<br>" + esc(g.programme) : "")).addTo(im); });
    (A.nep || []).forEach(function (p) { if (p.kind !== "minigrid" || p.in_se4all_layer || p.lat == null) return; var m = nepDot(p); m.setStyle({ fillColor: "#6B3FA0" }); m.addTo(im); });''')
js = b["s"]; k = js.rstrip().rfind("})();")
js = js[:k] + open(os.path.join(HERE, "assets", "js", "projects.js"), encoding="utf-8").read() + "\n})();\n"
open(os.path.join(HERE, "assets", "js", "v7.js"), "w", encoding="utf-8").write(js)

# ================================================================ v6.css -> v7.css
css = open(os.path.join(HERE, "assets", "css", "v6.css"), encoding="utf-8").read() + "\n" + open(os.path.join(HERE, "assets", "css", "projects.css"), encoding="utf-8").read()
open(os.path.join(HERE, "assets", "css", "v7.css"), "w", encoding="utf-8").write(css)
print("build_v7.py, pages_v6b.py, v7.js, v7.css written")
