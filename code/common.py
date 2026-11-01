"""Shared paths, groupings and helpers for the tallest-buildings project.

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw8/tallest/wiki_History_of_the_world_s_tallest_buildings.json
      English Wikipedia, 'History of the world's tallest buildings' (revision 1379678838), parsed HTML. CC BY-SA 4.0.
      Gives the record-holders (two tables: churches and cathedrals to 1894, skyscrapers from 1894), the definitions of
      "building" and of height, and the prose on the Great Pyramid, the Washington Monument and the Eiffel Tower.
  /home/claude/newdata/raw8/tallest/wiki_List_of_tallest_buildings.json
      English Wikipedia, 'List of tallest buildings' (revision 1376498189), parsed HTML. CC BY-SA 4.0.
      Gives the 98 completed or architecturally topped-out buildings of 350 m or more, the buildings under construction
      (including Jeddah Tower) and the tallest building on each continent.
  /home/claude/newdata/raw8/tallest/wikidata_tall.tsv
      Wikidata (CC0) via QLever: structures (subclasses of architectural structure) with a height (P2048) of 100 or more,
      with coordinates, date of official opening (P1619), inception (P571), city, country and class. Units were NOT
      returned with the heights, so some are in feet or centimetres: see code/03_wikidata.py.
  CORGIS skyscrapers dataset (corgis-edu/corgis on GitHub, GPL-3.0; derived from the CTBUH Skyscraper Center, US
      buildings only, to 2016), fetched from GitHub into WORK and used ONLY to check whether Wikidata's heights for
      United States buildings are in metres. It is not redistributed and none of its values are published.
  /home/claude/newdata/raw/geo/  Natural Earth countries and populated places (public domain).
"""
import json, gzip, os, re, unicodedata
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("TALL_RAW", "/home/claude/newdata/raw8/tallest")
GEO = os.environ.get("TALL_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("TALL_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("TALLTMP", "/dev/shm/tallest"), "work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)
CORGIS_URL = "https://raw.githubusercontent.com/corgis-edu/corgis/master/website/datasets/csv/skyscrapers/skyscrapers.csv"

SLUG = "tallest-buildings"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "10.5281/zenodo.23857608"                 # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/tallest-buildings/"           # filled in by the publisher
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
NOW = 2026                      # the year the pages describe ("as of 2026")

# regions (order = legend order), from Natural Earth subregions; Hong Kong, Macau and Taiwan count as East Asia
REGIONS = [("East Asia", "#C8102E"), ("Southeast Asia", "#F28C28"), ("South Asia", "#E6B422"), ("Middle East", "#8E3B8E"),
           ("Europe", "#2F6FB0"), ("North America", "#17324D"), ("Latin America", "#2E8B57"), ("Africa", "#A0522D"),
           ("Oceania", "#4FA3A5")]
RNAME = [r[0] for r in REGIONS]
ASIA = {"East Asia", "Southeast Asia", "South Asia", "Middle East"}
SUB2REG = {"Eastern Asia": "East Asia", "South-Eastern Asia": "Southeast Asia", "Southern Asia": "South Asia",
           "Central Asia": "South Asia", "Western Asia": "Middle East", "Northern America": "North America",
           "Central America": "Latin America", "Caribbean": "Latin America", "South America": "Latin America",
           "Australia and New Zealand": "Oceania", "Melanesia": "Oceania", "Micronesia": "Oceania", "Polynesia": "Oceania",
           "Northern Africa": "Africa", "Western Africa": "Africa", "Eastern Africa": "Africa", "Middle Africa": "Africa",
           "Southern Africa": "Africa", "Northern Europe": "Europe", "Western Europe": "Europe", "Southern Europe": "Europe",
           "Eastern Europe": "Europe"}
# Egypt sits in Northern Africa; Turkey, Cyprus and the Caucasus are Western Asia in Natural Earth; Turkey and the
# Caucasus are put with the Middle East here as in Natural Earth. Central Asia (Kazakhstan) is grouped with South Asia.

# completion decades for the map and charts (colour ramp from old to new)
DECADES = list(range(1880, 2030, 10))
DEC_COL = {1880: "#5B4636", 1890: "#5B4636", 1900: "#6E4B3A", 1910: "#6E4B3A", 1920: "#7F4F3F", 1930: "#7F4F3F",
           1940: "#8C5A44", 1950: "#8C5A44", 1960: "#4E6E8E", 1970: "#3F7FA6", 1980: "#2E95A3", 1990: "#3BA676",
           2000: "#9CBF3B", 2010: "#F2A71B", 2020: "#E5482C"}
DEC_BANDS = [("Before 1960", 0, 1959, "#7F4F3F"), ("1960s and 1970s", 1960, 1979, "#3F7FA6"), ("1980s and 1990s", 1980, 1999, "#2E9A8C"),
             ("2000s", 2000, 2009, "#9CBF3B"), ("2010s", 2010, 2019, "#F2A71B"), ("2020s", 2020, 2029, "#E5482C")]


def band_of(y):
    for i, (n, a, b, c) in enumerate(DEC_BANDS):
        if y is not None and a <= y <= b:
            return i
    return None


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower().replace("&", " and ")
    s = re.sub(r"\b(the|tower|towers|building|centre|center|plaza)\b", " ", s)
    return re.sub(r"[\W_]+", " ", s).strip()


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", " - ").replace("–", "-").replace("−", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


class NpEnc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return super().default(o)


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(json.loads(json.dumps(obj, cls=NpEnc)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"), cls=NpEnc)


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "yr": return f"{-int(v)} BC" if int(v) < 0 else str(int(v))
    raise ValueError(f)


def haversine(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * np.arcsin(np.sqrt(a))
