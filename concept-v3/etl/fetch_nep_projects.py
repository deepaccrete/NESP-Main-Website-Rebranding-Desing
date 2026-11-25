"""
NEP projects job: reads the project arrays published in the map script on https://nep.rea.gov.ng/
(assets/js/maps.js) WITHOUT executing it (JSON5 parsing only), normalises every programme into one
projects file, checks each record against state boundaries, and links NEP mini-grids to the SE4ALL
mini-grid layer. Output: data/projects.json
Run: python3 fetch_nep_projects.py --states ../data/states.geojson --insights ../data/insights.json --out ../data
Source data: Rural Electrification Agency, Nigeria Electrification Project. Republishing should be confirmed with REA.
"""
import argparse, json, os, re, datetime
import requests, json5, numpy as np, pandas as pd, geopandas as gpd

SRC = "https://nep.rea.gov.ng/assets/js/maps.js"
PROGRAMMES = {
    "pbgapril2021": ("minigrid", "Solar hybrid mini-grid (Performance-Based Grant)"),
    "covid": ("health", "Health facility solar (COVID-19 intervention)"),
    "eep1": ("education", "Energizing Education Programme, phase I"),
    "eep2": ("education", "Energizing Education Programme, phase II"),
    "eep3": ("education", "Energizing Education Programme, phase III"),
}
FIX_STATE = {"nassarawa": "Nasarawa", "fct": "Federal Capital Territory", "abuja": "Federal Capital Territory", "akwa-ibom": "Akwa Ibom", "cross-river": "Cross River"}

def arrays(js):
    out = {}
    for m in re.finditer(r'const\s+(\w+)\s*=\s*\[', js):
        i = m.end() - 1; depth = 0; q = None; j = i
        for j in range(i, len(js)):
            ch = js[j]
            if q:
                if ch == "\\": continue
                if ch == q: q = None
                continue
            if ch in "'\"`": q = ch
            elif ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0: break
        try: out[m.group(1)] = json5.loads(js[i:j + 1])
        except Exception: pass                      # template arrays that are not plain data are skipped
    return out

def num(v):
    if v in (None, "", "#Name", "$0"): return None
    try: return float(str(v).replace(",", "").replace("$", "").replace("₦", "").strip())
    except ValueError: return None

def norm_state(s):
    s = str(s or "").strip(); k = s.lower().replace(" state", "")
    return FIX_STATE.get(k, s.title() if s else None)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--states", required=True); ap.add_argument("--insights", required=True); ap.add_argument("--out", default="data"); a = ap.parse_args()
    r = requests.get(SRC, timeout=120, headers={"User-Agent": "nigeriase4all-site-etl"}); r.raise_for_status()
    A = arrays(r.text)
    rows = []
    for key, (kind, prog) in PROGRAMMES.items():
        for i, o in enumerate(A.get(key, [])):
            lat = num(o.get("lat", o.get("latitude"))); lon = num(o.get("lng", o.get("longitude")))
            if kind == "minigrid":
                rec = dict(name=o.get("projectname"), developer=o.get("organization"), lga=o.get("lga"), stated_state=norm_state(o.get("state")),
                           capacity_kw=num(o.get("capacity")), customers=num(o.get("customers")), status=None, completion=None, grant=None)
            elif kind == "health":
                rec = dict(name=o.get("name"), developer=None, lga=None, stated_state=norm_state(o.get("state")), capacity_kw=num(o.get("capacity")),
                           customers=None, status=o.get("status"), completion=None, grant=None, lot=o.get("lotno"))
            else:
                dev = o.get("developer"); dev = None if dev in ("", "#Name") else dev
                pct = num(o.get("status")) if isinstance(o.get("status"), (int, float)) else None
                rec = dict(name=o.get("projecttitle"), developer=dev, lga=None, stated_state=norm_state(o.get("state")),
                           capacity_kw=num(o.get("installcapacity")) or None, customers=None,
                           status=(f"{int(pct)}% complete" if pct is not None else (o.get("status") or None)),
                           completion=(o.get("levelcompletion") or None) if pct is not None else None, grant=num(o.get("grant")) or None)
            rec.update(id=f"{key}-{i+1}", kind=kind, programme=prog, source_array=key, lat=lat, lon=lon)
            rows.append(rec)
    df = pd.DataFrame(rows)
    st = gpd.read_file(a.states)[["state", "geometry"]].rename(columns={"state": "geo_state"})
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
    j = gpd.sjoin(g, st, how="left", predicate="within"); j = j[~j.index.duplicated()]
    df["state"] = j["geo_state"].values
    df["state_mismatch"] = df.stated_state.notna() & df.state.notna() & (df.stated_state != df.state)
    df["duplicate_point"] = df.duplicated(["kind", "lat", "lon"], keep=False)

    # link NEP mini-grids to the SE4ALL mini-grid layer (same site within 1 km)
    I = json.load(open(a.insights)); fleet = pd.DataFrame(I["fleet"])
    mg = df[df.kind == "minigrid"]
    a_xy = gpd.GeoSeries(gpd.points_from_xy(mg.lon, mg.lat), crs=4326).to_crs(32632)
    f_xy = gpd.GeoSeries(gpd.points_from_xy(fleet.lon, fleet.lat), crs=4326).to_crs(32632)
    d = np.array([[p.distance(q) for q in f_xy] for p in a_xy]) if len(fleet) else np.zeros((len(mg), 0))
    near = d.min(axis=1) if d.size else np.full(len(mg), np.inf)
    df.loc[mg.index, "in_se4all_layer"] = near <= 1000
    overlap = int((near <= 1000).sum())

    shs = [dict(state=norm_state(o.get("State")), connections=num(o.get("Connections")), lat=num(o.get("latitude")), lon=num(o.get("longitude"))) for o in A.get("shsobf", [])]
    clean = lambda v: None if (isinstance(v, float) and v != v) else (bool(v) if isinstance(v, (np.bool_,)) else v)
    projects = [{k: clean(v) for k, v in rec.items()} for rec in df.drop(columns=[]).to_dict("records")]
    summary = dict(
        pulled=datetime.date.today().isoformat(), source=SRC, snapshot_label="pbgapril2021 (April 2021)",
        minigrids=int((df.kind == "minigrid").sum()), minigrid_kw=float(df.loc[df.kind == "minigrid", "capacity_kw"].sum()),
        minigrid_customers=float(df.loc[df.kind == "minigrid", "customers"].sum()), minigrid_developers=int(df.loc[df.kind == "minigrid", "developer"].nunique()),
        minigrid_states=int(df.loc[df.kind == "minigrid", "state"].nunique()), overlap_with_se4all=overlap, se4all_layer=int(len(fleet)),
        health=int((df.kind == "health").sum()), education=int((df.kind == "education").sum()),
        education_by_phase={k: int((df.source_array == k).sum()) for k in ("eep1", "eep2", "eep3")},
        shs_connections=float(sum(s["connections"] or 0 for s in shs)), shs_states=len(shs),
        checks=dict(state_mismatch=int(df.state_mismatch.sum()), duplicate_points=int(df.duplicate_point.sum()),
                    health_capacity_values=sorted(df.loc[df.kind == "health", "capacity_kw"].dropna().unique().tolist())))
    os.makedirs(a.out, exist_ok=True)
    json.dump(dict(summary=summary, projects=projects, shs=shs), open(os.path.join(a.out, "projects.json"), "w"), ensure_ascii=False, indent=0, default=str)
    print(json.dumps(summary, indent=1))
    print(df[df.state_mismatch][["name", "stated_state", "state"]].to_string())

if __name__ == "__main__":
    main()
