"""Static charts shared by the figures (06_figures.py) and the collage (reddit/collage.py)."""
import pandas as pd
import matplotlib.patheffects as pe
from figstyle import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
HALO = [pe.withStroke(linewidth=4, foreground=BG)]


def halo(c=BG, w=4):
    return [pe.withStroke(linewidth=w, foreground=c)]


def skyline(ax, fs=9, yfs=8.5, lw=.8, show_axis=True, label=True, gap=14, ystep=200, ymax=1240, years=True):
    items = lineup_items()
    pos, xmax = draw_lineup(ax, items, gap=gap, lw=lw)
    ax.set_ylim(-70 if years else 0, ymax); ax.set_aspect("equal")
    ax.axis("off")
    if show_axis:
        for m in range(0, 1001, ystep):
            ax.plot([-gap, xmax], [m, m], color=RULE, lw=.8 if m else 1.4, zorder=1)
            ax.text(-gap - 8, m, f"{m} m" if m else "0", ha="right", va="center", fontsize=yfs, color=MUT)
    if label:
        for j, (cx, it) in enumerate(pos):
            nm = LONGNAME.get(it["name"], it["name"]) + (", planned" if it["mode"] == "p" else "")
            ax.text(cx, it["h"] + 14, f"{nm}  {it['h']:g} m", rotation=90, ha="center", va="bottom", fontsize=fs, color=FG, path_effects=halo())
            if years:
                yl = {"c. 2560 BC": "2560 BC", None: ""}.get(it.get("from_txt"), it.get("from_txt") or "")
                if it["mode"] == "p": yl = "2028?"
                if yl == "13th century": yl = "1200s"
                ax.text(cx, -22 - (j % 2) * 26, yl, ha="center", va="top", fontsize=yfs, color=MUT)
    return pos, xmax


def ribbon(ax, fs=9, h=.34, label_years=True):
    """Two horizontal tracks, 1300 to 2026: tallest building and tallest structure, coloured by city."""
    y0, y1 = 1300, NOW
    rows = [(1, SITE["hb"], "Tallest building"), (0, SITE["hs"][1:], "Tallest structure")]
    for yy, lst, lab in rows:
        for hh in lst:
            a = max(y0, hh["from"] if hh["from"] is not None else 1300); b = hh["to"] if hh["to"] is not None else y1
            if b <= a and hh["from"] != hh["to"]:
                continue
            col = RULE if hh["kind"] == "mast" else CITY_COL.get(hh["city"], "#999")
            ax.add_patch(plt.Rectangle((a, yy - h), max(1.2, b - a), 2 * h, fc=col, ec=BG, lw=.5))
            tx = "masts" if hh["kind"] == "mast" else ("New York" if hh["city"] == "New York City" else ("churches" if hh["name"].startswith("Lincoln Cathedral and") else hh["city"]))
            if b - a > len(tx) * fs * .95 + 6:
                ax.text(a + 4, yy, tx, ha="left", va="center", fontsize=fs, color=FG if hh["kind"] == "mast" else "white", fontweight="medium")
        ax.text(y0 - 8, yy, lab, ha="right", va="center", fontsize=fs + .5, color=FG, fontweight="medium")
    ax.set_xlim(y0 - 4, y1 + 4); ax.set_ylim(-.75, 1.6)
    for t in range(1300, 2001, 100):
        ax.plot([t, t], [-.48, -.42], color=MUT, lw=.8)
        if label_years:
            ax.text(t, -.56, str(t), ha="center", va="top", fontsize=fs - .5, color=MUT)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])


def city_years(ax, fs=10, n=None, bar=.62, val_fmt="{} years"):
    cs = [c for c in R["records"]["cities"] if c["years"] is not None][: n or 99]
    for i, c in enumerate(cs):
        ax.barh(i, c["years"], height=bar, color=CITY_COL.get(c["city"], "#999"))
        ax.text(c["years"] + 4, i, val_fmt.format(c["years"]), va="center", fontsize=fs - 1, color=MUT)
        ax.text(-6, i, "New York" if c["city"] == "New York City" else c["city"], va="center", ha="right", fontsize=fs, color=FG)
    ax.set_ylim(len(cs) - .4, -.6); ax.set_xlim(0, cs[0]["years"] * 1.22)
    ax.axis("off")


def boom(ax, key="grid", fs=10, decs=None, share=True, ylab=True):
    G = R["wd"][key]
    decs = decs or [str(d) for d in range(1930, 2030, 10)]
    for i, d in enumerate(decs):
        acc = 0
        for r, c in REGIONS:
            v = G[d][r]
            if v:
                ax.bar(i, v, bottom=acc, width=.72, color=c, ec=BG, lw=.4); acc += v
        if share and acc >= 3:
            a = sum(G[d][r] for r in ASIA)
            ax.text(i, acc + max(2, acc * .01), f"{round(100 * a / acc)}%", ha="center", va="bottom", fontsize=fs - .5, color=FG, fontweight="medium")
    ax.set_xticks(range(len(decs))); ax.set_xticklabels([d + "s" for d in decs], fontsize=fs - 1)
    tops = [sum(G[d][r] for r, c in REGIONS) for d in decs]
    ax.set_ylim(0, max(tops) * 1.12)
    spines(ax); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0, labelsize=fs - 1)
    ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
    return decs


def cities(ax, n=12, fs=10, key="n"):
    cs = sorted(R["wd"]["cities"], key=lambda c: (-c[key], -c["n"]))[:n]
    mx = max(c["n"] for c in cs)
    for i, c in enumerate(cs):
        col = RCOL.get(c["region"], "#999")
        ax.barh(i, c["n"], height=.66, color=col, alpha=.45)
        if c["n350"]:
            ax.barh(i, c["n350"], height=.66, color=col)
        ax.text(c["n"] + mx * .015, i, f"{c['n']}" + (f"  ({c['n350']} of 350 m+)" if c["n350"] else ""), va="center", fontsize=fs - 1.5, color=MUT)
        ax.text(-mx * .02, i, c["city"], va="center", ha="right", fontsize=fs, color=FG)
    ax.set_ylim(n - .4, -.6); ax.set_xlim(0, mx * 1.42); ax.axis("off")
    return cs


def pts200():
    D = pd.read_csv(f"{DATA}/tall_buildings.csv", keep_default_na=False)
    D = D[(D.counted.astype(str) == "True") & (D.height_m.astype(float) >= 200)].copy()
    D["height_m"] = D.height_m.astype(float); D["year"] = D.year.astype(int)
    assert len(D) == R["wd"]["n200"]
    return D.sort_values("height_m")


WEXT = (-11.6e6, 15.2e6, -5.1e6, 8.0e6)


def size_of(h, k=1.0):
    return k * (11 + ((h - 195) / 22) ** 1.3)


def city_bubbles():
    """Buildings of 200 m or more grouped by city (Natural Earth place), with region and median position."""
    D = pts200()
    g = D.groupby(["city", "iso"]).agg(n=("name", "size"), lat=("lat", "median"), lon=("lon", "median"), region=("region", "first"),
                                       tallest=("height_m", "max")).reset_index()
    assert g.n.sum() == R["wd"]["n200"]
    return g.sort_values("n", ascending=False)


def bsize(n, k=1.0):
    return k * 34 * n


def map200(ax, ext=WEXT, k=1.0, lw=.25):
    world(ax, ext, sea=SEA, land=LAND, lw=lw)
    g = city_bubbles()
    x, y = proj(g.lon.values, g.lat.values)
    ax.scatter(x, y, s=[bsize(n, k) for n in g.n], c=[RCOL.get(r, "#999") for r in g.region], ec="white", lw=.8 * k ** .5, zorder=5, alpha=.88)
    return g
