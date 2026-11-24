"""
Role briefings - nightly insight job.
Reads per-state figures (states.json from fetch_state_stats.py) and pulls the field-survey and
mini-grid layers from the public GeoServer, then writes data/insights.json for the role pages.
Every number on a role page comes from this file.
Run: python3 compute_insights.py --states ../../nesp-website-v2/data/states.json --out ../data
"""
import argparse, io, json, os, datetime
import numpy as np, pandas as pd, requests

WFS = "https://data.nigeriase4all.gov.ng/geoserver/ows"
# Build-ready criteria (shown on the page; to be agreed with the client)
READY = dict(min_buildings=200, min_business_genset_pct=50, need_all_year_access=True, need_payments_or_data=True)

def layer(name):
    r = requests.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=name,
                     outputFormat="application/json", srsName="EPSG:4326"), timeout=300)
    r.raise_for_status()
    fs = r.json()["features"]
    df = pd.DataFrame([f["properties"] for f in fs]).replace(["null", "None", ""], np.nan)
    df["lon"] = [f["geometry"]["coordinates"][0] if f.get("geometry") else np.nan for f in fs]
    df["lat"] = [f["geometry"]["coordinates"][1] if f.get("geometry") else np.nan for f in fs]
    return df

def n(s): return pd.to_numeric(s, errors="coerce")
def pc(s): return pd.to_numeric(s.astype(str).str.rstrip("%"), errors="coerce")
def clean(v):
    if isinstance(v, dict): return {k: clean(x) for k, x in v.items()}
    if isinstance(v, list): return [clean(x) for x in v]
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating, float)): return None if v != v else round(float(v), 4)
    if isinstance(v, (np.bool_,)): return bool(v)
    return v

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--states", required=True); ap.add_argument("--out", default="data"); a = ap.parse_args()
    S = json.load(open(a.states)); pulled = S["pulled"]; S = S["states"]
    sv = layer("se4allWS:cluster_offgrid_survey"); mg = layer("se4allWS:minigrids")

    # ---------- survey features
    sv["bld"] = n(sv.building_count); sv["hh_gen"] = pc(sv.households_with_genset_percentage); sv["bz_gen"] = pc(sv.businesses_with_genset_percentage)
    sv["petrol"] = n(sv.petrol_price_ngn_per_litre); sv["diesel"] = n(sv.diesel_price_ngn_per_litre)
    sv["mills"] = n(sv.count_productive_use_grinding_mills); sv["presses"] = n(sv.count_productive_use_oil_press)
    sv["health"] = n(sv.count_health_facilities); sv["schools"] = n(sv.count_primary_schools).fillna(0) + n(sv.count_secondary_schools).fillna(0)
    sv["mobile_money"] = sv.mobile_money_available.astype(str) == "True"
    sv["data_3g4g"] = sv[["network_mtn", "network_airtel", "network_glo", "network_9mobile"]].isin(["3G", "4G"]).any(axis=1)
    sv["all_year"] = sv.accessibility_truck.eq("all_year_round") | sv.accessibility_4x4_car.eq("all_year_round")
    sv["year"] = sv.survey_date.astype(str).str[:4]
    sv["uid"] = sv.cluster_offgrid_id.astype(str) + "-" + sv.settlement_wo_id.astype(str) + "-" + sv.wo_number.astype(str)
    sv["uid"] = sv["uid"] + sv.groupby("uid").cumcount().map(lambda k: "" if k == 0 else f"-{k}")
    sv["grid"] = sv.grid_presence
    sv["never_functional"] = sv.grid_functionality.eq("never_functional")
    nog = sv[sv.grid == "no"]
    rdy = nog[(nog.bld >= READY["min_buildings"]) & (nog.bz_gen >= READY["min_business_genset_pct"]) & nog.all_year & (nog.mobile_money | nog.data_3g4g)]

    keep = ["uid", "community_name", "lga_name", "state_name", "bld", "hh_gen", "bz_gen", "mills", "presses", "health", "schools",
            "mobile_money", "data_3g4g", "all_year", "year", "grid", "never_functional", "lat", "lon"]
    communities = sv[keep].rename(columns={"community_name": "name", "lga_name": "lga", "state_name": "state"})

    # ---------- mini-grid fleet
    mg["kw"] = n(mg.power_kw); mg["conn"] = n(mg.number_of_connections)
    mg["operational"] = mg.condition.astype(str).str.lower().eq("operational")
    fleet = mg[["community", "lga_name", "power_system", "kw", "conn", "status", "condition", "project", "owner", "operational", "lat", "lon"]] \
        .rename(columns={"lga_name": "lga", "power_system": "system", "project": "programme"})

    # ---------- per-state rollup
    st = pd.DataFrame(S).T
    for c in ("offgrid_buildings", "buildings_over_5km", "buildings", "clusters"): st[c] = st[c].astype(int)
    st["mg_n"] = st.minigrids.apply(len); st["mg_kw"] = st.minigrids.apply(lambda m: sum((x["kw"] or 0) for x in m))
    st["disco"] = st.disco.apply(lambda d: d[0]["code"] if d else None)
    st["under_grid_b"] = st.bands.apply(lambda b: b[0]["buildings"])
    st["rank_offgrid"] = st.offgrid_buildings.rank(ascending=False, method="min").astype(int)
    st["rank_b5"] = st.buildings_over_5km.rank(ascending=False, method="min").astype(int)
    by = sv.groupby("state_name")
    states = {}
    for s, r in st.iterrows():
        g = sv[sv.state_name == s]; ng = g[g.grid == "no"]
        states[s] = dict(
            state=s, disco=r.disco, buildings=r.buildings, clusters=r.clusters, offgrid_buildings=r.offgrid_buildings,
            buildings_over_5km=r.buildings_over_5km, share_over_5km=r.buildings_over_5km / r.buildings if r.buildings else 0,
            under_grid_buildings=r.under_grid_b, mv_km=r.mv_km, minigrids=int(r.mg_n), minigrid_kw=r.mg_kw,
            rank_offgrid=int(r.rank_offgrid), rank_over_5km=int(r.rank_b5),
            surveyed=int(len(g)), surveyed_no_grid=int(len(ng)),
            no_grid_with_health=int((ng.health > 0).sum()), no_grid_health_facilities=float(ng.health.sum()),
            no_grid_with_school=int((ng.schools > 0).sum()), no_grid_schools=float(ng.schools.sum()),
            never_functional=int(g.never_functional.sum()), present_not_connected=int((g.grid == "yes_not_connected_national_grid").sum()),
            ready_sites=int((rdy.state_name == s).sum()),
        )

    top = st.sort_values("offgrid_buildings", ascending=False)
    top10 = list(top.index[:10])
    nat = dict(
        pulled=pulled, criteria=READY,
        survey=dict(total=int(len(sv)), no_grid=int(len(nog)), connected=int((sv.grid == "yes_connected_national_grid").sum()),
                    present_not_connected=int((sv.grid == "yes_not_connected_national_grid").sum()),
                    by_year=sv.year.value_counts().sort_index().to_dict(),
                    never_functional=int(sv.never_functional.sum()), never_functional_buildings=float(sv.loc[sv.never_functional, "bld"].sum()),
                    never_functional_by_state=sv[sv.never_functional].state_name.value_counts().head(6).to_dict()),
        developer=dict(ready=int(len(rdy)), ready_by_state=rdy.state_name.value_counts().to_dict(),
                       no_grid_median_buildings=float(nog.bld.median()),
                       mills=float(nog.mills.sum()), presses=float(nog.presses.sum()),
                       share_business_genset50=float((nog.bz_gen >= 50).mean()), share_household_genset50=float((nog.hh_gen >= 50).mean()),
                       share_mobile_money=float(nog.mobile_money.mean()), share_3g4g=float(nog.data_3g4g.mean()), share_all_year=float(nog.all_year.mean()),
                       fuel={y: dict(n=int(len(g)), petrol=float(g.petrol.median()), diesel=float(g.diesel.median()) if g.diesel.notna().any() else None,
                                     states=sorted(g.state_name.dropna().unique().tolist()))
                             for y, g in sv[sv.year.isin(["2022", "2026"])].groupby("year")}),
        investor=dict(top5=list(top.index[:5]), top5_share=float(top.offgrid_buildings.head(5).sum() / top.offgrid_buildings.sum()),
                      top10=top10, top10_no_minigrid=[s for s in top10 if st.loc[s, "mg_n"] == 0],
                      fleet_n=int(len(mg)), fleet_kw=float(mg.kw.sum()), fleet_median_kw=float(mg.kw.median()),
                      fleet_conn=float(mg.conn.sum()), conn_per_kw=float(mg.conn.sum() / mg.loc[mg.conn.notna(), "kw"].sum()),
                      fleet_non_operational=int((~mg.operational & mg.condition.notna()).sum()),
                      fleet_under_construction=int(mg.status.eq("Under Construction").sum()),
                      systems=mg.power_system.value_counts().to_dict()),
        health=dict(no_grid_with_health=int((nog.health > 0).sum()), facilities=float(nog.health.sum()),
                    no_grid_with_school=int((nog.schools > 0).sum()), schools=float(nog.schools.sum())),
    )
    out = clean(dict(national=nat, states=states, communities=communities.to_dict("records"), fleet=fleet.to_dict("records")))
    os.makedirs(a.out, exist_ok=True)
    # full survey records (all fields) for the community pages
    raw = [c for c in sv.columns if c not in ("bld", "hh_gen", "bz_gen", "petrol", "diesel", "mills", "presses", "health", "schools", "mobile_money", "data_3g4g", "all_year", "year", "grid", "never_functional")]
    full = {r["uid"]: clean({k: (None if (isinstance(v, float) and v != v) else v) for k, v in r.items()}) for r in sv[raw].to_dict("records")}
    json.dump(full, open(os.path.join(a.out, "survey_full.json"), "w"), ensure_ascii=False, separators=(",", ":"), default=str)
    json.dump(out, open(os.path.join(a.out, "insights.json"), "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    print(json.dumps(out["national"], indent=1)[:3000])

if __name__ == "__main__":
    main()
