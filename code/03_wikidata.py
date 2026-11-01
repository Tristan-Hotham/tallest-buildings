"""Clean the Wikidata extract into a table of tall buildings, and place the record-holders and the 98 buildings of the
List page on the map.

Wikidata heights came without units, so some are feet or centimetres. The rules, in order:
  1. Keep items whose classes include a kind of building (skyscraper, tower block, office, hotel, residential,
     apartment, commercial, civic, church, cathedral, mosque, temple and so on). Drop items that are also towers,
     masts, transmitters, chimneys, bridges, dams, monuments or similar unless they are also skyscrapers or offices.
  2. Drop items still under construction, unfinished, proposed or destroyed, and items with no opening or inception
     year, or one after 2026.
  3. Height: the largest value given; where an item has two values about 3.28 apart, the smaller (metres).
     Drop heights over 830 m (taller than the Burj Khalifa: units wrong).
  4. 350 m and over: the List page's table of all 98 buildings of 350 m or more is the authority. Wikidata items
     matched to it take the List's height, year and city; items of 350 m or more that are not on it are dropped.
     Buildings on the List that Wikidata lacks are added at their city's position.
  5. United States, under 350 m: Wikidata often records feet as metres here. Items are kept only if a building of
     the same name within 30 km in the CORGIS skyscrapers dataset (from the CTBUH Skyscraper Center, to 2016) has a
     height within 8%; the rest are marked unchecked and left out of all counts.
  6. Elsewhere, heights under 350 m are kept as given (a caveat on the page and in the paper), apart from four that
     are evidently feet (REVIEW below).
  7. Churches, mosques and temples stay in the table but are not mapped or counted: Wikidata dates them by their
     founding, not by when they reached their height.
"""
import pandas as pd, subprocess
from collections import Counter, defaultdict
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

W = jload(f"{WORK}/wiki.json")
CT = jload(f"{WORK}/countries.json")
PL = jload(f"{WORK}/places.json")

# ---------- read and group the Wikidata extract ----------
df = pd.read_csv(f"{RAW}/wikidata_tall.tsv", sep="\t", dtype=str, quoting=3, keep_default_na=False)
df.columns = [c.lstrip("?") for c in df.columns]
for c in df.columns:
    df[c] = df[c].str.replace(r'^"(.*)"@en$', r"\1", regex=True).str.replace(r"^<http://www.wikidata.org/entity/(Q\d+)>$", r"\1", regex=True)
df["h"] = df.h.astype(float)
yr = lambda s: int(re.match(r'"?(-?\d+)-', s).group(1)) if s and re.match(r'"?-?\d+-', s) else None   # unknown values (genid) give None
N_ROWS, N_ITEMS = len(df), df.b.nunique()
items = {}
for r in df.itertuples():
    it = items.setdefault(r.b, {"qid": r.b, "label": r.bL, "sl": int(r.sl or 0), "coord": r.coord, "h": set(), "open": set(), "inc": set(),
                                "city": set(), "country": set(), "cls": set()})
    it["h"].add(r.h)
    if yr(r.open) is not None: it["open"].add(yr(r.open))
    if yr(r.inc) is not None: it["inc"].add(yr(r.inc))
    if r.cityL: it["city"].add(r.cityL)
    if r.cL: it["country"].add(r.cL)
    if r.clsL: it["cls"].add(r.clsL)
    if not it["label"] and r.bL: it["label"] = r.bL

BLD = re.compile(r"skyscraper|tower block|office|^building$|hotel|residential|apartment|condominium|university building|bank building|"
                 r"commercial|public administration|city hall|Rathaus|headquarters|supertall|shopping|high-rise|mixed-use|multifamily|"
                 r"tower building|dormitory|student housing|government building|parliament|capitol|courthouse|library building|"
                 r"hospital building|municipal|broadcasting house|newspaper building|casino|retail building|academic building|"
                 r"data center|state office|prefectural office|federal building|administrative building|multi-story")
REL = re.compile(r"church|cathedral|basilica|mosque|minster|temple|pagoda|stupa|abbey|shrine|chapel")
NOTB = re.compile(r"television tower|transmitter|communication tower|observation tower|lattice tower|radio|mast|chimney|lighthouse|"
                  r"bridge|dam$|dam\b|monument|memorial|statue|ferris|coaster|fountain|elevator test tower|water tower|obelisk|"
                  r"flagpole|bell tower|clock tower|cooling tower|^tower$|wind turbine|cross|stele|arch$")
DEAD = re.compile(r"under construction|unfinished|destroyed|demolished|proposed|former|unbuilt|planned|cancel")
EE_Q = "Q37200"   # Great Pyramid of Giza
NOTB_NAME = re.compile(r"television tower|tv tower|radio tower|transmitter", re.I)
# Excluded after reading the cleaned list of buildings of 200 m or more outside the United States: heights that are
# evidently feet given as metres (all are far older or smaller buildings than the value implies). Their real height in
# metres is not in this extract, so they are left out rather than converted.
REVIEW = {"Q373143": "Edifice Price, Quebec City, 1929: 269 is feet", "Q1736182": "Chichester Cathedral, 1075: 277 is feet",
          "Q23527286": "Commerce Court West, Toronto: 287 is not metres", "Q110162752": "The Bank Tower 2, Birmingham: 334.6 is feet"}


def kind_of(cls):
    b = any(BLD.search(c) for c in cls); rel = any(REL.search(c) for c in cls); nb = any(NOTB.search(c) for c in cls)
    sky = any(re.search(r"skyscraper|office|tower block|hotel|residential|apartment", c) for c in cls)
    if nb and not sky:
        return None
    if b or sky:
        return "tall"
    if rel:
        return "religious"
    return None


def coord(s):
    m = re.match(r"POINT\(([-\d.]+) ([-\d.]+)\)", s)
    return (float(m.group(2)), float(m.group(1))) if m else (None, None)


# ---------- country and region of a point (Natural Earth 10m; nearest country within 30 km for points on the shore) ----------
W50 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]
GEOMS = [shape(f["geometry"]) for f in W50["features"]]; ISOS = [iso_of(f["properties"]) for f in W50["features"]]
TREE = STRtree(GEOMS)


def iso_at(lat, lon):
    pt = Point(lon, lat)
    for i in TREE.query(pt):
        if GEOMS[i].contains(pt):
            return ISOS[i]
    i = TREE.nearest(pt)
    return ISOS[i] if GEOMS[i].distance(pt) < .3 else None


# ---------- city: nearest large Natural Earth place ----------
PLA = np.array([[p["lat"], p["lon"], p["pop"]] for p in PL])
MERGE = {"Kowloon": "Hong Kong", "Jersey City": "New York", "Sharjah": "Sharjah", "Puteaux": "Paris", "Courbevoie": "Paris",
         "Nanterre": "Paris", "Bnei Brak": "Tel Aviv-Yafo", "Ramat Gan": "Tel Aviv-Yafo", "Givatayim": "Tel Aviv-Yafo",
         "Miami Beach": "Miami", "Sunny Isles Beach": "Miami", "Wan Chai": "Hong Kong", "Kowloon City": "Hong Kong"}


def city_at(lat, lon):
    d = haversine(lat, lon, PLA[:, 0], PLA[:, 1])
    big = np.where((PLA[:, 2] >= 400000) & (d <= 40))[0]
    if len(big):
        # the biggest place within 40 km, unless a place of 150,000 or more is much nearer (twin cities)
        i = big[np.argmax(PLA[big, 2])]
        near = np.where((PLA[:, 2] >= 150000) & (d <= 12))[0]
        if len(near) and d[near].min() < d[i] / 3:
            i = near[np.argmin(d[near])]
    else:
        near = np.where(d <= 30)[0]
        if not len(near):
            return None
        i = near[np.argmin(d[near])]
    nm = PL[i]["name"]
    return MERGE.get(nm, nm)


def place_named(name, iso=None):
    alias = {"New York City": "New York", "Washington, D.C.": "Washington, D.C.", "Saint Petersburg": "St. Petersburg", "Xi'an": "Xian",
             "Ho Chi Minh City": "Ho Chi Minh City", "Kuwait City": "Kuwait", "Xi'an": "Xian", "Gold Coast": "Gold Coast",
             "New Administrative Capital": "Cairo", "Mecca": "Makkah", "Shenyang": "Shenyeng", "Jinan": "Jinan", "Taipei": "Taipei", "Cologne": "Cologne"}
    nm = alias.get(name, name)
    c = [p for p in PL if norm(p["name"]) == norm(nm) and (iso is None or p["iso"] == iso)]
    if not c:
        c = [p for p in PL if norm(p["name"]) == norm(nm)]
    c.sort(key=lambda p: -p["pop"])
    return (c[0]["lat"], c[0]["lon"]) if c else (None, None)


# ---------- clean ----------
drops = Counter(); B = []
for q, it in items.items():
    k = kind_of(it["cls"])
    if k is not None and NOTB_NAME.search(it["label"] or ""):
        k = None
    if k is None:
        drops["not a building"] += 1; continue
    if any(DEAD.search(c) for c in it["cls"]):
        drops["under construction, unfinished or destroyed"] += 1; continue
    hs = sorted(it["h"])
    h = hs[-1]
    if len(hs) >= 2 and any(abs(b / a - 3.2808) < .08 for a in hs for b in hs if a > 0):
        h = min(a for a in hs for b in hs if a > 0 and abs(b / a - 3.2808) < .08)
    y = min(it["open"]) if it["open"] else (min(it["inc"]) if it["inc"] else None)
    ysrc = "opening" if it["open"] else ("inception" if it["inc"] else None)
    lat, lon = coord(it["coord"])
    if lat is None:
        drops["no coordinates"] += 1; continue
    if h > 830:
        drops["height over 830 m (units)"] += 1; continue
    B.append({"qid": q, "name": it["label"] or f"{q} (no English label)", "lat": round(lat, 5), "lon": round(lon, 5), "h": h, "year": y, "ysrc": ysrc, "kind": k,
              "sl": it["sl"], "wd_city": "; ".join(sorted(it["city"])), "wd_country": "; ".join(sorted(it["country"])), "cls": "; ".join(sorted(it["cls"]))})
print("items", N_ITEMS, "buildings kept so far", len(B), dict(drops))

# ---------- match the List's 98 buildings ----------
TOP = W["top"]
ALIAS = {"Mecca Royal Clock Tower": ["Makkah Clock Royal Tower Hotel", "Abraj Al Bait"], "CITIC Tower": ["China Zun"], "KK100": ["Kingkey 100"],
         "Tianjin CTF Finance Centre": ["Tianjin Chow Tai Fook Binhai Center"], "Guangzhou CTF Finance Centre": ["CTF Finance Centre"],
         "Lakhta Center": ["Lakhta Centre"], "International Finance Centre": ["Two International Finance Centre"],
         "Haeundae LCT The Sharp Landmark Tower": ["Haeundae LCT The Sharp"], "Changsha IFS T1": ["Changsha IFS"],
         "Suzhou International Financial Center": ["Suzhou IFS"], "Petronas Tower 1": ["Petronas Towers"], "Petronas Tower 2": ["Petronas Towers"],
         "Willis Tower": ["Willis Tower", "Sears Tower"], "International Land-Sea Center": ["International Commerce Center 1"],
         "Shandong International Financial Center": ["Greenland Shandong International Financial Center"],
         "Minying International Trade Center T2": ["Dongguan International Trade Center 1"], "Eton Place Dalian Tower 1": ["Dalian Eton Center"],
         "Guangxi China Resources Tower": ["Nanning China Resources Tower"], "Federation Tower (East Tower)": ["Federation Tower"],
         "Ciel Dubai Marina": ["Ciel Tower"], "OKO – South Tower": ["OKO South Tower"], "Xi'an Glory International Financial Center": ["Xi An Glory International Financial Center"],
         "Lotte World Tower": ["Lotte World Tower"], "Galaxy World Tower 1": ["Galaxy World Tower 1"], "Galaxy World Tower 2": ["Galaxy World Tower 2"],
         "Raffles City Chongqing T3N": ["Raffles City Chongqing"], "Kempinski The Boulevard Dubai": ["Address Boulevard"],
         "Shanghai International Trade Center Tower": ["Shanghai International Trade Center"], "Wuhan Center": ["Wuhan Center"],
         "Guiyang International Financial Center T1": ["Guiyang International Financial Center T1"], "Public Investment Fund Tower": ["Capital Market Authority Headquarters"],
         "Burj Mohammed bin Rashid": ["Central Market Project"], "Merdeka Maybank Tower": ["Merdeka 118"], "Autograph Tower": ["Thamrin Nine"],
         "Ningbo Central Plaza": ["Ningbo Center"]}
TWIN = {"Petronas Tower 2": "Petronas Tower 1", "Raffles City Chongqing T4N": "Raffles City Chongqing T3N"}   # one Wikidata item for two buildings
ALLW = [dict(qid=q, name=it["label"] or "", h=sorted(it["h"])[-1], latlon=coord(it["coord"]), cls=it["cls"]) for q, it in items.items()]
byname = defaultdict(list)
for w in ALLW:
    byname[norm(w["name"])].append(w)
used = set(); matched = 0
for t in TOP:
    cands = []
    for nm in [t["name"]] + ALIAS.get(t["name"], []):
        cands += byname.get(norm(nm), [])
    cands = [c for c in cands if c["qid"] not in used]
    if t["name"] in TWIN:
        cands = []
    clat, clon = place_named(t["city"])
    near = [c for c in cands if clat is not None and c["latlon"][0] is not None and haversine(clat, clon, c["latlon"][0], c["latlon"][1]) < 80]
    cands = near or [c for c in cands if c["latlon"][0] is not None and abs(c["h"] - t["h"]) <= .03 * t["h"]]
    t["qid"] = None; t["lat"], t["lon"], t["loc"] = clat, clon, "city"
    if cands:
        c = min(cands, key=lambda c: abs(c["h"] - t["h"]))
        t["qid"] = c["qid"]; t["lat"], t["lon"] = c["latlon"]; t["loc"] = "wikidata"; used.add(c["qid"]); matched += 1
    assert t["lat"] is not None, t["name"]
print("List buildings matched to Wikidata:", matched, "of", len(TOP), "; placed at city:", [t["name"] for t in TOP if t["loc"] == "city"])
TOPQ = {t["qid"]: t for t in TOP if t["qid"]}

# ---------- CORGIS check for US heights ----------
cpath = f"{WORK}/corgis_skyscrapers.csv"
if not os.path.exists(cpath):
    subprocess.run(["curl", "-sSfL", "-o", cpath, CORGIS_URL], check=True)
C = pd.read_csv(cpath)
C = C[C["status.current"].isin(["completed", "architecturally topped out", "demolished"])]
CN = defaultdict(list)
for r in C.itertuples():
    CN[norm(r.name)].append((getattr(r, "_8"), getattr(r, "_9"), getattr(r, "_34"), getattr(r, "_4")))
assert "statistics.height" == C.columns[33] and "location.latitude" == C.columns[7], list(C.columns[:10])


def corgis(b):
    """'ok' if CORGIS has the same building with a height within 8%, 'feet' if it has it at about Wikidata's value
    divided by 3.28, 'differs' otherwise, None if not found."""
    out = None
    for lat, lon, h, city in CN.get(norm(b["name"]), []):
        if lat and abs(lat) > .1:
            if haversine(lat, lon, b["lat"], b["lon"]) > 30: continue
        elif norm(city) not in norm(b["wd_city"]) and norm(b["wd_city"]) not in norm(city):
            continue
        if h and abs(b["h"] - h) <= .08 * h: return "ok"
        if h and abs(b["h"] / 3.2808 - h) <= .08 * h: out = "feet"
        elif out is None: out = "differs"
    return out


# ---------- assemble ----------
drops2 = Counter(); OUT = []
for b in B:
    iso = iso_at(b["lat"], b["lon"])
    b["iso"] = iso; b["country"] = CT["cname"].get(iso, b["wd_country"]); b["region"] = CT["creg"].get(iso)
    b["city"] = city_at(b["lat"], b["lon"]) or (b["wd_city"].split("; ")[0] if b["wd_city"] else "")
    b["rank350"] = None
    if b["qid"] in TOPQ:
        t = TOPQ[b["qid"]]
        b.update({"h": t["h"], "year": t["year"], "ysrc": "list", "check": "List page", "rank350": t["rank"], "name": t["name"]})
    elif b["h"] >= 350:
        drops2["350 m or more but not on the List page"] += 1; continue
    elif b["qid"] in REVIEW:
        drops2["evidently feet (manual review)"] += 1; continue
    elif b["year"] is None:
        drops2["no year"] += 1; continue
    elif b["year"] > NOW:
        drops2["year after 2026"] += 1; continue
    elif b["kind"] == "religious":
        b["check"] = "religious building (dated by founding; not mapped)"
    elif iso == "USA":
        c = corgis(b)
        b["check"] = {"ok": "CORGIS agrees", "feet": "feet in Wikidata", "differs": "CORGIS differs", None: "unchecked (United States)"}[c]
    else:
        b["check"] = "as given"
    b["count"] = b["check"] in ("List page", "CORGIS agrees", "as given")
    b["decade"] = (b["year"] // 10) * 10 if b["year"] is not None else None
    OUT.append(b)
# List buildings not yet in the table: not in Wikidata, dropped above (unit errors such as Merdeka 118's 2,227, or a
# class such as "under construction"), or the second of two towers sharing one Wikidata item (placed just beside it)
have = {b["name"] for b in OUT if b["rank350"]}
TP = {t["name"]: t for t in TOP}
for t in TOP:
    if t["name"] in have:
        continue
    lat, lon, q, chk = t["lat"], t["lon"], t["qid"] or "", "List page" if t["qid"] else "List page (placed at city)"
    if t["name"] in TWIN:
        u = TP[TWIN[t["name"]]]; lat, lon, q, chk = u["lat"] - .0005, u["lon"] + .0005, u["qid"] or "", "List page"
    iso = iso_at(lat, lon)
    OUT.append({"qid": q, "name": t["name"], "lat": round(lat, 5), "lon": round(lon, 5), "h": t["h"], "year": t["year"],
                "ysrc": "list", "kind": "tall", "sl": items[q]["sl"] if q else 0, "wd_city": "", "wd_country": "", "cls": "", "iso": iso, "country": CT["cname"].get(iso, t["country"]),
                "region": CT["creg"].get(iso), "city": city_at(lat, lon) or t["city"], "rank350": t["rank"], "check": chk,
                "count": True, "decade": (t["year"] // 10) * 10})
assert sum(1 for b in OUT if b["rank350"]) == 98, sum(1 for b in OUT if b["rank350"])
assert all(b["region"] for b in OUT if b["count"]), [b["name"] for b in OUT if b["count"] and not b["region"]][:5]

# ---------- record-holders on the map ----------
QN = {norm(it["label"]): q for q, it in items.items() if it["label"]}
GEOREC = {"Old St Paul's Cathedral": ("London", "GBR"), "Lincoln Cathedral": ("Lincoln", "GBR"), "St. Mary's Church": ("Stralsund", "DEU"),
          "St. Pierre's Cathedral": ("Beauvais", "FRA"), "Cathedral of Our Lady of Strasbourg": ("Strasbourg", "FRA"), "Church of St. Nicholas": ("Hamburg", "DEU"),
          "Rouen Cathedral": ("Rouen", "FRA"), "Cologne Cathedral": ("Cologne", "DEU"), "Ulm Minster": ("Ulm", "DEU")}
WDREC = {"Lincoln Cathedral": "Lincoln Cathedral", "Cathedral of Our Lady of Strasbourg": "Strasbourg Cathedral", "Rouen Cathedral": "Rouen Cathedral",
         "Cologne Cathedral": "Cologne Cathedral", "Ulm Minster": "Ulm Minster", "Philadelphia City Hall": "Philadelphia City Hall",
         "Metropolitan Life Tower": "Metropolitan Life Insurance Company Tower", "Woolworth Building": "Woolworth Building", "40 Wall Street": "40 Wall Street",
         "Chrysler Building": "Chrysler Building", "Empire State Building": "Empire State Building", "Sears Tower": "Willis Tower", "Petronas Towers": "Petronas Towers",
         "Taipei 101": "Taipei 101", "Burj Khalifa": "Burj Khalifa", "Great Pyramid of Giza": "Great Pyramid of Giza", "Washington Monument": "Washington Monument",
         "Eiffel Tower": "Eiffel Tower", "Church of St. Nicholas": "St. Nicholas Church, Hamburg", "St. Pierre's Cathedral": "Beauvais Cathedral",
         "St. Mary's Church": "St. Mary's Church, Stralsund", "Singer Building": "Singer Building", "1 World Trade Center": "One World Trade Center (1971-2001)",
         "Old St Paul's Cathedral": "Old St Paul's Cathedral"}


# two medieval record-holders are neither in the Wikidata extract (too short today) nor near a Natural Earth place;
# their positions are entered by hand (cathedral sites)
MANUAL = {"Lincoln Cathedral": (53.2343, -0.5361), "St. Pierre's Cathedral": (49.4322, 2.0811)}
SITE_OF = {"1 World Trade Center": "One World Trade Center"}   # the original North Tower stood on the same site


def locate(name, city, cty=None):
    if name in MANUAL:
        return None, MANUAL[name][0], MANUAL[name][1], "hand"
    if name in SITE_OF and norm(SITE_OF[name]) in QN:
        lat, lon = coord(items[QN[norm(SITE_OF[name])]]["coord"])
        return None, lat, lon, "site"
    q = None
    for nm in (WDREC.get(name), name):
        if nm and norm(nm) in QN:
            q = QN[norm(nm)]; break
    if q and name == "Washington Monument":
        q = "Q178114"   # the one in Washington, D.C., not Baltimore
    if q:
        lat, lon = coord(items[q]["coord"])
        if lat is not None:
            return q, lat, lon, "wikidata"
    c, iso = GEOREC.get(name, (city, cty))
    lat, lon = place_named(c, iso)
    return None, lat, lon, "city"


for r in W["records"] + W["structures"]:
    if r["city"] is None:
        r["qid"], r["lat"], r["lon"], r["loc"] = None, None, None, None; continue
    r["qid"], r["lat"], r["lon"], r["loc"] = locate(r["name"], r["city"], {"Lincoln Cathedral and the churches": "GBR"}.get(r["name"]))
    if r["name"] == "Lincoln Cathedral and the churches":
        r["qid"], r["lat"], r["lon"], r["loc"] = locate("Lincoln Cathedral", "Lincoln", "GBR")
    assert r["lat"] is not None, r["name"]
pyr = items[EE_Q]
assert min(pyr["inc"]) == -2559 and 1311 - (-2560) > 3800      # 2560 BC: consistent with "over 3,800 years" before 1311
W["structures"][0]["from"] = -2560; W["structures"][0]["from_src"] = "Wikidata inception of the Great Pyramid (Q37200): -2559 in XSD years, that is 2560 BC"
print("record-holders placed:", [(r["name"], r["loc"]) for r in W["records"] + W["structures"] if r.get("loc") != "wikidata"])

# ---------- buildings under construction (List page): position from Wikidata where the name, or the city and height, match ----------
for u in W["uc"]:
    clat, clon = place_named(u["city"])
    u["lat"] = u["lon"] = u["qid"] = None; u["loc"] = None
    cands = [w for w in ALLW if w["latlon"][0] is not None and (norm(w["name"]) == norm(u["name"]) or
             (u["h"] and abs(w["h"] - u["h"]) <= .01 * u["h"] and clat is not None and haversine(clat, clon, *w["latlon"]) < 60))]
    if clat is not None:
        cands = [w for w in cands if haversine(clat, clon, *w["latlon"]) < 80]
    if cands:
        w = min(cands, key=lambda w: abs(w["h"] - (u["h"] or 0)))
        u["qid"], (u["lat"], u["lon"]), u["loc"] = w["qid"], w["latlon"], "wikidata"
    elif clat is not None:
        u["lat"], u["lon"], u["loc"] = clat, clon, "city"
jed = W["uc"][0]
assert jed["qid"] == "Q737945" and abs(jed["lat"] - 21.734) < .01, jed     # Jeddah Tower (no English label in the extract)
print("under construction placed:", sum(u["loc"] == "wikidata" for u in W["uc"]), "by Wikidata,", sum(u["loc"] == "city" for u in W["uc"]), "at city,",
      [u["name"] for u in W["uc"] if not u["loc"]], "not placed")

jsave(W, f"{WORK}/wiki_geo.json", indent=1)
cols = ["qid", "name", "lat", "lon", "h", "year", "ysrc", "decade", "kind", "city", "country", "iso", "region", "rank350", "check", "count", "sl", "wd_city", "cls"]
D = pd.DataFrame(OUT)[cols].sort_values(["h", "name"], ascending=[False, True])
D.to_csv(f"{WORK}/tall_all.csv", index=False)
jsave({"n_rows": N_ROWS, "n_items": N_ITEMS, "drops": dict(drops), "drops2": dict(drops2), "matched_list": matched,
       "check": D.check.value_counts().to_dict()}, f"{WORK}/clean_stats.json", indent=1)
print(D.check.value_counts().to_dict(), dict(drops2))
print("counted, 200 m+:", int(((D.h >= 200) & D["count"]).sum()), " counted all:", int(D["count"].sum()))
