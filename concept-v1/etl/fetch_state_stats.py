"""
Nigeria SE4ALL - nightly ETL for state profiles.
Pulls public WFS layers from data.nigeriase4all.gov.ng (GeoServer) and writes
data/states.json + data/national.json + data/states.geojson for the static site.
Run:  python3 fetch_state_stats.py  [--out ../site/data]
"""
import argparse, io, json, os, sys, datetime
import pandas as pd, geopandas as gpd, requests

WFS = "https://data.nigeriase4all.gov.ng/geoserver/ows"
S = requests.Session(); S.headers["User-Agent"] = "nigeriase4all-site-etl"
PAGE = 50000

def wfs_csv(layer, props):
    frames, start = [], 0
    while True:
        r = S.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=layer,
                  outputFormat="csv", propertyName=",".join(props), count=PAGE, startIndex=start,
                  sortBy=props[0]), timeout=300)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), low_memory=False)
        frames.append(df)
        if len(df) < PAGE: break
        start += PAGE
    return pd.concat(frames, ignore_index=True)

def wfs_geo(layer):
    r = S.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=layer,
              outputFormat="application/json", srsName="EPSG:4326"), timeout=600)
    r.raise_for_status()
    g = gpd.read_file(io.BytesIO(r.content))
    return g.set_crs(4326, allow_override=True)

def num(s): return pd.to_numeric(s, errors="coerce")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="data"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pulled = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    log = lambda *x: print(*x, file=sys.stderr, flush=True)

    log("states"); st = wfs_geo("se4allWS:nigeria_state_boundaries")[["adm1_en", "geometry"]].rename(columns={"adm1_en": "state"})
    st_m = st.to_crs(3857)  # metric-ish for overlaps; lengths computed geodesically below via EPSG:32632
    names = sorted(st.state)

    log("clusters (all)"); ca = wfs_csv("se4allWS:cluster_all_simple_new", ["cluster_all_id", "number_of_buildings", "grid_dist_km", "state_name"])
    log("clusters (off-grid)"); co = wfs_csv("se4allWS:cluster_offgrid_simple", ["cluster_offgrid_id", "building_count", "grid_dist_km", "state_name", "number_of_schools", "number_of_healthcenters"])
    log("survey"); sv = wfs_geo("se4allWS:cluster_offgrid_survey")
    log("minigrids"); mg = wfs_geo("se4allWS:minigrids")
    log("mv lines"); mv = wfs_geo("se4allWS:distribution_line_mv")
    log("hv lines"); hv = wfs_geo("geonode:existing_lines_high_voltage")
    log("substations"); ss = wfs_geo("geonode:substations_currently_installed")
    log("thermal"); th = wfs_geo("geonode:generation_thermal")
    log("hydro"); hy = wfs_geo("geonode:hydro_generation")
    log("disco"); dc = wfs_geo("se4allWS:disco_coverage")
    log("markets"); mk = wfs_csv("se4allWS:grid3_market_edited", ["gid", "adm1_en"])

    for d, c in ((ca, "number_of_buildings"), (ca, "grid_dist_km"), (co, "building_count"), (co, "grid_dist_km"),
                 (co, "number_of_schools"), (co, "number_of_healthcenters")):
        d[c] = num(d[c])

    def join_pts(g):
        g = g.copy(); g["geometry"] = g.geometry.representative_point() if g.geom_type.iloc[0] != "Point" else g.geometry
        return gpd.sjoin(g, st, how="left", predicate="within")

    mgj, ssj, thj, hyj, svj = (join_pts(x) for x in (mg, ss, th, hy, sv))
    # line lengths per state (clip, then measure in UTM 32N - adequate for Nigeria)
    def km_by_state(lines):
        cl = gpd.overlay(lines[["geometry"]].explode(index_parts=False), st, how="intersection", keep_geom_type=True)
        cl["km"] = cl.to_crs(32632).length / 1000
        return cl.groupby("state").km.sum()
    log("clip mv"); mv_km = km_by_state(mv)
    mv_v = mv.copy(); mv_v["voltage_kv"] = num(mv_v.get("voltage_kv"))
    log("clip hv"); hv_km = km_by_state(hv)
    # disco: largest overlap per state
    ov = gpd.overlay(st_m, dc.to_crs(3857)[["disco_name", "disco_full", "geometry"]], how="intersection")
    ov["a"] = ov.area
    disco = {}
    for s_, grp in ov.groupby("state"):
        tot = st_m[st_m.state == s_].area.iloc[0]
        disco[s_] = [dict(code=r.disco_name, name=str(r.disco_full).strip(), share=round(float(r.a / tot), 3))
                     for r in grp.sort_values("a", ascending=False).itertuples() if r.a / tot > 0.05]

    # pre-computed lookups so the site-finder and distance charts need no live queries
    BANDS = [(0, 1), (1, 5), (5, 10), (10, 20), (20, 1e9)]
    D = [0, 1, 2, 5, 10, 15, 20, 30, 50]
    N = [0, 50, 100, 250, 500, 1000, 2000, 5000]
    def bands(df):
        return [dict(lo=lo, hi=None if hi > 1e8 else hi,
                     clusters=int(((df.grid_dist_km >= lo) & (df.grid_dist_km < hi)).sum()),
                     buildings=int(df.loc[(df.grid_dist_km >= lo) & (df.grid_dist_km < hi), "number_of_buildings"].sum()))
                for lo, hi in BANDS]
    def finder(df):
        c, b = [], []
        for d in D:
            m = df[df.grid_dist_km >= d]
            c.append([int((m.number_of_buildings >= n).sum()) for n in N])
            b.append([int(m.loc[m.number_of_buildings >= n, "number_of_buildings"].sum()) for n in N])
        return dict(c=c, b=b)
    FIND = dict(D=D, N=N, national=finder(ca), states={s_: finder(ca[ca.state_name == s_]) for s_ in names})
    json.dump(FIND, open(os.path.join(a.out, "finder.json"), "w"), separators=(",", ":"))

    out = {}
    for s_ in names:
        a_ = ca[ca.state_name == s_]; o_ = co[co.state_name == s_]
        m_ = mgj[mgj.state == s_]; sv_ = svj[svj.state == s_]
        out[s_] = dict(
            state=s_,
            clusters=int(len(a_)), buildings=int(a_.number_of_buildings.sum()),
            clusters_over_5km=int((a_.grid_dist_km > 5).sum()),
            buildings_over_5km=int(a_.loc[a_.grid_dist_km > 5, "number_of_buildings"].sum()),
            offgrid_clusters=int(len(o_)), offgrid_buildings=int(o_.building_count.sum()),
            offgrid_with_school=int((o_.number_of_schools > 0).sum()),
            offgrid_with_health=int((o_.number_of_healthcenters > 0).sum()),
            mv_km=round(float(mv_km.get(s_, 0)), 1), hv_km=round(float(hv_km.get(s_, 0)), 1),
            substations=int((ssj.state == s_).sum()), thermal_plants=int((thj.state == s_).sum()),
            hydro_plants=int((hyj.state == s_).sum()), markets=int((mk.adm1_en == s_).sum()),
            surveyed=int(len(sv_)), disco=disco.get(s_, []), bands=bands(a_),
            minigrids=[dict(community=r.community, lga=r.lga_name, kw=None if pd.isna(num(pd.Series([r.power_kw]))[0]) else float(num(pd.Series([r.power_kw]))[0]),
                            connections=None if pd.isna(num(pd.Series([r.number_of_connections]))[0]) else int(num(pd.Series([r.number_of_connections]))[0]),
                            status=r.status, system=r.power_system, programme=r.project, owner=r.owner, condition=r.condition,
                            lat=round(r.geometry.y, 5), lon=round(r.geometry.x, 5)) for r in m_.itertuples()],
            survey=[dict(community=r.community_name, lga=r.lga_name, date=str(r.survey_date)[:10], grid=r.grid_presence,
                         functionality=r.grid_functionality, income=r.income_source_primary,
                         lat=round(r.geometry.y, 5), lon=round(r.geometry.x, 5)) for r in sv_.itertuples()],
        )
    nat = dict(pulled=pulled, source=WFS,
               clusters=int(len(ca)), buildings=int(ca.number_of_buildings.sum()),
               offgrid_clusters=int(len(co)), offgrid_buildings=int(co.building_count.sum()),
               mv_km=round(float(mv_km.sum()), 0), hv_km=round(float(hv_km.sum()), 0),
               substations=int(len(ss)), thermal_plants=int(len(th)), hydro_plants=int(len(hy)),
               minigrids=int(len(mg)), minigrid_kw=float(num(mg.power_kw).sum()), minigrid_connections=int(num(mg.number_of_connections).sum()),
               surveyed=int(len(sv)), markets=int(len(mk)), bands=bands(ca),
               unassigned=dict(clusters_no_state=int(ca.state_name.isna().sum()), minigrids_no_state=int(mgj.state.isna().sum())))
    def clean(v):  # NaN/None/"null" -> null so browsers can JSON.parse the output
        if isinstance(v, dict): return {k: clean(x) for k, x in v.items()}
        if isinstance(v, list): return [clean(x) for x in v]
        if isinstance(v, float) and v != v: return None
        if isinstance(v, str) and v.strip().lower() in ("", "null", "none", "nan"): return None
        return v
    out = clean(out)
    json.dump(dict(pulled=pulled, states=out), open(os.path.join(a.out, "states.json"), "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    json.dump(nat, open(os.path.join(a.out, "national.json"), "w"), indent=1)
    simp = st.copy(); simp["geometry"] = simp.geometry.simplify(0.01, preserve_topology=True)
    simp.to_file(os.path.join(a.out, "states.geojson"), driver="GeoJSON")
    log("done", nat)

if __name__ == "__main__":
    main()
