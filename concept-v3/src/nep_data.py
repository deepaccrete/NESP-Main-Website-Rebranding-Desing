# v7: Nigeria Electrification Project (REA) projects, read from data/projects.json (made by etl/fetch_nep_projects.py).
# Executed inside build_v7.py's namespace, after `states` and `fleet` exist and before atlas-data.js is written.
import math
NEPJ = json.load(open(os.path.join(ROOT, "data", "projects.json")))
NS = NEPJ["summary"]; NEP_ALL = NEPJ["projects"]; SHS = NEPJ["shs"]
NEP_PULLED = datetime.date.fromisoformat(NS["pulled"]).strftime("%-d %B %Y")
NEP_SRC = "https://nep.rea.gov.ng/"
KIND_L = {"minigrid": "Mini-grid", "health": "Health facility", "education": "University"}
PHASE = {"eep1": "EEP phase I", "eep2": "EEP phase II", "eep3": "EEP phase III"}
for p in NEP_ALL:
    if not p["state"]: p["state"] = state_of(p["lat"], p["lon"]) if p["lat"] is not None else p["stated_state"]
    if p["kind"] == "health": p["capacity_kw"] = None              # every record carries the same value (50): a placeholder, not shown
    if p["kind"] == "education" and p["source_array"] != "eep1": p["grant"] = None   # phase II/III "grant" fields hold row numbers, not amounts
    p["short"] = KIND_L[p["kind"]] if p["kind"] != "education" else PHASE[p["source_array"]]
NEP_MG = [p for p in NEP_ALL if p["kind"] == "minigrid"]
NEP_H = [p for p in NEP_ALL if p["kind"] == "health"]
NEP_E = [p for p in NEP_ALL if p["kind"] == "education"]
NEP_NEW = [p for p in NEP_MG if not p["in_se4all_layer"]]            # not already in the platform's mini-grid layer
SHS_BY = {s["state"]: s for s in SHS}
for s, d in states.items():
    mg = [p for p in NEP_MG if p["state"] == s]
    d["nep_minigrids"] = len(mg); d["nep_kw"] = sum(p["capacity_kw"] or 0 for p in mg); d["nep_customers"] = sum(p["customers"] or 0 for p in mg)
    d["nep_new"] = sum(1 for p in mg if not p["in_se4all_layer"])
    d["all_minigrids"] = d["minigrids"] + d["nep_new"]
    d["nep_health"] = sum(1 for p in NEP_H if p["state"] == s); d["nep_edu"] = sum(1 for p in NEP_E if p["state"] == s)
    d["shs_connections"] = (SHS_BY.get(s) or {}).get("connections")
ALL_MG_N = len(fleet) + len(NEP_NEW)
TOP10_NONE = [s for s in inv["top10"] if states[s]["all_minigrids"] == 0]
TOP10_NEP_ONLY = [s for s in inv["top10_no_minigrid"] if states[s]["all_minigrids"] > 0]
DEVS = {}
for p in NEP_MG:
    r = DEVS.setdefault(p["developer"] or "Not stated", dict(n=0, kw=0, cust=0, states=set()))
    r["n"] += 1; r["kw"] += p["capacity_kw"] or 0; r["cust"] += p["customers"] or 0; r["states"].add(p["state"])

# nearest recorded mini-grid (SE4ALL layer + NEP sites not already in it) for every surveyed community
_mgpts = [(g["lat"], g["lon"], g["community"] or "Mini-grid", "SE4ALL mini-grid layer") for g in fleet if g["lat"] is not None] + \
         [(p["lat"], p["lon"], p["name"] or "Mini-grid", "NEP " + (p["developer"] or "")) for p in NEP_NEW if p["lat"] is not None]
def _hav(a, b, c, d):
    r = math.radians; x = math.sin(r(c - a) / 2) ** 2 + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
for c in I3["communities"]:
    if c["lat"] is None: continue
    best = min(_mgpts, key=lambda q: (q[0] - c["lat"]) ** 2 + ((q[1] - c["lon"]) * math.cos(math.radians(c["lat"]))) ** 2)
    c["mg_km"] = round(_hav(c["lat"], c["lon"], best[0], best[1]), 1); c["mg_name"] = best[2]; c["mg_src"] = best[3].strip()

NEP_LITE = [{k: p[k] for k in ("id", "kind", "short", "name", "developer", "lga", "state", "capacity_kw", "customers", "status", "lot", "lat", "lon", "in_se4all_layer", "state_mismatch", "stated_state")} for p in NEP_ALL]
