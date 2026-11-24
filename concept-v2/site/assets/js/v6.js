/* v4 data components. All figures come from window.ATLAS (generated from the public GeoServer). */
(function () {
  var A = window.ATLAS || {}, P = window.PAGE || {};
  var WMS = "https://data.nigeriase4all.gov.ng/geoserver/wms";
  var fmt = function (n) { return n == null || isNaN(n) ? "—" : Number(n).toLocaleString("en-GB", { maximumFractionDigits: 0 }); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var slug = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); };
  var stateUrl = function (s) { return P.root + "states/" + slug(s) + "/index.html"; };
  var RAMP = ["#F6EBD6", "#EBCB91", "#D9A445", "#B9770E", "#7A4E07"], BRK = [10, 20, 30, 40];
  var colour = function (v) { var i = 0; while (i < BRK.length && v >= BRK[i]) i++; return RAMP[i]; };
  var share = function (s) { return s.buildings ? 100 * s.buildings_over_5km / s.buildings : 0; };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  // ---------- inner-page header (home uses the design's own script)
  if (P.kind !== "home") {
    var hdr = document.getElementById("hdr"), dd = document.getElementById("dd"), mnav = document.getElementById("mnav"), burger = document.querySelector(".burger");
    var onScroll = function () { hdr.classList.toggle("solid", scrollY > 40 || hdr.classList.contains("menu-open")); };
    addEventListener("scroll", onScroll, { passive: true }); onScroll();
    if (dd) { var b = dd.querySelector(".dd-btn"), setDD = function (o) { dd.classList.toggle("open", o); b.setAttribute("aria-expanded", o); };
      var h1 = 0;
      b.addEventListener("click", function (e) { e.stopPropagation(); setDD(Date.now() - h1 < 500 ? true : !dd.classList.contains("open")); });
      dd.addEventListener("mouseenter", function () { h1 = Date.now(); setDD(true); }); dd.addEventListener("mouseleave", function () { setDD(false); });
      document.addEventListener("click", function (e) { if (!dd.contains(e.target)) setDD(false); }); }
    if (burger && mnav) burger.addEventListener("click", function () { var o = mnav.hidden; mnav.hidden = !o; hdr.classList.toggle("menu-open", o); burger.setAttribute("aria-expanded", o); });
    var yr = document.getElementById("yr"); if (yr) yr.textContent = new Date().getFullYear();
  }

  // ---------- "Explore webmaps" menu (all pages)
  var d2 = document.getElementById("dd2");
  if (d2) { var b2 = d2.querySelector(".a-dd2-btn"), set2 = function (o) { d2.classList.toggle("open", o); b2.setAttribute("aria-expanded", o); };
    var h2 = 0;
    b2.addEventListener("click", function (e) { e.stopPropagation(); set2(Date.now() - h2 < 500 ? true : !d2.classList.contains("open")); });
    d2.addEventListener("mouseenter", function () { h2 = Date.now(); set2(true); }); d2.addEventListener("mouseleave", function () { set2(false); });
    document.addEventListener("click", function (e) { if (!d2.contains(e.target)) set2(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") set2(false); }); }

  // ---------- state jump selects
  document.querySelectorAll("[data-state-go]").forEach(function (el) {
    var sel = el.tagName === "SELECT" ? el : el.querySelector("select");
    var go = function () { if (sel.value) { store.set("atlas.state", sel.value); location.href = stateUrl(sel.value); } };
    if (el.tagName === "FORM") el.addEventListener("submit", function (e) { e.preventDefault(); go(); }); else sel.addEventListener("change", go);
  });

  // ---------- maps (no third-party basemap; our own boundaries + live GeoServer layers)
  function baseMap(el, interactiveBase) {
    var m = L.map(el, { scrollWheelZoom: false });
    [["wms", 410], ["mask", 420], ["outline", 430], ["pts", 440]].forEach(function (p) { var e = m.createPane(p[0]); e.style.zIndex = p[1]; if (p[0] !== "pts") e.style.pointerEvents = "none"; });
    m.attributionControl.setPrefix(false);
    m.attributionControl.addAttribution('Data: <a href="https://data.nigeriase4all.gov.ng/">Nigeria SE4ALL GeoNode</a>');
    m.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
    if (!interactiveBase) L.geoJSON(A.geo, { interactive: false, style: { color: "#C9CFC9", weight: 1, fillColor: "#fff", fillOpacity: 1 } }).addTo(m);
    return m;
  }
  function wms(layer, op) { return L.tileLayer.wms(WMS, { layers: layer, format: "image/png", transparent: true, version: "1.1.1", pane: "wms", opacity: op || .8 }); }
  function dot(c, r, color, html) { return L.circleMarker([c.lat, c.lon], { pane: "pts", radius: r, color: "#fff", weight: 1.5, fillColor: color, fillOpacity: .95 }).bindPopup(html); }

  // choropleth (home + states index)
  var cm = document.getElementById("a-nat-map");
  if (cm && window.L) {
    var map = baseMap(cm, true), hb = document.querySelector(".a-hover");
    var gj = L.geoJSON(A.geo, {
      style: function (f) { var s = A.states[f.properties.state]; return { weight: 1, color: "#fff", fillOpacity: .88, fillColor: s ? colour(share(s)) : "#ddd" }; },
      onEachFeature: function (f, l) {
        var s = A.states[f.properties.state];
        l.on("mouseover", function () { l.setStyle({ weight: 2.5, color: "#0F172A" }); l.bringToFront();
          if (hb && s) { hb.style.display = "block"; hb.innerHTML = "<b>" + esc(s.state) + "</b>" + share(s).toFixed(1) + "% of buildings &gt;5 km from mapped grid<br>" + fmt(s.offgrid_buildings) + " off-grid buildings · " + s.surveyed + " surveyed<br><span class='a-muted'>Click for the state profile</span>"; } });
        l.on("mouseout", function () { gj.resetStyle(l); if (hb) hb.style.display = "none"; });
        l.on("click", function () { location.href = stateUrl(f.properties.state); });
      } }).addTo(map);
    wms("se4allWS:distribution_line_mv", .5).addTo(map);
    map.fitBounds(gj.getBounds(), { padding: [10, 10] });
  }

  // site-finder (exact lookup in a pre-computed table) -> deep link into the live off-grid webmap with the same filters
  var ff = document.getElementById("a-finder");
  if (ff && A.finder) {
    var st = ff.querySelector("[name=state]"), dd2 = ff.querySelector("[name=dist]"), nn = ff.querySelector("[name=bldg]");
    var oc = document.getElementById("f-c"), ob = document.getElementById("f-b"), go = document.getElementById("f-go"), sp = document.getElementById("f-sp");
    var run = function () {
      var t = st.value ? A.finder.states[st.value] : A.finder.national, i = A.finder.D.indexOf(+dd2.value), j = A.finder.N.indexOf(+nn.value);
      oc.textContent = fmt(t.c[i][j]); ob.textContent = fmt(t.b[i][j]);
      go.href = "https://apps.nigeriase4all.gov.ng/minigrid-offgrid?buildings_min=" + nn.value + "&buildings_max=100000&grid_dist_min=" + dd2.value + "&grid_dist_max=200";
      sp.innerHTML = st.value ? '<a class="btn btn-ghost" href="' + stateUrl(st.value) + '">' + esc(st.value) + " state profile</a>" : "";
    };
    [st, dd2, nn].forEach(function (x) { x.addEventListener("change", run); }); run();
  }

  // ---------- sortable tables + filters
  function sortable(t) {
    var ths = t.querySelectorAll("th");
    ths.forEach(function (th, i) { th.addEventListener("click", function () {
      var asc = !th.classList.contains("asc"); ths.forEach(function (x) { x.classList.remove("asc", "desc"); }); th.classList.add(asc ? "asc" : "desc");
      var rows = [].slice.call(t.tBodies[0].rows), num = th.classList.contains("n");
      rows.sort(function (a, b) {
        var x = a.cells[i].getAttribute("data-v"), y = b.cells[i].getAttribute("data-v");
        x = x == null ? a.cells[i].textContent : x; y = y == null ? b.cells[i].textContent : y;
        if (num) { x = parseFloat(x); y = parseFloat(y); x = isNaN(x) ? -1e12 : x; y = isNaN(y) ? -1e12 : y; return asc ? x - y : y - x; }
        return asc ? x.localeCompare(y) : y.localeCompare(x); });
      rows.forEach(function (r) { t.tBodies[0].appendChild(r); }); }); });
  }
  document.querySelectorAll("table.a-t").forEach(sortable);
  document.querySelectorAll(".a-filters").forEach(function (fs) {
    var t = document.getElementById(fs.getAttribute("data-for"));
    fs.querySelectorAll("button").forEach(function (b) { b.addEventListener("click", function () {
      fs.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
      var v = b.getAttribute("data-f"); [].forEach.call(t.tBodies[0].rows, function (r) { r.style.display = (v === "all" || (" " + r.getAttribute("data-f") + " ").indexOf(" " + v + " ") > -1) ? "" : "none"; }); }); });
  });

  // ---------- state profile map
  if (P.kind === "state" && window.L) {
    store.set("atlas.state", P.state);
    var m2 = baseMap("a-state-map");
    var feat = A.geo.features.filter(function (f) { return f.properties.state === P.state; })[0];
    var outline = L.geoJSON(feat, { pane: "outline", style: { color: "#0F172A", weight: 2, fill: false } }).addTo(m2);
    var holes = (feat.geometry.type === "Polygon" ? [feat.geometry.coordinates] : feat.geometry.coordinates).map(function (p) { return p[0].map(function (q) { return [q[1], q[0]]; }); });
    L.polygon([[[-90, -180], [-90, 180], [90, 180], [90, -180]]].concat(holes), { pane: "mask", stroke: false, fillColor: "#F4F7F5", fillOpacity: .82, interactive: false }).addTo(m2);
    var cs = A.communities.filter(function (c) { return c.state === P.state && c.lat != null; });
    var lay = {
      settle: wms("se4allWS:cluster_all_new", .7), offgrid: wms("se4allWS:cluster_offgrid", .9), mv: wms("se4allWS:distribution_line_mv", .85),
      hv: wms("geonode:existing_lines_high_voltage", .9),
      subs: L.layerGroup(((P.infra || {}).substations || []).map(function (x) { return L.marker([x.lat, x.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='a-sq'></span>", iconSize: [12, 12] }) }).bindPopup("<b>" + esc(x.name) + "</b><br>Installed substation · " + (x.kv || "—") + " kV"); })),
      planned: L.layerGroup(((P.infra || {}).planned_substations || []).map(function (x) { return L.marker([x.lat, x.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='a-sq a-sq-p'></span>", iconSize: [12, 12] }) }).bindPopup("<b>" + esc(x.name) + "</b><br>Planned substation · " + (x.kv || "—") + " kV"); })),
      plants: L.layerGroup(((P.infra || {}).plants || []).map(function (x) { return L.marker([x.lat, x.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='a-tri'></span>", iconSize: [14, 14] }) }).bindPopup("<b>" + esc(x.name) + "</b><br>" + esc(x.kind) + " power plant · " + esc(x.status)); })),
      mg: L.layerGroup(A.fleet.filter(function (g) { return g.state === P.state && g.lat != null; }).map(function (g) {
        return dot(g, 8, g.status === "Under Construction" ? "#1E4E79" : (g.operational ? "#065F46" : "#9F2A2A"), "<b>" + esc(g.community || "Mini-grid") + "</b><br>" + fmt(g.kw) + " kW · " + esc(g.system || "") + "<br>" + esc(g.status || "") + (g.condition ? " · " + esc(g.condition) : "")); })),
      survey: L.layerGroup(cs.map(function (c) {
        return dot(c, 5, c.never_functional ? "#9F2A2A" : (c.grid === "no" ? "#B7791F" : "#1E4E79"), "<b>" + esc(c.name) + "</b><br>" + esc(c.lga || "") + " · surveyed " + esc(c.year) + "<br>" + fmt(c.bld) + " buildings" + (c.health ? "<br>" + fmt(c.health) + " health facilities" : "")); }))
    };
    ["settle", "mv", "hv", "subs", "mg", "survey"].forEach(function (k) { lay[k].addTo(m2); });
    m2.fitBounds(outline.getBounds(), { padding: [14, 14] });
    document.querySelectorAll("[data-layer]").forEach(function (cb) { var k = cb.getAttribute("data-layer"); cb.checked = m2.hasLayer(lay[k]);
      cb.addEventListener("change", function () { cb.checked ? lay[k].addTo(m2) : m2.removeLayer(lay[k]); }); });
  }

  // ---------- developer briefing
  if (P.kind === "developer" && window.L) {
    var f = document.getElementById("a-criteria"), cnt = document.getElementById("a-ready-count"), body = document.querySelector("#a-ready tbody"), more = document.getElementById("a-ready-more");
    var dm = baseMap("a-dev-map"), layer = L.layerGroup().addTo(dm); wms("se4allWS:distribution_line_mv", .25).addTo(dm);
    var current = [], showAll = false, LIMIT = 15;
    var runD = function () {
      var minB = +f.minb.value, minG = +f.ming.value, road = f.road.checked, pay = f.pay.checked, s = f.state.value, mvd = f.mvd.value;
      var mvOk = function (c) { var d = c.mv_km; if (mvd === "any") return true; if (d == null) return false; return mvd === "gt5" ? d > 5 : mvd === "gt10" ? d > 10 : d <= 5; };
      current = A.communities.filter(function (c) { return c.grid === "no" && (c.bld || 0) >= minB && (c.bz_gen || 0) >= minG && (!road || c.all_year) && (!pay || c.mobile_money || c.data_3g4g) && (!s || c.state === s) && mvOk(c); })
        .sort(function (a, b) { return (b.bld || 0) - (a.bld || 0); });
      cnt.textContent = fmt(current.length);
      more.style.display = current.length > LIMIT ? "" : "none";
      more.textContent = showAll ? "Show top " + LIMIT + " only" : "Show all " + current.length + " communities";
      body.innerHTML = (showAll ? current : current.slice(0, LIMIT)).map(function (c) {
        return "<tr><td><b>" + esc(c.name) + "</b><br><span class='a-muted'>" + esc(c.lga || "") + "</span></td><td><a class='a-go' href='" + stateUrl(c.state) + "'>" + esc(c.state) + "</a></td><td class='n' data-v='" + (c.bld || 0) + "'>" + fmt(c.bld) + "</td><td class='n' data-v='" + (c.bz_gen || 0) + "'>" + (c.bz_gen != null ? c.bz_gen + "%" : "—") + "</td><td class='n' data-v='" + (c.mills || 0) + "'>" + fmt(c.mills) + "</td><td class='n' data-v='" + (c.presses || 0) + "'>" + fmt(c.presses) + "</td><td class='n' data-v='" + (c.health || 0) + "'>" + fmt(c.health) + "</td><td class='n' data-v='" + (c.mv_km == null ? "" : c.mv_km) + "'>" + (c.mv_km == null ? "—" : c.mv_km + " km") + "</td><td class='n' data-v='" + (c.sub_km == null ? "" : c.sub_km) + "'>" + (c.sub_km == null ? "—" : c.sub_km + " km") + "<br><span class='a-muted' style='font-size:12.5px'>" + esc(c.sub_name || "") + "</span></td><td>" + (c.mobile_money ? "<span class='a-pill ok'>Mobile money</span> " : "") + (c.data_3g4g ? "<span class='a-pill ok'>3G/4G</span>" : "") + "</td><td class='n'>" + esc(c.year) + "</td></tr>";
      }).join("") || "<tr><td colspan='11' class='a-muted'>No surveyed community meets these criteria. Try relaxing one of them.</td></tr>";
      layer.clearLayers();
      current.forEach(function (c) { if (c.lat != null) dot(c, 4 + Math.min(10, Math.sqrt(c.bld || 0) / 6), "#B7791F", "<b>" + esc(c.name) + "</b><br>" + esc(c.lga || "") + ", " + esc(c.state) + "<br>" + fmt(c.bld) + " buildings" + (c.mv_km != null ? "<br>" + c.mv_km + " km to nearest MV line" : "")).addTo(layer); });
      var pts = current.filter(function (c) { return c.lat != null; });
      if (pts.length && s) dm.fitBounds(L.latLngBounds(pts.map(function (c) { return [c.lat, c.lon]; })).pad(.25)); else dm.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
    };
    more.addEventListener("click", function () { showAll = !showAll; runD(); });
    f.addEventListener("change", runD); f.addEventListener("submit", function (e) { e.preventDefault(); });
    document.getElementById("a-ready-csv").addEventListener("click", function () {
      var cols = [["name", "Community"], ["lga", "LGA"], ["state", "State"], ["bld", "Buildings"], ["mv_km", "Nearest MV line km"], ["sub_name", "Nearest substation"], ["sub_km", "Nearest substation km"], ["bz_gen", "Businesses with generators %"], ["hh_gen", "Households with generators %"], ["mills", "Grinding mills"], ["presses", "Oil presses"], ["health", "Health facilities"], ["schools", "Schools"], ["mobile_money", "Mobile money"], ["data_3g4g", "3G/4G"], ["all_year", "All-year road access"], ["year", "Survey year"], ["lat", "Latitude"], ["lon", "Longitude"]];
      var q = function (v) { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
      var out = [cols.map(function (c) { return c[1]; }).join(",")].concat(current.map(function (r) { return cols.map(function (c) { return q(r[c[0]]); }).join(","); })).join("\n");
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([out], { type: "text/csv" })); a.download = "build-ready-communities.csv"; a.click();
    });
    runD();
  }

  // ---------- field survey explorer
  if (P.kind === "communities" && window.L) {
    var cf = document.getElementById("a-cf"), tb = document.querySelector("#a-ct tbody"), cc = document.getElementById("a-cc"), cm2 = document.getElementById("a-cmore");
    var cmap = baseMap("a-comm-map"), clay = L.layerGroup().addTo(cmap); wms("se4allWS:distribution_line_mv", .3).addTo(cmap);
    var K = P.criteria, cur = [], all = false, LIM = 50;
    var isReady = function (c) { return c.grid === "no" && (c.bld || 0) >= K.min_buildings && (c.bz_gen || 0) >= K.min_business_genset_pct && c.all_year && (c.mobile_money || c.data_3g4g); };
    var gridLabel = function (c) { return c.never_functional ? "<span class='a-pill bad'>Never functional</span>" : c.grid === "no" ? "<span class='a-pill mid'>No grid</span>" : c.grid === "yes_connected_national_grid" ? "<span class='a-pill ok'>Connected</span>" : "<span class='a-pill'>Present, not connected</span>"; };
    var runC = function () {
      var q = cf.q.value.trim().toLowerCase(), st = cf.state.value, g = cf.grid.value, cl = cf.clinic.checked, rd = cf.ready.checked;
      cur = A.communities.filter(function (c) {
        if (q && ((c.name || "") + " " + (c.lga || "")).toLowerCase().indexOf(q) < 0) return false;
        if (st && c.state !== st) return false;
        if (g === "no" && c.grid !== "no") return false; if (g === "grid" && c.grid === "no") return false; if (g === "broken" && !c.never_functional) return false;
        if (cl && !(c.health > 0)) return false; if (rd && !isReady(c)) return false; return true;
      }).sort(function (a, b) { return (b.bld || 0) - (a.bld || 0); });
      cc.textContent = fmt(cur.length);
      cm2.style.display = cur.length > LIM ? "" : "none"; cm2.textContent = all ? "Show first " + LIM + " only" : "Show all " + cur.length + " communities";
      tb.innerHTML = (all ? cur : cur.slice(0, LIM)).map(function (c) {
        return "<tr><td><a class='a-go' style='font-weight:600' href='" + c.slug + "/index.html'>" + esc(c.name) + "</a><br><span class='a-muted'>" + esc(c.lga || "") + "</span></td><td>" + esc(c.state) + "</td><td class='n' data-v='" + (c.bld || 0) + "'>" + fmt(c.bld) + "</td><td>" + gridLabel(c) + "</td><td class='n' data-v='" + (c.mv_km == null ? "" : c.mv_km) + "'>" + (c.mv_km == null ? "—" : c.mv_km + " km") + "</td><td class='n' data-v='" + (c.bz_gen || 0) + "'>" + (c.bz_gen == null ? "—" : c.bz_gen + "%") + "</td><td class='n' data-v='" + (c.health || 0) + "'>" + fmt(c.health) + "</td><td class='n'>" + esc(c.year) + "</td></tr>";
      }).join("") || "<tr><td colspan='8' class='a-muted'>No community matches. Try removing a filter.</td></tr>";
      clay.clearLayers();
      cur.forEach(function (c) { if (c.lat == null) return; dot(c, 5, c.never_functional ? "#9F2A2A" : c.grid === "no" ? "#B7791F" : "#1E4E79", "<b><a href='" + c.slug + "/index.html'>" + esc(c.name) + "</a></b><br>" + esc(c.lga || "") + ", " + esc(c.state) + "<br>" + fmt(c.bld) + " buildings").addTo(clay); });
      var pts = cur.filter(function (c) { return c.lat != null; });
      if (pts.length && pts.length < A.communities.length) cmap.fitBounds(L.latLngBounds(pts.map(function (c) { return [c.lat, c.lon]; })).pad(.2)); else cmap.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
    };
    cf.addEventListener("input", runC); cf.addEventListener("change", runC); cm2.addEventListener("click", function () { all = !all; runC(); });
    document.getElementById("a-ccsv").addEventListener("click", function () {
      var cols = [["name", "Community"], ["lga", "LGA"], ["state", "State"], ["bld", "Buildings"], ["grid", "Grid at survey"], ["never_functional", "Grid never functional"], ["mv_km", "Nearest MV line km"], ["sub_name", "Nearest substation"], ["sub_km", "Nearest substation km"], ["bz_gen", "Businesses with generators %"], ["hh_gen", "Households with generators %"], ["mills", "Grinding mills"], ["presses", "Oil presses"], ["health", "Health facilities"], ["schools", "Schools"], ["mobile_money", "Mobile money"], ["data_3g4g", "3G/4G"], ["all_year", "All-year road access"], ["year", "Survey year"], ["lat", "Latitude"], ["lon", "Longitude"]];
      var q = function (v) { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
      var out = [cols.map(function (c) { return c[1]; }).join(",")].concat(cur.map(function (r) { return cols.map(function (c) { return q(r[c[0]]); }).join(","); })).join("\n");
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([out], { type: "text/csv" })); a.download = "surveyed-communities.csv"; a.click();
    });
    runC();
  }

  // ---------- one community: small map
  if (P.kind === "community" && window.L && P.point) {
    var om = baseMap("a-one-map"); wms("se4allWS:distribution_line_mv", .9).addTo(om);
    var pt = { lat: P.point[0], lon: P.point[1] }; dot(pt, 9, "#B7791F", "<b>" + esc(P.name) + "</b>").addTo(om);
    var bnds = [[pt.lat, pt.lon]];
    if (P.sub) { L.marker([P.sub.lat, P.sub.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='a-sq'></span>", iconSize: [12, 12] }) }).bindPopup("<b>" + esc(P.sub.name) + "</b><br>Nearest installed substation").addTo(om); bnds.push([P.sub.lat, P.sub.lon]); }
    if (bnds.length > 1) om.fitBounds(L.latLngBounds(bnds).pad(.3), { maxZoom: 12 }); else om.setView(bnds[0], 11);
  }

  // ---------- investor fleet map
  if (P.kind === "investor" && window.L) {
    var im = baseMap("a-inv-map");
    A.fleet.forEach(function (g) { if (g.lat == null) return;
      dot(g, 4 + Math.min(10, Math.sqrt(g.kw || 1) / 2), g.status === "Under Construction" ? "#1E4E79" : (g.operational ? "#065F46" : "#9F2A2A"),
        "<b>" + esc(g.community || "Mini-grid") + "</b><br>" + esc(g.lga || "") + "<br>" + fmt(g.kw) + " kW · " + esc(g.system || "") + "<br>" + esc(g.status || "") + (g.condition ? " · " + esc(g.condition) : "") + (g.programme ? "<br>" + esc(g.programme) : "")).addTo(im); });
  }
})();
