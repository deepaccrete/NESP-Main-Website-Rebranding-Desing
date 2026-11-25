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
  function nepDot(p) { var c = { minigrid: "#065F46", health: "#9F2A2A", education: "#1E4E79" }[p.kind];
    var h = "<b>" + esc(p.name || "Project") + "</b><br>" + esc(p.short) + (p.lga ? " · " + esc(p.lga) : "") + (p.state ? ", " + esc(p.state) : "") +
      (p.developer ? "<br>" + esc(p.developer) : "") + (p.capacity_kw ? "<br>" + fmt(p.capacity_kw) + " kW" : "") + (p.customers ? " · " + fmt(p.customers) + " customers" : "") +
      (p.status ? "<br>" + esc(p.status) : "") + (p.kind === "minigrid" ? "<br><small>" + (p.in_se4all_layer ? "Also in the platform's mini-grid layer" : "Not yet in the platform's mini-grid layer") + "</small>" : "") +
      (p.state_mismatch ? "<br><small>Listed at source in " + esc(p.stated_state) + "</small>" : "") + "<br><small>Source: NEP project map (REA)</small>";
    return dot(p, p.kind === "minigrid" ? 4 + Math.min(9, Math.sqrt(p.capacity_kw || 1) / 2) : 5, c, h); }
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
      nep: L.layerGroup((A.nep || []).filter(function (p) { return p.state === P.state && p.lat != null; }).map(nepDot)),
      survey: L.layerGroup(cs.map(function (c) {
        return dot(c, 5, c.never_functional ? "#9F2A2A" : (c.grid === "no" ? "#B7791F" : "#1E4E79"), "<b>" + esc(c.name) + "</b><br>" + esc(c.lga || "") + " · surveyed " + esc(c.year) + "<br>" + fmt(c.bld) + " buildings" + (c.health ? "<br>" + fmt(c.health) + " health facilities" : "")); }))
    };
    ["settle", "mv", "hv", "subs", "mg", "nep", "survey"].forEach(function (k) { lay[k].addTo(m2); });
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
    (A.nep || []).forEach(function (p) { if (p.kind !== "minigrid" || p.in_se4all_layer || p.lat == null) return; var m = nepDot(p); m.setStyle({ fillColor: "#6B3FA0" }); m.addTo(im); });
  }

  // ---------- v7: NEP projects page
  if (P.kind === "projects" && window.L) {
    var pf = document.getElementById("a-pf"), ptb = document.querySelector("#a-pt tbody"), pc = document.getElementById("a-pc"), pmore = document.getElementById("a-pmore");
    var pmap = baseMap("a-proj-map"); pmap.attributionControl.addAttribution('Projects: <a href="https://nep.rea.gov.ng/">NEP, REA</a>'); var play = L.layerGroup().addTo(pmap), shsl = L.layerGroup();
    var N = A.nep || [], pcur = [], pall = false, PLIM = 60;
    (A.shs || []).forEach(function (s) { if (s.lat == null) return;
      L.circleMarker([s.lat, s.lon], { pane: "pts", radius: 5 + Math.sqrt(s.connections || 0) / 22, color: "#B7791F", weight: 2, fillColor: "#B7791F", fillOpacity: .25 })
        .bindPopup("<b>" + esc(s.state) + "</b><br>" + fmt(s.connections) + " solar home system connections<br><small>State total · NEP project map (REA)</small>").addTo(shsl); });
    var kindFromHash = { "#minigrid": "minigrid", "#health": "health", "#education": "education" }[location.hash];
    if (kindFromHash) pf.kind.value = kindFromHash;
    if (location.hash === "#shs") pf.shs.checked = true;
    var runP = function () {
      var q = pf.q.value.trim().toLowerCase(), k = pf.kind.value, st = pf.state.value, dv = pf.dev.value, nw = pf.newonly.checked;
      pcur = N.filter(function (p) {
        if (k && p.kind !== k) return false; if (st && p.state !== st) return false;
        if (dv && !(p.kind === "minigrid" && p.developer === dv)) return false;
        if (nw && !(p.kind === "minigrid" && !p.in_se4all_layer)) return false;
        if (q && ((p.name || "") + " " + (p.lga || "") + " " + (p.state || "") + " " + (p.developer || "")).toLowerCase().indexOf(q) < 0) return false;
        return true;
      }).sort(function (a, b) { return (b.capacity_kw || 0) - (a.capacity_kw || 0); });
      pc.textContent = fmt(pcur.length);
      pmore.style.display = pcur.length > PLIM ? "" : "none"; pmore.textContent = pall ? "Show first " + PLIM + " only" : "Show all " + pcur.length + " projects";
      ptb.innerHTML = (pall ? pcur : pcur.slice(0, PLIM)).map(function (p) {
        return "<tr><td><b>" + esc(p.name || "—") + "</b>" + (p.lga ? "<br><span class='a-muted'>" + esc(p.lga) + "</span>" : "") + (p.state_mismatch ? " <span class='a-pill bad'>Listed in " + esc(p.stated_state) + "</span>" : "") + "</td><td>" + esc(p.short) +
          (p.kind === "minigrid" && !p.in_se4all_layer ? " <span class='a-pill mid'>New to platform</span>" : "") + "</td><td>" + (p.state ? "<a class='a-go' href='../states/" + slug(p.state) + "/index.html'>" + esc(p.state) + "</a>" : "—") + "</td><td>" + esc(p.developer || "—") +
          "</td><td class='n' data-v='" + (p.capacity_kw || 0) + "'>" + (p.capacity_kw ? fmt(p.capacity_kw) + " kW" : "—") + "</td><td class='n' data-v='" + (p.customers || 0) + "'>" + fmt(p.customers) + "</td><td>" + esc(p.status || "—") + "</td></tr>";
      }).join("") || "<tr><td colspan='7' class='a-muted'>No project matches. Try removing a filter.</td></tr>";
      play.clearLayers(); pcur.forEach(function (p) { if (p.lat != null) nepDot(p).addTo(play); });
      pf.shs.checked ? shsl.addTo(pmap) : pmap.removeLayer(shsl);
      var pts = pcur.filter(function (p) { return p.lat != null; });
      if (pts.length && pts.length < N.length) pmap.fitBounds(L.latLngBounds(pts.map(function (p) { return [p.lat, p.lon]; })).pad(.2), { maxZoom: 10 }); else pmap.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
    };
    pf.addEventListener("input", runP); pf.addEventListener("change", runP); pmore.addEventListener("click", function () { pall = !pall; runP(); });
    document.getElementById("a-pcsv").addEventListener("click", function () {
      var cols = [["name", "Project"], ["short", "Programme"], ["developer", "Developer"], ["lga", "LGA"], ["state", "State (by location)"], ["stated_state", "State (as listed)"], ["capacity_kw", "Capacity kW"], ["customers", "Customers"], ["status", "Status at source"], ["in_se4all_layer", "In platform mini-grid layer"], ["lat", "Latitude"], ["lon", "Longitude"]];
      var q = function (v) { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
      var out = ["# Source: Nigeria Electrification Project map, nep.rea.gov.ng (Rural Electrification Agency). No licence stated at source.", cols.map(function (c) { return c[1]; }).join(",")]
        .concat(pcur.map(function (r) { return cols.map(function (c) { return q(r[c[0]]); }).join(","); })).join("\n");
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([out], { type: "text/csv" })); a.download = "nep-projects.csv"; a.click();
    });
    runP();
  }


  // ================= v8: map-first workspaces (mini-grid hub, developers, investors)
  if (window.MG && window.L && ["hub", "dev8", "inv8"].indexOf(P.kind) > -1) {
  (function () {   // own scope: block-level vars must not overwrite the header menu's variables (e.g. dd)
    var M = window.MG, Dm = {}; Object.keys(M.demo).forEach(function (k) { Dm[k] = M.demo[k]; });
    var SC = { "Operational / commissioned": "#065F46", "Under construction / approved": "#1E4E79", "In evaluation": "#E8A317", "Not operational": "#9F2A2A", "Not stated": "#94A3B8" };
    var SRCC = { platform: "#065F46", eae: "#1E4E79", nep: "#6B3FA0" };
    var C = M.cand.map(function (r) { var o = {}; M.ccols.forEach(function (k, i) { o[k] = r[i]; }); return o; });
    var MGBY = {}; M.sites.forEach(function (s) { MGBY[s.id] = s; });
    var cr = L.canvas({ pane: "pts", padding: .4 });
    var f1 = function (n) { return n == null || isNaN(n) ? "—" : Number(n).toLocaleString("en-GB", { maximumFractionDigits: 1 }); };
    var money = function (n) { return n >= 1e6 ? "US$ " + f1(n / 1e6) + " m" : "US$ " + fmt(n); };
    var calc = function (bld) { var c = bld * Dm.conn_per_bld, kwh = c * Dm.kwh_day, kwp = kwh / (Dm.yield_ * Dm.pr || 1);
      return { conn: c, kwh: kwh, kwp: kwp, capex: kwp * Dm.capex_kwp, grant: Math.min(kwp * Dm.capex_kwp, c * Dm.grant_conn) }; };
    Dm.use_wb = true;
    // per-site figures: World Bank DRE Atlas demand where the settlement matched (connections, kWh/day, PV yield), demo assumptions otherwise
    var OWN = P.variant === "own", SVB = function (c) { return c.slug && window.SVR ? window.SVR.byId[c.slug] : null; };
    var calcC = function (c) {
      if (!OWN && Dm.use_wb && c.dre_kwh_day != null && c.dre_conn) { var yd = c.dre_pv ? c.dre_pv / 365 : Dm.yield_, kwp = c.dre_kwh_day / (yd * Dm.pr || 1);
        return { conn: c.dre_conn, kwh: c.dre_kwh_day, kwp: kwp, capex: kwp * Dm.capex_kwp, grant: Math.min(kwp * Dm.capex_kwp, c.dre_conn * Dm.grant_conn), wb: true }; }
      var k = calc(c.bld); k.wb = false; return k; };
    var sumC = function (rows) { var t = { conn: 0, kwh: 0, kwp: 0, capex: 0, grant: 0, wb: 0 }; rows.forEach(function (c) { var k = calcC(c); t.conn += k.conn; t.kwh += k.kwh; t.kwp += k.kwp; t.capex += k.capex; t.grant += k.grant; if (k.wb) t.wb++; }); return t; };
    var cname = function (c) { var dn = c.dre_name && !/^Location #/.test(c.dre_name) ? c.dre_name : null;   // DRE uses "Location #n" when it has no name
      return (OWN ? c.nesp_name : dn) || (SVB(c) || {}).n || idl(c); };
    var idl = function (c) { return c.sv_cid != null ? "Survey cluster " + c.sv_cid : "Off-grid cluster " + c.cid; };
    var strip = function (a) { [1, 2, 3].forEach(function (i) { var x = a[i - 1] || ["—", ""]; document.getElementById("w-n" + i).textContent = x[0]; document.getElementById("w-l" + i).textContent = x[1]; }); };
    var hav = function (a, b, c, d) { var r = Math.PI / 180, x = Math.sin((c - a) * r / 2), y = Math.sin((d - b) * r / 2); return 12742 * Math.asin(Math.sqrt(x * x + Math.cos(a * r) * Math.cos(c * r) * y * y)); };
    var save = function (rows, cols, name, kind, note) {
      var out, type;
      if (kind === "geojson") {
        out = JSON.stringify({ type: "FeatureCollection", note: note, features: rows.map(function (r) { var p = {}; cols.forEach(function (c) { if (c[0] !== "lat" && c[0] !== "lon") p[c[0]] = r[c[0]]; });
          return { type: "Feature", geometry: { type: "Point", coordinates: [r.lon, r.lat] }, properties: p }; }) }); type = "application/geo+json";
      } else {
        var q = function (v) { v = v == null ? "" : Array.isArray(v) ? v.join(";") : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
        out = ["# " + note, cols.map(function (c) { return c[1]; }).join(",")].concat(rows.map(function (r) { return cols.map(function (c) { return q(r[c[0]]); }).join(","); })).join("\n"); type = "text/csv";
      }
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([out], { type: type })); a.download = name + "." + (kind === "geojson" ? "geojson" : "csv"); document.body.appendChild(a); a.click(); a.remove();
    };
    document.addEventListener("click", function (ev) { var a = ev.target.closest && ev.target.closest("a[href='#w-assume']"); if (a) { var d = document.getElementById("w-assume"); if (d) d.open = true; } });
    var onAssume = function (fn) { document.querySelectorAll("#w-assume input[data-k]").forEach(function (inp) { inp.addEventListener("input", function () { if (inp.type === "checkbox") { Dm[inp.getAttribute("data-k")] = inp.checked; fn(); return; } var v = parseFloat(inp.value); if (!isNaN(v)) { Dm[inp.getAttribute("data-k")] = v; fn(); } }); }); };
    var mgDetail = function (s) {
      var recs = (s.recs || []).map(function (r) { return "<tr><td><i class='w-dot' style='background:" + SRCC[r.src] + "'></i>" + esc(M.srcl[r.src]) + "</td><td>" + esc(r.name || "—") + "</td><td class='n'>" + f1(r.kw) + "</td><td class='n'>" + fmt(r.conn) + "</td><td>" + esc(r.status || "—") + "</td></tr>"; }).join("");
      return "<span class='a-kick'>Mini-grid · " + esc(s.id) + "</span><h3>" + esc(s.name || "Mini-grid") + "</h3><p class='w-sub'>" + esc([s.lga, s.state].filter(Boolean).join(", ")) + "</p>" +
        "<dl class='w-dl2'><dt>Status</dt><dd><span class='w-st' style='background:" + SC[s.status] + "'></span>" + esc(s.status) + "</dd><dt>Developer</dt><dd>" + esc(s.developer || "—") + "</dd><dt>Capacity</dt><dd>" + f1(s.kw) + " kW</dd><dt>Connections</dt><dd>" + fmt(s.connections) + "</dd><dt>Programme</dt><dd>" + esc(s.programme || "—") + "</dd></dl>" +
        "<h4>What each source says</h4><div class='a-tbl'><table class='a-t w-small'><thead><tr><th>Source</th><th>Name</th><th class='n'>kW</th><th class='n'>Conn.</th><th>Status</th></tr></thead><tbody>" + recs + "</tbody></table></div>";
    };

    // ---------- mini-grid hub
    if (P.kind === "hub") {
      var hm = baseMap("h-map"), hl = L.layerGroup().addTo(hm), ol = L.layerGroup(), hf = document.getElementById("h-f"), hd = document.getElementById("h-detail"), hcur = [];
      M.osm.forEach(function (o) { L.circleMarker([o.lat, o.lon], { renderer: cr, radius: 5, color: "#475569", weight: 1.5, fill: false })
        .on("click", function () { hd.innerHTML = "<span class='a-kick'>OpenStreetMap · possible mini-grid</span><h3>" + esc(o.name || "Unnamed solar plant") + "</h3><dl class='w-dl2'><dt>Operator</dt><dd>" + esc(o.operator || "—") + "</dd><dt>Size</dt><dd>" + (o.kw ? f1(o.kw) + " kW" : "not tagged") + "</dd><dt>State</dt><dd>" + esc(o.state || "—") + "</dd><dt>Nearest known mini-grid</dt><dd>" + f1(o.near_known_km) + " km</dd></dl><p class='sm a-muted'>Mapped by OpenStreetMap contributors (ODbL). Not counted in the totals. <a class='a-go' href='https://www.openstreetmap.org/" + o.osm + "' target='_blank' rel='noopener'>View on OSM</a></p>"; }).addTo(ol); });
      var runH = function () {
        var q = hf.q.value.trim().toLowerCase(), st = hf.state.value, ss = hf.status.value, dv = hf.dev.value, only = hf.only.checked, byS = hf.colour.value === "source";
        var on = [].filter.call(hf.querySelectorAll("input[name=src]"), function (x) { return x.checked; }).map(function (x) { return x.value; });
        hcur = M.sites.filter(function (s) {
          if (st && s.state !== st) return false; if (ss && s.status !== ss) return false; if (dv && s.developer !== dv) return false;
          if (!s.sources.some(function (x) { return on.indexOf(x) > -1; })) return false; if (only && s.sources.length > 1) return false;
          if (q && [s.name, s.developer, s.lga, s.project_title].join(" ").toLowerCase().indexOf(q) < 0) return false; return true; });
        hl.clearLayers();
        hcur.forEach(function (s) { var col = byS ? ["#94A3B8", "#E8A317", "#1E4E79", "#065F46"][Math.min(3, s.sources.length)] : SC[s.status];
          L.circleMarker([s.lat, s.lon], { renderer: cr, radius: 4 + Math.min(9, Math.sqrt(s.kw || 4) / 2), color: "#fff", weight: 1.2, fillColor: col, fillOpacity: .92 })
            .on("click", function () { hd.setAttribute("data-site", s.id); hd.innerHTML = mgDetail(s) + "<p><button type='button' class='btn btn-outline' id='h-back'>Back to the summary</button></p>"; document.getElementById("h-back").onclick = function () { hd.removeAttribute("data-site"); runH(); }; }).addTo(hl); });
        hf.osm.checked ? ol.addTo(hm) : hm.removeLayer(ol);
        document.getElementById("h-legend").innerHTML = byS ? "<span><i style='background:#E8A317'></i>1 source</span><span><i style='background:#1E4E79'></i>2 sources</span><span><i style='background:#065F46'></i>3 sources</span>" :
          Object.keys(SC).map(function (k) { return "<span><i style='background:" + SC[k] + "'></i>" + k + "</span>"; }).join("");
        if (!hd.getAttribute("data-site")) {
          var bySt = {}; hcur.forEach(function (s) { bySt[s.status] = (bySt[s.status] || 0) + 1; });
          var bySrc = { platform: 0, eae: 0, nep: 0 }; hcur.forEach(function (s) { s.sources.forEach(function (x) { bySrc[x]++; }); });
          var mx = Math.max(1, hcur.length);
          hd.innerHTML = "<span class='a-kick'>This selection</span><h3>" + fmt(hcur.length) + " sites</h3><div class='w-hubsum'><h4>By status</h4>" +
            Object.keys(SC).map(function (k) { var n = bySt[k] || 0; return "<div class='row'><span>" + k + "</span><b>" + n + "</b></div><div class='bar'><i style='width:" + (100 * n / mx) + "%;background:" + SC[k] + "'></i></div>"; }).join("") +
            "<h4>Reported by</h4>" + Object.keys(bySrc).map(function (k) { return "<div class='row'><span><i class='w-dot' style='background:" + SRCC[k] + "'></i> " + M.srcl[k] + "</span><b>" + bySrc[k] + "</b></div>"; }).join("") +
            "</div><p class='sm a-muted' style='margin-top:12px'>Click a site on the map to compare what each source says.</p>";
        }
        var kw = hcur.reduce(function (a, s) { return a + (s.kw || 0); }, 0), cn = hcur.reduce(function (a, s) { return a + (s.connections || 0); }, 0);
        strip([[fmt(hcur.length), "mini-grid sites"], [f1(kw / 1000) + " MW", "recorded capacity"], [fmt(cn), "connections reported"]]);
        if (hcur.length && hcur.length < M.sites.length) hm.fitBounds(L.latLngBounds(hcur.map(function (s) { return [s.lat, s.lon]; })).pad(.25), { maxZoom: 10 }); else hm.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
      };
      hf.addEventListener("input", runH); hf.addEventListener("change", runH);
      var HC = [["id", "Site ID"], ["name", "Name"], ["developer", "Developer"], ["state", "State"], ["lga", "LGA"], ["kw", "Capacity kW"], ["connections", "Connections"], ["status", "Status"], ["status_raw", "Status as published"], ["programme", "Programme"], ["sources", "Sources"], ["source_ids", "Source record IDs"], ["lat", "Latitude"], ["lon", "Longitude"]];
      hf.querySelectorAll("[data-dl]").forEach(function (b) { b.addEventListener("click", function () { save(hcur, HC, "nigeria-minigrids-selection", b.getAttribute("data-dl"), "Nigeria mini-grids (selection), combined from SE4ALL, REA via Energy Access Explorer and the NEP map. Sources keep their own terms; see the mini-grid page."); }); });
      runH();
    }

    // ---------- developer workspace
    if (P.kind === "dev8") {
      var dm = baseMap("d-map"), df = document.getElementById("d-f"), dd = document.getElementById("d-detail"), dl = L.layerGroup().addTo(dm), dcur = [];
      var mvL = wms("se4allWS:distribution_line_mv", .35), mgL = L.layerGroup(), subL = L.layerGroup();
      M.sites.forEach(function (s) { L.circleMarker([s.lat, s.lon], { renderer: cr, radius: 5, color: "#fff", weight: 1.2, fillColor: "#065F46", fillOpacity: .95 }).on("click", function () { dd.innerHTML = mgDetail(s); }).addTo(mgL); });
      M.subs.forEach(function (x) { L.marker([x.lat, x.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='a-sq'></span>", iconSize: [12, 12] }) }).bindPopup("<b>" + esc(x.name) + "</b><br>" + (x.kv || "—") + " kV substation").addTo(subL); });
      var drad = function (b) { var z = dm.getZoom(), k = z <= 6 ? .45 : z <= 8 ? .75 : 1; return (2.5 + Math.min(8, Math.sqrt(b) / 10)) * k; };
      dm.on("zoomend", function () { dl.eachLayer(function (l) { l.setRadius(drad(l.options.bld)); }); });
      var HINT = { offgrid: "More than 5 km from the MV grid: off-grid mini-grid candidates.", near: "Within 5 km of the MV grid: interconnected mini-grid or grid-extension candidates.", all: "All off-grid settlements in the layer." };
      var site = function (c) {
        var k = calcC(c), m = MGBY[c.mg_id];
        var sv0 = SVB(c), bdiff = c.sv_bld != null && c.bld_layer != null && Math.abs(c.sv_bld - c.bld_layer) >= 1;
        dd.innerHTML = "<span class='a-kick'>" + (c.sv_cid != null ? "Field-surveyed site · survey cluster ID " + c.sv_cid : "Off-grid cluster ID " + c.cid) + "</span><h3>" + esc(cname(c)) + "</h3><p class='w-sub'>" + esc([OWN ? null : c.dre_lga, c.state].filter(Boolean).join(", ")) + (OWN && c.nesp_name && c.cid != null ? " · named town " + c.nesp_name_km + " km away" : "") + " · " + c.lat.toFixed(4) + ", " + c.lon.toFixed(4) + "</p>" +
          "<dl class='w-dl2'>" + (c.sv_cid != null ? "<dt>Survey cluster ID</dt><dd>" + c.sv_cid + "</dd>" : "") + "<dt>Off-grid layer cluster ID</dt><dd>" + (c.cid != null ? c.cid : "none within 2 km") + "</dd>" +
          "<dt>Buildings" + (c.bsrc === "survey" ? " (field survey)" : "") + "</dt><dd>" + fmt(c.bld) + "</dd>" + (bdiff ? "<dt>Buildings (off-grid layer)</dt><dd>" + fmt(c.bld_layer) + "</dd>" : "") +
          (c.sv_more ? "<dt>Other surveys linked here</dt><dd>" + c.sv_more + "</dd>" : "") + (!OWN && c.dre_pop != null ? "<dt>Population (World Bank)</dt><dd>" + fmt(c.dre_pop) + "</dd>" : "") + "<dt>To the MV grid</dt><dd>" + f1(c.mv_km) + " km</dd><dt>Nearest substation</dt><dd>" + esc(c.sub) + " · " + f1(c.sub_km) + " km</dd><dt>Nearest mini-grid</dt><dd>" + (m ? esc(m.name || m.id) + " · " : "") + f1(c.mg_km) + " km</dd>" +
          (bdiff ? "</dl><p class='a-flag' style='font-size:13px;margin:6px 0'>Building count from the field survey (" + fmt(c.sv_bld) + ") is used; the off-grid layer counts " + fmt(c.bld_layer) + " for its cluster " + c.cid + ".</p><dl class='w-dl2'>" : "") + "<dt>Schools · health · markets</dt><dd>" + fmt(c.schools || 0) + " · " + fmt(c.health || 0) + " · " + (c.markets == null && c.cid == null ? "—" : fmt(c.markets || 0)) + "</dd></dl>" +
          (c.slug ? (OWN && SVB(c) ? "<div class='sv-inpanel'><span class='a-kick'>Field survey · " + esc(SVB(c).n || "") + ", " + esc(SVB(c).d || SVB(c).y) + "</span>" + window.SVR.profile(SVB(c), { compact: true, link: true }) + "</div>" : "<p><a class='btn btn-primary' href='" + P.root + "communities/" + c.slug + "/index.html'>Field survey record</a></p>") : "<p class='sm a-muted'>No NESP field survey within 2 km.</p>") +
          "<h4>Indicative system <span class='a-pill mid'>Demo</span></h4><p class='sm a-muted'>" + (k.wb ? "Demand and connections: World Bank DRE Atlas estimate for this settlement." : OWN ? "Demand from buildings and the demo assumptions." : "Demand from the demo assumptions (no World Bank match).") + "</p><dl class='w-dl2'><dt>Connections</dt><dd>" + fmt(k.conn) + "</dd><dt>Daily demand</dt><dd>" + fmt(k.kwh) + " kWh</dd><dt>PV size</dt><dd>" + fmt(k.kwp) + " kWp</dd><dt>Capital cost</dt><dd>" + money(k.capex) + "</dd><dt>Grant at the assumed rate</dt><dd>" + money(k.grant) + "</dd></dl>" +
          "<p class='sm a-muted'>Costs from the demo assumptions below the map. <a class='a-go' href='#w-assume'>Change them</a></p>";
        dm.setView([c.lat, c.lon], Math.max(dm.getZoom(), 11));
      };
      var runD8 = function () {
        var mode = df.mode.value, st = df.state.value, bmin = +df.bmin.value, bmax = df.bmax.value ? +df.bmax.value : Infinity, free = +df.mgfree.value;
        document.getElementById("d-modehint").textContent = HINT[mode];
        var dq = (df.q.value || "").trim().toLowerCase();
        dcur = C.filter(function (c) {
          if (dq && ((c.dre_name || "") + " " + (c.dre_lga || "") + " " + (OWN ? (c.nesp_name || "") + " " + ((SVB(c) || {}).n || "") : "") + " " + c.cid + " " + (c.sv_cid != null ? c.sv_cid : "")).toLowerCase().indexOf(dq) < 0) return false;
          if (mode === "offgrid" && !(c.mv_km > 5)) return false; if (mode === "near" && !(c.mv_km <= 5)) return false;
          if (st && c.state !== st) return false; if (c.bld < bmin || c.bld > bmax) return false; if (free && !(c.mg_km > free)) return false;
          if (df.health.checked && !(c.health > 0)) return false; if (df.school.checked && !(c.schools > 0)) return false; if (df.market.checked && !(c.markets > 0)) return false;
          if (df.surveyed.checked && !c.slug) return false;
          if (df.sv_gen && (df.sv_gen.checked || df.sv_pay.checked || df.sv_road.checked || df.sv_mill.checked)) { var v = SVB(c); if (!v) return false;
            if (df.sv_gen.checked && !(v.bz >= 50)) return false; if (df.sv_pay.checked && v.mm !== 1) return false; if (df.sv_road.checked && !(v.tk === "all" || v.x4 === "all")) return false; if (df.sv_mill.checked && !(v.mi > 0)) return false; }
          return true; });
        dl.clearLayers();
        dcur.forEach(function (c) { L.circleMarker([c.lat, c.lon], { renderer: cr, radius: drad(c.bld), bld: c.bld, color: "#7A4E07", weight: .6, fillColor: c.slug ? "#D9480F" : "#B7791F", fillOpacity: .8 }).on("click", function () { site(c); }).addTo(dl); });
        df.l_mg.checked ? mgL.addTo(dm) : dm.removeLayer(mgL); df.l_mv.checked ? mvL.addTo(dm) : dm.removeLayer(mvL); df.l_sub.checked ? subL.addTo(dm) : dm.removeLayer(subL);
        var b = dcur.reduce(function (a, c) { return a + c.bld; }, 0);
        strip([[fmt(dcur.length), "matching sites"], [fmt(b), "buildings in them"], [f1(sumC(dcur).kwp / 1000) + " MWp", "indicative PV, all sites (demo)"]]);
        var top = dcur.slice(0, 50);
        document.querySelector("#d-t tbody").innerHTML = top.map(function (c, i) { var k = calcC(c);
          return "<tr data-i='" + i + "' style='cursor:pointer'><td><b>" + esc(cname(c)) + "</b><br><span class='a-muted' style='font-size:13px'>" + esc((OWN ? "" : c.dre_lga) || "") + " · " + idl(c) + "</span>" + (c.slug ? " <span class='a-pill ok'>Surveyed</span>" : "") + "</td><td>" + esc(c.state) + "</td><td class='n' data-v='" + c.bld + "'>" + fmt(c.bld) + "</td><td class='n' data-v='" + c.mv_km + "'>" + f1(c.mv_km) + " km</td><td class='n' data-v='" + c.mg_km + "'>" + f1(c.mg_km) + " km</td><td>" +
            [c.health > 0 ? "health" : "", c.schools > 0 ? "school" : "", c.markets > 0 ? "market" : ""].filter(Boolean).join(", ") + "</td><td class='n' data-v='" + k.kwp + "'>" + fmt(k.kwp) + "</td></tr>"; }).join("") || "<tr><td colspan='7' class='a-muted'>No site matches. Relax a filter.</td></tr>";
        document.querySelectorAll("#d-t tbody tr[data-i]").forEach(function (tr) { tr.addEventListener("click", function () { site(top[+tr.getAttribute("data-i")]); document.getElementById("d-map").scrollIntoView({ behavior: "smooth", block: "center" }); }); });
        var wl = document.getElementById("d-webmap");
        wl.href = mode === "near" ? M.apps + "minigrid-interconnected?buildings_max=" + (isFinite(bmax) ? bmax : 20000) + "&buildings_min=" + bmin + "&grid_dist_max=5&grid_dist_min=0"
                                  : M.apps + "minigrid-offgrid?buildings_max=" + (isFinite(bmax) ? bmax : 20000) + "&buildings_min=" + bmin + "&grid_dist_max=40&grid_dist_min=" + (mode === "offgrid" ? 5 : 0);
        if (st) { var pts = dcur.map(function (c) { return [c.lat, c.lon]; }); var f = A.geo.features.filter(function (x) { return x.properties.state === st; })[0];
          dm.fitBounds(L.geoJSON(f).getBounds(), { padding: [10, 10] }); } else dm.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
      };
      df.addEventListener("change", runD8); df.q.addEventListener("input", runD8);
      var DC8 = (OWN ? [["sv_cid", "Survey cluster ID"], ["cid", "Cluster ID (off-grid layer)"], ["bsrc", "Building count source"], ["bld_layer", "Buildings (off-grid layer)"], ["nesp_name", "Nearest named town/village (platform)"], ["state", "State"],["lat", "Latitude"], ["lon", "Longitude"], ["bld", "Buildings"], ["mv_km", "To MV grid km"], ["sub", "Nearest substation"], ["sub_km", "Substation km"], ["mg_id", "Nearest mini-grid"], ["mg_km", "Mini-grid km"], ["schools", "Schools"], ["health", "Health centres"], ["markets", "Markets"], ["survey", "Field survey page"], ["conn", "Indicative connections (demo)"], ["kwp", "Indicative kWp (demo)"], ["capex", "Indicative capex US$ (demo)"]] : null) || [["sv_cid", "Survey cluster ID"], ["cid", "Cluster ID (off-grid layer)"], ["bsrc", "Building count source"], ["bld_layer", "Buildings (off-grid layer)"], ["dre_name", "Name (World Bank DRE Atlas)"], ["dre_lga", "LGA (DRE Atlas)"], ["state", "State"], ["lat", "Latitude"], ["lon", "Longitude"], ["bld", "Buildings"], ["mv_km", "To MV grid km"], ["sub", "Nearest substation"], ["sub_km", "Substation km"], ["mg_id", "Nearest mini-grid"], ["mg_km", "Mini-grid km"], ["schools", "Schools"], ["health", "Health centres"], ["markets", "Markets"], ["survey", "Field survey page"], ["dre_pop", "Population (DRE Atlas)"], ["dre_kwh_day", "Demand kWh/day (DRE Atlas)"], ["dre_rwi", "Relative wealth index (DRE Atlas)"], ["dsrc", "Demand basis"], ["conn", "Indicative connections (demo)"], ["kwp", "Indicative kWp (demo)"], ["capex", "Indicative capex US$ (demo)"]];
      df.querySelectorAll("[data-dl]").forEach(function (b) { b.addEventListener("click", function () {
        var rows = dcur.map(function (c) { var k = calcC(c), r = {}; Object.keys(c).forEach(function (x) { r[x] = c[x]; }); r.survey = c.slug ? location.origin + location.pathname.replace(/for\/developers\/.*$/, "") + "communities/" + c.slug + "/index.html" : ""; r.conn = Math.round(k.conn); r.kwp = Math.round(k.kwp); r.capex = Math.round(k.capex); r.dsrc = k.wb ? "World Bank DRE Atlas" : "Demo assumptions"; return r; });
        save(rows, DC8, "nigeria-sites-selection", b.getAttribute("data-dl"), "Off-grid settlements (selection) from the SE4ALL platform; distances recalculated. Columns marked demo use editable demo assumptions, not REA figures."); }); });
      onAssume(runD8); runD8();
    }

    // ---------- investor workspace
    if (P.kind === "inv8") {
      var im8 = baseMap("i-map", true), iff = document.getElementById("i-f"), idt = document.getElementById("i-detail"), il = L.layerGroup().addTo(im8), area = null, circ = null;
      var BC = { A: "#065F46", B: "#1E4E79", C: "#6B3FA0", D: "#E8A317", S: "#94A3B8" }, BL = { A: "A · Field-verified", B: "B · Large off-grid", C: "C · Mid-size off-grid", D: "D · Near grid", S: "Served" };
      var band = function (c, served) { if (c.mg_km <= served) return "S"; if (c.mv_km <= 5) return "D"; if (c.slug) return "A"; return c.bld >= 1000 ? "B" : "C"; };
      var stKW = {}, stN = {}, stPipe = {};
      M.sites.forEach(function (s) { stKW[s.state] = (stKW[s.state] || 0) + (s.kw || 0); stN[s.state] = (stN[s.state] || 0) + 1;
        if (s.status === "In evaluation" || s.status === "Under construction / approved") stPipe[s.state] = (stPipe[s.state] || 0) + 1; });
      var RAMPI = ["#F6EBD6", "#EBCB91", "#D9A445", "#B9770E", "#7A4E07"];
      var gj8 = L.geoJSON(A.geo, { style: function () { return { weight: 1, color: "#fff", fillOpacity: .85, fillColor: "#ddd" }; } }).addTo(im8);
      var perState = function (bmin, served) {
        var o = {}; C.forEach(function (c) { if (c.bld < bmin) return; var b = band(c, served); if (b === "A" || b === "B" || b === "C") { var r = o[c.state] || (o[c.state] = { n: 0, bld: 0, capex: 0 }); r.n++; r.bld += c.bld; r.capex += calcC(c).capex; } }); return o; };
      var colourStates = function (ps) {
        var metric = iff.colour.value, vals = {};
        Object.keys(P.stats).forEach(function (s) { vals[s] = metric === "gap" ? (stKW[s] ? P.stats[s].off / stKW[s] : Infinity) : ((ps[s] || {}).n || 0); });
        var fin = Object.keys(vals).map(function (k) { return vals[k]; }).filter(isFinite).sort(function (a, b) { return a - b; });
        var q = [0.2, 0.4, 0.6, 0.8].map(function (p) { return fin[Math.floor(p * (fin.length - 1))]; });
        var cls = function (v) { if (!isFinite(v)) return RAMPI.length - 1; var i = 0; while (i < q.length && v > q[i]) i++; return i; };
        gj8.setStyle(function (f) { var s = f.properties.state; var sel = area && area.state === s; return { weight: sel ? 3 : 1, color: sel ? "#0F172A" : "#fff", fillOpacity: area ? (sel ? .25 : .35) : .85, fillColor: RAMPI[cls(vals[s])] }; });
        document.getElementById("i-legend").innerHTML = "<b>" + (metric === "gap" ? "Off-grid buildings per recorded kW" : "Unserved off-grid sites") + "</b><span><i style='background:" + RAMPI[0] + "'></i>lowest</span><span><i style='background:" + RAMPI[2] + "'></i>middle</span><span><i style='background:" + RAMPI[4] + "'></i>highest" + (metric === "gap" ? " or no recorded kW" : "") + "</span>" +
          Object.keys(BC).map(function (k) { return "<span><i style='background:" + BC[k] + "'></i>" + BL[k] + "</span>"; }).join("");
      };
      var pcur = [];
      var runI = function () {
        var bmin = +iff.bmin.value, served = +iff.served.value, ps = perState(bmin, served);
        colourStates(ps);
        // state table
        document.querySelector("#i-t tbody").innerHTML = Object.keys(P.stats).sort(function (a, b) { return ((ps[b] || {}).bld || 0) - ((ps[a] || {}).bld || 0); }).map(function (s) {
          var r = ps[s] || { n: 0, bld: 0, capex: 0 }, cx = r.capex;
          return "<tr data-s='" + esc(s) + "' style='cursor:pointer'><td><b>" + esc(s) + "</b></td><td class='n' data-v='" + r.n + "'>" + fmt(r.n) + "</td><td class='n' data-v='" + r.bld + "'>" + fmt(r.bld) + "</td><td class='n' data-v='" + (stN[s] || 0) + "'>" + fmt(stN[s] || 0) + "</td><td class='n' data-v='" + (stKW[s] || 0) + "'>" + fmt(stKW[s] || 0) + "</td><td class='n' data-v='" + (stPipe[s] || 0) + "'>" + fmt(stPipe[s] || 0) + "</td><td class='n' data-v='" + cx + "'>" + f1(cx / 1e6) + "</td></tr>"; }).join("");
        document.querySelectorAll("#i-t tbody tr").forEach(function (tr) { tr.addEventListener("click", function () { iff.area.value = "state"; setArea(); iff.state.value = tr.getAttribute("data-s"); area = { state: tr.getAttribute("data-s") }; runI(); document.getElementById("i-map").scrollIntoView({ behavior: "smooth", block: "center" }); }); });
        il.clearLayers();
        if (!area) { pcur = []; strip([[fmt(Object.keys(ps).reduce(function (a, s) { return a + ps[s].n; }, 0)), "unserved off-grid sites, all Nigeria"], [fmt(M.sites.length), "mini-grids recorded"], [f1(M.sites.reduce(function (a, s) { return a + (s.kw || 0); }, 0) / 1000) + " MW", "recorded capacity"]]); return; }
        var inA = area.state ? function (x) { return x.state === area.state; } : function (x) { return hav(area.lat, area.lon, x.lat, x.lon) <= area.r; };
        pcur = C.filter(function (c) { return c.bld >= bmin && inA(c); }).map(function (c) { var r = {}; Object.keys(c).forEach(function (k) { r[k] = c[k]; }); r.band = band(c, served); var k = calcC(c); r.dsrc = k.wb ? "World Bank DRE Atlas" : "Demo assumptions"; r.conn = Math.round(k.conn); r.kwp = Math.round(k.kwp); r.capex = Math.round(k.capex); r.grant = Math.round(k.grant); return r; });
        var mgs = M.sites.filter(inA);
        pcur.forEach(function (c) { L.circleMarker([c.lat, c.lon], { renderer: cr, radius: 3 + Math.min(8, Math.sqrt(c.bld) / 10), color: "#fff", weight: .8, fillColor: BC[c.band], fillOpacity: .9 })
          .bindPopup("<b>" + esc(cname(c)) + "</b><br>" + idl(c) + (c.sv_cid != null && c.cid != null ? " · off-grid cluster " + c.cid : "") + "<br>" + BL[c.band] + "<br>" + fmt(c.bld) + " buildings · " + f1(c.mv_km) + " km to MV grid<br>Indicative " + fmt(c.kwp) + " kWp (demo)" + (c.slug ? "<br><a href='" + P.root + "communities/" + c.slug + "/index.html'>Field survey record</a>" : "")).addTo(il); });
        mgs.forEach(function (s) { L.marker([s.lat, s.lon], { pane: "pts", icon: L.divIcon({ className: "", html: "<span class='w-mgsq' style='background:" + SC[s.status] + "'></span>", iconSize: [11, 11] }) }).on("click", function () { idt.innerHTML = mgDetail(s); }).addTo(il); });
        var agg = {}; Object.keys(BL).forEach(function (k) { agg[k] = { n: 0, bld: 0 }; }); pcur.forEach(function (c) { agg[c.band].n++; agg[c.band].bld += c.bld; });
        var port = pcur.filter(function (c) { return c.band === "A" || c.band === "B" || c.band === "C"; }), k = sumC(port);
        var mkw = mgs.reduce(function (a, s) { return a + (s.kw || 0); }, 0), pipe = mgs.filter(function (s) { return s.status === "In evaluation" || s.status === "Under construction / approved"; }).length;
        idt.innerHTML = "<span class='a-kick'>Indicative portfolio</span><h3>" + (area.state ? esc(area.state) : area.r + " km around " + area.lat.toFixed(3) + ", " + area.lon.toFixed(3)) + "</h3>" +
          "<table class='w-bandt'><tbody>" + Object.keys(BL).map(function (b) { return "<tr><td><i style='background:" + BC[b] + "'></i>" + BL[b] + "</td><td class='n'>" + fmt(agg[b].n) + " sites</td><td class='n'>" + fmt(agg[b].bld) + " bldgs</td></tr>"; }).join("") + "</tbody></table>" +
          "<h4>Off-grid portfolio (A + B + C) <span class='a-pill mid'>Demo</span></h4><p class='sm a-muted'>World Bank demand estimates for " + fmt(k.wb) + " of " + fmt(port.length) + " sites; demo assumptions for the rest.</p><dl class='w-dl2'><dt>Sites</dt><dd>" + fmt(port.length) + "</dd><dt>Connections</dt><dd>" + fmt(k.conn) + "</dd><dt>PV size</dt><dd>" + f1(k.kwp / 1000) + " MWp</dd><dt>Capital cost</dt><dd>" + money(k.capex) + "</dd><dt>Grant at the assumed rate</dt><dd>" + money(k.grant) + "</dd><dt>Left to finance</dt><dd>" + money(Math.max(0, k.capex - k.grant)) + "</dd></dl>" +
          "<h4>Already recorded here</h4><dl class='w-dl2'><dt>Mini-grids</dt><dd>" + fmt(mgs.length) + " (" + fmt(mkw) + " kW)</dd><dt>In the pipeline</dt><dd>" + fmt(pipe) + " in evaluation or construction</dd></dl><p class='sm a-muted'>Money figures use the demo assumptions below. <a class='a-go' href='#w-assume'>Change them</a></p>";
        strip([[fmt(port.length), "unserved off-grid sites in the area"], [f1(k.kwp / 1000) + " MWp", "indicative PV (demo)"], [money(k.capex), "indicative capital cost (demo)"]]);
        var bb = pcur.map(function (c) { return [c.lat, c.lon]; }).concat(mgs.map(function (s) { return [s.lat, s.lon]; }));
        if (area.state) im8.fitBounds(gj8.getLayers().filter(function (l) { return l.feature.properties.state === area.state; })[0].getBounds(), { padding: [10, 10] });
        else if (circ) im8.fitBounds(circ.getBounds(), { padding: [10, 10] });
      };
      var setArea = function () { var st = iff.area.value === "state"; document.getElementById("i-state-box").hidden = !st; document.getElementById("i-circle-box").hidden = st; if (circ && st) { im8.removeLayer(circ); circ = null; } };
      gj8.on("click", function (ev) { if (iff.area.value !== "state") return; area = { state: ev.layer.feature.properties.state }; iff.state.value = area.state; runI(); });
      im8.on("click", function (ev) { if (iff.area.value !== "circle") return; var r = +iff.radius.value; area = { lat: ev.latlng.lat, lon: ev.latlng.lng, r: r };
        if (circ) im8.removeLayer(circ); circ = L.circle(ev.latlng, { radius: r * 1000, color: "#0F172A", weight: 2, fill: false, dashArray: "6 4", interactive: false }).addTo(im8); runI(); });
      iff.addEventListener("change", function (ev) {
        if (ev.target.name === "area") { setArea(); area = null; }
        if (ev.target.name === "state") area = iff.state.value ? { state: iff.state.value } : null;
        if (ev.target.name === "radius" && area && !area.state) { area.r = +iff.radius.value; if (circ) circ.setRadius(area.r * 1000); }
        runI(); });
      var IC = [["sv_cid", "Survey cluster ID"], ["cid", "Cluster ID (off-grid layer)"], ["bsrc", "Building count source"], ["bld_layer", "Buildings (off-grid layer)"], ["dre_name", "Name (World Bank DRE Atlas)"], ["dre_lga", "LGA (DRE Atlas)"], ["state", "State"], ["lat", "Latitude"], ["lon", "Longitude"], ["band", "Investment band"], ["bld", "Buildings"], ["mv_km", "To MV grid km"], ["mg_km", "Nearest mini-grid km"], ["sub", "Nearest substation"], ["sub_km", "Substation km"], ["dre_pop", "Population (DRE Atlas)"], ["dre_kwh_day", "Demand kWh/day (DRE Atlas)"], ["dsrc", "Demand basis"], ["conn", "Indicative connections (demo)"], ["kwp", "Indicative kWp (demo)"], ["capex", "Indicative capex US$ (demo)"], ["grant", "Grant at assumed rate US$ (demo)"]];
      iff.querySelectorAll("[data-dl]").forEach(function (b) { b.addEventListener("click", function () {
        if (!pcur.length) { idt.insertAdjacentHTML("afterbegin", "<p class='a-flag'>Choose a state or click the map first.</p>"); return; }
        save(pcur.map(function (r) { var o = {}; Object.keys(r).forEach(function (k) { o[k] = k === "band" ? BL[r[k]] : r[k]; }); return o; }), IC, "nigeria-portfolio-sites", b.getAttribute("data-dl"), "Indicative portfolio (demo). Sites from the SE4ALL off-grid settlement layer; demo columns use editable assumptions, not REA figures."); }); });
      onAssume(runI); runI();
    }
    })();
  }

})();
