# The world's tallest building

Who held the title of world's tallest building, for how long, and where today's tall buildings are: every record-holder from the Great Pyramid of Giza and Lincoln Cathedral to the Burj Khalifa, from English Wikipedia's history of the record, with Wikipedia's list of the 98 buildings of 350 m or more and 1,343 buildings of 100 m or more from Wikidata after unit checks. Includes Jeddah Tower, which Wikipedia lists as under construction.

Interactive page: https://maps.tristanhotham.com/tallest-buildings/
Paper: https://doi.org/10.5281/zenodo.23857608
Blog post: https://blog.tristanhotham.com/2026/10/31/tallest-buildings/

## Headline results

- Since the 13th century the record has been held in 15 cities (churches count as buildings, as in the source). Lincoln Cathedral held it longest: 238 years, 1311 to 1549, at 159.7 m. Strasbourg held it 227 years and Stralsund 94. Churches held it for 583 of the 715 years since 1311 (82%).
- New York held it for 65 years (1908 to 1973), Chicago 25, the United States 104 (1894 to 1998). Since 1998 it has been in Asia: Kuala Lumpur, Taipei and, since 2010, Dubai (828 m, 62% taller than Taipei 101, the biggest jump in the record).
- The Great Pyramid (146.5 m) was the tallest structure for about 3,870 years; it, the Washington Monument and the Eiffel Tower held the record for structures but were never buildings.
- 81 of the 98 buildings of 350 m or more (83%) are in Asia and 82 were finished in 2010 or later. Dubai has the most (15), then Shenzhen (12) and New York (9).
- Among 464 checked buildings of 200 m or more in Wikidata, Asia's share of completions rose from 27% in the 1980s to 75% in the 2010s (212 buildings, the peak decade).
- Jeddah Tower is under construction at a planned 1,008 m, completion planned for 2028 (Wikipedia, List of tallest buildings).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/record_holders.csv` | Every holder of the title, for buildings (Wikipedia's tables) and structures (its text): years, years held, city, country, height, position. |
| `data/city_tenure.csv` | Years each city was home of the world's tallest building. |
| `data/tallest_350m_list.csv` | The 98 buildings of 350 m or more on Wikipedia's list, with region and position. |
| `data/under_construction.csv` | The 46 buildings of 350 m or more under construction on the list, with planned height and completion. |
| `data/tall_buildings.csv` | 1,681 Wikidata buildings of 100 m or more after cleaning, with height, year and its source, city, country, region and the height check (only rows with `counted` true are used in the counts) (0.3 MB). |
| `data/decade_region.csv` | Buildings finished per decade and region: 200 m or more (Wikidata) and 350 m or more (list). |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/points.json`, `data/world.json`, `data/cities.json` | Page data (Natural Earth outlines and place names). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source, blog post and figures, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Definitions: the history of the record counts churches and cathedrals as buildings and measures to the architectural top (spires, not antennas), following the CTBUH; the list of today's tallest counts enclosed buildings with occupiable floors of 350 m or more. Structures that were not buildings (the pyramid, the Washington Monument, the Eiffel Tower, masts) are kept on a separate track.
- Years held run from one record to the next; the Burj Khalifa's run to 2026. London (13th century to 1311) is left out of the totals. The pyramid's date (2560 BC) is Wikidata's.
- Wikidata heights came without units. Kept: buildings only; nothing taller than 830 m; every building of 350 m or more must be on Wikipedia's list (which supplies its height and year); United States heights under 350 m only if the CORGIS skyscrapers dataset (from the CTBUH Skyscraper Center, to 2016) agrees within 8%; 4 plain feet values removed by hand; churches, mosques and temples left off the map because Wikidata dates them by founding.
- Cities: the largest Natural Earth place within 40 km. Regions: Natural Earth subregions; Asia includes the Middle East.
- Caveats: Wikidata is a record, not a census, and is patchy for China; some heights outside the United States will still be feet; unchecked American records are left out, which lowers North America's share; inception years are sometimes construction starts; Wikipedia's medieval heights are disputed and its pages disagree in places (noted in the paper).

## How to rerun

Needs Python 3 with pandas, shapely, pyproj, matplotlib, fontTools, BeautifulSoup and Pillow, xelatex and pdftotext; node with Playwright for QA. Raw inputs are read in place from `/home/claude/newdata/raw8/tallest/` and `/home/claude/newdata/raw/geo/` (set in `code/common.py`); the CORGIS file is fetched from GitHub into `/dev/shm/tallest/work` (set `TALLTMP` to change), used only as a check.

```
python3 code/01_wiki.py         # parse the two Wikipedia pages
python3 code/02_geo.py          # world outline, regions, place names
python3 code/03_wikidata.py     # clean Wikidata, match the list, place record-holders
python3 code/04_results.py      # results.json, data files, page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/08_readme.py       # README and LICENSE
python3 code/09_release.py      # blog post, Zenodo files, Reddit post
python3 reddit/collage.py       # collage
node code/qa.js                 # screenshots to qa/ (serve the folder on port 9463 first)
```

## Sources and licences

- English Wikipedia, 'History of the world's tallest buildings' (revision 1379678838) and 'List of tallest buildings' (revision 1376498189). CC BY-SA 4.0.
- Wikidata, via QLever. CC0.
- CORGIS skyscrapers dataset (github.com/corgis-edu/corgis, GPL-3.0), derived from the CTBUH Skyscraper Center: a check on units only, not redistributed.
- Natural Earth countries and populated places (public domain). Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) The world's tallest building: who held the record, for how long, and where today's tall buildings are. Zenodo. https://doi.org/10.5281/zenodo.23857608

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
