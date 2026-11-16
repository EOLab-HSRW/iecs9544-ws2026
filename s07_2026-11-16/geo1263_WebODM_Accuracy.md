# geo1263 How good is our drone map? Accuracy against RTK points and the NRW terrain model

**Tool:** Jupyter notebook `geo1263_WebODM_Accuracy.ipynb` (+ QGIS for a stretch task) · **Time:** about 2–2.5 h · **Builds on:** slides `geo1260_Drone_Imagery_WebODM` (parts *Control* and *Results*), the field day (RTK points, flight) · **Data:** field data of the drone day: on the JupyterHub in the shared folder `~/shared/data/opengeo/geo1260/`, for laptops on Moodle (save the folder `gfl_…` into `data/` next to the notebook)

On the field day the drone flew one mapping mission with RTK corrections from SAPOS, and WebODM computed an orthophoto and a surface model (DSM) **without ground control points**. On the ground, 31 points were measured with RTK: 21 permanent markers (`P1`–`P21`) and 10 student panels. None of them was used in the processing, so all of them are check points. You test the drone result against these points and against the official terrain model DGM1 of Geobasis NRW, and decide whether ground control points would have been worth the effort.

## Files
| File | Content |
|---|---|
| `geo1263_WebODM_Accuracy.ipynb` | the workbook: read the text cells, fill in the cells marked `# YOUR CODE HERE` |
| `geo1263_ODM_Tools.py` | given tools (imported as `ot`): read the points, height transformation (quasigeoid GCG2016), sample a DSM or a coarse grid, download NRW tiles, statistics, checks. Keep it next to the notebook |

Your results go into `geo1263_out/` next to the notebook.

## Tasks
1. **RTK points (§1):** read the points, check their quality (FIX, RMS), look at them on the orthophoto.
2. **CRS (§2):** which EPSG code do the drone products report, which is right, and why reprojecting is not the fix.
3. **Heights (§3):** ellipsoidal height *h* and DHHN2016 height *H*; the quasigeoid at our site.
4. **DSM vs RTK (§4):** height error of the DSM at all 31 points; statistics per point set and per surface; read the pattern.
5. **DGM1 (§5):** RTK and DSM against the official terrain model; surface model vs terrain model.
6. **A suspicious point (§6):** one point is 1.8 m higher than the others. Error or not? Profiles through DSM and DGM1.
7. **GCPs worth it? (§7):** questions on cost and benefit, number of check points, next year's layout.
8. **Stretch:** horizontal check in QGIS; a WebODM task with GCPs; drone DSM vs DOM1.

## Hints
- Errors are always **map − reference**.
- Compare heights in **one system**: DSM and RTK points are ellipsoidal, DGM1/DOM1 are DHHN2016 (difference about 45 m).
- Read the **pattern** before you trust a number: a table per point set can hide a difference between surfaces.
- Never delete a suspicious point without checking it against independent data.

## Hand in
Upload the notebook (with outputs) and `geo1263_out/geo1263_dz_surface.png` to Moodle.

## Sources
- RTK points, orthophoto and DSM: own field data (EOLab-HSRW, course use only).
- DGM1, DOM1: Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (opengeodata.nrw.de).
- Quasigeoid GCG2016: BKG, PROJ grid `de_bkg_gcg2016.tif` (cdn.proj.org, CC BY 4.0).
- OpenDroneMap and WebODM documentation (docs.opendronemap.org, docs.webodm.org).
- ASPRS Positional Accuracy Standards for Digital Geospatial Data, Edition 2 (2023, Version 2 2024).
- EPSG registry (epsg.org): EPSG:25832, EPSG:32632, EPSG:7837; Wikipedia: *Digital elevation model*, *Root-mean-square deviation*.
