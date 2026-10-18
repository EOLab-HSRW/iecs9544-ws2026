# geo0242 Georeferencing an excavation plan: Lehner 1930, Vetera I

**Tool:** QGIS Georeferencer · **Time:** about 3 h at home · **Builds on:** geo0241 (your georeferenced TK25 1998 and your polygon) · **Slides:** `geo0240_Georeferencing_Castra_Vetera.pdf`

Between 1905 and 1929 the Bonn Provinzialmuseum excavated the legionary fortress *Vetera I* on the Fürstenberg. Hans Lehner published the results in 1930. Plate I (*Tafel I*) shows the excavated buildings and the fortress wall within the fields, roads and railways of that time. The plate has a scale bar and a north arrow, but **no coordinate grid**. You georeference it with control points (GCPs) on features that still exist today, digitise the fortress and check where it really lies – also against a map that is widely used on the web.

## Files
| File | Use |
|---|---|
| Lehner 1930, *Tafel I* | download it yourself from the Heidelberg University Library: https://digi.ub.uni-heidelberg.de/diglit/lehner1930/0083 (*Download* → image, the largest size offered). Save it as `data/lehner1930_Tafel_I.jpg`. Plates III/IV (detailed plan) are optional. |
| `geo0241_Georeferencing_Castra_Vetera.qgz` | reference project from geo0241: DTK (WMS), DTM hillshade, orthophotos, OpenStreetMap |
| your results of geo0241 | georeferenced TK25 1998 and `castra_vetera.gpkg` |
| historical map (WMS) | TK25 1936–1945, Geobasis NRW: `https://www.wms.nrw.de/geobasis/wms_nw_tk25_1936-1945`, layer `nw_tk25_1936-1945` |
| map to check | Wikimedia Commons, *Vetera.png*: https://commons.wikimedia.org/wiki/File:Vetera.png |

The plate is protected by copyright: use it for this exercise only, do not upload or share it.

## Task
1. **Read the plate.** What does it show, and what not? Measure the scale bar (0–200 m) in pixels and compute the scale of the image in m/px. Which features (roads, railways, buildings, field boundaries, slopes) do you expect to have survived for 100 years, which not?
2. **Find identical points.** Look for at least **6** features that you find both on the plate and in today's DTK, spread over the whole plate. Road names have changed: use your georeferenced TK25 1998 and the TK25 1936–1945 (WMS) as a bridge between Lehner's map and today. Good GCPs are road crossings, level crossings and long-lived structures; avoid field boundaries and single buildings. Make a table: *number – feature on the plate (old name) – feature today*.
3. **Georeference the plate** (*Layer → Georeferencer…*, target CRS **EPSG:25832**). Set the GCPs in today's DTK (WMS `wms_nw_dtk`); zoom in until the large-scale map (ABK) appears, but not beyond about 1:2 000. Compare *Helmert* and *Polynomial 1*: RMS error and residuals. Then switch each GCP off once and note how far it lies from the transformed position (check error). Why would *Polynomial 2* or *Thin Plate Spline* be a poor choice here? Save the GCPs (*Save GCP Points as…*, `.points`).
4. **Check the scale:** which scale (m/px) and rotation does your transformation imply? Compare with the scale bar and the north arrow (task 1). What could explain a difference between x and y?
5. **Digitise the fortress:** draw the fortress wall as shown by Lehner as a polygon in the layer `vetera_lehner` of your `castra_vetera.gpkg`. Area in hectares (`$area / 10000`)?
6. **Compare and judge:**
   - your polygon from geo0241 (TK25 1998, *KD*) and the reconstruction by Dießenbacher;
   - the railway: does today's line cut through the fortress? Where, and over what length?
   - the map *Vetera.png*: where does it place Vetera I? Estimate the offset in metres and direction. Is the difference larger than your own error?
7. **Sources of error:** list the error sources of your result (plate, paper, changed roads, reference map, your clicks) and estimate their size.

## Hand in
Report (max. 2 pages):
- the GCP table (task 2) with the residual of each point;
- a table *transformation – number of GCPs – RMS – mean check error* (metres) and your choice with a reason;
- a map (layout) with the georeferenced plate, today's DTK, the railway and your polygons from geo0241 and geo0242;
- answers to 1, 4, 6 and 7 in a few sentences each.

Deadline and channel: see the course plan.

## Sources
- H. Lehner, *Vetera. Die Ergebnisse der Ausgrabungen des Bonner Provinzialmuseums bis 1929*. Römisch-Germanische Forschungen 4 (Berlin/Leipzig 1930), Tafel I. https://doi.org/10.11588/diglit.42466
- Geobasis NRW, WMS DTK and TK25 1936–1945, Datenlizenz Deutschland – Zero – Version 2.0.
- QGIS user manual, Georeferencer: https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/georeferencer.html
