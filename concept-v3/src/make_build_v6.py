# build_v6.py = build_v5.py + checked patches (USP-led homepage, fresh data, recalculated distances, new pages).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "build_v5.py"), encoding="utf-8").read()
def P(old, new, count=1):
    global src
    n = src.count(old)
    if n != count: sys.exit(f"patch failed ({n}x): {old[:110]!r}")
    src = src.replace(old, new)

# ---- data: everything from this concept's own fresh pull
P('V2 = os.path.join(os.path.dirname(ROOT), "nesp-website-v2", "data")', 'V2 = os.path.join(ROOT, "data")')
P('V3 = os.path.join(os.path.dirname(ROOT), "nesp-website-v3", "data")', 'V3 = os.path.join(ROOT, "data")\nSURVEY = json.load(open(os.path.join(ROOT, "data", "survey_full.json"))); HEALTH = json.load(open(os.path.join(ROOT, "data", "data_health.json")))')
P('from icons import ROLE_ICONS, WEBMAP_ICONS, CHEVRON, EXT', 'from icons import ROLE_ICONS, WEBMAP_ICONS, USP_ICONS, CHEVRON, EXT')
P('''for i, c in enumerate(I3["communities"]):
    c.update(X["communities"].get(str(i), {}))''', '''for c in I3["communities"]:
    c.update(X["communities"].get(c["uid"], {}))
    c["slug"] = (re.sub(r"[^a-z0-9]+", "-", (c["name"] or "community").lower()).strip("-")[:40] + "-" + c["uid"]).lower()''')
for a, b in [('"v5.css"', '"v6.css"'), ('"v5.js"', '"v6.js"')]:
    P(a, b, count=2)
P('assets/css/v5.css', 'assets/css/v6.css'); P('assets/js/v5.js', 'assets/js/v6.js', count=2)

# ---- header + footer: the field survey gets its own entry
P('''f'<a href="{{R}}index.html#data">Data</a><a href="{ORIG}/blog">Blog</a><a href="{ORIG}/about">About</a>', count=2)''',
  '''f'<a href="{{R}}communities/index.html">Field survey</a><a href="{{R}}index.html#data">Data</a><a href="{ORIG}/blog">Blog</a><a href="{ORIG}/about">About</a>', count=2)''')
P('''<a href="{{R}}index.html#explore">Map by state</a>''', '''<a href="{{R}}communities/index.html">Field survey explorer</a><a href="{{R}}data-health/index.html">Data health</a><a href="{{R}}index.html#explore">Map by state</a>''')

# ---- home: USP-led hero and figures strip
P('''    s = must(s, \'\'\'const words = "Planning Nigeria's electrification from the ground up.".split(' ');\'\'\', \'\'\'const words = "The right electrification evidence for every decision-maker.".split(' ');\'\'\')
    s = must(s, 'const hlWords = new Set([1, 2]);', 'const hlWords = new Set([2, 3]);')''',
  '''    s = must(s, \'\'\'const words = "Planning Nigeria's electrification from the ground up.".split(' ');\'\'\', \'\'\'const words = "Ground truth for Nigeria's electrification, open to everyone.".split(' ');\'\'\')
    s = must(s, 'const hlWords = new Set([1, 2]);', 'const hlWords = new Set([0, 1]);')''')
P('''<div class="eyebrow">Electrification evidence · Nigeria</div>''', '''<div class="eyebrow">Field-verified electrification data · Nigeria</div>''')
P("""'<p class="lead">The platform maps every settlement, grid line, surveyed community and mini-grid in Nigeria. Instead of searching through layers, choose who you are and read a briefing calculated from the latest data.</p>'""",
  """f'<p class="lead">{sv["total"]} communities surveyed on the ground, {f0(NAT2["mv_km"])} km of field-mapped grid, and every one of Nigeria\\'s {f0(NAT2["clusters"])} settlements measured against it. Choose who you are and get answers, not just layers.</p>'""")
P('''    s = must(s, '<a class="btn btn-leaf" href="#tools">Explore the map', '<a class="btn btn-leaf" href="#briefings">Find your briefing')''',
  '''    s = must(s, '<a class="btn btn-leaf" href="#tools">Explore the map', '<a class="btn btn-leaf" href="#survey">Inside the field survey')''')
P('''    s = must(s, '<a class="btn btn-ghost" href="about.html">About the platform</a>', '<a class="btn btn-ghost" href="#explore">Explore by state</a>')''',
  '''    s = must(s, '<a class="btn btn-ghost" href="about.html">About the platform</a>', '<a class="btn btn-ghost" href="#briefings">Who are you?</a>')
    s = must(s, r'<div class="l">states with the medium-voltage grid mapped</div>\\s*<div class="s">11 kV and 33 kV · NESP field mapping</div>',
             f'<div class="l">states with a field-mapped medium-voltage grid</div><div class="s">{f0(NAT2["mv_km"])} km · 11 and 33 kV</div>', regex=True)''')
P('''<div class="l">communities surveyed on site</div><div class="s">NESP field surveys, 2019–2026</div>''',
  '''<div class="l">communities surveyed on the ground</div><div class="s">About 100 facts each · 2019–2026</div>''')
P('''    s = must(s, r'<span data-count="3.2" data-dec="1">3.2</span>M<sup>\\+</sup></div>\\s*<div class="l">off-grid buildings mapped</div>\\s*<div class="s">Building footprints</div>',
             f'<span data-count="{off_total/1e6:.1f}" data-dec="1">{off_total/1e6:.1f}</span>M<sup>+</sup></div><div class="l">buildings in off-grid settlements</div><div class="s">SE4ALL off-grid settlement layer</div>', regex=True)''',
  '''    s = must(s, r'<span data-count="3.2" data-dec="1">3.2</span>M<sup>\\+</sup></div>\\s*<div class="l">off-grid buildings mapped</div>\\s*<div class="s">Building footprints</div>',
             f'<span data-count="{NAT2["clusters"]}">{f0(NAT2["clusters"])}</span></div><div class="l">settlements measured against the current grid</div><div class="s">Recalculated nightly</div>', regex=True)''')

# ---- home: USP + field-survey sections before the briefings; drop OSIP and the old method section
P('''    i = s.index('<section class="sec what" id="about">'); s = s[:i] + NEW + s[i:]''',
  '''    i = s.index('<section class="sec what" id="about">'); s = s[:i] + usp_sections() + NEW + s[i:]''')
P('''    s = s[:a0] + METHOD + s[a1:]''', '''    s = s[:a0] + s[a1:]          # the USP section now carries "how the data is made"
    o0 = s.index('<section class="osip"'); o1 = s.index("</section>", o0) + len("</section>")
    s = s[:o0] + s[o1:]          # OSIP removed from the homepage (kept in the briefings' next steps)''')
P('''<p class="fine">The webmap opens with the same distance and size filters. Distances are those recorded in the settlement layer.</p>''',
  '''<p class="fine">The webmap opens with the same distance and size filters. Distances are recalculated against the field-mapped MV grid.</p>''')
P('''for bad in ["[contact@", "CC BY", "19 lessons", "Last updated", "blog.html", "about.html", "mini-grids.html", "Federal Ministry of Education", "ground up"]:''',
  '''for bad in ["[contact@", "CC BY", "19 lessons", "Last updated", "blog.html", "about.html", "mini-grids.html", "Federal Ministry of Education", "ground up", "os-card", "osip-wind"]:''')

# ---- wording: distances are now recalculated (fix at source), not the old recorded values
P('''"&gt;5 km" uses the distance recorded in the settlement layer, which may not yet reflect recently mapped MV lines.</li>''',
  '''Distances are recalculated for every settlement against the field-mapped MV grid (<code>distribution_line_mv</code>).</li>''')
P('''are more than 5 km from the mapped grid. Distances come from the settlement layer and may not reflect recently mapped lines.</div>''',
  '''are more than 5 km from the field-mapped grid, recalculated against the current MV layer.</div>''')
P('''<li>Distance to grid is the value recorded for each settlement in the settlement layer.</li>''',
  '''<li>Distance to grid is recalculated for every settlement against the current MV layer (accurate to about 50 m).</li>''')
P('''"&gt;5 km" uses the distance recorded in the settlement layer.</li>''', '''"&gt;5 km" uses distances recalculated against the field-mapped MV grid.</li>''')

# ---- new pages
P('exec(open(os.path.join(HERE, "pages_v5.py"), encoding="utf-8").read())',
  'exec(open(os.path.join(HERE, "pages_v5.py"), encoding="utf-8").read())\nexec(open(os.path.join(HERE, "pages_v6.py"), encoding="utf-8").read())')
P('home(); states_index(); developers(); investors(); researchers(); learners()',
  'home(); states_index(); developers(); investors(); researchers(); learners(); communities_index(); community_pages(); data_health()')
# usp_sections() must exist before home() runs: pages_v6 is exec'd before the calls above.
open(os.path.join(HERE, "build_v6.py"), "w", encoding="utf-8").write(src)
print("build_v6.py written")
