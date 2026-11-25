
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
