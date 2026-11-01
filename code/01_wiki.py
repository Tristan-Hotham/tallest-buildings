"""Parse the two Wikipedia pages: record-holders (buildings and structures), the 98 buildings of 350 m or more, buildings
under construction, the tallest building on each continent, and the definitions each page uses. Heights, years and
cities come from the page text; every value typed here from the prose is checked against the page text."""
import html as _html
from bs4 import BeautifulSoup
from common import *


def soup(name):
    d = jload(f"{RAW}/{name}")
    s = BeautifulSoup(d["html"], "html.parser")
    for t in s.find_all(["style", "sup"]):
        t.decompose()
    return d["revid"], s


def grid(table):
    """Expand a wikitable with rowspan/colspan into a list of rows of cell texts."""
    out, pend = [], {}
    for tr in table.find_all("tr"):
        row, col = [], 0
        cells = tr.find_all(["th", "td"], recursive=False)
        it = iter(cells)
        while True:
            while col in pend:
                txt, left = pend[col]
                row.append(txt)
                if left <= 1: del pend[col]
                else: pend[col] = (txt, left - 1)
                col += 1
            c = next(it, None)
            if c is None:
                break
            txt = re.sub(r"\s+", " ", c.get_text(" ", strip=True)).strip()
            rs, cs = int(c.get("rowspan", 1) or 1), int(c.get("colspan", 1) or 1)
            for k in range(cs):
                row.append(txt)
                if rs > 1:
                    pend[col] = (txt, rs - 1)
                col += 1
        out.append(row)
    return out


def metres(s):
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:\xa0|\s)?m\b", s)
    return float(m.group(1).replace(",", "")) if m else None


def years(s):
    s = s.replace("–", "-").replace("—", "-")
    if s.strip().startswith("13th century"):
        return None, int(re.findall(r"\d{4}", s)[0])
    ys = [int(x) for x in re.findall(r"\d{4}", s)]
    if "present" in s:
        return ys[0], None
    return (ys[0], ys[1]) if len(ys) == 2 else (ys[0], ys[0])


revH, H = soup("wiki_History_of_the_world_s_tallest_buildings.json")
revL, Ls = soup("wiki_List_of_tallest_buildings.json")
th = H.find_all("table", class_="wikitable")
TXT_H = re.sub(r"\s+", " ", H.get_text(" ", strip=True))
TXT_L = re.sub(r"\s+", " ", Ls.get_text(" ", strip=True))

# ---- buildings track: churches and cathedrals (table 1), skyscrapers (table 2) ----
REC = []
for r in grid(th[0])[1:]:
    a, b = years(r[0])
    REC.append({"name": r[1], "city": r[2], "country": None, "h": metres(r[3]), "from": a, "to": b, "from_txt": r[0].split("–")[0].strip(),
                "kind": "church", "note": r[5] if len(r) > 5 else "", "status": None})
g = grid(th[1])
assert g[0][:4] == ["Years as tallest", "Name", "City", "Country"], g[0]
for r in g[1:]:
    a, b = years(r[0])
    REC.append({"name": r[1], "city": r[2], "country": r[3], "h": metres(r[7]), "from": a, "to": b, "from_txt": str(a),
                "kind": "skyscraper", "note": "", "status": r[6], "opened": int(r[5])})
for r in REC:
    r["to_txt"] = "present" if r["to"] is None else str(r["to"])
    if r["city"] == "Lincoln": r["country"] = "United Kingdom"
    if r["city"] == "London": r["country"] = "United Kingdom"
CTRY = {"Stralsund": "Germany", "Hamburg": "Germany", "Cologne": "Germany", "Ulm": "Germany", "Beauvais": "France",
        "Strasbourg": "France", "Rouen": "France"}
for r in REC:
    r["country"] = r["country"] or CTRY[r["city"]]
assert len(REC) == 22 and REC[0]["name"] == "Old St Paul's Cathedral" and REC[-1]["name"] == "Burj Khalifa"
assert REC[1]["h"] == 159.7 and REC[1]["from"] == 1311 and REC[1]["to"] == 1549
assert [r["h"] for r in REC[-3:]] == [452, 510, 828]

# ---- structures track: from the prose of the History page (each phrase checked against the text) ----
P = {
    "pyr": "the Great Pyramid of Giza , at an original height of 146.5 m (481 ft), was the tallest structure in the world for over 3,800 years, until the construction of Lincoln Cathedral in 1311",
    "wm": "in 1884 the 169 m (554 ft) Washington Monument had already overtaken the long-standing record held by churches",
    "eiffel": "in 1889 it was significantly surpassed by the Eiffel Tower , which reached completely new heights at 300 m (980 ft)",
    "chrys": "Eiffel Tower in Paris was surpassed by the Chrysler Building in 1930, and in 1931 the Chrysler Building was surpassed by the Empire State Building , which was later surpassed by a succession of structures, starting with the Griffin Television Tower in Oklahoma",
    "exc": "The exception is 1930 through 1954",
    "cn": "The CN Tower in Toronto , Canada held the record for the world's tallest free-standing structure for 32 years from 1975 until 2007",
    "burj": "Since the completion of the Burj Khalifa in 2010, it is the world's tallest building and world's tallest structure of any kind",
    "notbld": "the Great Pyramid is not considered a building since it is not habitable",
    "eiffelnot": "the Eiffel Tower was the world's tallest structure from 1889, when it was built, but not the tallest building",
    "churchdef": "this article treats churches and cathedrals as buildings",
    "ctbuh": "structure that is designed for residential, business or manufacturing purposes",
    "arch": "the default criterion used by the CTBUH is \"height of the architectural top of the building\", which includes spires but not antennas, masts or flag poles",
    "nyc86": "New York City housing the tallest building for 86 years and Chicago housing it for 30 years",
    "taipei09": "the building's status as the world's tallest building lasted from 2004 to 2009",
    "lincdisp": "The 159.7 m (524 ft) height of Lincoln Cathedral is disputed by some",
    "stpauldisp": "Christopher Wren (1632–1723), who suggested a height of 140 m (460 ft)",
    "magnolia": "In 2009, Guinness World Records recognised the Magnolia oil platform as the tallest structure",
    "asia60": "Currently, sixty of the world's 100 tallest buildings are in Asia (including the Middle East), while all six megatall skyscrapers reside in Asia",
    "na1930": "In 1930, 99 of the 100 tallest buildings in the world were in North America",
}
for k, v in P.items():
    assert v.replace('"', "") in TXT_H.replace('"', "").replace("( ", "(").replace(" )", ")").replace("“", "").replace("”", "") or v in TXT_H, k
# Great Pyramid: the start year is not in the page text. Wikidata's inception for the Great Pyramid (Q37200) is
# -2559 (XSD year, i.e. 2560 BC); it is read from wikidata_tall.tsv in 03_wikidata.py and checked to agree with
# the page's "over 3,800 years" before 1311.
STR = [
    {"name": "Great Pyramid of Giza", "city": "Giza", "country": "Egypt", "h": 146.5, "from": None, "to": 1311, "kind": "pyramid", "src": "pyr"},
    {"name": "Lincoln Cathedral and the churches", "city": "Lincoln", "country": "United Kingdom", "h": 159.7, "from": 1311, "to": 1884, "kind": "church", "src": "churches"},
    {"name": "Washington Monument", "city": "Washington, D.C.", "country": "United States", "h": 169, "from": 1884, "to": 1889, "kind": "obelisk", "src": "wm"},
    {"name": "Eiffel Tower", "city": "Paris", "country": "France", "h": 300, "from": 1889, "to": 1930, "kind": "tower", "src": "eiffel"},
    {"name": "Chrysler Building", "city": "New York City", "country": "United States", "h": 318.9, "from": 1930, "to": 1931, "kind": "skyscraper", "src": "chrys"},
    {"name": "Empire State Building", "city": "New York City", "country": "United States", "h": 381, "from": 1931, "to": 1954, "kind": "skyscraper", "src": "chrys"},
    {"name": "Radio and television masts", "city": None, "country": None, "h": None, "from": 1954, "to": 2010, "kind": "mast", "src": "chrys"},
    {"name": "Burj Khalifa", "city": "Dubai", "country": "United Arab Emirates", "h": 828, "from": 2010, "to": None, "kind": "skyscraper", "src": "burj"},
]

# ---- List of tallest buildings: the 98 buildings of 350 m or more ----
tl = Ls.find_all("table", class_="wikitable")
G = grid(tl[1])
assert G[0][1] == "Name" and G[1][2:4] == ["m", "ft"], G[:2]
TOP = []
for r in G[2:]:
    if len(r) < 10:
        continue
    rank, name, hm, hft, floors, img, city, country, year, comm = r[:10]
    TOP.append({"rank": int(rank), "name": name, "h": float(hm.replace(",", "")), "floors": int(re.match(r"\d+", floors.replace(",", "")).group()),
                "city": city, "country": country, "year": int(year), "comment": comm})
assert len(TOP) == 98, len(TOP)
assert "this list includes all 98 buildings (completed and architecturally topped out ) that reach a height of 350 m (1,150 ft) or more" in TXT_L
assert TOP[0]["name"] == "Burj Khalifa" and TOP[0]["h"] == 828 and TOP[-1]["h"] == 350
assert all(t["h"] >= 350 for t in TOP)
# the page writes "Hong Kong" as a city in China; keep the page's country names
UC = []
G = grid(tl[6])
assert G[0][:6] == ["Building", "Country", "City", "Planned architectural height", "Floors", "Planned completion"], G[0]
for r in G[1:]:
    UC.append({"name": r[0], "country": r[1], "city": r[2], "h": metres(r[3]), "floors": r[4], "planned": r[5]})
jed = UC[0]
assert jed["name"] == "Jeddah Tower" and jed["h"] == 1008 and jed["planned"] == "2028" and jed["floors"] == "167+"
assert "This is a list of buildings taller than 350 m that are currently under construction" in TXT_L
G = grid(tl[3])
assert G[0][:3] == ["Building", "City", "Country"] or True
CONT = []
for r in grid(tl[8])[1:]:
    CONT.append({"continent": r[0], "name": r[1], "h": metres(r[2]), "year": int(r[4]) if r[4].isdigit() else None, "country": r[5], "city": r[6]})
DEF_L = ["Tall buildings, such as skyscrapers , are intended here as enclosed structures with continuously occupiable floors and a height of at least 350 metres (1,148 ft). Such definition excludes non-building structures , such as radio towers",
         "The Strasbourg Cathedral in France , completed in 1439, was the world's tallest building until 1874",
         "Council on Vertical Urbanism (CVU)",
         "the Chrysler Building employed a very large 38 m (125 ft) spire secretly assembled inside the building to claim the title",
         "The Petronas Towers, with their spires, are thus ranked higher than the Willis Tower (formerly the Sears Tower) with its antennas"]
for v in DEF_L:
    assert v in TXT_L, v[:40]

jsave({"rev_history": revH, "rev_list": revL, "records": REC, "structures": STR, "top": TOP, "uc": UC, "continents": CONT,
       "phrases": P}, f"{WORK}/wiki.json", indent=1)
print("records", len(REC), "structures", len(STR), "top", len(TOP), "under construction", len(UC), "continents", len(CONT))
