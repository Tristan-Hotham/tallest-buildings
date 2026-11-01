"""Every number used anywhere (page, paper, blog, collage, post) goes into data/results.json; plus the clean data
files in data/ and the page data (site.json, points.json)."""
import pandas as pd
from collections import Counter, defaultdict
from common import *

W = jload(f"{WORK}/wiki_geo.json")
CS = jload(f"{WORK}/clean_stats.json")
CT = jload(f"{WORK}/countries.json")
D = pd.read_csv(f"{WORK}/tall_all.csv", keep_default_na=False)
D["count"] = D["count"].astype(str) == "True"
D["rank350"] = pd.to_numeric(D["rank350"], errors="coerce")
D["year"] = pd.to_numeric(D["year"], errors="coerce")
R = {"meta": {"slug": SLUG, "page": PAGE, "repo": REPO, "doi": DOI, "now": NOW, "rev_history": W["rev_history"], "rev_list": W["rev_list"]}}

# ======================= 1. record-holders =======================
REC, STR = W["records"], W["structures"]
for r in REC:
    r["years"] = None if r["from"] is None else (r["to"] if r["to"] is not None else NOW) - r["from"]
for s in STR:
    s["years"] = None if s["from"] is None else (s["to"] if s["to"] is not None else NOW) - s["from"] - (1 if s["from"] < 0 < (s["to"] or NOW) else 0)
pyr = STR[0]
assert pyr["years"] == 3870 and pyr["years"] > 3800
city_y, ctry_y = defaultdict(int), defaultdict(int)
for r in REC:
    if r["years"] is not None:
        city_y[r["city"]] += r["years"]; ctry_y[r["country"]] += r["years"]
cities = sorted(city_y.items(), key=lambda kv: -kv[1])
assert sum(city_y.values()) == NOW - 1311 and sum(ctry_y.values()) == NOW - 1311
first = {}
for r in REC:
    first.setdefault(r["city"], r)
CITY = [{"city": c, "country": first[c]["country"], "years": y, "first": first[c]["from"], "holders": sorted({r["name"] for r in REC if r["city"] == c}),
         "spans": [[r["from"], r["to"] if r["to"] is not None else NOW] for r in REC if r["city"] == c]} for c, y in cities]
CITY.append({"city": "London", "country": "United Kingdom", "years": None, "first": None, "holders": ["Old St Paul's Cathedral"], "spans": [[None, 1311]]})
R["records"] = {
    "n_rows": len(REC), "n_buildings": len({r["name"] + r["city"] for r in REC}), "n_cities": len({r["city"] for r in REC}),
    "n_church": sum(r["kind"] == "church" for r in REC), "n_sky": sum(r["kind"] == "skyscraper" for r in REC),
    "cities": CITY, "countries": [{"country": c, "years": y} for c, y in sorted(ctry_y.items(), key=lambda kv: -kv[1])],
    "span_years": NOW - 1311, "church_years": 1894 - 1311, "church_pct": 100 * (1894 - 1311) / (NOW - 1311),
    "us_years": 1998 - 1894, "nyc_years": city_y["New York City"], "chi_years": city_y["Chicago"], "lincoln_years": city_y["Lincoln"],
    "stras_years": city_y["Strasbourg"], "stral_years": city_y["Stralsund"], "dubai_years": city_y["Dubai"], "phl_years": city_y["Philadelphia"],
    "asia_years": NOW - 1998, "pyr_years": pyr["years"], "pyr_h": pyr["h"], "pyr_from": pyr["from"],
    "lincoln_h": REC[1]["h"], "stpaul_h": REC[0]["h"], "ulm_h": REC[9]["h"], "phl_h": REC[10]["h"], "singer_h": REC[11]["h"], "chrysler_h": REC[15]["h"],
    "esb_h": REC[16]["h"], "esb_years": REC[16]["years"], "wtc_h": REC[17]["h"], "sears_h": REC[18]["h"], "petronas_h": REC[19]["h"], "taipei_h": REC[20]["h"],
    "burj_h": REC[21]["h"], "burj_jump_pct": 100 * (REC[21]["h"] / REC[20]["h"] - 1), "burj_jump_m": REC[21]["h"] - REC[20]["h"],
    "burj_x_lincoln": REC[21]["h"] / REC[1]["h"], "strasbourg_h": REC[5]["h"], "wall40_h": REC[14]["h"],
    "wm_h": STR[2]["h"], "eiffel_h": STR[3]["h"], "eiffel_years": STR[3]["years"], "nyc_struct_years": STR[4]["years"] + STR[5]["years"],
    "mast_years": STR[6]["years"], "shortest_h": min(r["h"] for r in REC), "shortest": min(REC, key=lambda r: r["h"])["name"],
}
rc = R["records"]
assert rc["n_cities"] == 15 and rc["n_buildings"] == 21 and rc["lincoln_years"] == 238 and rc["stras_years"] == 227 and rc["nyc_years"] == 65
assert cities[0][0] == "Lincoln" and cities[1][0] == "Strasbourg" and cities[2][0] == "Stralsund" and cities[3][0] == "New York City"
assert rc["us_years"] == 104 and rc["chi_years"] == 25 and round(rc["burj_jump_pct"]) == 62 and rc["shortest"] == "Cathedral of Our Lady of Strasbourg"
# the page's introduction says New York held the title for 86 years and Chicago for 30; its own table gives 65 and 25
R["records"]["intro_nyc"], R["records"]["intro_chi"] = 86, 30
assert W["phrases"]["nyc86"].startswith("New York City housing the tallest building for 86 years")

# record-holder table (both tracks) for data/
rows = []
for r in REC:
    rows.append({"track": "building", "name": r["name"], "city": r["city"], "country": r["country"], "height_m": r["h"],
                 "from": r["from_txt"] if r["from"] is None else r["from"], "to": r["to_txt"], "years": r["years"], "kind": r["kind"],
                 "lat": round(r["lat"], 5), "lon": round(r["lon"], 5), "position": r["loc"], "wikidata": r["qid"] or "", "status_2026": r.get("status") or "",
                 "source": "Wikipedia, History of the world's tallest buildings, tables"})
for s in STR:
    rows.append({"track": "structure", "name": s["name"], "city": s["city"] or "", "country": s["country"] or "", "height_m": s["h"] if s["h"] else "",
                 "from": s["from"], "to": s["to"] if s["to"] is not None else "present", "years": s["years"], "kind": s["kind"],
                 "lat": round(s["lat"], 5) if s["lat"] else "", "lon": round(s["lon"], 5) if s["lon"] else "", "position": s["loc"] or "", "wikidata": s["qid"] or "",
                 "status_2026": "", "source": "Wikipedia, History of the world's tallest buildings, text" + ("; start year from Wikidata" if s["from"] == -2560 else "")})
pd.DataFrame(rows).to_csv(f"{DATA}/record_holders.csv", index=False)
pd.DataFrame([{"city": c["city"], "country": c["country"], "years_as_tallest_building": c["years"], "first_year": c["first"],
               "buildings": "; ".join(c["holders"])} for c in CITY]).to_csv(f"{DATA}/city_tenure.csv", index=False)

# ======================= 2. the List page: 98 buildings of 350 m or more =======================
T = D[D.rank350.notna()].copy()
assert len(T) == 98
regs = T.region.value_counts()
asia = int(T.region.isin(ASIA).sum())
dec = T.groupby("decade").size()
tc = T.city.value_counts()
TL = {t["name"]: t for t in W["top"]}
R["list350"] = {
    "n": 98, "asia": asia, "asia_pct": 100 * asia / 98, "by_region": {r: int(regs.get(r, 0)) for r in RNAME},
    "since2010": int((T.year >= 2010).sum()), "since2010_pct": 100 * (T.year >= 2010).sum() / 98, "before2000": int((T.year < 2000).sum()),
    "since2020": int((T.year >= 2020).sum()), "by_decade": {str(int(k)): int(v) for k, v in dec.items()},
    "cities": [{"city": c, "n": int(n), "region": T[T.city == c].region.iloc[0]} for c, n in tc.items()], "n_cities": int(T.city.nunique()),
    "china": int((T.iso.isin(["CHN"])).sum()), "hk": int((T.iso == "HKG").sum()), "uae": int((T.iso == "ARE").sum()), "usa": int((T.iso == "USA").sum()),
    "n_countries": int(T.iso.nunique()), "oldest": T.sort_values("year").iloc[0][["name", "year", "city"]].to_dict(),
    "europe": int(regs.get("Europe", 0)), "na": int(regs.get("North America", 0)), "africa": int(regs.get("Africa", 0)),
    "me": int(regs.get("Middle East", 0)), "ea": int(regs.get("East Asia", 0)), "sea": int(regs.get("Southeast Asia", 0)),
    "megatall": int((T.h >= 600).sum()), "supertall_def": 300, "megatall_def": 600, "placed_city": int((T.check == "List page (placed at city)").sum()),
}
L = R["list350"]
assert L["cities"][0]["city"] == "Dubai" and L["cities"][1]["city"] == "Shenzhen" and L["cities"][2]["city"] == "New York"
assert L["oldest"]["name"] == "Empire State Building" and L["china"] + L["hk"] == 52   # the page's country table: Mainland China 48, Hong Kong 4
assert L["usa"] == 12 and L["uae"] == 16
T.assign(city_page=[TL[n]["city"] for n in T.name], country_page=[TL[n]["country"] for n in T.name], floors=[TL[n]["floors"] for n in T.name]).sort_values("rank350")[
    ["rank350", "name", "h", "floors", "year", "city_page", "country_page", "region", "lat", "lon", "check", "qid"]].rename(
    columns={"rank350": "rank", "h": "height_m", "check": "position", "qid": "wikidata"}).replace({"position": {"List page": "Wikidata", "List page (placed at city)": "city centre (not in Wikidata)"}}).to_csv(
    f"{DATA}/tallest_350m_list.csv", index=False)

# ======================= 3. Wikidata buildings: the boom by decade and region, and the cities =======================
C = D[D["count"]].copy()
C2 = C[C.h >= 200]
n200 = len(C2)
DECS = list(range(1900, 2030, 10))
grid = {str(d): {r: int(((C2.decade == d) & (C2.region == r)).sum()) for r in RNAME} for d in DECS}
tot = {str(d): sum(grid[str(d)].values()) for d in DECS}
asia_share = {str(d): (100 * sum(grid[str(d)][r] for r in ASIA) / tot[str(d)] if tot[str(d)] else None) for d in DECS}
# sensitivity: count every unchecked United States record too (many are feet, so this overstates North America)
CU = D[(D["count"] | (D.check == "unchecked (United States)")) & (D.h >= 200)]
asia_share_us = {str(d): (100 * (CU[CU.decade == d].region.isin(ASIA)).mean() if (CU.decade == d).sum() else None) for d in DECS}
n_us_unchecked200 = int(((D.check == "unchecked (United States)") & (D.h >= 200)).sum())
grid350 = {str(d): {r: int(((T.decade == d) & (T.region == r)).sum()) for r in RNAME} for d in DECS}
cc = C2.groupby(["city", "iso"]).size().sort_values(ascending=False)
top_cities = [{"city": c, "iso": i, "country": CT["cname"].get(i, i), "region": CT["creg"].get(i), "n": int(n), "n350": int(((T.city == c)).sum()),
               "tallest": C2[C2.city == c].sort_values("h").iloc[-1]["name"], "tallest_h": float(C2[C2.city == c].h.max()),
               "lat": float(C2[C2.city == c].lat.median()), "lon": float(C2[C2.city == c].lon.median())} for (c, i), n in cc.items()]
ctry = C2.groupby("iso").size().sort_values(ascending=False)
pre1990 = C2[C2.year < 1990]; s2000 = C2[C2.year >= 2000]
asia_s2000 = 100 * s2000.region.isin(ASIA).mean()
asia_pre90 = 100 * pre1990.region.isin(ASIA).mean()
na_pre90 = 100 * (pre1990.region == "North America").mean()
R["wd"] = {
    "n_rows": CS["n_rows"], "n_items": CS["n_items"], "n_buildings": int(len(D)), "n_counted": int(len(C)), "n200": n200,
    "n_unchecked_us": int((D.check == "unchecked (United States)").sum()), "n_corgis_ok": int((D.check == "CORGIS agrees").sum()),
    "n_corgis_bad": int(D.check.isin(["CORGIS differs", "feet in Wikidata"]).sum()), "n_corgis_feet": int((D.check == "feet in Wikidata").sum()),
    "drop_notbuilding": CS["drops"]["not a building"], "drop_dead": CS["drops"]["under construction, unfinished or destroyed"],
    "drop_830": CS["drops"]["height over 830 m (units)"], "drop_noyear": CS["drops2"]["no year"], "drop_350": CS["drops2"]["350 m or more but not on the List page"],
    "drop_review": CS["drops2"]["evidently feet (manual review)"], "list_matched": CS["matched_list"],
    "grid": grid, "tot": tot, "asia_share": asia_share, "grid350": grid350, "asia_share_us": asia_share_us, "n_us_unchecked200": n_us_unchecked200,
    "cities": top_cities[:40], "n_cities": int(C2.city.nunique()), "countries": [{"iso": i, "country": CT["cname"].get(i, i), "n": int(n)} for i, n in ctry.items()],
    "pre1990": int(len(pre1990)), "since2000": int(len(s2000)), "since2000_pct": 100 * len(s2000) / n200, "since2010": int((C2.year >= 2010).sum()),
    "asia_since2000_pct": asia_s2000, "asia_pre1990_pct": asia_pre90, "na_pre1990_pct": na_pre90,
    "asia_n": int(C2.region.isin(ASIA).sum()), "asia_pct": 100 * C2.region.isin(ASIA).mean(),
    "peak_decade": max(DECS, key=lambda d: tot[str(d)]), "peak_n": max(tot.values()),
    "china": int(C2.iso.isin(["CHN", "HKG", "MAC"]).sum()), "usa": int((C2.iso == "USA").sum()),
    "ysrc_open": int((C.ysrc == "opening").sum()), "ysrc_inc": int((C.ysrc == "inception").sum()), "ysrc_list": int((C.ysrc == "list").sum()),
    "religious": int((D.kind == "religious").sum()), "first_year": int(C.year.min()),
    "first_name": C.sort_values("year").iloc[0]["name"],
}
# how many of the List's buildings were missing from the Wikidata extract (placed at their city), China against the rest
miss = T[T.check == "List page (placed at city)"]
R["list350"]["missing_cn"] = int(miss.iso.isin(["CHN", "HKG"]).sum()); R["list350"]["missing_other"] = int((~miss.iso.isin(["CHN", "HKG"])).sum())
R["list350"]["china_hk"] = R["list350"]["china"] + R["list350"]["hk"]; R["list350"]["n_other"] = 98 - R["list350"]["china_hk"]
R["list350"]["missing_cn_pct"] = 100 * R["list350"]["missing_cn"] / (R["list350"]["china"] + R["list350"]["hk"])
R["list350"]["missing_other_pct"] = 100 * R["list350"]["missing_other"] / (98 - R["list350"]["china"] - R["list350"]["hk"])
WD = R["wd"]
assert WD["peak_decade"] == 2010 and [c["city"] for c in top_cities[:3]] == ["New York", "Dubai", "Shenzhen"]
assert asia_share["2010"] > 70 and asia_share["1980"] < 50 and WD["asia_since2000_pct"] > 65 and WD["na_pre1990_pct"] > 50
assert WD["n_counted"] + WD["n_unchecked_us"] + WD["n_corgis_bad"] + WD["religious"] == WD["n_buildings"]
# decade-by-region table for data/
dr = []
for d in DECS:
    for r in RNAME:
        dr.append({"decade": d, "region": r, "wikidata_200m_plus": grid[str(d)][r], "list_350m_plus": grid350[str(d)][r]})
pd.DataFrame(dr).to_csv(f"{DATA}/decade_region.csv", index=False)
out = D.rename(columns={"h": "height_m", "ysrc": "year_source", "check": "height_check", "count": "counted", "rank350": "list_rank", "sl": "sitelinks",
                        "qid": "wikidata", "wd_city": "wikidata_place", "cls": "wikidata_classes"})
out["list_rank"] = out["list_rank"].map(lambda v: "" if pd.isna(v) else int(v))
out["year"] = out["year"].map(lambda v: "" if pd.isna(v) else int(v))
out["decade"] = pd.to_numeric(out["decade"], errors="coerce").map(lambda v: "" if pd.isna(v) else int(v))
out.to_csv(f"{DATA}/tall_buildings.csv", index=False)

# ======================= 4. under construction, continents, definitions =======================
UC = W["uc"]
ucr = Counter()
for u in UC:
    iso = {"China": "CHN", "UAE": "ARE", "Saudi Arabia": "SAU", "Brazil": "BRA", "Mexico": "MEX", "Ivory Coast": "CIV", "Japan": "JPN",
           "United States": "USA", "Taiwan": "TWN", "Cambodia": "KHM"}[u["country"]]
    u["iso"] = iso; u["region"] = CT["creg"][iso]; ucr[u["region"]] += 1
pd.DataFrame([{k: u[k] for k in ("name", "city", "country", "h", "floors", "planned", "lat", "lon", "loc", "qid")} for u in UC]).rename(
    columns={"h": "planned_height_m", "planned": "planned_completion", "loc": "position", "qid": "wikidata"}).to_csv(f"{DATA}/under_construction.csv", index=False)
jed = UC[0]
R["uc"] = {"n": len(UC), "asia": sum(ucr[r] for r in ASIA), "asia_pct": 100 * sum(ucr[r] for r in ASIA) / len(UC), "china": sum(u["iso"] == "CHN" for u in UC),
           "uae": sum(u["iso"] == "ARE" for u in UC), "usa": sum(u["iso"] == "USA" for u in UC), "by_region": dict(ucr),
           "jeddah_h": jed["h"], "jeddah_planned": int(jed["planned"]), "jeddah_floors": jed["floors"], "jeddah_x_burj": jed["h"] / rc["burj_h"],
           "jeddah_over_burj_m": jed["h"] - rc["burj_h"], "azizi_h": UC[1]["h"], "azizi_planned": int(UC[1]["planned"]),
           "over600": sum(u["h"] >= 600 for u in UC if u["h"])}
assert R["uc"]["jeddah_h"] == 1008 and R["uc"]["jeddah_planned"] == 2028 and R["uc"]["over600"] == 2
R["continents"] = W["continents"]
R["defs"] = {"list_min": 350, "wd_min": 100, "map_min": 100}
R["retrieved"] = "2026"

# ======================= 5. headline numbers for the collage and post =======================
R["head"] = {"burj_h": rc["burj_h"], "lincoln_years": rc["lincoln_years"], "nyc_years": rc["nyc_years"], "pyr_years": rc["pyr_years"],
             "n200": n200, "list_asia": asia, "jed_h": R["uc"]["jeddah_h"]}

jsave(R, f"{DATA}/results.json", indent=1)

# ======================= page data =======================
KC = {"religious building (dated by founding; not mapped)": 6, "List page": 0, "List page (placed at city)": 1, "CORGIS agrees": 2, "as given": 3, "unchecked (United States)": 4, "CORGIS differs": 5, "feet in Wikidata": 5}
P = []
for b in D[D.kind == "tall"].itertuples():
    P.append([round(b.lat, 4), round(b.lon, 4), round(float(b.h), 1), int(b.year) if not pd.isna(b.year) else None, 0 if b.kind == "tall" else 1, KC[b.check],
              int(b.rank350) if not pd.isna(b.rank350) else 0, b.name, b.city, CT["cname"].get(b.iso, b.country) if b.iso else b.country, b.qid,
              {"opening": "o", "inception": "i", "list": "l"}.get(b.ysrc, ""), RNAME.index(b.region) if b.region in RNAME else None])
P.sort(key=lambda p: p[2])
jsave(P, f"{DATA}/points.json")


def holder(r, track):
    return {"name": r["name"], "city": r["city"], "country": r["country"], "h": r["h"], "from": r["from"], "to": r["to"], "years": r["years"],
            "kind": r["kind"], "lat": r["lat"], "lon": r["lon"], "qid": r.get("qid"), "track": track, "status": r.get("status"), "note": r.get("note", ""),
            "from_txt": r.get("from_txt") or ("c. 2560 BC" if r["from"] == -2560 else str(r["from"])), "to_txt": "present" if r["to"] is None else str(r["to"])}


HB = [holder(r, "b") for r in REC]; HS = [holder(s, "s") for s in STR]
# slider steps: each change of either title, in order
steps = []
ev = sorted({(h["from"] if h["from"] is not None else 1300) for h in HB} | {h["from"] for h in HS})
for y in ev:
    bs = [i for i, h in enumerate(HB) if (h["from"] if h["from"] is not None else 1300) <= y and (h["to"] is None or y < h["to"] or (h["from"] == h["to"] == y))]
    ss = [i for i, h in enumerate(HS) if h["from"] <= y and (h["to"] is None or y < h["to"])]
    if y == 1930:   # 40 Wall Street, then the Chrysler Building, both in 1930
        steps.append({"y": 1930, "b": 14, "s": ss[-1] if ss else None, "lab": "1930"})
        steps.append({"y": 1930, "b": 15, "s": 4, "lab": "1930"})
        continue
    steps.append({"y": y, "b": bs[-1] if bs else None, "s": ss[-1] if ss else None, "lab": "c. 2560 BC" if y == -2560 else ("13th century" if y == 1300 else str(y))})
steps.append({"y": NOW, "b": steps[-1]["b"], "s": steps[-1]["s"], "lab": str(NOW)})   # today
for s in steps:
    if s["y"] < 1300: s["b"] = None
assert steps[0]["lab"] == "c. 2560 BC" and steps[1]["lab"] == "13th century" and HB[steps[1]["b"]]["name"] == "Old St Paul's Cathedral"
assert HB[steps[-1]["b"]]["name"] == "Burj Khalifa" and HS[steps[-1]["s"]]["name"] == "Burj Khalifa"
uc = [{"name": u["name"], "city": u["city"], "country": u["country"], "h": u["h"], "floors": u["floors"], "planned": u["planned"],
       "lat": u["lat"], "lon": u["lon"], "loc": u["loc"]} for u in UC]
SITE = {"regions": REGIONS, "bands": [[n, a, b, c] for n, a, b, c in DEC_BANDS], "hb": HB, "hs": HS, "steps": steps, "uc": uc,
        "cname": CT["cname"], "cpos": CT["cpos"], "checks": ["List page", "List page, placed at the city centre", "CORGIS agrees",
        "Wikidata, as given", "Unchecked: United States, may be feet", "Wrong units: CORGIS differs"]}
jsave(SITE, f"{DATA}/site.json")
print(json.dumps({k: R["records"][k] for k in ("n_cities", "lincoln_years", "nyc_years", "us_years", "pyr_years")}),
      json.dumps({k: L[k] for k in ("asia", "since2010", "china", "uae", "usa")}), "n200", n200, "asia share by decade",
      {k: round(v) for k, v in asia_share.items() if v is not None}, "points", len(P), os.path.getsize(f"{DATA}/points.json") // 1024, "KB")
