# New v5 pages. Executed inside build_v5.py's namespace (uses its helpers and data).
COURSES = [  # from the learning platform's public course API
    ("course-v1:se4all+1+1", "Nigeria SE4ALL introduction course", "The project, its activities and how the data is gathered.", "Self-paced", "asset-v1:se4all+1+1+type@asset+block@thumb.PNG", "Start here"),
    ("course-v1:NigeriaSE4ALL+2+v1", "QGIS training", "The fundamental components and capabilities of QGIS, the free desktop GIS.", "Self-paced", "asset-v1:NigeriaSE4ALL+2+v1+type@asset+block@QGIS-course-thumb.png", "Core skill"),
    ("course-v1:NigeriaSE4ALL+3+202303", "Project development", "Data-driven project planning for the private sector.", "Self-paced", "asset-v1:NigeriaSE4ALL+3+202303+type@asset+block@NESP_training_3_thumbnail.PNG", "Apply it"),
    ("course-v1:NigeriaSE4ALL+MPTN01+2020", "Mapathon introduction", "The basics of OpenStreetMap, to gather and use ground-truth data.", "Instructor-led", "asset-v1:NigeriaSE4ALL+MPTN01+2020+type@asset+block@MicrosoftTeams-image.png", "Contribute"),
]
LEARN = "https://learning.nigeriase4all.gov.ng/"

def researchers():
    cat = X["catalogue"]
    tot = sum(c["features"] or 0 for c in cat)
    rows = "".join(
        f'<tr><td><a class="a-go" href="{c["page"]}" target="_blank" rel="noopener">{e(c["title"])}</a><br><code class="a-code">{e(c["layer"])}</code></td>'
        f'<td class="n" data-v="{c["features"] or 0}">{f0(c["features"])}</td>'
        f'<td>{" · ".join(f"<a href=\'{u}\'>{n}</a>" for n, u in (("SHP", c["shapefile"]), ("GeoJSON", c["geojson"]), ("CSV", c["csv"])) if u)}</td></tr>' for c in cat)
    wfs_ex = PORTAL + "geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=se4allWS:minigrids&outputFormat=application/json"
    body = phero('<a href="../../index.html">Home</a> <span>/</span> <span>Researchers and data users</span>', "Briefing for researchers and data users",
                 "Every layer behind the platform, open and documented",
                 "The full catalogue with feature counts and direct downloads, live access through WMS and WFS, and what to watch for in the data.") + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Open layers", f0(len(cat)), "layers", f"on the data portal, holding {f0(tot)} features in total.", "GeoNode catalogue", "good", '<a class="a-go" href="#catalogue">Browse the catalogue</a>')}
{card("Settlement clusters", "454,267", "clusters", "with building counts, area and recorded distance to grid: the national base layer.", "cluster_all_new")}
{card("Field survey", f0(sv["total"]), "communities", "each with about 100 fields: grid status, generators, fuel prices, businesses, crops, services, network and access.", "cluster_offgrid_survey")}
{card("Live access", "WMS · WFS", "", "Stream any layer into QGIS, ArcGIS or your own code; WFS returns GeoJSON, CSV, Excel, GML and shapefiles.", "GeoServer", "", f'<a class="a-go" href="{WFS_CAP}">WFS capabilities</a>')}
{card("Data quality", f'{XN["duplicate_substations_removed"]}', "duplicate points", f"in the installed-substation layer ({XN['source_substation_points']} points, {XN['substations'] + 0} unique in Nigeria's states); the power-plant layers repeat each plant too.", "our checks, " + PULLED, "warn", '<a class="a-go" href="#quality">All data notes</a>')}
{card("Licences", "Not specified", "", "No licence is set on the portal's datasets yet. Ask before republishing; this platform will show licences once they are set.", "GeoNode metadata", "alert")}
</div></div></section>
<section class="sec field" id="catalogue"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Catalogue</span><h2>All {len(cat)} layers</h2><p class="sub">Click a column to sort. Download links come straight from the portal.</p></div><a class="link" href="{PORTAL}" target="_blank" rel="noopener">Open the data portal</a></div>
<div class="a-tbl"><table class="a-t"><thead><tr><th>Layer</th><th class="n">Features</th><th>Download</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Access</span><h2>Three ways in</h2></div></div>
<div class="a-steps">
<div class="a-stepl"><b>1 · Download</b><span>Each layer as a shapefile, GeoJSON, CSV or Excel file from the catalogue above or the portal. Guide: <a class="a-go" href="{PORTAL}documents/29/download">how to download geodata</a>.</span></div>
<div class="a-stepl"><b>2 · Connect QGIS</b><span>Add a WMS or WFS connection with <code class="a-code">{PORTAL}geoserver/ows</code>. Guide: <a class="a-go" href="{PORTAL}documents/28/download">how to use WMS/WFS</a>.</span></div>
<div class="a-stepl"><b>3 · Query from code</b><span>Request GeoJSON directly, for example all mini-grids: <a class="a-go" href="{wfs_ex}" style="word-break:break-all">WFS GetFeature</a>.</span></div>
</div></div></section>
<section class="sec field" id="quality"><div class="wrap"><h2 style="margin-bottom:14px">What to watch for in the data</h2><ul class="a-notes">
<li>Installed substations ({XN["source_substation_points"]} points) and thermal and hydro plants are each listed twice in the source layers; de-duplicate by name before counting.</li>
<li>The settlement layer's recorded distance to grid pre-dates recent MV mapping. For surveyed communities we recalculated it against <code>distribution_line_mv</code>: the median is {sorted(v["mv_km"] for v in X["communities"].values())[len(X["communities"])//2]:.1f} km to the nearest MV line.</li>
<li>The mini-grid layer holds {inv["fleet_n"]} sites and does not yet include every programme mini-grid.</li>
<li>Field-survey records date from 2019 to 2026; new communities are still being added.</li>
<li>Dataset licences and update dates are not yet set on the portal (all layers show the same re-publish date).</li></ul>
<p style="margin-top:14px">Found something else? <a class="a-go" href="mailto:{EMAIL}?subject=Data%20quality">Tell the data team</a></p></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Next steps</span><h2>Go further</h2></div></div>
{steps([("QGIS training", "Free, self-paced course on the learning platform.", LEARN + "courses/course-v1:NigeriaSE4ALL+2+v1/about"), ("Request or share data", "Ask the data team for data that is not here.", f"mailto:{EMAIL}?subject=Data%20request"), ("State profiles", "The same data summarised for each state.", "../../states/index.html")])}</div></section>'''
    page("for/researchers/index.html", "Data briefing | Nigeria Electrification Atlas", "Catalogue, downloads, WMS/WFS access and data-quality notes for researchers.", body, "researcher")

def learners():
    cards = "".join(
        f'<a class="a-course" href="{LEARN}courses/{cid}/about" target="_blank" rel="noopener"><div class="a-cimg"><img src="{LEARN}{img}" alt="" loading="lazy"></div>'
        f'<div class="a-cbd"><span class="a-pill ok">Step {i+1} · {tag}</span><h3>{t}</h3><p>{d}</p><span class="a-muted" style="font-size:14px">{pace} · free</span></div></a>'
        for i, (cid, t, d, pace, img, tag) in enumerate(COURSES))
    gis = post("this-is-a-test-article-about-something-going-on-in-the-minigrid-sector"); mp = post("nigeria-se4-all-mapathon"); tr = post("training-se4all-platform")
    body = phero('<a href="../../index.html">Home</a> <span>/</span> <span>Students and GIS careers</span>', "Welcome, future GIS professionals",
                 "Start your career in GIS with Nigeria's electrification data",
                 "Free courses, real national datasets and a community of mappers. No background needed: if you can use a computer, you can start today.",
                 f'<div class="hero-cta" style="margin-top:24px"><a class="btn btn-leaf" href="{LEARN}" target="_blank" rel="noopener">Register free on the learning platform</a><a class="btn btn-ghost" href="#path">See the learning path</a></div>') + f'''
<section class="sec"><div class="wrap"><div class="a-cards">
{card("Free courses", "4", "courses", "on the Learning Platform, from an introduction to QGIS and data-driven project development.", "learning.nigeriase4all.gov.ng", "good")}
{card("Mapathon community", "280+", "participants", "students and professionals from across Nigeria have joined the mapathons, with 400+ mappers in the Slack workspace.", "mapathon blog post")}
{card("Real impact", "75,000+", "buildings mapped", "in off-grid areas of Kogi, Yobe and Imo, now part of the data used for electrification planning.", "mapathon blog post")}
</div></div></section>
<section class="sec field" id="path"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Learning path</span><h2>From first map to professional skills</h2><p class="sub">Take the courses in order, then put your skills to work at a mapathon.</p></div><a class="link" href="{LEARN}" target="_blank" rel="noopener">All courses</a></div>
<div class="a-courses">{cards}</div></div></section>
<section class="sec"><div class="wrap"><div class="a-split">
<div><span class="a-kick">Why GIS</span><h2>Skills the energy sector needs</h2><p class="sub" style="margin-top:10px">Electrification planning runs on maps: finding communities without power, measuring their distance to the grid, estimating demand and siting mini-grids. The platform's own team learned these skills through the same courses and mapathons.</p>
<ul class="a-notes" style="margin-top:16px"><li>Read and analyse settlement, grid and survey data in QGIS.</li><li>Map buildings from satellite imagery on OpenStreetMap.</li><li>Turn data into project decisions for developers and government.</li></ul></div>
<div><span class="a-kick">Read first</span><h2>Beginner guides</h2>
<div class="a-steps" style="grid-template-columns:1fr;margin-top:14px">
<a class="a-stepl" href="{POST_URL(gis)}"><b>GIS For The Rest Of Us</b><span>A step-by-step introduction to GIS, whatever your background.</span></a>
<a class="a-stepl" href="{POST_URL(mp)}"><b>Mapathons: mapping for improved access to electricity</b><span>How the events work and how to take part.</span></a>
<a class="a-stepl" href="{POST_URL(tr)}"><b>Training on the Central Data Management System</b><span>The four-module training developed for the Federal Ministry of Power.</span></a>
</div></div></div></div></section>
<section class="sec field"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Voices from the community</span><h2>What mappers say</h2></div></div>
<div class="a-cards">
<div class="a-card"><p style="font-size:18px;color:var(--ink)">“The mapathon went beyond my expectation, the introduction was on point and very informative as well.”</p><div class="a-src">Mapathon participant</div></div>
<div class="a-card"><p style="font-size:18px;color:var(--ink)">“The experience was awesome and I would like to take part in the subsequent events to increase my knowledge and expertise on the subject matter.”</p><div class="a-src">Mapathon participant</div></div>
<div class="a-card"><p style="font-size:18px;color:var(--ink)">“Everything about the project is awesome.”</p><div class="a-src">Mapathon participant</div></div>
</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head"><div><span class="a-kick">Next steps</span><h2>Start today</h2></div></div>
{steps([("Register for free", "Create your account on the Learning Platform.", LEARN), ("Watch past mapathons", "Recordings on the Nigeria SE4ALL YouTube channel.", "https://www.youtube.com/channel/UCGLZ__z2xdwSiyb15veGRQA/featured"), ("Practise with real data", "Download layers from the data briefing.", "../researchers/index.html")])}</div></section>
<section class="sec field" id="notes"><div class="wrap"><ul class="a-notes"><li>Course list from the Learning Platform's public course catalogue. Community figures from the mapathon blog post (August 2022).</li></ul></div></section>'''
    body = re.sub(r'<p class="a-stamp">.*?</p>', "", body, count=1, flags=re.S)  # no data stamp on the welcome page
    page("for/learners/index.html", "Students and GIS careers | Nigeria Electrification Atlas", "Free GIS courses, mapathons and a learning path for students and new professionals.", body, "learner")
