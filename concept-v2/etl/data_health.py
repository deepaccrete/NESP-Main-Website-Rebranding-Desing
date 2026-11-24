"""Data-health job: what users should know about each layer, refreshed with the data.
Counts, exact-duplicate check (ignoring ID columns), licence/date metadata, and a check of key links."""
import argparse, io, json, re, os, datetime
import pandas as pd, requests
PORTAL = "https://data.nigeriase4all.gov.ng"; WFS = PORTAL + "/geoserver/ows"
ID = re.compile(r"^(fid|ogc_fid|objectid.*|oid.*|gid|id|globalid|.*_id|orig_fid|fid_\d+)$", re.I)
LINKS = {"Off-grid webmap": "https://apps.nigeriase4all.gov.ng/minigrid-offgrid", "Interconnected webmap": "https://apps.nigeriase4all.gov.ng/minigrid-interconnected",
         "Power sector webmap": "https://apps.nigeriase4all.gov.ng/power-sector", "Solar home systems webmap": "https://apps.nigeriase4all.gov.ng/shs",
         "Mini-grid monitor": "https://minigridmonitor.nigeriase4all.gov.ng/", "Learning platform": "https://learning.nigeriase4all.gov.ng/",
         "Guide: how to download geodata": PORTAL + "/documents/29/download", "Guide: how to use WMS/WFS": PORTAL + "/documents/28/download",
         "Off-grid site map PDF (linked from the current homepage)": PORTAL + "/documents/367/download", "30:30:30 source document (linked from the current Power Sector page)": PORTAL + "/documents/357"}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="data"); a = ap.parse_args()
    ds = requests.get(PORTAL + "/api/v2/datasets", params=dict(page_size=100, format="json"), timeout=120).json()["datasets"]
    rows = []
    for d in sorted(ds, key=lambda x: x["title"]):
        lyr = d["alternate"]
        hits = requests.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=lyr, resultType="hits"), timeout=120).text
        n = int(re.search(r'numberMatched="(\d+)"', hits).group(1))
        dup, checked = None, False
        if n <= 30000:
            r = requests.get(WFS, params=dict(service="WFS", version="2.0.0", request="GetFeature", typeNames=lyr, outputFormat="csv"), timeout=600)
            df = pd.read_csv(io.StringIO(r.text), low_memory=False)
            cols = [c for c in df.columns if not ID.match(str(c)) and str(c) != "FID"]
            dup, checked = int(df.duplicated(cols).sum()), True
        lic = d.get("license"); lic = (lic.get("identifier") if isinstance(lic, dict) else lic) or "not_specified"
        rows.append(dict(title=d["title"], layer=lyr, features=n, duplicates=dup, checked=checked, licence=lic,
                         last_updated=(d.get("last_updated") or "")[:10], page=f"{PORTAL}/catalogue/#/dataset/{d['pk']}"))
        print(lyr, n, dup)
    links = {}
    for k, u in LINKS.items():
        try: links[k] = dict(url=u, status=requests.get(u, timeout=60, allow_redirects=True).status_code)
        except Exception as e: links[k] = dict(url=u, status=str(e)[:60])
    out = dict(checked_on=datetime.date.today().isoformat(), layers=rows, links=links)
    json.dump(out, open(os.path.join(a.out, "data_health.json"), "w"), indent=1); print(json.dumps(links, indent=1))
if __name__ == "__main__": main()
