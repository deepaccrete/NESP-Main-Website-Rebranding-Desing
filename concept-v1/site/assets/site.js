/* Nigeria SE4ALL concept v2 — maps, site-finder, tables. Data comes from window.SE4ALL (generated nightly from GeoNode). */
(function () {
  var D = window.SE4ALL || {}, P = window.PAGE || {};
  var WMS = "https://data.nigeriase4all.gov.ng/geoserver/wms";
  var fmt = function (n) { return n == null ? "—" : Number(n).toLocaleString("en-GB"); };
  var slug = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); };
  var RAMP = ["#F6EBD6", "#EBCB91", "#D9A445", "#B9770E", "#7A4E07"], BREAKS = [10, 20, 30, 40];
  var colour = function (v) { var i = 0; while (i < BREAKS.length && v >= BREAKS[i]) i++; return RAMP[i]; };
  var share = function (s) { return s.buildings ? 100 * s.buildings_over_5km / s.buildings : 0; };

  // mobile menu
  var mb = document.querySelector(".menu-btn"), nav = document.querySelector(".top nav");
  if (mb && nav) mb.addEventListener("click", function () { nav.classList.toggle("open"); mb.setAttribute("aria-expanded", nav.classList.contains("open")); });

  // state picker
  document.querySelectorAll("[data-state-go]").forEach(function (f) {
    f.addEventListener("submit", function (e) { e.preventDefault(); var v = f.querySelector("select").value; if (v) location.href = P.root + "states/" + slug(v) + "/index.html"; });
  });

  // No third-party basemap: state boundaries from our own data are the base layer (no API keys, no extra dependency).
  function basemap(map) {
    panes(map);
    map.attributionControl.setPrefix(false);
    map.attributionControl.addAttribution('Data: <a href="https://data.nigeriase4all.gov.ng/">Nigeria SE4ALL GeoNode</a>');
    if (D.geo) L.geoJSON(D.geo, { interactive: false, style: { color: "#B9B5A8", weight: 1, fillColor: "#FFFFFF", fillOpacity: 1 } }).addTo(map);
  }
  function wms(layer, opts) { return L.tileLayer.wms(WMS, Object.assign({ layers: layer, format: "image/png", transparent: true, version: "1.1.1", pane: "wms" }, opts || {})); }
  // pane order: base shapes (overlay 400) < GeoServer images (410) < mask (420) < outline (430) < points (440)
  function panes(map) {
    [["wms", 410], ["mask", 420], ["outline", 430], ["pts", 440]].forEach(function (p) {
      var el = map.createPane(p[0]); el.style.zIndex = p[1]; if (p[0] !== "pts") el.style.pointerEvents = "none";
    });
  }

  // ---------- home / states-index choropleth
  var cm = document.getElementById("nat-map");
  if (cm && window.L && D.geo && D.states) {
    var map = L.map(cm, { zoomControl: true, scrollWheelZoom: false, attributionControl: true }).setView([9.1, 8.3], 6);
    basemap(map);
    var hb = document.querySelector(".hoverbox");
    var gj = L.geoJSON(D.geo, {
      style: function (f) { var s = D.states[f.properties.state]; return { weight: 1, color: "#fff", fillOpacity: .85, fillColor: s ? colour(share(s)) : "#ddd" }; },
      onEachFeature: function (f, l) {
        var s = D.states[f.properties.state];
        l.on("mouseover", function () {
          l.setStyle({ weight: 2.5, color: "#14231C" }); l.bringToFront();
          if (hb && s) { hb.style.display = "block"; hb.innerHTML = "<b>" + s.state + "</b><span class='num'>" + share(s).toFixed(1) + "%</span> of buildings &gt;5 km from mapped grid<br><span class='num'>" + fmt(s.buildings_over_5km) + "</span> buildings · <span class='num'>" + fmt(s.clusters_over_5km) + "</span> settlements<br><span class='muted small'>Click to open state profile</span>"; }
        });
        l.on("mouseout", function () { gj.resetStyle(l); if (hb) hb.style.display = "none"; });
        l.on("click", function () { location.href = P.root + "states/" + slug(f.properties.state) + "/index.html"; });
      } }).addTo(map);
    wms("se4allWS:distribution_line_mv", { opacity: .85 }).addTo(map);
    map.fitBounds(gj.getBounds(), { padding: [10, 10] });
  }

  // ---------- site-finder (exact lookup in a pre-computed table — no live query of 454k points)
  var ff = document.getElementById("finder");
  if (ff && D.finder) {
    var st = ff.querySelector("[name=state]"), dd = ff.querySelector("[name=dist]"), nn = ff.querySelector("[name=bldg]");
    var outC = document.getElementById("f-clusters"), outB = document.getElementById("f-buildings"), go = document.getElementById("f-go");
    function run() {
      var t = st.value ? D.finder.states[st.value] : D.finder.national;
      var i = D.finder.D.indexOf(+dd.value), j = D.finder.N.indexOf(+nn.value);
      outC.textContent = fmt(t.c[i][j]); outB.textContent = fmt(t.b[i][j]);
      go.href = st.value ? P.root + "states/" + slug(st.value) + "/index.html#map" : "https://apps.nigeriase4all.gov.ng/minigrid-offgrid";
      go.textContent = st.value ? "See " + st.value + " on the map" : "Open the off-grid webmap";
    }
    [st, dd, nn].forEach(function (x) { x.addEventListener("change", run); }); run();
  }

  // ---------- state profile map
  var sm = document.getElementById("state-map");
  if (sm && window.L && P.state) {
    var m2 = L.map(sm, { scrollWheelZoom: false });
    var feat = D.geo.features.filter(function (f) { return f.properties.state === P.state; })[0];
    var outline = L.geoJSON(feat, { pane: "outline", style: { color: "#14231C", weight: 2, fill: false } });
    m2.fitBounds(outline.getBounds(), { padding: [16, 16] });
    basemap(m2);
    // mask everything outside the state
    var world = [[-90, -180], [-90, 180], [90, 180], [90, -180]];
    var holes = []; (feat.geometry.type === "Polygon" ? [feat.geometry.coordinates] : feat.geometry.coordinates).forEach(function (p) { holes.push(p[0].map(function (c) { return [c[1], c[0]]; })); });
    L.polygon([world].concat(holes), { pane: "mask", stroke: false, fillColor: "#F7F6F2", fillOpacity: .8, interactive: false }).addTo(m2);
    var lay = {
      settle: wms("se4allWS:cluster_all_new", { opacity: .7 }),
      offgrid: wms("se4allWS:cluster_offgrid", { opacity: .9 }),
      mv: wms("se4allWS:distribution_line_mv", { opacity: .9 }),
      hv: wms("geonode:existing_lines_high_voltage", { opacity: .9 }),
      subs: wms("geonode:substations_currently_installed"),
      mg: L.layerGroup((P.minigrids || []).map(function (g) {
        return L.circleMarker([g.lat, g.lon], { pane: "pts", radius: 8, color: "#fff", weight: 2, fillColor: "#0E5A3A", fillOpacity: 1 })
          .bindPopup("<b>" + (g.community || "Mini-grid") + "</b><br>" + (g.lga || "") + "<br>" + (g.kw != null ? g.kw + " kW · " : "") + (g.system || "") + "<br>" + (g.status || "") + (g.condition ? " · " + g.condition : "") + (g.programme ? "<br><span class='muted'>" + g.programme + "</span>" : ""));
      })),
      survey: L.layerGroup((P.survey || []).map(function (s) {
        var c = s.grid === "no" ? "#B9770E" : "#2B5C8A";
        return L.circleMarker([s.lat, s.lon], { pane: "pts", radius: 5, color: "#fff", weight: 1.5, fillColor: c, fillOpacity: 1 })
          .bindPopup("<b>" + (s.community || "Surveyed community") + "</b><br>LGA: " + (s.lga || "—") + "<br>Surveyed " + (s.date || "—") + "<br>Grid: " + (s.grid || "—").replace(/_/g, " "));
      }))
    };
    ["settle", "mv", "hv", "mg", "survey"].forEach(function (k) { lay[k].addTo(m2); });
    outline.addTo(m2);
    m2.fitBounds(outline.getBounds(), { padding: [16, 16] });
    document.querySelectorAll("[data-layer]").forEach(function (cb) {
      var k = cb.getAttribute("data-layer"); cb.checked = m2.hasLayer(lay[k]);
      cb.addEventListener("change", function () { cb.checked ? lay[k].addTo(m2) : m2.removeLayer(lay[k]); outline.bringToFront && outline.bringToFront(); });
    });
  }

  // ---------- sortable tables + filters
  document.querySelectorAll("table.t[data-sort]").forEach(function (t) {
    var ths = t.querySelectorAll("th");
    ths.forEach(function (th, i) {
      th.addEventListener("click", function () {
        var asc = !th.classList.contains("sorted-asc"); ths.forEach(function (x) { x.classList.remove("sorted-asc", "sorted-desc"); });
        th.classList.add(asc ? "sorted-asc" : "sorted-desc");
        var rows = [].slice.call(t.tBodies[0].rows), num = th.hasAttribute("data-n");
        rows.sort(function (a, b) {
          var x = a.cells[i].getAttribute("data-v") || a.cells[i].textContent, y = b.cells[i].getAttribute("data-v") || b.cells[i].textContent;
          if (num) { x = parseFloat(x); y = parseFloat(y); x = isNaN(x) ? -1 : x; y = isNaN(y) ? -1 : y; return asc ? x - y : y - x; }
          return asc ? x.localeCompare(y) : y.localeCompare(x);
        });
        rows.forEach(function (r) { t.tBodies[0].appendChild(r); });
      });
    });
  });
  document.querySelectorAll(".filters").forEach(function (fs) {
    var t = document.getElementById(fs.getAttribute("data-for"));
    fs.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        fs.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
        var v = b.getAttribute("data-f");
        [].forEach.call(t.tBodies[0].rows, function (r) { r.style.display = (v === "all" || r.getAttribute("data-f") === v) ? "" : "none"; });
      });
    });
  });
})();
