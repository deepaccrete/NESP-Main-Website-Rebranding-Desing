
  // ================= v9: field-survey profiles, explorer and shared renderer (window.SVR)
  if (window.SV) (function () {
    var S = window.SV, R = S.rows, IC = S.icons, BY = {};
    R.forEach(function (r) { BY[r.id] = r; });
    var GRID = { no: ["No grid", "#c47f00"], nc: ["Grid present, not connected", "#2a78d6"], c: ["Connected to the grid", "#2f8f5b"] }, NFC = "#d14d3a";
    var ACC = { all: "All year", dry: "Dry season only", never: "Never" }, NET = { none: "No signal" };
    var nf = function (n, d) { return n == null || isNaN(n) ? "—" : Number(n).toLocaleString("en-GB", { maximumFractionDigits: d || 0 }); };
    var med = function (a) { a = a.filter(function (x) { return x != null && !isNaN(x); }).sort(function (x, y) { return x - y; }); if (!a.length) return null; var m = Math.floor(a.length / 2); return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2; };
    var pct = function (a, f) { var b = a.filter(function (r) { return f(r) != null; }); return b.length ? 100 * b.filter(function (r) { return f(r); }).length / b.length : null; };
    var fuelMed = {}; ["pe", "di", "ke"].forEach(function (k) { fuelMed[k] = {}; Object.keys(R.reduce(function (o, r) { o[r.y] = 1; return o; }, {})).forEach(function (y) { fuelMed[k][y] = med(R.filter(function (r) { return r.y === y; }).map(function (r) { return r[k]; })); }); });
    var natMed = { hh: med(R.map(function (r) { return r.hh; })), bz: med(R.map(function (r) { return r.bz; })) };
    var gridOf = function (r) { return r.nf ? ["Grid never worked", NFC] : (GRID[r.g] || ["Not recorded", "#94A3B8"]); };
    var tile = function (ic, label, value, sub, cls) { return "<div class='sv-tile" + (cls ? " " + cls : "") + "'><span class='sv-ic'>" + IC[ic] + "</span><div><b>" + value + "</b><span>" + label + "</span>" + (sub ? "<small>" + sub + "</small>" : "") + "</div></div>"; };
    var meter = function (v, m) { if (v == null) return ""; return "<span class='sv-meter'><i style='width:" + Math.max(0, Math.min(100, v)) + "%'></i>" + (m != null ? "<em style='left:" + m + "%' title='Survey median'></em>" : "") + "</span>"; };
    var vsMed = function (v, m, unit) { if (v == null || m == null) return ""; var d = v - m; if (Math.abs(d) < 0.5) return "same as the survey median"; return (d > 0 ? "₦" + nf(d) + " above" : "₦" + nf(-d) + " below") + " the " + unit + " median"; };
    var yes = function (v) { return v === 1 ? "Yes" : v === 0 ? "No" : "—"; };
    var chips = function (arr, cls) { return arr && arr.length ? "<div class='sv-chips'>" + arr.map(function (x) { return "<span class='" + (cls || "") + "'>" + x + "</span>"; }).join("") + "</div>" : "<p class='a-muted sm'>Not recorded</p>"; };
    var group = function (title, ic, inner) { return "<section class='sv-group'><h4><span class='sv-ic'>" + IC[ic] + "</span>" + title + "</h4><div class='sv-tiles'>" + inner + "</div></section>"; };

    var profile = function (r, opt) {
      opt = opt || {}; var g = gridOf(r), root = (window.PAGE || {}).root || "";
      var net = [["MTN", r.mtn], ["Airtel", r.air], ["Glo", r.glo], ["9mobile", r.nm]].map(function (x) { return "<span class='" + (x[1] && x[1] !== "none" ? "on" : "off") + "'>" + x[0] + " · " + (x[1] ? (NET[x[1]] || x[1]) : "—") + "</span>"; }).join("");
      var acc = [["truck", "Truck", r.tk], ["truck", "4x4", r.x4], ["house", "Saloon car", r.sc], ["moto", "Motorbike", r.mb]].map(function (x) { return tile(x[0], x[1], ACC[x[2]] || "—", null, x[2] === "all" ? "ok" : x[2] === "never" ? "bad" : ""); }).join("");
      var crafts = (r.cr || 0), shops = [["shop", "Shops and kiosks", r.sh], ["pos", "POS shops", r.po], ["phone", "Phone charging", r.ph], ["craft", "Craft workshops", crafts]];
      var head = opt.compact ? "" : "";
      return head +
        "<div class='sv-hero' style='border-left-color:" + g[1] + "'><span class='sv-ic big' style='color:" + g[1] + "'>" + IC.grid + "</span><div><b>" + g[0] + "</b><span>" +
        (r.gy ? "Grid built " + r.gy + ". " : "") + (r.tr === 1 ? "Transformer present. " : r.tr === 0 ? "No transformer. " : "") + (r.mv != null ? r.mv + " km to the nearest MV line" : "") + "</span></div></div>" +
        group("Energy today", "gen",
          tile("gen", "of households run generators", r.hh != null ? nf(r.hh) + "%" : "—", meter(r.hh, natMed.hh)) +
          tile("gen", "of businesses run generators", r.bz != null ? nf(r.bz) + "%" : "—", meter(r.bz, natMed.bz)) +
          tile("fuel", "petrol, ₦ per litre", r.pe != null ? "₦" + nf(r.pe) : "—", vsMed(r.pe, (fuelMed.pe || {})[r.y], r.y)) +
          tile("fuel", "diesel, ₦ per litre", r.di != null ? "₦" + nf(r.di) : "—", vsMed(r.di, (fuelMed.di || {})[r.y], r.y)) +
          (opt.compact ? "" : tile("fuel", "petrol station in the community", yes(r.ps)) + tile("sun", "mini-grid present", yes(r.mgp)))) +
        group("Economy and productive use", "income",
          tile("mill", "grinding mills", nf(r.mi || 0)) + tile("mill", "oil presses", nf(r.op || 0)) + shops.map(function (x) { return tile(x[0], x[1], nf(x[2] || 0)); }).join("") +
          (opt.compact ? "" : tile("income", "main income", r.i1 || "—", [r.i2, r.i3].filter(Boolean).join(", ")))) +
        (opt.compact ? "" : "<div class='sv-sub'><span class='sv-ic'>" + IC.market + "</span><b>Market days</b>" + chips(r.md) + "</div>") +
        group("Services and finance", "health",
          tile("health", "health facilities", nf(r.he || 0), null, r.g === "no" && r.he > 0 ? "warn" : "") + tile("school", "primary schools", nf(r.p1 || 0)) + tile("school", "secondary schools", nf(r.p2 || 0)) +
          tile("money", "mobile money", yes(r.mm), null, r.mm === 1 ? "ok" : "") + tile("bank", "bank", yes(r.ba))) +
        "<div class='sv-sub'><span class='sv-ic'>" + IC.signal + "</span><b>Mobile networks</b><div class='sv-chips net'>" + net + "</div></div>" +
        group("Access", "truck", acc) +
        "<div class='sv-sub'><span class='sv-ic'>" + IC.crop + "</span><b>Crops grown</b>" + chips(r.cp) + "</div>" +
        "<div class='sv-sub'><span class='sv-ic'>" + IC.sub + "</span><b>Nearest infrastructure</b><p class='sm'>" + (r.sub ? esc(r.sub) + ", " + r.sk + " km · " : "") + (r.mgn ? "mini-grid " + esc(r.mgn) + ", " + r.mgk + " km" : "") + "</p></div>" +
        (opt.link ? "<p style='margin-top:12px;display:flex;gap:8px;flex-wrap:wrap'><a class='btn btn-primary' href='" + root + "communities/" + r.id + "/index.html'>Full survey record</a></p>" : "");
    };
    var header = function (r) {
      return "<span class='a-kick'>Surveyed " + esc(r.d || r.y) + (r.rd ? " · <span class='sv-ready'>build-ready</span>" : "") + "</span><h3>" + esc(r.n || "Surveyed community") + "</h3><p class='w-sub'>" + esc([r.l, r.s].filter(Boolean).join(" LGA, ")) + " · " + nf(r.b) + " buildings · survey cluster ID " + esc(String(r.u).split("-")[0]) + "</p>";
    };
    window.SVR = { byId: BY, profile: profile, header: header };

    // ---------- single community page: icon profile above the detailed tables
    if (P.kind === "community") { var host = document.getElementById("sv-profile"); if (host && BY[host.getAttribute("data-id")]) host.innerHTML = profile(BY[host.getAttribute("data-id")]); }

    // ---------- explorer
    if (P.kind === "survey9" && window.L) {
      var f = document.getElementById("sv-f"), det = document.getElementById("sv-detail"), cur = [], sel = null;
      var mp = baseMap("sv-map"), crr = L.canvas({ pane: "pts", padding: .4 }), lay = L.layerGroup().addTo(mp); wms("se4allWS:distribution_line_mv", .3).addTo(mp);
      var RAMP = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"];
      var bars = function (title, items, unit) { var mx = Math.max.apply(null, items.map(function (x) { return x[1] || 0; }).concat([1]));
        return "<div class='sv-chart'><h4>" + title + "</h4>" + items.map(function (x) { return "<div class='sv-bar" + (title.indexOf("crops") > -1 ? " cap" : "") + "' title='" + esc(x[0]) + ": " + nf(x[1], 1) + (unit || "") + "'><span>" + esc(x[0]) + "</span><i><em style='width:" + (100 * (x[1] || 0) / mx) + "%'></em></i><b>" + nf(x[1], unit === "%" ? 0 : 0) + (unit || "") + "</b></div>"; }).join("") + "</div>"; };
      var summary = function () {
        var n = cur.length, ng = cur.filter(function (r) { return r.g === "no"; }).length, withGrid = cur.filter(function (r) { return r.g !== "no" && r.g; });
        var yrs = {}; cur.forEach(function (r) { yrs[r.y] = (yrs[r.y] || 0) + 1; }); var ly = Object.keys(yrs).sort().pop();
        var crops = {}; cur.forEach(function (r) { (r.cp || []).slice(0, 2).forEach(function (c) { crops[c] = (crops[c] || 0) + 1; }); });
        var topc = Object.keys(crops).sort(function (a, b) { return crops[b] - crops[a]; }).slice(0, 6).map(function (c) { return [c, crops[c]]; });
        var good = function (k) { return pct(cur, function (r) { return r[k] == null ? null : (r[k] === "3G" || r[k] === "4G" || r[k] === "5G"); }); };
        var allyr = function (k) { return pct(cur, function (r) { return r[k] == null ? null : r[k] === "all"; }); };
        var sum = function (k) { return cur.reduce(function (a, r) { return a + (r[k] || 0); }, 0); };
        det.innerHTML = "<span class='a-kick'>This selection</span><h3>" + nf(n) + " surveyed communities</h3>" +
          "<div class='sv-tiles'>" + tile("grid", "have no grid", n ? nf(100 * ng / n) + "%" : "—", nf(ng) + " communities") +
          tile("grid", "of those with grid say it never worked", withGrid.length ? nf(100 * withGrid.filter(function (r) { return r.nf; }).length / withGrid.length) + "%" : "—") +
          tile("gen", "median share of businesses on generators", med(cur.map(function (r) { return r.bz; })) != null ? nf(med(cur.map(function (r) { return r.bz; }))) + "%" : "—") +
          tile("fuel", "median petrol price, " + (ly || ""), med(cur.filter(function (r) { return r.y === ly; }).map(function (r) { return r.pe; })) != null ? "₦" + nf(med(cur.filter(function (r) { return r.y === ly; }).map(function (r) { return r.pe; }))) : "—", (yrs[ly] || 0) + " communities surveyed in " + ly) +
          tile("money", "have mobile money", pct(cur, function (r) { return r.mm == null ? null : r.mm === 1; }) != null ? nf(pct(cur, function (r) { return r.mm == null ? null : r.mm === 1; })) + "%" : "—") +
          tile("mill", "grinding mills in total", nf(sum("mi"))) + "</div>" +
          bars("Grid at the time of survey", [["No grid", ng], ["Present, not connected", cur.filter(function (r) { return r.g === "nc"; }).length], ["Connected", cur.filter(function (r) { return r.g === "c"; }).length], ["…of which never worked", cur.filter(function (r) { return r.nf; }).length]]) +
          bars("3G or 4G signal, by operator", [["MTN", good("mtn")], ["Airtel", good("air")], ["Glo", good("glo")], ["9mobile", good("nm")]], "%") +
          bars("Year-round access", [["Motorbike", allyr("mb")], ["4x4", allyr("x4")], ["Truck", allyr("tk")], ["Saloon car", allyr("sc")]], "%") +
          bars("Businesses that need power", [["Shops and kiosks", sum("sh")], ["Grinding mills", sum("mi")], ["Craft workshops", sum("cr")], ["POS shops", sum("po")], ["Phone charging", sum("ph")], ["Oil presses", sum("op")]]) +
          bars("Main crops (first or second crop)", topc) + "<p class='sm a-muted'>Click a community on the map for its full profile.</p>";
      };
      var show = function (r) { sel = r.id; det.innerHTML = header(r) + profile(r, { compact: true, link: true }) + "<p><button type='button' class='btn btn-outline' id='sv-back'>Back to the selection</button></p>";
        document.getElementById("sv-back").onclick = function () { sel = null; summary(); }; mp.setView([r.la, r.lo], Math.max(mp.getZoom(), 9)); };
      var run = function () {
        var q = f.q.value.trim().toLowerCase(), st = f.state.value, g = f.grid.value, yr = f.year.value, col = f.colour.value;
        cur = R.filter(function (r) {
          if (q && ((r.n || "") + " " + (r.l || "")).toLowerCase().indexOf(q) < 0) return false; if (st && r.s !== st) return false;
          if (g === "nf" ? !r.nf : g && r.g !== g) return false; if (yr && r.y !== yr) return false;
          if (f.health.checked && !(r.he > 0)) return false; if (f.school.checked && !((r.p1 || 0) + (r.p2 || 0) > 0)) return false; if (f.mm.checked && r.mm !== 1) return false;
          if (f.g34.checked && ["mtn", "air", "glo", "nm"].every(function (k) { return ["3G", "4G", "5G"].indexOf(r[k]) < 0; })) return false;
          if (f.truck.checked && r.tk !== "all") return false; if (f.mill.checked && !(r.mi > 0)) return false; if (f.ready.checked && !r.rd) return false; return true; }).sort(function (a, b) { return (b.b || 0) - (a.b || 0); });
        lay.clearLayers();
        cur.forEach(function (r) { if (r.la == null) return; var c = col === "bz" ? (r.bz == null ? "#cbd5e1" : RAMP[Math.min(4, Math.floor((r.bz || 0) / 20))]) : gridOf(r)[1];
          L.circleMarker([r.la, r.lo], { renderer: crr, radius: 6, color: r.nf && col !== "bz" ? "#7a1f12" : "#fff", weight: r.nf && col !== "bz" ? 2.2 : 1.2, fillColor: c, fillOpacity: .95 }).on("click", function () { show(r); }).addTo(lay); });
        document.getElementById("sv-legend").innerHTML = col === "bz" ? "<b>Businesses running generators</b>" + RAMP.map(function (c, i) { return "<span><i style='background:" + c + "'></i>" + (i * 20) + "–" + (i * 20 + 20) + "%</span>"; }).join("") :
          [["no", 0], ["nc", 0], ["c", 0]].map(function (x) { return "<span><i style='background:" + GRID[x[0]][1] + "'></i>" + GRID[x[0]][0] + "</span>"; }).join("") + "<span><i style='background:" + NFC + ";box-shadow:0 0 0 2px #7a1f12'></i>Grid never worked</span>";
        var ng = cur.filter(function (r) { return r.g === "no"; }).length;
        strip([[nf(cur.length), "communities"], [cur.length ? nf(100 * ng / cur.length) + "%" : "—", "without grid at survey"], [nf(cur.filter(function (r) { return r.rd; }).length), "meet the build-ready criteria"]]);
        if (!sel) summary();
        var pts = cur.filter(function (r) { return r.la != null; }).map(function (r) { return [r.la, r.lo]; });
        if (pts.length && pts.length < R.length) mp.fitBounds(L.latLngBounds(pts).pad(.2), { maxZoom: 10 }); else mp.fitBounds([[4.2, 2.6], [13.9, 14.7]]);
        document.querySelector("#sv-t tbody").innerHTML = cur.slice(0, 60).map(function (r) { var gg = gridOf(r);
          return "<tr><td><a class='a-go' style='font-weight:600' href='" + r.id + "/index.html'>" + esc(r.n || "—") + "</a><br><span class='a-muted'>" + esc(r.l || "") + "</span></td><td>" + esc(r.s) + "</td><td><span class='sv-dot' style='background:" + gg[1] + "'></span>" + gg[0] + "</td><td class='n' data-v='" + (r.b || 0) + "'>" + nf(r.b) + "</td><td class='n' data-v='" + (r.bz == null ? "" : r.bz) + "'>" + (r.bz == null ? "—" : nf(r.bz) + "%") + "</td><td class='n' data-v='" + (r.he || 0) + "'>" + nf(r.he || 0) + "</td><td class='n'>" + esc(r.y) + "</td></tr>"; }).join("") || "<tr><td colspan='7' class='a-muted'>No community matches. Remove a filter.</td></tr>";
      };
      var strip = function (a) { [1, 2, 3].forEach(function (i) { document.getElementById("w-n" + i).textContent = a[i - 1][0]; document.getElementById("w-l" + i).textContent = a[i - 1][1]; }); };
      f.addEventListener("change", run); f.q.addEventListener("input", run);
      document.getElementById("sv-csv").addEventListener("click", function () {
        var cols = [["n", "Community"], ["l", "LGA"], ["s", "State"], ["d", "Survey date"], ["b", "Buildings"], ["g", "Grid (no / nc = present not connected / c = connected)"], ["nf", "Grid never functional"], ["mv", "Nearest MV line km"], ["hh", "Households with generators %"], ["bz", "Businesses with generators %"], ["pe", "Petrol NGN/l"], ["di", "Diesel NGN/l"], ["mi", "Grinding mills"], ["op", "Oil presses"], ["sh", "Shops"], ["po", "POS shops"], ["he", "Health facilities"], ["p1", "Primary schools"], ["p2", "Secondary schools"], ["mm", "Mobile money (1/0)"], ["mtn", "MTN"], ["air", "Airtel"], ["glo", "Glo"], ["nm", "9mobile"], ["tk", "Truck access"], ["cp", "Crops"], ["la", "Latitude"], ["lo", "Longitude"]];
        var q = function (v) { v = v == null ? "" : Array.isArray(v) ? v.join(";") : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
        var out = ["# NESP field survey (se4allWS:cluster_offgrid_survey), selection. Licence not yet specified on the data portal.", cols.map(function (c) { return c[1]; }).join(",")].concat(cur.map(function (r) { return cols.map(function (c) { return q(r[c[0]]); }).join(","); })).join("\n");
        var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([out], { type: "text/csv" })); a.download = "field-survey-selection.csv"; document.body.appendChild(a); a.click(); a.remove(); });
      run();
    }
  })();
