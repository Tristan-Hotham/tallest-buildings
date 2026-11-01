"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo), Reddit post text (reddit/post.md).
10.5281/zenodo.23857608, https://doi.org/10.5281/zenodo.23857608 and https://blog.tristanhotham.com/2026/10/31/tallest-buildings/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_The_Worlds_Tallest_Building"
rc, L, WD, UC = R["records"], R["list350"], R["wd"], R["uc"]

# the page build checks the shared facts; these are statements made in words only in the blog
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
import pandas as pd
D = pd.read_csv(f"{WORK}/tall_all.csv", keep_default_na=False)
q = D[D.qid == "Q373143"]
assert q.empty   # Edifice Price is excluded; the blog quotes its raw Wikidata record
raw = pd.read_csv(f"{RAW}/wikidata_tall.tsv", sep="\t", dtype=str, quoting=3)
r = raw[raw["?b"].str.contains("Q373143>")]
assert (r["?h"].astype(float) == 269).all() and r["?inc"].str.contains("1929-").any()
assert [c["city"] for c in WD["cities"][:5]] == ["New York", "Dubai", "Shenzhen", "Chicago", "Tokyo"]
assert [c["city"] for c in L["cities"][:3]] == ["Dubai", "Shenzhen", "New York"]

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG|DOI_URL|BLOG_URL|DOI\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
left = [t for t in re.findall(r"\{\{(?!IMG)[^}]*\}\}", post) if t not in ("https://doi.org/10.5281/zenodo.23857608", "https://blog.tristanhotham.com/2026/10/31/tallest-buildings/", "10.5281/zenodo.23857608")]
assert not left, left
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "The world's tallest building: who held the record, and for how long",
        "slug": "tallest-buildings",
        "excerpt": f"From the Great Pyramid to Jeddah Tower: I followed the title of world's tallest building through time. Lincoln Cathedral held it for {rc['lincoln_years']} years, New York for {rc['nyc_years']}, and since 1998 it has been in Asia, where {L['asia']} of the {L['n']} buildings of 350 m or more now stand.",
        "seo_description": f"Every world's tallest building from the pyramids to Jeddah Tower: Lincoln held the record {rc['lincoln_years']} years, New York {rc['nyc_years']}. Maps and data.",
        "tags": ["skyscrapers", "tallest buildings", "architecture", "history", "cathedrals", "maps", "data visualisation", "Wikidata"],
        "header_alt": f"Title card reading 'The world's tallest building' in black and red on cream paper, above a row of silhouettes of every record-holder drawn to scale, from a hatched pyramid and small church spires to New York skyscrapers, the Petronas Towers, Taipei 101, the Burj Khalifa and a dashed Jeddah Tower. Text: 828 m, Burj Khalifa, Dubai, since 2010; {rc['lincoln_years']} years, Lincoln Cathedral, 1311 to 1549; {int(UC['jeddah_h']):,} m, Jeddah Tower, planned for {UC['jeddah_planned']}."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/tallest-buildings_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"tallest-buildings/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"tallest-buildings/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "tallest-buildings/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("~", " ")
zmeta = {"title": "The World's Tallest Building: Who Held the Record, for How Long, and Where Today's Tall Buildings Are, from the Great Pyramid to Jeddah Tower",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/tallest-buildings/}}.</p><p>Data: English Wikipedia, 'History of the world's tallest buildings' and 'List of tallest buildings' (CC BY-SA 4.0); Wikidata (CC0); Natural Earth (public domain). United States heights checked against the CORGIS skyscrapers dataset (not redistributed).</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["tallest buildings", "skyscrapers", "architectural history", "cathedrals", "CTBUH", "Wikidata", "Wikipedia", "data quality", "maps"],
         "license": "cc-by-sa-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://en.wikipedia.org/wiki/History_of_the_world%27s_tallest_buildings", "relation": "isDerivedFrom", "resource_type": "other"},
                                 {"identifier": "https://en.wikipedia.org/wiki/List_of_tallest_buildings", "relation": "isDerivedFrom", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")

# Reddit post text
post_md = f"""## Title

[OC] The world's tallest building, from the pyramids to Jeddah: Lincoln Cathedral held the record for {rc['lincoln_years']} years, New York for {rc['nyc_years']}, and {L['asia']} of today's {L['n']} buildings over 350 m are in Asia

## Body

I followed the title of world's tallest building through Wikipedia's history of the record and drew every holder to scale. Counting churches as buildings, as the source does, the record has been held in {rc['n_cities']} cities. The longest reign is not a skyscraper's: Lincoln Cathedral's {rc['lincoln_h']} m spire held it from 1311 until it collapsed in 1549 ({rc['lincoln_years']} years), and Strasbourg Cathedral held it for {rc['stras_years']}. Churches held it for {rc['church_pct']:.0f}% of the time since 1311. New York had it for {rc['nyc_years']} years and the United States for {rc['us_years']}, until the Petronas Towers took it to Kuala Lumpur in 1998; it has stayed in Asia since. The pyramid, the Washington Monument and the Eiffel Tower are hatched because they were the tallest structures but never buildings. The map counts {WD['n200']} buildings of 200 m or more from Wikidata after unit checks (many Wikidata heights are really feet, so I matched everything over 350 m against Wikipedia's complete list and checked US heights against a CTBUH-derived dataset). Caveat: Wikidata is a record, not a census, and is patchy for China, so the city counts are records of buildings rather than a full count. Jeddah Tower is listed as under construction at a planned {int(UC['jeddah_h']):,} m. Interactive map with a slider through time: https://maps.tristanhotham.com/tallest-buildings/

## Source comment

Sources: English Wikipedia, 'History of the world's tallest buildings' and 'List of tallest buildings' (CC BY-SA 4.0); Wikidata via QLever (CC0); CORGIS skyscrapers dataset, derived from the CTBUH Skyscraper Center (used only to check US height units); Natural Earth outlines and place names (public domain). Pyramid date from Wikidata. Silhouettes: heights to scale, outlines simplified.

Tools: Python (pandas, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/tallest-buildings/
Paper: {{https://doi.org/10.5281/zenodo.23857608}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/tallest-buildings/}}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in post_md, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post_md)
print("reddit title chars", len(post_md.splitlines()[2]))
