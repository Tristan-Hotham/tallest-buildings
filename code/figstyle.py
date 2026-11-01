"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the palette, Natural Earth outlines in the Equal Earth projection, and the stylised silhouettes of
the record-holders. Silhouettes: heights are to scale (from the Wikipedia tables); widths and outlines are simplified
sketches, not survey drawings."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from pyproj import Transformer
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#6B6660", "axes.labelcolor": "#1E1B18",
                     "xtick.color": "#6B6660", "ytick.color": "#6B6660", "hatch.linewidth": 1.2})
BG, FG, MUT, LAND, RULE, SEA = "#F7F3EA", "#1E1B18", "#6B6660", "#E4DDCE", "#DCD3C2", "#EEF1F0"
HOT, GOLD, NAVY = "#B3122E", "#C8932B", "#1F3B63"
RCOL = {n: c for n, c in REGIONS}
BCOL = [b[3] for b in DEC_BANDS]

CITY_COL = {"London": "#9A8778", "Lincoln": "#6B4A35", "Stralsund": "#A3794F", "Beauvais": "#C2A06E", "Strasbourg": "#C0623E", "Hamburg": "#7F6B58",
            "Rouen": "#9A5236", "Cologne": "#4F443C", "Ulm": "#B8874F", "Philadelphia": "#6A8DB3", "New York City": "#1F3B63", "Chicago": "#3F7FB8",
            "Kuala Lumpur": "#E58A1F", "Taipei": "#D24B3E", "Dubai": "#B3122E", "Giza": "#D8AE62", "Washington, D.C.": "#8E99A4", "Paris": "#58606A"}

EE = Transformer.from_crs(4326, 8857, always_xy=True)
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    for ring in rings(f["geometry"]):
        SHAPES.append((f["properties"]["iso"], ring))


def proj(lon, lat, tr=EE):
    return tr.transform(np.asarray(lon, dtype=float), np.asarray(lat, dtype=float))


def ext_of(lon0, lat0, lon1, lat1, tr=EE):
    lo = np.linspace(lon0, lon1, 50); la = np.linspace(lat0, lat1, 50)
    xs, ys = proj(np.r_[lo, lo, np.full(50, lon0), np.full(50, lon1)], np.r_[np.full(50, lat0), np.full(50, lat1), la, la], tr)
    return (xs.min(), xs.max(), ys.min(), ys.max())


def world(ax, ext, tr=EE, lw=.3, ec="#FFFFFF", land=LAND, z=1, sea=None):
    if sea:
        ax.add_patch(plt.Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], fc=sea, ec="none", zorder=0))
    for iso, ring in SHAPES:
        if iso == "ATA":
            continue
        x, y = tr.transform(np.clip(ring[:, 0], -179.9, 179.9), np.clip(ring[:, 1], -89.5, 89.5))
        if x.max() < ext[0] or x.min() > ext[1] or y.max() < ext[2] or y.min() > ext[3]:
            continue
        ax.add_patch(MPoly(np.column_stack([x, y]), closed=True, fc=land, ec=ec, lw=lw, zorder=z))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


# ------------------------------------------------------------------ silhouettes
def stack(tiers):
    """Symmetric stepped outline from tiers [(y_bottom, y_top, halfwidth_bottom, halfwidth_top)], bottom to top."""
    L = []
    for y0, y1, a, b in tiers:
        L += [(-a, y0), (-b, y1)]
    R = [(-x, y) for x, y in L[::-1]]
    return [L + R]


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]


def church(h, body_hw, body_h, tw, th, sw=None):
    return stack([(0, body_h, body_hw, body_hw), (body_h, th, tw, tw), (th, h, sw or tw * .85, .4)])


def silhouette(name, h):
    """Polygons (in metres, x centred on 0) for a record-holder of height h."""
    n = name
    if n == "Great Pyramid of Giza":
        return [[(-115, 0), (0, h), (115, 0)]]
    if n == "Washington Monument":
        return stack([(0, 152, 8.4, 5.3), (152, h, 5.3, .3)])
    if n == "Eiffel Tower":
        legs = [[(-62, 0), (-40, 0), (-27, 57), (-47, 57)], [(62, 0), (40, 0), (27, 57), (47, 57)]]
        return legs + [rect(-50, 50, 55, 61)] + [[(-40, 61), (-17, 115), (-5, 272), (-1.6, h), (1.6, h), (5, 272), (17, 115), (40, 61)]] + [rect(-21, 21, 113, 118)]
    if n == "Old St Paul's Cathedral":
        return church(h, 22, 30, 9, 75, 8)
    if n == "Lincoln Cathedral" or n == "Lincoln Cathedral and the churches":
        return [[(-24, 0), (-24, 26), (-10, 26), (-10, 83), (-7.5, 83), (0, h), (7.5, 83), (10, 83), (10, 26), (24, 26), (24, 0)]]
    if n == "St. Mary's Church":
        return church(h, 18, 32, 11, 100, 9)
    if n == "St. Pierre's Cathedral":
        return church(h, 26, 48, 10, 100, 8)
    if n == "Cathedral of Our Lady of Strasbourg":
        return [[(-24, 0), (-24, 66), (-4, 66), (-4, 100), (-6, 100), (-1, h), (2, 100), (3, 100), (3, 66), (12, 66), (12, 70), (24, 70), (24, 0)]]
    if n == "Church of St. Nicholas":
        return church(h, 17, 28, 9, 82, 8)
    if n == "Rouen Cathedral":
        return [[(-24, 0), (-24, 40), (-9, 40), (-9, 80), (-6, 80), (0, h), (6, 80), (9, 80), (9, 40), (24, 40), (24, 0)]]
    if n == "Cologne Cathedral":
        out = [rect(-30, 30, 0, 45)]
        for c in (-16, 16):
            out.append([(c - 9, 45), (c - 9, 100), (c - 7, 100), (c, h), (c + 7, 100), (c + 9, 100), (c + 9, 45)])
        return out
    if n == "Ulm Minster":
        return church(h, 21, 40, 9.5, 100, 7.5)
    if n == "Philadelphia City Hall":
        return [rect(-55, 55, 0, 36)] + stack([(36, 110, 13, 13), (110, 142, 9.5, 9.5), (142, 158, 9.5, 3), (158, h, 1.4, .8)])
    if n == "Singer Building":
        return [rect(-24, 24, 0, 45)] + stack([(45, 160, 10.5, 10.5), (160, 182, 10.5, 3.5), (182, h, 1.2, .5)])
    if n == "Metropolitan Life Tower":
        return [rect(-30, 30, 0, 42)] + stack([(42, 188, 12.5, 12.5), (188, 207, 12.5, 2), (207, h, 1, .4)])
    if n == "Woolworth Building":
        return [rect(-38, 38, 0, 100)] + stack([(100, 180, 15, 15), (180, 205, 11.5, 11.5), (205, 222, 8.5, 8.5), (222, h, 8.5, 1)])
    if n == "40 Wall Street":
        return [rect(-36, 36, 0, 120)] + stack([(120, 232, 20, 20), (232, 266, 14, 3), (266, h, 1.2, .4)])
    if n == "Chrysler Building":
        return [rect(-34, 34, 0, 70)] + stack([(70, 242, 18, 18), (242, 252, 13.5, 13.5), (252, 262, 11, 11), (262, 272, 8.5, 8.5), (272, 282, 6, 6), (282, h, 2.2, .3)])
    if n == "Empire State Building":
        return [rect(-50, 50, 0, 25), rect(-35, 35, 25, 82)] + stack([(82, 320, 25, 25), (320, 338, 15, 15), (338, 350, 9, 7), (350, h, 3.5, .6)])
    if n == "1 World Trade Center":
        return [rect(-32, 32, 0, h)]
    if n == "Sears Tower":
        return [rect(-34, 34, 0, 205), rect(-34, 11, 205, 272), rect(-11, 34, 205, 336), rect(-11, 11, 272, h)]
    if n == "Petronas Towers":
        out = [rect(-26, 26, 168, 176)]
        for c in (-45, 45):
            out += [[(x + c, y) for x, y in p] for p in stack([(0, 300, 22, 22), (300, 345, 18, 18), (345, 375, 13.5, 13.5), (375, 397, 9, 9), (397, h, 2.2, .3)])]
        return out
    if n == "Taipei 101":
        out = stack([(0, 100, 33, 27)])
        for k in range(8):
            y0 = 100 + k * 39
            out += [[(-21, y0), (-28.5, y0 + 39), (28.5, y0 + 39), (21, y0)]]
        out += stack([(412, 448, 14, 9), (448, h, 2.6, .3)])
        return out
    if n == "Burj Khalifa":
        return stack([(0, 160, 74, 70), (160, 262, 60, 58), (262, 362, 49, 47), (362, 452, 39, 37), (452, 532, 29, 27), (532, 590, 21, 19), (590, 640, 12, 9), (640, h, 6, .4)])
    if n == "Jeddah Tower":
        return [[(-62, 0), (-34, 400), (-14, 760), (-6, 880), (-1, h), (1, h), (6, 880), (14, 760), (34, 400), (62, 0)]]
    raise KeyError(n)


def holder_col(h):
    return CITY_COL.get(h["city"], "#888888")


LONGNAME = {"Cathedral of Our Lady of Strasbourg": "Strasbourg Cathedral", "Church of St. Nicholas": "St Nicholas, Hamburg", "St. Mary's Church": "St Mary's, Stralsund",
            "St. Pierre's Cathedral": "Beauvais Cathedral", "Old St Paul's Cathedral": "Old St Paul's", "Philadelphia City Hall": "Philadelphia City Hall",
            "Metropolitan Life Tower": "Metropolitan Life", "1 World Trade Center": "World Trade Center", "Great Pyramid of Giza": "Great Pyramid"}


def lineup_items():
    """Record-holders in order of first year: buildings (filled), structures that were not buildings (hatched), and
    Jeddah Tower (planned, dashed). Stralsund's St Mary's held the title twice and is drawn once."""
    S = jload(f"{DATA}/site.json")
    out, seen = [], set()
    for h in S["hb"]:
        if h["name"] in seen:
            continue
        seen.add(h["name"]); out.append(dict(h, mode="b"))
    for h in S["hs"]:
        if h["name"] in ("Great Pyramid of Giza", "Washington Monument", "Eiffel Tower"):
            out.append(dict(h, mode="s"))
    key = lambda h: (h["from"] if h["from"] is not None else 1300) + (0.5 if h["mode"] == "s" else 0)
    out.sort(key=key)
    R = jload(f"{DATA}/results.json")
    out.append({"name": "Jeddah Tower", "city": "Jeddah", "country": "Saudi Arabia", "h": R["uc"]["jeddah_h"], "from": R["uc"]["jeddah_planned"],
                "mode": "p", "from_txt": f"planned {R['uc']['jeddah_planned']}", "years": None})
    return out


def draw_lineup(ax, items, gap=14, lw=.8, label=True, fs=9.5, yfs=9, ink=FG, mut=MUT, paper=BG, show_years=True):
    x = 0; pos = []
    for it in items:
        polys = silhouette(it["name"], it["h"])
        xs = [p[0] for poly in polys for p in poly]
        w0, w1 = min(xs), max(xs)
        cx = x - w0
        col = "#C9C2B6" if it["mode"] == "p" else (holder_col(it))
        for poly in polys:
            P = [(cx + px, py) for px, py in poly]
            if it["mode"] == "b":
                ax.add_patch(MPoly(P, closed=True, fc=col, ec=paper, lw=lw * .5, zorder=3))
            elif it["mode"] == "s":
                ax.add_patch(MPoly(P, closed=True, fc=paper, ec=col, lw=lw * 1.6, hatch="////", zorder=3))
            else:
                ax.add_patch(MPoly(P, closed=True, fc="none", ec="#8A8278", lw=lw * 1.4, ls=(0, (3, 2)), zorder=3))
        pos.append((cx, it))
        x = cx + w1 + gap
    ax.set_xlim(-gap, x)
    return pos, x
