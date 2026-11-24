"""
Infrastructure and catalogue extras for v5 (run nightly after fetch_state_stats.py and compute_insights.py).
- Places substations (installed/planned), power plants and HV lines in each state.
- For each surveyed community: nearest installed substation and distance to the nearest MV line,
  recalculated against the current distribution_line_mv layer.
- Pulls the GeoNode dataset catalogue (titles, layer names, download links) for the researchers page.
Run: python3 compute_extras.py --states <states.geojson> --insights <insights.json> --out ../data
"""
import argparse, io, json, os
import geopandas as gpd, pandas as pd, numpy as np, requests

PORTAL = "https://data.nigeriase4all.gov.ng"
WFS = PORTAL + "/geoserver/ows"
UTM = 32632

def layer(name):
    r = requests.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=name,
                     outputFormat="application/json", srsName="EPSG:4326"), timeout=600)
    r.raise_for_status()
    return gpd.read_file(io.BytesIO(r.content)).set_crs(4326, allow_override=True)

def in_state(pts, st):
    """Point-in-state, with a 5 km tolerance for points just outside the simplified (coastal) boundaries.
    Points further away (e.g. planned West African Power Pool substations in neighbouring countries) stay unassigned."""
    j = gpd.sjoin(pts, st, how="left", predicate="within"); j = j[~j.index.duplicated()].drop(columns=["index_right"], errors="ignore")
    miss = j[j.state.isna()]
    if len(miss):
        nn = gpd.sjoin_nearest(miss.drop(columns=["state"]).to_crs(UTM), st.to_crs(UTM), how="left", max_distance=5000)
        nn = nn[~nn.index.duplicated()]
        j.loc[nn.index, "state"] = nn["state"]
    return j

def kv(v):
    v = str(v or "").lower().replace("kv", "").strip()
    try: return int(float(v))
    except ValueError: return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--states", required=True); ap.add_argument("--insights", required=True); ap.add_argument("--out", default="data"); a = ap.parse_args()
    st = gpd.read_file(a.states)[["state", "geometry"]].set_crs(4326, allow_override=True)
    I = json.load(open(a.insights))

    raw_subs = layer("geonode:substations_currently_installed")
    subs = in_state(raw_subs, st); subs["kv"] = subs.voltage.map(kv); subs["name"] = subs.sub_name
    dup_subs = int(subs.duplicated(["name", "kv"]).sum())
    subs = subs.drop_duplicates(["name", "kv"])            # the source layer repeats some substations
    fut = in_state(layer("geonode:substations_future"), st); fut["kv"] = fut.voltage.map(kv); fut = fut.drop_duplicates(["name", "kv"])
    plants = []
    for lyr, kind, status in [("geonode:generation_thermal", "Thermal (gas/steam)", "Existing"), ("geonode:hydro_generation", "Hydro", "Existing"),
                              ("geonode:wind_existing", "Wind", "Existing"), ("geonode:thermal_future", "Thermal", "Planned")]:
        g = in_state(layer(lyr), st).drop_duplicates(["name"]); g["kind"] = kind; g["status"] = status; plants.append(g[["name", "kind", "status", "state", "geometry"]])  # source layers repeat each plant
    plants = pd.concat(plants, ignore_index=True)
    hv = layer("geonode:existing_lines_high_voltage")
    hvc = gpd.overlay(hv[["name", "volt", "geometry"]], st, how="intersection", keep_geom_type=True)
    hvc["km"] = hvc.to_crs(UTM).length / 1000
    mv = layer("se4allWS:distribution_line_mv")[["geometry"]]

    # --- nearest substation + recalculated MV distance for surveyed communities
    com = pd.DataFrame(I["communities"])
    cg = gpd.GeoDataFrame(com, geometry=gpd.points_from_xy(com.lon, com.lat), crs=4326)
    ok = cg[cg.lat.notna()].to_crs(UTM)
    sub_m = subs.to_crs(UTM)[["name", "kv", "geometry"]].reset_index(drop=True)
    near = gpd.sjoin_nearest(ok[["geometry"]], sub_m, how="left", distance_col="d")
    near = near[~near.index.duplicated()]
    mv_m = mv.to_crs(UTM); mv_m = mv_m[mv_m.geometry.notna() & ~mv_m.geometry.is_empty]
    nm = gpd.sjoin_nearest(ok[["geometry"]], mv_m[["geometry"]], how="left", distance_col="d")
    nm = nm[~nm.index.duplicated()]
    per_comm = {}
    for i in ok.index:
        per_comm[str(com.at[i, "uid"])] = dict(sub_name=near.at[i, "name"], sub_kv=None if pd.isna(near.at[i, "kv"]) else int(near.at[i, "kv"]),
                                sub_km=round(float(near.at[i, "d"]) / 1000, 1), mv_km=round(float(nm.at[i, "d"]) / 1000, 2))

    states = {}
    for s in sorted(st.state):
        ss = subs[subs.state == s]; ff = fut[fut.state == s]; pp = plants[plants.state == s]; hh = hvc[hvc.state == s]
        lines = hh.groupby(["name", "volt"], dropna=False).km.sum().reset_index().sort_values("km", ascending=False)
        states[s] = dict(
            substations=[dict(name=r.name, kv=None if pd.isna(r.kv) else int(r.kv), lat=round(r.geometry.y, 5), lon=round(r.geometry.x, 5)) for r in ss.itertuples()],
            substations_by_kv={str(int(k)): int(v) for k, v in ss.kv.value_counts().sort_index(ascending=False).items()},
            planned_substations=[dict(name=r.name, kv=None if pd.isna(r.kv) else int(r.kv), lat=round(r.geometry.y, 5), lon=round(r.geometry.x, 5)) for r in ff.itertuples()],
            plants=[dict(name=r.name, kind=r.kind, status=r.status, lat=round(r.geometry.y, 5), lon=round(r.geometry.x, 5)) for r in pp.itertuples()],
            hv_lines=[dict(name=r.name, volt=r.volt, km=round(float(r.km), 1)) for r in lines.itertuples() if r.km >= 0.5],
        )
    nat = dict(source_substation_points=int(len(raw_subs)), duplicate_substations_removed=dup_subs, substations=int(subs.state.notna().sum()), substations_by_kv={str(int(k)): int(v) for k, v in subs[subs.state.notna()].kv.value_counts().sort_index(ascending=False).items()},
               planned_substations=int(fut.state.notna().sum()), plants=plants[plants.state.notna()].groupby(["kind", "status"]).size().reset_index().values.tolist(),
               hv_lines=int(hv.name.nunique()))

    # --- dataset catalogue
    cat = []
    r = requests.get(PORTAL + "/api/v2/datasets", params=dict(page_size=100, format="json"), timeout=120); r.raise_for_status()
    for d in r.json()["datasets"]:
        dd = requests.get(f"{PORTAL}/api/v2/datasets/{d['pk']}", params=dict(format="json"), timeout=120).json()["dataset"]
        links = {l.get("name"): l.get("url") for l in dd.get("links", []) if l.get("link_type") == "data"}
        n = requests.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=d["alternate"], resultType="hits"), timeout=120).text
        import re
        m = re.search(r'numberMatched="(\d+)"', n)
        cat.append(dict(pk=d["pk"], title=d["title"], layer=d["alternate"], features=int(m.group(1)) if m else None,
                        geometry=dd.get("subtype"), page=f"{PORTAL}/catalogue/#/dataset/{d['pk']}",
                        shapefile=links.get("Zipped Shapefile"), geojson=links.get("GeoJSON"), csv=links.get("CSV"), excel=links.get("Excel")))

    out = dict(states=states, national=nat, communities=per_comm, catalogue=sorted(cat, key=lambda c: c["title"]))
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "extras.json"), "w"), ensure_ascii=False, separators=(",", ":"), default=lambda o: None if (isinstance(o, float) and o != o) else str(o))
    print(json.dumps(nat, indent=1)); print("catalogue", len(cat), "communities", len(per_comm))
    print("median recalculated MV distance (km) for surveyed communities:", round(float(np.median([v["mv_km"] for v in per_comm.values()])), 2))

if __name__ == "__main__":
    main()
