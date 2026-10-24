# geo0265 Height benchmarks in NRW: from CSV to GeoPackage

**Tool:** Jupyter notebook `geo0265_Height_Benchmarks_NRW.ipynb` · **Time:** about 90 min for §1–§6, 30 min more for the stretch task §7 · **Builds on:** slides `geo0220_CRS_Projections` (EPSG codes, UTM) and `geo0260_GNSS` (*SAPOS*, *Heights: from GNSS to NHN*) · **Data:** downloaded by the notebook from opengeodata.nrw.de

Geobasis NRW publishes the official height benchmarks (*Höhenfestpunkte*, HFP) of North Rhine-Westphalia as a CSV file: about 88 000 bolts with a levelled height above NHN. The file has an east and a north coordinate, but it does not say in which coordinate reference system. You find out, check your answer against the metadata, save the benchmarks as a GeoPackage and look for the benchmarks next to the Green Fab Lab, where we measure with RTK.

## Files
| File | Content |
|---|---|
| `geo0265_Height_Benchmarks_NRW.ipynb` | the workbook: read the text cells, fill in the cells marked `# YOUR CODE HERE` |
| `data/original/geo0265/` | created by the notebook: `hfp_pl.csv`, `hfp_plzf.csv` (time series), the format description and the user information (PDF) |
| `data/derived/geo0265/hfp_nrw.gpkg` | your result: layer `hfp_points`, EPSG:25832 |

## Tasks
1. **Look before you read (§2):** list the properties of the file (encoding, separators, header, quoting) and compare them with the format description.
2. **Read (§3):** read the CSV with pandas, point IDs as text, and check what you read.
3. **Which EPSG? (§4):** decide from the numbers, test the candidates, and compare with the metadata record and the format description. Find the statement in the format description that cannot be right.
4. **GeoPackage (§5):** build a GeoDataFrame, transform it to EPSG:25832 and save it. Open it in QGIS.
5. **Near the Green Fab Lab (§6):** list and map the benchmarks within 2 km of the Green Fab Lab and the campus Kamp-Lintfort.
6. **Stretch, time series (§7):** plot how the benchmarks near the Green Fab Lab moved since the 1960s.
7. **Wrap-up (§8):** answer the three questions in a few sentences.

## Hints
- A wrong CRS rarely raises an error. It moves your points somewhere else, or to infinity (`inf`).
- Count the digits of the east coordinate. A UTM easting has six digits before the decimal point.
- Metadata can be wrong. Trust the numbers, then check which description agrees with them.

Data: Höhenfestpunkte NRW © Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (dl-de/zero-2-0).
