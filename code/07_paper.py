"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png beside them). The DOI stays a placeholder (10.5281/zenodo.23857608)."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_The_Worlds_Tallest_Building"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
rc, L, WD, UC = R["records"], R["list350"], R["wd"], R["uc"]

# statements made in words in the paper only
assert rc["countries"][0]["country"] == "United Kingdom" and rc["countries"][1]["country"] == "France" and rc["countries"][2]["country"] == "Germany"
assert WD["asia_share_us"]["2010"] > 60 and WD["asia_share"]["2010"] > WD["asia_share"]["2000"]
assert "2004 to 2009" in jload(f"{WORK}/wiki.json")["phrases"]["taipei09"]
assert SITE["hb"][5]["from"] == 1647 and SITE["hb"][5]["to"] == 1874


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Sources, what was used and licences.}\\label{tab:sources}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.6cm}>{\\raggedright\\arraybackslash}p{7.2cm}>{\\raggedright\\arraybackslash}p{2.6cm}}\\toprule Source & Used for & Licence\\\\\\midrule\n"
      f"Wikipedia, History of the world's tallest buildings & {rc['n_rows']} record-holder rows; definitions; structures in the text & CC BY-SA 4.0\\\\\n"
      f"Wikipedia, List of tallest buildings & {L['n']} buildings of 350 m or more; {UC['n']} under construction & CC BY-SA 4.0\\\\\n"
      f"Wikidata & {WD['n_items']:,} structures of height 100 or more; {WD['n_counted']:,} buildings kept & CC0\\\\\n"
      "CORGIS skyscrapers & Unit check for United States heights only & GPL-3.0 (not redistributed)\\\\\n"
      "Natural Earth & Countries, regions, city names & Public domain\\\\\n\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for h in SITE["hb"]:
    rows += f"{tex(h['from_txt'])} to {tex(h['to_txt'])} & {tex(h['name'])} & {tex(h['city'])} & {h['h']:g} & {'' if h['years'] is None else h['years']}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Holders of the title of world's tallest building (Wikipedia's tables; churches count as buildings). Years to " + str(NOW) + " for the Burj Khalifa.}\\label{tab:records}"
      "\\setlength{\\tabcolsep}{4pt}\\begin{tabular}{l>{\\raggedright\\arraybackslash}p{5.2cm}>{\\raggedright\\arraybackslash}p{2.6cm}rr}\\toprule Years & Building & City & Height (m) & Years held\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex('New York' if c['city'] == 'New York City' else c['city'])} & {tex(c['country'])} & {c['years']} & {tex('; '.join(c['holders']))}\\\\\n" for c in rc["cities"] if c["years"] is not None)
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Years as home of the world's tallest building, 1311 to " + str(NOW) + ", by city.}\\label{tab:cities}"
      "\\begin{tabular}{llr>{\\raggedright\\arraybackslash}p{6.4cm}}\\toprule City & Country & Years & Buildings\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(c['city'])} & {tex(c['country'])} & {c['n']} & {c['n350']} & {tex(c['tallest'])} ({c['tallest_h']:g} m)\\\\\n" for c in WD["cities"][:15])
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{The fifteen cities with the most buildings of 200 m or more in Wikidata after unit checks, with how many are 350 m or more (complete list) and the tallest.}\\label{tab:top}"
      "\\begin{tabular}{llrr>{\\raggedright\\arraybackslash}p{5.6cm}}\\toprule City & Country & 200 m+ & 350 m+ & Tallest\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(u['name'])} & {tex(u['city'])}, {tex(u['country'])} & {u['h']:g} & {tex(u['planned'] or 'not given')}\\\\\n" for u in SITE["uc"][:12])
TU = ("\\begin{table}[tbp]\\centering\\small\\caption{The twelve tallest buildings under construction on Wikipedia's list, with planned architectural height and planned completion as the page gives them.}\\label{tab:uc}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{5.2cm}>{\\raggedright\\arraybackslash}p{4.6cm}rr}\\toprule Building & City & Height (m) & Completion\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = t.replace("{{meta.doi}}", "@@DOI@@")
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("SOURCES", TS), ("RECORDS", TR), ("CITIES", TC), ("TOP", TT), ("UC", TU)):
    t = t.replace("{{TABLE_%s}}" % k, v)
assert "{{" not in t and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:3]
t = t.replace("\\href{https://doi.org/@@DOI@@}{https://doi.org/@@DOI@@}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/@@DOI@@}", "https://doi.org/\\{\\{DOI\\}\\}")
assert "@@" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
