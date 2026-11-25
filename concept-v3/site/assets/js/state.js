/* State profile v2: big map, side panel, click-for-details, priority communities.
   Data: window.ATLAS (platform extract) + live GeoServer (WMS tiles, WFS lookups on click). */
(function () {
  var P = window.PAGE || {}, A = window.ATLAS || {}, ST = P.state, INF = P.infra || {};
  if (!ST || !window.L || !document.getElementById("sp-map")) return;
  var GS = "https://data.nigeriase4all.gov.ng/geoserver/";
  var fmt = function (n, d) { return n == null || isNaN(n) ? "—" : Number(n).toLocaleString("en-GB", { maximumFractionDigits: d || 0 }); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var km = function (a, b, c, d) { var R = 6371, x = (c - a) * Math.PI / 180, y = (d - b) * Math.PI / 180, h = Math.sin(x / 2) * Math.sin(x / 2) + Math.cos(a * Math.PI / 180) * Math.cos(c * Math.PI / 180) * Math.sin(y / 2) * Math.sin(y / 2); return 2 * R * Math.asin(Math.sqrt(h)); };

  // ---------------- data for this state
  var feat = (A.geo.features || []).filter(function (f) { return f.properties.state === ST; })[0];
  var comm = (A.communities || []).filter(function (c) { return c.state === ST; });
  var fleet = (A.fleet || []).filter(function (g) { return g.state === ST && g.lat != null; });
  var nep = (A.nep || []).filter(function (p) { return p.state === ST && p.lat != null; });
  var status = function (c) {
    if (c.never_functional) return { k: "bad", t: "Grid never worked", col: "#B91C1C" };
    if (c.grid === "no") return { k: "no", t: "No grid", col: "#D97706" };
    if (c.grid === "yes_not_connected_national_grid") return { k: "mid", t: "Grid nearby, not connected", col: "#6D28D9" };
    return { k: "ok", t: "Connected to grid", col: "#1E4E79" };
  };
  var unserved = function (c) { return c.never_functional || c.grid === "no" || c.grid === "yes_not_connected_national_grid"; };
  var clinic = function (c) { return unserved(c) && (c.health || 0) > 0; };
  comm.sort(function (a, b) { return (unserved(b) - unserved(a)) || (clinic(b) - clinic(a)) || ((b.bld || 0) - (a.bld || 0)); });
  comm.forEach(function (c, i) { c._rank = i + 1; });

  // ---------------- map
  var map = L.map("sp-map", { zoomControl: false, preferCanvas: true, minZoom: 5, zoomSnap: .25 });
  L.control.zoom({ position: "bottomright" }).addTo(map);
  L.control.scale({ position: "bottomright", imperial: false }).addTo(map);
  map.attributionControl.setPrefix(false);
  [["wms", 410], ["mask", 420], ["outline", 430], ["pts", 450], ["sel", 460]].forEach(function (p) { var e = map.createPane(p[0]); e.style.zIndex = p[1]; if (p[0] === "wms" || p[0] === "mask" || p[0] === "outline") e.style.pointerEvents = "none"; });
  var BASE = {
    streets: L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap contributors" }),
    satellite: L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", { maxZoom: 19, attribution: "Imagery © Esri" }),
    plain: null
  };
  var base = null, setBase = function (k) {
    if (base) map.removeLayer(base); base = BASE[k]; if (base) base.addTo(map);
    $$("[data-base]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-base") === k); });
    if (mask) mask.setStyle({ fillColor: k === "satellite" ? "#0F172A" : "#FFFFFF", fillOpacity: k === "plain" ? 1 : (k === "satellite" ? .6 : .75) });
  };
  map.attributionControl.addAttribution('Data: <a href="https://data.nigeriase4all.gov.ng/">Nigeria SE4ALL</a>');
  var outline = L.geoJSON(feat, { pane: "outline", renderer: L.svg({ pane: "outline" }), interactive: false, style: { color: "#043D2E", weight: 2.5, fill: false } }).addTo(map);
  var rings = (feat.geometry.type === "Polygon" ? [feat.geometry.coordinates] : feat.geometry.coordinates).map(function (p) { return p[0].map(function (q) { return [q[1], q[0]]; }); });
  var mask = L.polygon([[[-85, -179.9], [-85, 179.9], [85, 179.9], [85, -179.9]]].concat(rings), { pane: "mask", renderer: L.svg({ pane: "mask" }), stroke: false, interactive: false, fillColor: "#fff", fillOpacity: .75 }).addTo(map);
  setBase("streets"); window.SPMAP = map;
  var home = function () { map.fitBounds(outline.getBounds(), { padding: [20, 20] }); };
  home();
  var moved = false; ["pointerdown", "wheel", "touchstart"].forEach(function (ev) { map.getContainer().addEventListener(ev, function () { moved = true; }, { passive: true }); });
  if (window.ResizeObserver) new ResizeObserver(function () { map.invalidateSize(); if (!moved) home(); }).observe($("#sp-map"));

  var wms = function (layer, op) { return L.tileLayer.wms(GS + "wms", { layers: layer, format: "image/png", transparent: true, version: "1.1.1", pane: "wms", opacity: op }); };
  var svg = function (body, s) { return '<svg viewBox="0 0 24 24" width="' + s + '" height="' + s + '">' + body + "</svg>"; };
  var G = {
    sub: '<rect x="3" y="3" width="18" height="18" rx="3" fill="#0F172A" stroke="#fff" stroke-width="2"/><path d="M13 5l-5 8h4l-1 6 5-8h-4z" fill="#FACC15"/>',
    subp: '<rect x="3" y="3" width="18" height="18" rx="3" fill="#fff" stroke="#0F172A" stroke-width="2" stroke-dasharray="3 2"/><path d="M13 6l-4 7h3l-1 5 4-7h-3z" fill="#0F172A"/>',
    plant: '<path d="M12 2l10 19H2z" fill="#7C2D12" stroke="#fff" stroke-width="1.8"/><path d="M12 9v6M9 12h6" stroke="#fff" stroke-width="2"/>',
    mg: function (c) { return '<circle cx="12" cy="12" r="10" fill="' + c + '" stroke="#fff" stroke-width="2"/><path d="M8 13h8M9 10h6M10 16h4" stroke="#fff" stroke-width="1.6"/><circle cx="12" cy="6.5" r="1.6" fill="#FACC15"/>'; },
    nepmg: '<path d="M12 1.5l10.5 10.5L12 22.5 1.5 12z" fill="#7C3AED" stroke="#fff" stroke-width="2"/><path d="M13 6l-4 7h3l-1 5 4-7h-3z" fill="#fff"/>',
    health: '<circle cx="12" cy="12" r="10" fill="#BE185D" stroke="#fff" stroke-width="2"/><path d="M12 7v10M7 12h10" stroke="#fff" stroke-width="2.6"/>',
    edu: '<circle cx="12" cy="12" r="10" fill="#1D4ED8" stroke="#fff" stroke-width="2"/><path d="M6 10l6-3 6 3-6 3zM8.5 11.5v3c2 1.6 5 1.6 7 0v-3" fill="none" stroke="#fff" stroke-width="1.6"/>'
  };
  var icon = function (g, s) { return L.divIcon({ className: "sp-ic", html: svg(g, s), iconSize: [s, s], iconAnchor: [s / 2, s / 2] }); };
  var mgCol = function (g) { return g.status === "Under Construction" ? "#1E4E79" : (g.operational ? "#047857" : "#B91C1C"); };

  var selLayer = L.layerGroup().addTo(map);
  var mk = function (lat, lon, ic, fn) { return L.marker([lat, lon], { pane: "pts", icon: ic, keyboard: false }).on("click", function (e) { L.DomEvent.stop(e); fn(); }); };
  var surveyMarks = {};
  var LAY = {
    settle: wms("se4allWS:cluster_all_new", .6),
    offgrid: wms("se4allWS:cluster_offgrid", .9),
    mv: wms("se4allWS:distribution_line_mv", .9),
    hv: wms("geonode:existing_lines_high_voltage", .95),
    subs: L.layerGroup((INF.substations || []).filter(function (x) { return x.lat != null; }).map(function (x) { return mk(x.lat, x.lon, icon(G.sub, 22), function () { showAsset("Substation", x.name, [["Voltage", (x.kv || "—") + " kV"], ["Status", "Installed"]], x); }); })),
    planned: L.layerGroup((INF.planned_substations || []).filter(function (x) { return x.lat != null; }).map(function (x) { return mk(x.lat, x.lon, icon(G.subp, 20), function () { showAsset("Planned substation", x.name, [["Voltage", (x.kv || "—") + " kV"], ["Status", "Planned"]], x); }); })),
    plants: L.layerGroup((INF.plants || []).filter(function (x) { return x.lat != null; }).map(function (x) { return mk(x.lat, x.lon, icon(G.plant, 24), function () { showAsset("Power plant", x.name, [["Type", x.kind], ["Status", x.status]], x); }); })),
    mg: L.layerGroup(fleet.map(function (g) { return mk(g.lat, g.lon, icon(G.mg(mgCol(g)), 22), function () { showAsset("Mini-grid (platform layer)", g.community || "Mini-grid", [["LGA", g.lga], ["Capacity", fmt(g.kw) + " kW"], ["Connections", fmt(g.conn)], ["System", g.system], ["Status", (g.status || "—") + (g.condition ? " · " + g.condition : "")], ["Programme", g.programme], ["Owner", g.owner]], g); }); })),
    nep: L.layerGroup(nep.map(function (p) { var g = p.kind === "minigrid" ? G.nepmg : (p.kind === "health" ? G.health : G.edu);
      return mk(p.lat, p.lon, icon(g, p.kind === "minigrid" ? 22 : 20), function () { showAsset("NEP project · " + p.short, (p.name || "Project").trim(), [["LGA", p.lga], ["Developer", p.developer], ["Capacity", p.capacity_kw ? fmt(p.capacity_kw) + " kW" : null], ["Customers", p.customers ? fmt(p.customers) : null], ["Status at source", p.status], ["In platform mini-grid layer", p.kind === "minigrid" ? (p.in_se4all_layer ? "Yes" : "Not yet") : null]], p, "Source: Nigeria Electrification Project map (REA)."); }); })),
    survey: L.layerGroup(comm.filter(function (c) { return c.lat != null; }).map(function (c) {
      var s = status(c), m = L.circleMarker([c.lat, c.lon], { pane: "pts", radius: Math.max(5, Math.min(12, Math.sqrt(c.bld || 100) / 4)), color: "#fff", weight: 1.5, fillColor: s.col, fillOpacity: .95 });
      m.on("click", function (e) { L.DomEvent.stop(e); selectCommunity(c, false); }); m.bindTooltip(esc(c.name), { direction: "top", offset: [0, -6] });
      surveyMarks[c.uid] = m; return m; }))
  };
  var DEF = ["offgrid", "mv", "subs", "planned", "plants", "mg", "nep", "survey"];
  DEF.forEach(function (k) { LAY[k].addTo(map); });
  $$("[data-lay]").forEach(function (cb) { var k = cb.getAttribute("data-lay"); cb.checked = map.hasLayer(LAY[k]);
    cb.addEventListener("change", function () { cb.checked ? LAY[k].addTo(map) : map.removeLayer(LAY[k]); }); });
  // swatches in the layers panel
  var SW = { subs: svg(G.sub, 18), planned: svg(G.subp, 18), plants: svg(G.plant, 18), mg: svg(G.mg("#047857"), 18), nep: svg(G.nepmg, 18) };
  $$("[data-sw]").forEach(function (el) { if (SW[el.getAttribute("data-sw")]) el.innerHTML = SW[el.getAttribute("data-sw")]; });
  $$("[data-base]").forEach(function (b) { b.addEventListener("click", function () { setBase(b.getAttribute("data-base")); }); });
  $("#sp-home").addEventListener("click", function () { moved = false; home(); });
  $("#sp-fs").addEventListener("click", function () { var on = document.body.classList.toggle("sp-full"); this.textContent = on ? "Exit full screen" : "Full screen"; setTimeout(function () { map.invalidateSize(); }, 60); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && document.body.classList.contains("sp-full")) $("#sp-fs").click(); });

  // ---------------- side panel
  var tabs = $$(".sp-tabs button"), panes = { list: $("#sp-p-list"), layers: $("#sp-p-layers"), det: $("#sp-p-det") };
  var showTab = function (k) { tabs.forEach(function (t) { t.setAttribute("aria-selected", t.getAttribute("data-tab") === k); }); Object.keys(panes).forEach(function (p) { panes[p].hidden = p !== k; }); };
  tabs.forEach(function (t) { t.addEventListener("click", function () { showTab(t.getAttribute("data-tab")); }); });
  var lastTab = "list";
  var det = function (html) { panes.det.innerHTML = '<button class="sp-back" type="button">← Back</button>' + html; $(".sp-back", panes.det).onclick = function () { selLayer.clearLayers(); showTab(lastTab); }; showTab("det"); panes.det.scrollTop = 0; };
  var dl = function (rows) { return '<dl class="sp-dl">' + rows.filter(function (r) { return r[1] != null && r[1] !== "" && r[1] !== "— kW"; }).map(function (r) { return "<dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>"; };
  var nearest = function (lat, lon, arr) { var b = null; arr.forEach(function (x) { if (x.lat == null) return; var d = km(lat, lon, x.lat, x.lon); if (!b || d < b.d) b = { x: x, d: d }; }); return b; };
  var context = function (lat, lon) {
    var s = nearest(lat, lon, INF.substations || []), m = nearest(lat, lon, fleet.concat(nep.filter(function (p) { return p.kind === "minigrid"; }))), c = nearest(lat, lon, comm);
    return "<h4>Around this point</h4>" + dl([
      ["Nearest substation", s ? s.x.name + " · " + fmt(s.d, 1) + " km" : "None in this state"],
      ["Nearest mini-grid", m ? (m.x.community || m.x.name || "Mini-grid").trim() + " · " + fmt(m.d, 1) + " km" : "None recorded in this state"],
      ["Nearest surveyed community", c ? c.x.name + " · " + fmt(c.d, 1) + " km" : "None surveyed in this state"]]);
  };
  var pin = function (lat, lon) { selLayer.clearLayers(); L.circleMarker([lat, lon], { pane: "sel", radius: 14, color: "#FACC15", weight: 3, fill: false, interactive: false }).addTo(selLayer); };
  var showAsset = function (kind, name, rows, x, note) { if (x.lat != null) pin(x.lat, x.lon);
    det('<div class="sp-det"><div class="sub">' + esc(kind) + "</div><h3>" + esc(name) + "</h3>" + dl(rows) + (x.lat != null ? context(x.lat, x.lon) : "") + (note ? '<p class="sp-empty">' + esc(note) + "</p>" : "") + "</div>"); };

  var verdictFor = function (dkm) {
    if (dkm == null) return "";
    if (dkm <= 1) return '<div class="verdict">Within 1 km of the mapped MV grid. Usually a <b>grid connection</b> or <b>interconnected mini-grid</b> case; check supply quality with the DisCo.</div>';
    if (dkm <= 5) return '<div class="verdict amber">1–5 km from the MV grid. A candidate for <b>grid extension</b> or an <b>interconnected mini-grid</b>, depending on size and demand.</div>';
    return '<div class="verdict red">More than 5 km from the MV grid. A typical <b>off-grid mini-grid</b> or <b>solar home system</b> market.</div>';
  };
  var selectCommunity = function (c, fly) {
    var s = status(c); if (c.lat != null) { pin(c.lat, c.lon); if (fly) map.flyTo([c.lat, c.lon], Math.max(map.getZoom(), 12), { duration: .6 }); }
    $$(".sp-list li").forEach(function (li) { li.classList.toggle("on", li.getAttribute("data-uid") === c.uid); });
    var yn = function (v) { return v == null ? null : (v ? "Yes" : "No"); }, pct = function (v) { return v == null ? null : fmt(v) + "%"; };
    det('<div class="sp-det"><div class="sub">Surveyed community · ' + esc(c.lga || "") + " · " + esc(c.year) + "</div><h3>" + esc(c.name) + '</h3><span class="sp-tag ' + s.k + '">' + s.t + "</span>" + (clinic(c) ? '<span class="sp-tag hc">Clinic without grid</span>' : "") +
      verdictFor(c.mv_km) +
      "<h4>Demand</h4>" + dl([["Buildings", fmt(c.bld)], ["Households with generators", pct(c.hh_gen)], ["Businesses with generators", pct(c.bz_gen)], ["Grinding mills", c.mills != null ? fmt(c.mills) : null], ["Oil presses", c.presses != null ? fmt(c.presses) : null], ["Health facilities", fmt(c.health)], ["Schools", fmt(c.schools)]]) +
      "<h4>Access</h4>" + dl([["To MV grid", c.mv_km != null ? fmt(c.mv_km, 1) + " km" : null], ["Nearest substation", c.sub_name ? c.sub_name + " · " + fmt(c.sub_km, 1) + " km" : null], ["Nearest mini-grid", c.mg_name ? c.mg_name + " · " + fmt(c.mg_km, 1) + " km" : null], ["All-year road access", yn(c.all_year)], ["3G/4G data", yn(c.data_3g4g)], ["Mobile money", yn(c.mobile_money)]]) +
      '<div class="sp-acts"><a class="pri" href="' + P.root + "communities/" + esc(c.slug) + '/index.html">Full survey record</a><a href="' + P.root + "for/developers/index.html#state=" + encodeURIComponent(ST) + '">Compare in Site finder</a></div></div>');
    try { history.replaceState(null, "", "#c=" + c.uid); } catch (e) {}
  };

  // click anywhere: look up the settlement under the cursor (live WFS)
  var busy = $("#sp-busy");
  var wfs = function (t, ex) { return GS + "se4allWS/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=se4allWS:" + t + "&outputFormat=application/json&srsName=EPSG:4326" + ex; };
  var inRing = function (pt, ring) { var x = pt[0], y = pt[1], ins = false; for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) { var xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1]; if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) ins = !ins; } return ins; };
  var polys = function (g) { return g.type === "Polygon" ? [g.coordinates] : (g.type === "MultiPolygon" ? g.coordinates : []); };
  var cen = function (g) { if (g.type === "Point") return g.coordinates; if (g.type === "MultiPoint") return g.coordinates[0]; var r = polys(g)[0][0], x = 0, y = 0; r.forEach(function (p) { x += p[0]; y += p[1]; }); return [x / r.length, y / r.length]; };
  var reqId = 0;
  map.on("click", function (e) {
    var lat = e.latlng.lat, lon = e.latlng.lng, id = ++reqId;
    if (!feat || !polys(feat.geometry).some(function (p) { return inRing([lon, lat], p[0]); })) { det('<div class="sp-det"><h3>Outside ' + esc(ST) + '</h3><p class="sp-empty">Click inside the state outline, or switch state above.</p></div>'); return; }
    pin(lat, lon); busy.classList.add("on");
    var d = .012, bb = [lon - d, lat - d, lon + d, lat + d].join(",") + ",EPSG:4326";
    Promise.all([
      fetch(wfs("cluster_all_simple_new", "&maxFeatures=400&propertyName=geom,cluster_all_id,number_of_buildings,grid_dist_km,area_km2&bbox=" + bb)).then(function (r) { return r.json(); }),
      fetch(wfs("cluster_offgrid_simple", "&maxFeatures=200&bbox=" + bb)).then(function (r) { return r.json(); }).catch(function () { return { features: [] }; })
    ]).then(function (res) {
      if (id !== reqId) return; busy.classList.remove("on");
      var hit = null, best = null;
      res[0].features.forEach(function (f) { if (!f.geometry) return;
        if (polys(f.geometry).some(function (p) { return inRing([lon, lat], p[0]); })) hit = f;
        var c = cen(f.geometry), dd = km(lat, lon, c[1], c[0]); if (!best || dd < best.d) best = { f: f, d: dd }; });
      var f = hit || (best && best.d < .8 ? best.f : null);
      if (!f) { det('<div class="sp-det"><div class="sub">Map point</div><h3>No mapped settlement here</h3><p class="sp-empty">Zoom in and click on a settlement (the shaded areas), a surveyed community or an asset.</p>' + context(lat, lon) + "</div>"); return; }
      var p = f.properties, c = cen(f.geometry), og = null, ogd = 1e9;
      res[1].features.forEach(function (g) { if (!g.geometry) return; var q = g.geometry.type === "Point" ? g.geometry.coordinates : cen(g.geometry), dd = km(c[1], c[0], q[1], q[0]); if (dd < ogd) { ogd = dd; og = g.properties; } });
      if (ogd > 1) og = null;
      selLayer.clearLayers(); L.geoJSON(f, { pane: "sel", interactive: false, pointToLayer: function (g, ll) { return L.circleMarker(ll, { radius: 14, color: "#FACC15", weight: 3, fill: false }); }, style: { color: "#FACC15", weight: 3, fillOpacity: .08 } }).addTo(selLayer);
      var dens = p.area_km2 ? p.number_of_buildings / p.area_km2 : null;
      det('<div class="sp-det"><div class="sub">Settlement · cluster ' + esc(p.cluster_all_id) + (og ? " · SE4ALL off-grid list" : "") + "</div><h3>" + fmt(p.number_of_buildings) + " buildings</h3>" +
        verdictFor(p.grid_dist_km) +
        dl([["Distance to MV grid", p.grid_dist_km != null ? fmt(p.grid_dist_km, 1) + " km" : null], ["Area", p.area_km2 != null ? fmt(p.area_km2, 2) + " km²" : null], ["Buildings per km²", dens ? fmt(dens) : null]]) +
        (og ? "<h4>Off-grid settlement record</h4>" + dl([["Schools", fmt(og.number_of_schools || 0)], ["Health centres", fmt(og.number_of_healthcenters || 0)], ["Markets", fmt(og.number_of_markets || 0)], ["Large buildings", og.percentage_large_building != null ? fmt(og.percentage_large_building) + "%" : null]]) : "") +
        context(c[1], c[0]) +
        '<div class="sp-acts"><a class="pri" href="' + P.root + "for/developers/index.html#state=" + encodeURIComponent(ST) + '">Assess in Site finder</a><button type="button" id="sp-zoom">Zoom here</button></div></div>');
      $("#sp-zoom").onclick = function () { map.flyTo([c[1], c[0]], 15); };
    }).catch(function () { if (id !== reqId) return; busy.classList.remove("on"); det('<div class="sp-det"><h3>Could not reach the data portal</h3><p class="sp-empty">The settlement lookup uses the live GeoServer. Try again in a moment.</p>' + context(lat, lon) + "</div>"); });
  });

  // ---------------- communities list (side panel) + priority table
  var F = { prio: unserved, clinic: clinic, broken: function (c) { return c.never_functional; }, all: function () { return true; } };
  var cur = "prio", q = "";
  var row = function (c) { var s = status(c);
    return '<li data-uid="' + esc(c.uid) + '"><div class="t"><b title="' + esc(c.name) + '">' + esc(c.name) + "</b><span>" + fmt(c.bld) + " bldgs</span></div>" +
      '<div class="m">' + esc(c.lga || "—") + (c.mv_km != null ? " · " + fmt(c.mv_km, 1) + " km to MV grid" : "") + " · " + esc(c.year) + "</div>" +
      '<span class="sp-tag ' + s.k + '">' + s.t + "</span>" + ((c.health || 0) > 0 ? '<span class="sp-tag hc">' + fmt(c.health) + " clinic" + (c.health > 1 ? "s" : "") + "</span>" : "") + ((c.schools || 0) > 0 ? '<span class="sp-tag">' + fmt(c.schools) + " school" + (c.schools > 1 ? "s" : "") + "</span>" : "") + "</li>"; };
  var listEl = $("#sp-list"), cnt = $("#sp-count");
  var renderList = function () {
    if (!listEl) return;
    var rows = comm.filter(F[cur]).filter(function (c) { return !q || (c.name + " " + (c.lga || "")).toLowerCase().indexOf(q) > -1; });
    cnt.textContent = rows.length + " of " + comm.length + " surveyed communities";
    listEl.innerHTML = rows.map(row).join("") || '<li class="sp-empty" style="cursor:default">No community matches.</li>';
    $$("li[data-uid]", listEl).forEach(function (li) { li.addEventListener("click", function () { var c = comm.filter(function (x) { return x.uid === li.getAttribute("data-uid"); })[0]; lastTab = "list"; selectCommunity(c, true); }); });
    // map: dim communities outside the filter
    comm.forEach(function (c) { var m = surveyMarks[c.uid]; if (m) m.setStyle({ fillOpacity: F[cur](c) ? .95 : .2, opacity: F[cur](c) ? 1 : .3 }); });
  };
  var setFilter = function (k) { cur = k; $$("[data-cf]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-cf") === k); }); renderList(); };
  $$("[data-cf]").forEach(function (b) { b.addEventListener("click", function () { setFilter(b.getAttribute("data-cf")); }); });
  var se = $("#sp-q"); if (se) se.addEventListener("input", function () { q = se.value.trim().toLowerCase(); renderList(); });
  renderList();
  // buttons elsewhere on the page that drive the map
  $$("[data-show]").forEach(function (b) { b.addEventListener("click", function () { if (!map.hasLayer(LAY.survey)) { LAY.survey.addTo(map); var cb = $('[data-lay="survey"]'); if (cb) cb.checked = true; } setFilter(b.getAttribute("data-show")); showTab("list"); $("#map").scrollIntoView({ behavior: "smooth" }); }); });

  var tb = $("#sp-tbody");
  if (tb) {
    var all = false, pri = comm.filter(unserved);
    var renderT = function () {
      var rows = all ? comm : pri.slice(0, 10);
      tb.innerHTML = rows.map(function (c) { var s = status(c);
        return '<tr data-uid="' + esc(c.uid) + '"><td class="rk">' + c._rank + "</td><td><b>" + esc(c.name) + '</b><br><span class="sp-empty" style="font-size:13px">' + esc(c.lga || "—") + '</span></td><td><span class="sp-tag ' + s.k + '">' + s.t + "</span></td>" +
          '<td class="n">' + fmt(c.bld) + '</td><td class="n">' + fmt(c.health) + " / " + fmt(c.schools) + '</td><td class="n">' + (c.bz_gen != null ? fmt(c.bz_gen) + "%" : "—") + '</td><td class="n">' + (c.mv_km != null ? fmt(c.mv_km, 1) + " km" : "—") + '</td><td class="n">' + esc(c.year) + "</td></tr>"; }).join("");
      $$("tr", tb).forEach(function (tr) { tr.addEventListener("click", function () { var c = comm.filter(function (x) { return x.uid === tr.getAttribute("data-uid"); })[0]; $("#map").scrollIntoView({ behavior: "smooth" }); lastTab = "list"; setTimeout(function () { selectCommunity(c, true); }, 250); }); });
      var mb = $("#sp-tmore"); if (mb) { mb.hidden = comm.length <= 10 && pri.length <= 10; mb.textContent = all ? "Show the top 10 only" : "Show all " + comm.length + " surveyed communities"; }
    };
    var mb = $("#sp-tmore"); if (mb) mb.addEventListener("click", function () { all = !all; renderT(); });
    renderT();
    var csv = $("#sp-csv");
    if (csv) csv.addEventListener("click", function () {
      var cols = [["_rank", "Priority"], ["name", "Community"], ["lga", "LGA"], ["grid", "Grid at survey"], ["never_functional", "Grid never functional"], ["bld", "Buildings"], ["hh_gen", "Households with generators %"], ["bz_gen", "Businesses with generators %"], ["mills", "Grinding mills"], ["health", "Health facilities"], ["schools", "Schools"], ["mv_km", "To MV grid km"], ["sub_name", "Nearest substation"], ["sub_km", "Substation km"], ["mg_name", "Nearest mini-grid"], ["mg_km", "Mini-grid km"], ["all_year", "All-year road"], ["data_3g4g", "3G/4G"], ["mobile_money", "Mobile money"], ["year", "Survey year"], ["lat", "Latitude"], ["lon", "Longitude"]];
      var cell = function (v) { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
      var txt = cols.map(function (c) { return c[1]; }).join(",") + "\n" + comm.map(function (r) { return cols.map(function (c) { return cell(r[c[0]]); }).join(","); }).join("\n");
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([txt], { type: "text/csv" })); a.download = ST.toLowerCase().replace(/[^a-z0-9]+/g, "-") + "-surveyed-communities.csv"; document.body.appendChild(a); a.click(); a.remove();
    });
  }

  // deep link: #c=<uid>
  var m = /#c=([^&]+)/.exec(location.hash);
  if (m) { var c0 = comm.filter(function (x) { return x.uid === decodeURIComponent(m[1]); })[0]; if (c0) setTimeout(function () { selectCommunity(c0, true); }, 300); }
})();
