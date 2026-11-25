"""
v8 job: one combined, de-duplicated list of Nigeria's mini-grids from every open source we can read, plus a site list of
off-grid settlements (candidate sites) with distances recalculated against the field-mapped MV grid.

Sources (each record keeps the list of sources that report it):
  platform  - SE4ALL GeoNode layer se4allWS:minigrids (via insights.json)              licence: not specified on the portal
  nep       - Nigeria Electrification Project map, nep.rea.gov.ng (via projects.json)   licence: none stated; REA agreement needed
  eae       - REA mini-grid data published by WRI's Energy Access Explorer (S3 GeoJSON) licence: (c) REA, extracts may be published with acknowledgement
  osm       - OpenStreetMap solar plants <= 1 MW or unknown size ("possible mini-grids")  licence: ODbL. Kept SEPARATE (share-alike), never merged into the combined file.
Optional: World Bank DRE Atlas settlements CSV (CC BY 4.0) -> --dre path, adds estimated demand/connections to candidate sites.

Run: python3 compile_minigrids.py --data ../data --raw ../data/raw [--dre nigeria_dre_atlas_settlements.csv]
"""
import argparse, io, json, os, re, math, datetime
import numpy as np, pandas as pd, geopandas as gpd, requests, shapely
from scipy.spatial import cKDTree

WFS = "https://data.nigeriase4all.gov.ng/geoserver/ows"
S = requests.Session(); S.headers["User-Agent"] = "nigeriase4all-site-etl"
EAE_URL = "https://wri-public-data.s3.amazonaws.com/EnergyAccess/NGA/Minigrids/NGA_REA_Minigrids_Merged.geojson"
MATCH_M = 1000

def wfs_json(layer, **kw):
    r = S.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=layer, outputFormat="application/json", srsName="EPSG:4326", **kw), timeout=600)
    r.raise_for_status(); return r.json()

def status_norm(s):
    t = (s or "").lower()
    if not t: return "Not stated"
    if "non" in t and "operational" in t: return "Not operational"
    if "commission" in t and "not commission" not in t and "completed" in t: return "Operational / commissioned"
    if t in ("existing", "operational"): return "Operational / commissioned"
    if "completed but not" in t or "advanced" in t or "construction" in t or "approved" in t: return "Under construction / approved"
    if "evaluation" in t or "review" in t: return "In evaluation"
    return s.strip().capitalize()

def title(s):
    if not s: return None
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s.title() if s.isupper() else s

def mw_to_kw(v):
    if not v: return None
    m = re.match(r"\s*([\d.]+)\s*(mw|kw|w)?", str(v).lower().replace(",", "."))
    if not m: return None
    x = float(m.group(1)); u = m.group(2) or "mw"
    return x * 1000 if u == "mw" else (x if u == "kw" else x / 1000)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--raw", required=True); ap.add_argument("--dre"); a = ap.parse_args()
    I = json.load(open(os.path.join(a.data, "insights.json"))); NEP = json.load(open(os.path.join(a.data, "projects.json")))
    st = gpd.read_file(os.path.join(a.data, "states.geojson"))[["state", "geometry"]]
    raw_eae = os.path.join(a.raw, "eae_rea_minigrids.geojson")
    if not os.path.exists(raw_eae):
        open(raw_eae, "wb").write(S.get(EAE_URL, timeout=120).content)
    eae = json.load(open(raw_eae))

    R = []
    for i, g in enumerate(I["fleet"]):
        R.append(dict(src="platform", sid=f"platform-{i+1}", name=g["community"], developer=g.get("owner"), lga=g["lga"], kw=g["kw"], connections=g["conn"],
                      status=status_norm(g["condition"] if g["status"] == "Existing" else g["status"]), status_raw=" · ".join(x for x in (g["status"], g["condition"]) if x),
                      programme=g["programme"], system=g["system"], lat=g["lat"], lon=g["lon"]))
    for p in NEP["projects"]:
        if p["kind"] != "minigrid": continue
        R.append(dict(src="nep", sid=p["id"], name=p["name"], developer=p["developer"], lga=p["lga"], kw=p["capacity_kw"], connections=p["customers"],
                      status="Not stated", status_raw=None, programme="NEP Performance-Based Grant", system="Solar hybrid", lat=p["lat"], lon=p["lon"]))
    for i, f in enumerate(eae["features"]):
        q = f["properties"]
        conn = q.get("Total_Conn"); conn = conn if isinstance(conn, (int, float)) else None
        name = q.get("Project") or ""
        m = re.search(r"\bAT\s+(.+?)\s+COMMUNITY", name.upper())
        R.append(dict(src="eae", sid=f"eae-{i+1}", name=title(m.group(1)) if m else title(name), project_title=title(name), developer=title(q.get("Name")), lga=None,
                      kw=q.get("CAPACITY") if isinstance(q.get("CAPACITY"), (int, float)) else None, connections=conn,
                      status=status_norm(q.get("Status/Lev")), status_raw=q.get("Status/Lev"),
                      programme={"REF": "Rural Electrification Fund (REF)"}.get(q.get("Programme"), "NEP Performance-Based Grant" if "Performance" in (q.get("Programme") or "") else q.get("Programme")),
                      system="Solar hybrid", lat=f["geometry"]["coordinates"][1], lon=f["geometry"]["coordinates"][0]))
    df = pd.DataFrame(R)
    df = df[df.lat.notna() & df.lon.notna()].reset_index(drop=True)

    # ---- one-to-one matching across sources: two records are the same site when they are each other's nearest
    # record in the other source and within 1 km (no chaining, so neighbouring sites stay separate).
    # Exact duplicates inside one source (same point) are merged first.
    xy = gpd.GeoSeries(gpd.points_from_xy(df.lon, df.lat), crs=4326).to_crs(32632)
    df["x"], df["y"] = xy.x.values, xy.y.values
    df["site"] = -1; nxt = 0
    sites_xy = {}                                   # site id -> (x, y)
    for src in ("eae", "nep", "platform"):
        sub = df[df.src == src]
        groups = list(sub.groupby([sub.x.round(0), sub.y.round(0)]))
        pts = np.array([[k[0], k[1]] for k, _ in groups])
        if sites_xy:
            ids = np.array(list(sites_xy.keys())); spts = np.array(list(sites_xy.values()))
            d1, i1 = cKDTree(spts).query(pts)                   # each new record -> nearest existing site
            d2, i2 = cKDTree(pts).query(spts)                   # each existing site -> nearest new record
            taken = set()
            for gi, (key, grp) in enumerate(groups):
                si = i1[gi]
                if d1[gi] <= MATCH_M and i2[si] == gi and ids[si] not in taken and src not in set(df.loc[df.site == ids[si], "src"]):
                    df.loc[grp.index, "site"] = ids[si]; taken.add(ids[si]); continue
                df.loc[grp.index, "site"] = nxt; sites_xy[nxt] = (key[0], key[1]); nxt += 1
        else:
            for key, grp in groups:
                df.loc[grp.index, "site"] = nxt; sites_xy[nxt] = (key[0], key[1]); nxt += 1
    PREF = {"platform": 0, "eae": 1, "nep": 2}
    sites = []
    for k, grp in df.groupby("site"):
        grp = grp.sort_values("src", key=lambda s: s.map(PREF))
        first = lambda col: next((v for v in grp[col] if v is not None and not (isinstance(v, float) and math.isnan(v)) and v != ""), None)
        statuses = [s for s in grp.status if s and s != "Not stated"]
        sites.append(dict(name=first("name"), project_title=first("project_title") if "project_title" in grp else None, developer=first("developer"), lga=first("lga"),
                          kw=first("kw"), connections=first("connections"), status=statuses[0] if statuses else "Not stated", status_raw=first("status_raw"),
                          programme=first("programme"), system=first("system"), lat=float(grp.lat.iloc[0]), lon=float(grp.lon.iloc[0]),
                          sources=sorted(set(grp.src), key=lambda s: PREF[s]), source_ids=list(grp.sid),
                          recs=[dict(src=r.src, sid=r.sid, name=r.name, developer=r.developer, kw=None if r.kw is None or r.kw != r.kw else r.kw,
                                     conn=None if r.connections is None or r.connections != r.connections else r.connections, status=r.status_raw if isinstance(r.status_raw, str) else r.status) for r in grp.itertuples()]))
    S_ = pd.DataFrame(sites)
    g = gpd.GeoDataFrame(S_, geometry=gpd.points_from_xy(S_.lon, S_.lat), crs=4326)
    j = gpd.sjoin(g, st, how="left", predicate="within"); j = j[~j.index.duplicated()]
    S_["state"] = j["state"].values
    miss = S_.state.isna()
    if miss.any():
        stm = st.to_crs(32632); pm = g[miss].to_crs(32632)
        S_.loc[miss, "state"] = [stm.state.iloc[stm.distance(p).values.argmin()] for p in pm.geometry]
    S_ = S_.sort_values(["state", "name"], na_position="last").reset_index(drop=True)
    S_["id"] = [f"MG-{i+1:04d}" for i in range(len(S_))]

    # ---- OSM solar plants (separate, ODbL)
    osm = json.load(open(os.path.join(a.raw, "osm_power_plants_nigeria.json")))
    O = []
    for e in osm["elements"]:
        t = e.get("tags", {})
        if t.get("power") != "plant" or (t.get("plant:source") or t.get("generator:source")) != "solar": continue
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        kw = mw_to_kw(t.get("plant:output:electricity")) if t.get("plant:output:electricity") not in (None, "yes") else None
        if kw and kw > 1000: continue            # utility or campus scale: not a mini-grid
        O.append(dict(osm=f"{e['type']}/{e['id']}", name=t.get("name"), operator=t.get("operator"), kw=kw, start=t.get("start_date"), lat=c["lat"], lon=c["lon"]))
    O = pd.DataFrame(O)
    if len(O):
        oxy = gpd.GeoSeries(gpd.points_from_xy(O.lon, O.lat), crs=4326).to_crs(32632)
        sxy = gpd.GeoSeries(gpd.points_from_xy(S_.lon, S_.lat), crs=4326).to_crs(32632)
        d, _ = cKDTree(np.column_stack([sxy.x, sxy.y])).query(np.column_stack([oxy.x, oxy.y]))
        O["near_known_km"] = np.round(d / 1000, 2)
        go = gpd.GeoDataFrame(O, geometry=gpd.points_from_xy(O.lon, O.lat), crs=4326)
        jo = gpd.sjoin(go, st, how="left", predicate="within"); jo = jo[~jo.index.duplicated()]; O["state"] = jo["state"].values

    # ---- candidate sites: SE4ALL off-grid settlements, distances recalculated
    og = wfs_json("se4allWS:cluster_offgrid_simple")
    C = pd.DataFrame([dict(cid=f["properties"]["cluster_offgrid_id"], bld=f["properties"]["building_count"], dist_rec=f["properties"]["grid_dist_km"],
                           schools=f["properties"].get("number_of_schools"), health=f["properties"].get("number_of_healthcenters"), markets=f["properties"].get("number_of_markets"),
                           state=f["properties"].get("state_name"), lon=f["geometry"]["coordinates"][0], lat=f["geometry"]["coordinates"][1])
                      for f in og["features"] if f.get("geometry")])
    mv = gpd.GeoDataFrame.from_features(wfs_json("se4allWS:distribution_line_mv")["features"], crs=4326).to_crs(32632)
    mv = mv[mv.geometry.notna() & ~mv.geometry.is_empty]
    coords, idx = shapely.get_coordinates(mv.geometry.values, return_index=True)
    p0, p1 = coords[:-1], coords[1:]; same = idx[:-1] == idx[1:]; p0, p1 = p0[same], p1[same]
    L = np.hypot(*(p1 - p0).T); n = np.maximum(1, np.ceil(L / 100.0).astype(int))
    seg = np.repeat(np.arange(len(p0)), n); k = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
    verts = np.vstack([p0[seg] + (p1[seg] - p0[seg]) * (k / n[seg])[:, None], coords])
    cxy = gpd.GeoSeries(gpd.points_from_xy(C.lon, C.lat), crs=4326).to_crs(32632); CP = np.column_stack([cxy.x, cxy.y])
    C["mv_km"] = np.round(cKDTree(verts).query(CP, workers=-1)[0] / 1000, 2)
    sxy = gpd.GeoSeries(gpd.points_from_xy(S_.lon, S_.lat), crs=4326).to_crs(32632)
    dmg, imgi = cKDTree(np.column_stack([sxy.x, sxy.y])).query(CP)
    C["mg_km"] = np.round(dmg / 1000, 1); C["mg_id"] = S_.id.values[imgi]
    X = json.load(open(os.path.join(a.data, "extras.json")))
    subs = [s for v in X["states"].values() for s in v["substations"]]
    bxy = gpd.GeoSeries(gpd.points_from_xy([s["lon"] for s in subs], [s["lat"] for s in subs]), crs=4326).to_crs(32632)
    dsb, isb = cKDTree(np.column_stack([bxy.x, bxy.y])).query(CP)
    C["sub_km"] = np.round(dsb / 1000, 1); C["sub"] = [subs[i]["name"] for i in isb]
    gc = gpd.GeoDataFrame(C.drop(columns=["state"]), geometry=cxy.to_crs(4326).values, crs=4326)
    jc = gpd.sjoin(gc, st, how="left", predicate="within"); jc = jc[~jc.index.duplicated()]
    C["state"] = pd.Series(jc["state"].values).fillna(C["state"]).values
    # surveyed community within 2 km
    sv = pd.DataFrame(I["communities"]); sv = sv[sv.lat.notna()]
    vxy = gpd.GeoSeries(gpd.points_from_xy(sv.lon, sv.lat), crs=4326).to_crs(32632)
    dsv, isv = cKDTree(np.column_stack([vxy.x, vxy.y])).query(CP)
    C["survey_uid"] = np.where(dsv <= 2000, sv.uid.values[isv], None)
    dre_note = None
    if a.dre and os.path.exists(a.dre):
        # World Bank DRE Atlas (CC BY 4.0): nearest DRE settlement within 1 km of each candidate
        D = pd.read_csv(a.dre, low_memory=False, usecols=["lat", "lon", "village_name", "admin_cgaz_2", "num_buildings", "population", "num_connections",
                                                         "demand", "demand_connection", "pv_value", "mean_rwi", "main_road_access", "dist_main_road_km"])
        D = D[D.lat.notna() & D.lon.notna()].reset_index(drop=True)
        dxy = gpd.GeoSeries(gpd.points_from_xy(D.lon, D.lat), crs=4326).to_crs(32632)
        dd, di = cKDTree(np.column_stack([dxy.x, dxy.y])).query(CP)
        ok = dd <= 1000
        num_map = {"demand": ("dre_kwh_day", 1), "num_connections": ("dre_conn", 0), "pv_value": ("dre_pv", 0), "mean_rwi": ("dre_rwi", 2), "population": ("dre_pop", 0), "dist_main_road_km": ("dre_road_km", 1)}
        for col, (out, nd) in num_map.items():
            v = pd.to_numeric(D[col], errors="coerce").values[di]
            C[out] = np.where(ok, np.round(v, nd), np.nan)
        for col, out in (("village_name", "dre_name"), ("admin_cgaz_2", "dre_lga")):
            v = D[col].astype(object).values[di]
            C[out] = [x if (o and isinstance(x, str) and x.strip()) else None for x, o in zip(v, ok)]
        dre_note = dict(rows=int(len(D)), matched=int(ok.sum()), source="World Bank DRE Atlas, energydata.info (CC BY 4.0)")
    C = C.sort_values("bld", ascending=False).reset_index(drop=True)

    clean = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else (v.item() if hasattr(v, "item") else v)
    recs = [{k: clean(v) for k, v in r.items()} for r in S_.to_dict("records")]
    out = dict(pulled=datetime.date.today().isoformat(), match_m=MATCH_M, sites=recs,
               osm=[{k: clean(v) for k, v in r.items()} for r in O.to_dict("records")],
               candidates=[{k: clean(v) for k, v in r.items()} for r in C.drop(columns=["dist_rec"]).to_dict("records")],
               checks=dict(records_in=int(len(df)), by_source={s: int((df.src == s).sum()) for s in PREF}, sites=int(len(S_)),
                           multi_source=int(S_.sources.map(len).gt(1).sum()), candidates=int(len(C)), osm=int(len(O)), dre=dre_note,
                           candidate_dist_median_recorded=float(np.nanmedian(C.get("dist_rec", pd.Series([np.nan])))) if "dist_rec" in C else None))
    out["sites"] = json.loads(json.dumps(out["sites"], default=str).replace("NaN", "null"))
    json.dump(out, open(os.path.join(a.data, "minigrids.json"), "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    print(json.dumps(out["checks"], indent=1))
    print(S_.groupby(S_.sources.map(lambda s: "+".join(s))).size())
    print(S_.status.value_counts())

if __name__ == "__main__":
    main()
