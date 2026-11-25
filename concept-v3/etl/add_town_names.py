"""
v9: give every candidate settlement a place name from the platform's own layer geonode:towns_villages
(nearest named town or village within 2 km; the layer lists each place twice, de-duplicated by name + point).
Updates data/minigrids.json in place (fields nesp_name, nesp_name_km). Run after compile_minigrids.py.
"""
import json, os, sys, requests, numpy as np, geopandas as gpd
from scipy.spatial import cKDTree
DATA = sys.argv[1] if len(sys.argv) > 1 else "../data"
r = requests.get("https://data.nigeriase4all.gov.ng/geoserver/ows", params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames="geonode:towns_villages",
                 outputFormat="application/json", srsName="EPSG:4326"), headers={"User-Agent": "nigeriase4all-site-etl"}, timeout=300)
r.raise_for_status()
T = [(f["properties"]["name"], round(f["geometry"]["coordinates"][0], 5), round(f["geometry"]["coordinates"][1], 5)) for f in r.json()["features"] if f.get("geometry") and f["properties"].get("name")]
raw = len(T); T = sorted(set(T))
txy = gpd.GeoSeries(gpd.points_from_xy([t[1] for t in T], [t[2] for t in T]), crs=4326).to_crs(32632)
P = os.path.join(DATA, "minigrids.json"); d = json.load(open(P)); C = d["candidates"]
cxy = gpd.GeoSeries(gpd.points_from_xy([c["lon"] for c in C], [c["lat"] for c in C]), crs=4326).to_crs(32632)
dist, idx = cKDTree(np.column_stack([txy.x, txy.y])).query(np.column_stack([cxy.x, cxy.y]))
for c, dd, ii in zip(C, dist, idx):
    c["nesp_name"] = T[ii][0] if dd <= 2000 else None; c["nesp_name_km"] = round(dd / 1000, 1) if dd <= 2000 else None
d["checks"]["towns"] = dict(records=raw, unique=len(T), named_candidates=sum(1 for c in C if c["nesp_name"]))
json.dump(d, open(P, "w"), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
print(d["checks"]["towns"])
