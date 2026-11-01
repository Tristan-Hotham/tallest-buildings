"""Header card (header.png, 1200 x 630), blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png)."""
import shutil
from charts import *

BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
for d in (BLOG, PAP):
    os.makedirs(d, exist_ok=True)
rc, L, WD, UC = R["records"], R["list350"], R["wd"], R["uc"]


def both(fig, name, dpi=200):
    fig.savefig(f"{BLOG}/b_{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    shutil.copy(f"{BLOG}/b_{name}.png", f"{PAP}/f_{name}.png")


# ---------------- header card ----------------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
fig.text(.045, .86, "The world's", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .72, "tallest building", fontproperties=DISP, fontsize=50, color=HOT, va="top")
fig.text(.045, .575, f"From the Great Pyramid to Jeddah Tower: who held the record,\nfor how long, and where the skyscrapers are now. Lincoln held it\nfor {rc['lincoln_years']} years, New York for {rc['nyc_years']}; {L['asia']} of the {L['n']} buildings\nof 350 m or more are in Asia.",
         fontproperties=SERP, fontsize=15.5, color=FG, va="top", linespacing=1.45)
fig.text(.955, .93, "maps.tristanhotham.com/tallest-buildings", fontsize=10.5, color=MUT, ha="right", va="top")
ax = fig.add_axes([.03, .03, .94, .36]); ax.set_facecolor(BG)
skyline(ax, label=False, show_axis=False, years=False, ymax=1030)
ax.set_ylim(-8, 1030)
ax2 = fig.add_axes([.60, .40, .37, .45]); ax2.set_facecolor(BG)
for i, (k, v, c) in enumerate([("828 m", "Burj Khalifa, Dubai, since 2010", HOT), (f"{rc['lincoln_years']} years", "Lincoln Cathedral, 1311 to 1549", CITY_COL["Lincoln"]),
                               (f"{int(UC['jeddah_h']):,} m", f"Jeddah Tower, planned for {UC['jeddah_planned']}", FG)]):
    ax2.text(0, 1 - i * .34, k, fontproperties=DISP, fontsize=28, color=c, va="top")
    ax2.text(0, .86 - i * .34, v, fontsize=10.5, color=MUT, va="top")
ax2.axis("off")
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)

# ---------------- skyline ----------------
fig = plt.figure(figsize=(16, 8.4), facecolor=BG)
ax = fig.add_axes([.05, .02, .94, .9]); ax.set_facecolor(BG)
skyline(ax, fs=9.5, yfs=9)
fig.text(.05, .965, "Every record-holder, to scale", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.05, .915, "Filled: tallest building (Wikipedia counts churches). Hatched: tallest structure, not a building. Dashed: Jeddah Tower, under construction. Colour: city.",
         fontsize=10, color=MUT, va="top")
both(fig, "skyline", dpi=150)

# ---------------- tenure ----------------
fig = plt.figure(figsize=(12, 8.2), facecolor=BG)
fig.text(.04, .965, "How long each city held the record", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.04, .915, f"Years as home of the world's tallest building, 1311 to {NOW}. Before 1311 the Great Pyramid of Giza, a structure, held the record\nfor about {rc['pyr_years']:,} years.",
         fontsize=10, color=MUT, va="top", linespacing=1.4)
ax = fig.add_axes([.19, .62, .78, .2]); ax.set_facecolor(BG); ribbon(ax, fs=9.5)
ax = fig.add_axes([.19, .03, .7, .55]); ax.set_facecolor(BG); city_years(ax, fs=11)
both(fig, "tenure")

# ---------------- boom ----------------
fig = plt.figure(figsize=(12, 7.6), facecolor=BG)
fig.text(.04, .965, "Tall buildings finished per decade, by region", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.04, .912, f"Left: {WD['n200']} buildings of 200 m or more in Wikidata after unit checks. Right: all {L['n']} buildings of 350 m or more on Wikipedia's list.\nFigure above each bar: Asia's share, including the Middle East. The 2020s run to {NOW}.",
         fontsize=10, color=MUT, va="top", linespacing=1.4)
ax = fig.add_axes([.05, .15, .58, .63]); ax.set_facecolor(BG); boom(ax, "grid", fs=10.5)
ax.set_title("200 m and over (Wikidata)", fontsize=11, loc="left", color=FG)
ax = fig.add_axes([.69, .15, .29, .63]); ax.set_facecolor(BG); boom(ax, "grid350", fs=10.5, decs=["1930", "1970", "1990", "2000", "2010", "2020"])
ax.set_title("350 m and over (complete list)", fontsize=11, loc="left", color=FG)
hs = [plt.Rectangle((0, 0), 1, 1, fc=c) for n, c in REGIONS]
fig.legend(hs, RNAME, loc="lower center", ncol=9, frameon=False, fontsize=9.5, handlelength=1, columnspacing=1.1, bbox_to_anchor=(.5, .01))
both(fig, "boom")

# ---------------- cities ----------------
fig = plt.figure(figsize=(12, 7.4), facecolor=BG)
fig.text(.04, .965, "Cities with the most tall buildings", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.04, .915, "Light bars: buildings of 200 m or more in Wikidata after unit checks. Dark: those of 350 m or more (complete list). Colour: region.",
         fontsize=10, color=MUT, va="top")
ax = fig.add_axes([.16, .03, .4, .78]); ax.set_facecolor(BG); cities(ax, n=15, fs=11)
ax.set_title("Ranked by 200 m and over", fontsize=11, loc="left", color=FG, x=-.02)
ax = fig.add_axes([.69, .03, .29, .78]); ax.set_facecolor(BG)
cl = L["cities"][:15]
for i, c in enumerate(cl):
    reg = c["region"]
    ax.barh(i, c["n"], height=.66, color=RCOL.get(reg, "#999"))
    ax.text(c["n"] + .3, i, str(c["n"]), va="center", fontsize=10, color=MUT); ax.text(-.4, i, c["city"], va="center", ha="right", fontsize=11, color=FG)
ax.set_ylim(14.6, -.6); ax.set_xlim(0, cl[0]["n"] * 1.25); ax.axis("off")
ax.set_title("Ranked by 350 m and over", fontsize=11, loc="left", color=FG, x=-.02)
both(fig, "cities")

# ---------------- world map of 200 m+ ----------------
fig = plt.figure(figsize=(14, 7.9), facecolor=BG)
ax = fig.add_axes([.01, .08, .98, .8]); ax.set_facecolor(BG)
D = map200(ax, k=1.0)
fig.text(.02, .965, f"Where the {WD['n200']} buildings of 200 m or more are", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.02, .915, "Wikidata after unit checks, with Wikipedia's complete list of 350 m buildings, grouped by city. Circle size: number of buildings. Colour: region.", fontsize=10, color=MUT, va="top")
TOPC = {c["city"]: c for c in WD["cities"]}
LAB = [("New York", -50.0, 38.0, "left"), ("Dubai", 61.5, 15.0, "left"), ("Shenzhen", 131.0, 17.0, "left"),
       ("Shanghai", 134.0, 29.5, "left"), ("Tokyo", 150.0, 39.5, "left")]
for c, lo, la, ha in LAB:
    cc = TOPC[c]; x, y = proj(lo, la)
    txt = (f"{c} {cc['n']}" if c != "New York" else f"New York {cc['n']}\nChicago {TOPC['Chicago']['n']}") if c != "Shenzhen" else f"Shenzhen {cc['n']}\nHong Kong {TOPC['Hong Kong']['n']}\nGuangzhou {TOPC['Guangzhou']['n']}"
    ax.text(x, y, txt, fontsize=10.5, ha=ha, va="center", color=FG, fontweight="medium", path_effects=halo(SEA, 4), linespacing=1.25, zorder=8)
hs = [plt.Line2D([], [], marker="o", ls="", mfc=c, mec="white", ms=9) for n, c in REGIONS]
fig.legend(hs, RNAME, loc="lower left", ncol=9, frameon=False, fontsize=9, bbox_to_anchor=(.01, .005), handletextpad=.1, columnspacing=.8)
for i, n in enumerate((1, 10, 40)):
    x, y = proj(-110, -16 - i * 9)
    ax.scatter([x], [y], s=bsize(n), c="#A39C90", ec="white", lw=.8, zorder=6)
    xt, _ = proj(-110 + (3.5 if n == 1 else 6 if n == 10 else 10.5), -16 - i * 9)
    ax.text(xt, y, f"{n} building" + ("s" if n > 1 else ""), va="center", fontsize=9.5, color=FG, path_effects=halo(SEA, 3), zorder=7)
x, y = proj(-114, -8); ax.text(x, y, "Circle size", fontsize=9.5, color=MUT, va="center", zorder=7)
both(fig, "map200")

# ---------------- the record's journey ----------------
HBU = []
for h in SITE["hb"]:
    if not any(u["name"] == h["name"] for u in HBU):
        HBU.append(h)
fig = plt.figure(figsize=(14, 6.4), facecolor=BG)
fig.text(.02, .965, "The record's journey", fontproperties=DISP, fontsize=22, color=FG, va="top")
fig.text(.02, .905, f"Where each tallest building stood, in order of first year. Triangles: structures that held the overall record but were not buildings.", fontsize=10, color=MUT, va="top")
ax = fig.add_axes([.01, .03, .6, .82]); ax.set_facecolor(BG)
ext = ext_of(-100, -16, 135, 64)
world(ax, ext, sea=SEA, lw=.3)
xy = [proj(h["lon"], h["lat"]) for h in HBU]
for i, (h, (x, y)) in enumerate(zip(HBU, xy)):
    ax.scatter([x], [y], s=70, c=CITY_COL[h["city"]], ec="white", lw=1, zorder=6)
for s in SITE["hs"]:
    if s["name"] in ("Great Pyramid of Giza", "Washington Monument", "Eiffel Tower"):
        x, y = proj(s["lon"], s["lat"]); ax.scatter([x], [y], s=110, marker="^", c=CITY_COL[s["city"]], ec="white", lw=1, zorder=7)
x, y = proj(-52, 27); ax.text(x, y, "United States, 1894 to 1998:\nPhiladelphia, New York, Chicago", fontsize=10, ha="center", color=FG, path_effects=halo(SEA), zorder=8)
x, y = proj(-38, 50); ax.text(x, y, "Medieval and 19th century\nEurope, 1311 to 1894 (right)", fontsize=10, ha="center", va="center", color=FG, path_effects=halo(SEA), zorder=8)
x, y = proj(78, -7); ax.text(x, y, "Asia since 1998:\nKuala Lumpur, Taipei, Dubai", fontsize=10, ha="center", va="center", color=FG, path_effects=halo(SEA), zorder=8)
x, y = proj(26, 34.3); ax.text(x, y, "Giza", fontsize=10, ha="center", va="center", color=FG, path_effects=halo(SEA), zorder=8)
ax2 = fig.add_axes([.63, .42, .36, .45]); ax2.set_facecolor(BG)
ext2 = ext_of(-4.5, 47.6, 15.5, 56.2)
world(ax2, ext2, sea=SEA, lw=.4)
EU = [h for h in HBU if h["country"] in ("United Kingdom", "Germany", "France")]
for h in EU:
    x, y = proj(h["lon"], h["lat"]); ax2.scatter([x], [y], s=90, c=CITY_COL[h["city"]], ec="white", lw=1, zorder=6)
s = SITE["hs"][3]; x, y = proj(s["lon"], s["lat"]); ax2.scatter([x], [y], s=120, marker="^", c=CITY_COL["Paris"], ec="white", lw=1, zorder=7)
# labels on paper beside the inset, in order, numbered; numbers sit next to the dots on land without covering them
order = EU + [dict(SITE["hs"][3], name="Eiffel Tower (structure)")]
for i, h in enumerate(order):
    x, y = proj(h["lon"], h["lat"])
    dx = {"Hamburg": 1, "Stralsund": 1, "Cologne": -1, "Ulm": 1, "Rouen": -1, "Beauvais": 1, "Strasbourg": 1, "Lincoln": -1, "London": 1, "Paris": -1}[h["city"]]
    ax2.text(x + dx * 4.5e4, y, str(i + 1), fontsize=9.5, ha="left" if dx > 0 else "right", va="center", color=FG, fontweight="medium", path_effects=halo(LAND, 3), zorder=8)
def kname(h):
    n = LONGNAME.get(h["name"], h["name"])
    return n if h["city"] in n else f"{n}, {h['city']}"
keytxt = "\n".join(f"{i + 1:>2}  {kname(h)}, {h['from_txt']}" for i, h in enumerate(order))
fig.text(.635, .03, keytxt, fontsize=8.6, color=FG, va="bottom", ha="left", linespacing=1.4)
both(fig, "route")
print("figures:", sorted(os.listdir(BLOG)))
