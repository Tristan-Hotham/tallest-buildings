"""Reddit collage (r/dataisbeautiful style): every record-holder to scale, how long each city held the record, the boom
by decade and region, and a world map of today's buildings of 200 m or more. Light background; labels on paper or
sea only; numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
from charts import *

rc, L, WD, UC = R["records"], R["list350"], R["wd"], R["uc"]
OUT = os.path.join(ROOT, "reddit", "tallest_buildings.png")
FH = 23.4
fig = plt.figure(figsize=(12, FH), facecolor=BG)
X0 = .045
Y = lambda t: 1 - t / FH                      # inches from the top to figure fraction
H = lambda h: h / FH

# ---------------- title ----------------
fig.text(X0, Y(.25), "The world's tallest building, from the pyramids to Jeddah", fontproperties=DISP, fontsize=31, color=FG, va="top")
fig.text(X0, Y(.82), f"Every holder of the record, to scale, and how long each city kept it. Lincoln Cathedral held it for {rc['lincoln_years']} years\n"
         f"and New York for {rc['nyc_years']}. Since 1998 the record has been in Asia, where {L['asia']} of today's {L['n']} buildings of 350 m\n"
         f"or more stand. Jeddah Tower is under construction at a planned {int(UC['jeddah_h']):,} m.",
         fontproperties=SERP, fontsize=13, color=FG, va="top", linespacing=1.45)

# ---------------- skyline ----------------
fig.text(X0, Y(2.05), "Every record-holder, to scale", fontproperties=DISPB, fontsize=17, color=FG, va="top")
ax = fig.add_axes([X0 + .02, Y(7.3), .93, H(4.95)]); ax.set_facecolor(BG)
skyline(ax, fs=7.6, yfs=7.4, gap=12, ymax=1450)

# ---------------- legend for the skyline and the ribbon: every colour named ----------------
lg = fig.add_axes([X0, Y(8.25), .91, H(.95)]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
CITY_ORDER = ["Giza", "London", "Lincoln", "Stralsund", "Beauvais", "Strasbourg", "Hamburg", "Rouen", "Cologne", "Washington, D.C.", "Paris", "Ulm",
              "Philadelphia", "New York City", "Chicago", "Kuala Lumpur", "Taipei", "Dubai"]
for i, c in enumerate(CITY_ORDER):
    col, row = i % 6, i // 6
    x, y = col * .168, .84 - row * .34
    lg.add_patch(plt.Rectangle((x, y - .1), .016, .2, fc=CITY_COL[c], ec="none"))
    lg.text(x + .022, y, {"New York City": "New York", "Washington, D.C.": "Washington"}.get(c, c), va="center", fontsize=8.8, color=FG)
lgk = fig.add_axes([X0, Y(8.6), .91, H(.3)]); lgk.axis("off"); lgk.set_xlim(0, 1); lgk.set_ylim(0, 1)
lgk.add_patch(plt.Rectangle((0, .2), .016, .6, fc=MUT, ec="none")); lgk.text(.022, .5, "filled: tallest building (churches count)", va="center", fontsize=8.8)
lgk.add_patch(plt.Rectangle((.34, .2), .016, .6, fc=BG, ec=MUT, hatch="////", lw=1)); lgk.text(.362, .5, "hatched: tallest structure, not a building", va="center", fontsize=8.8)
lgk.add_patch(plt.Rectangle((.71, .2), .016, .6, fc="none", ec=MUT, ls=(0, (2, 1.5)), lw=1)); lgk.text(.732, .5, "dashed: under construction", va="center", fontsize=8.8)

# ---------------- ribbon and years by city ----------------
fig.text(X0, Y(9.0), "Who held the record, 1300 to 2026", fontproperties=DISPB, fontsize=17, color=FG, va="top")
fig.text(X0, Y(9.38), f"Before 1311 the Great Pyramid of Giza, a tomb rather than a building, was the tallest structure for about {rc['pyr_years']:,} years.", fontsize=9.5, color=MUT, va="top")
ax = fig.add_axes([X0 + .15, Y(11.0), .79, H(1.4)]); ax.set_facecolor(BG); ribbon(ax, fs=8.6)
fig.text(X0, Y(11.3), "Years as home of the tallest building", fontsize=10.5, color=FG, va="top", fontweight="medium")
ax = fig.add_axes([X0 + .1, Y(14.85), .33, H(3.25)]); ax.set_facecolor(BG); city_years(ax, fs=9.2, val_fmt="{}")

# ---------------- the boom ----------------
fig.text(.53, Y(11.3), "Buildings of 200 m or more finished per decade", fontsize=10.5, color=FG, va="top", fontweight="medium")
fig.text(.53, Y(11.6), "Figure on each bar: Asia's share, including the Middle East.\nColours: regions, as on the map below.", fontsize=8.8, color=MUT, va="top", linespacing=1.35)
ax = fig.add_axes([.56, Y(14.75), .41, H(2.6)]); ax.set_facecolor(BG)
boom(ax, "grid", fs=8.6, decs=[str(d) for d in range(1960, 2030, 10)])

# ---------------- world map ----------------
fig.text(X0, Y(15.25), f"Where today's {WD['n200']} buildings of 200 m or more are", fontproperties=DISPB, fontsize=17, color=FG, va="top")
fig.text(X0, Y(15.63), "Grouped by city; circle size is the number of buildings, colour the region. Counts are Wikidata records after\nunit checks, with Wikipedia's complete list of buildings of 350 m or more.",
         fontsize=9.2, color=MUT, va="top", linespacing=1.35)
ext = (-11.2e6, 15.2e6, -5.0e6, 7.6e6)
mw = .93; mh = mw * 12 * (ext[3] - ext[2]) / (ext[1] - ext[0])
ax = fig.add_axes([(1 - mw) / 2, Y(16.2 + mh), mw, H(mh)]); ax.set_facecolor(BG)
map200(ax, ext=ext, k=.95, lw=.25)
TOPC = {c["city"]: c for c in WD["cities"]}
for txt, lo, la, ha in [(f"New York {TOPC['New York']['n']}\nChicago {TOPC['Chicago']['n']}", -50, 37, "left"),
                        (f"Dubai {TOPC['Dubai']['n']}", 61.5, 14.5, "left"),
                        (f"Shenzhen {TOPC['Shenzhen']['n']}\nHong Kong {TOPC['Hong Kong']['n']}\nGuangzhou {TOPC['Guangzhou']['n']}", 131, 16, "left"),
                        (f"Shanghai {TOPC['Shanghai']['n']}", 134, 29.5, "left"), (f"Tokyo {TOPC['Tokyo']['n']}", 150, 39.5, "left")]:
    x, y = proj(lo, la)
    ax.text(x, y, txt, fontsize=10, ha=ha, va="center", color=FG, fontweight="medium", path_effects=halo(SEA, 3.5), linespacing=1.2, zorder=8)
x, y = proj(-114, -5); ax.text(x, y, "Circle size", fontsize=8.8, color=MUT, va="center", zorder=7)
for i, n in enumerate((1, 10, 40)):
    x, y = proj(-110, -12 - i * 8.5)
    ax.scatter([x], [y], s=bsize(n, .95), c="#A39C90", ec="white", lw=.6, zorder=6)
    xt, _ = proj(-110 + (3 if n == 1 else 5.5 if n == 10 else 10), -12 - i * 8.5)
    ax.text(xt, y, f"{n} building" + ("s" if n > 1 else ""), va="center", fontsize=8.8, color=FG, path_effects=halo(SEA, 3), zorder=7)
yl = 16.2 + mh + .3
lr = fig.add_axes([X0, Y(yl + .15), .91, H(.3)]); lr.axis("off"); lr.set_xlim(0, 1); lr.set_ylim(0, 1)
x = 0
for n, c in REGIONS:
    lr.add_patch(plt.Rectangle((x, .2), .013, .6, fc=c, ec="none")); lr.text(x + .018, .5, n, va="center", fontsize=8.8, color=FG)
    x += .018 + len(n) * .0072 + .022

# ---------------- footer ----------------
yf = yl + .45
fig.add_artist(plt.Line2D([X0, X0 + .91], [Y(yf), Y(yf)], color=FG, lw=1.2))
fig.text(X0, Y(yf + .1), "Sources: English Wikipedia, 'History of the world's tallest buildings' and 'List of tallest buildings' (CC BY-SA 4.0); Wikidata (CC0),\n"
         "heights checked against the List and, for US buildings, the CORGIS skyscrapers dataset; Natural Earth. Silhouettes: heights to\n"
         "scale, outlines simplified. Pyramid date from Wikidata.", fontsize=8, color=MUT, va="top", linespacing=1.4)
fig.text(X0, Y(yf + .75), "Analysis and chart: Tristan Hotham, with Python and matplotlib", fontsize=8.8, color=FG, va="top")
fig.text(X0 + .91, Y(yf + .75), "maps.tristanhotham.com/tallest-buildings", fontsize=8.8, color=FG, va="top", ha="right")
print("footer bottom at", yf + .95, "of", FH)
fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
from PIL import Image
print(OUT, Image.open(OUT).size)
