"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (results, site.json, silhouettes, world.json, cities) is embedded and data/points.json is
loaded by the page. Facts stated in words (page, blog, paper, collage) are checked here. 10.5281/zenodo.23857608 and https://blog.tristanhotham.com/2026/10/31/tallest-buildings/ stay
as placeholders for the publisher."""
import json
from common import *
from figstyle import silhouette, lineup_items, CITY_COL, LONGNAME

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
rc, L, WD, UC = R["records"], R["list350"], R["wd"], R["uc"]
HB, HS = SITE["hb"], SITE["hs"]

# ---------------- facts stated in words ----------------
cy = [c["city"] for c in rc["cities"] if c["years"] is not None]
assert cy[:4] == ["Lincoln", "Strasbourg", "Stralsund", "New York City"]                  # "Lincoln held it longest, then Strasbourg"
assert rc["shortest"] == "Cathedral of Our Lady of Strasbourg"                             # "the shortest record-holder of all"
assert [h["city"] for h in HB[6:10]] == ["Hamburg", "Rouen", "Cologne", "Ulm"] and all(1874 <= h["from"] <= 1890 for h in HB[6:10])
assert HB[3]["note"] == "Tower collapsed 1573" and HB[4]["note"] == "Bell tower burned down in 1647"
assert HB[9]["name"] == "Ulm Minster" and HB[10]["kind"] == "skyscraper"                    # Ulm, the last church
assert all(h["city"] == "New York City" for h in HB[11:18]) and HB[11]["from"] == 1908 and HB[17]["to"] == 1973
assert HB[14]["from"] == HB[14]["to"] == 1930 and HB[15]["from"] == 1930                    # 40 Wall Street and Chrysler, both 1930
assert max(HB, key=lambda h: h["years"] or 0)["name"] == "Lincoln Cathedral"
inc = [(HB[i]["h"] / HB[i - 1]["h"] - 1) for i in range(1, len(HB))]
assert max(range(len(inc)), key=lambda i: inc[i]) == len(inc) - 1                           # the Burj's jump is the biggest
assert all(HB[i]["country"] == "United States" for i in range(10, 19)) and HB[10]["from"] == 1894 and HB[18]["to"] == 1998   # a century in the US
assert HB[19]["city"] == "Kuala Lumpur" and HB[20]["city"] == "Taipei"
assert L["oldest"]["name"] == "Empire State Building" and L["oldest"]["year"] == 1931
assert UC["over600"] == 2 and UC["usa"] == 1 and SITE["uc"][1]["name"] == "Burj Azizi"
assert WD["peak_decade"] == 2010 and WD["asia_share"]["1980"] < WD["asia_share"]["1990"] < WD["asia_share"]["2000"] < WD["asia_share"]["2010"]
assert WD["cities"][0]["city"] == "New York" and L["cities"][0]["city"] == "Dubai"
assert R["records"]["n_cities"] == 15 and R["records"]["church_pct"] > 80
assert L["missing_cn_pct"] > 2 * L["missing_other_pct"]
for k in ("pyr", "wm", "eiffel", "chrys", "exc", "cn", "burj", "notbld", "eiffelnot", "churchdef", "arch", "lincdisp", "stpauldisp", "na1930"):
    assert k in jload(f"{WORK}/wiki.json")["phrases"]

# ---------------- silhouettes for the page ----------------
items = lineup_items()
x = 0; gap = 14; out = []
for it in items:
    polys = silhouette(it["name"], it["h"]); xs = [p[0] for poly in polys for p in poly]
    cx = x - min(xs)
    spans = " and ".join(f"{h['from_txt']} to {h['to_txt']}" for h in (HB if it["mode"] == "b" else HS) if h["name"] == it["name"])
    out.append({"name": it["name"], "city": it["city"], "h": it["h"], "mode": it["mode"], "x": round(cx, 1), "from_txt": it.get("from_txt", ""), "spans": spans})
    x = cx + max(xs) + gap
polys = {it["name"]: [[[round(a, 1), round(b, 1)] for a, b in poly] for poly in silhouette(it["name"], it["h"])] for it in items}
city = {it["name"]: it["city"] for it in items}
SIL = {"items": out, "total": round(x, 1), "poly": polys, "city": city, "citycol": CITY_COL, "short": LONGNAME}


def fill(tpl):
    html = re.sub(r"\{\{(?!DOI\}\}|BLOG_URL\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    left = [t for t in re.findall(r"\{\{[^}]*\}\}", html) if t not in ("10.5281/zenodo.23857608", "https://blog.tristanhotham.com/2026/10/31/tallest-buildings/")]
    assert not left, left[:5]
    return html


def build():
    html = fill(open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read())
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE)).replace("/*SIL*/", J(SIL))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": c["name"], "lat": c["lat"], "lon": c["lon"], "pop": c["pop"]} for c in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, (bad, scr[scr.find(bad) - 80: scr.find(bad) + 20])
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
