# geo0241 Georeferencing: Castra Vetera near Xanten

**Tool:** QGIS Georeferencer (code optional) · **Time:** demo 45 min + exercise 45 min, report at home · **Slides:** `geo0240_Georeferencing_Castra_Vetera.pdf` (history, method, case study)

Learn how to georeference a photographed map, or any image with identifiable features, and how to judge the result. The Roman legionary fortress *Vetera I* lay on the Fürstenberg near Xanten-Birten. You place a phone photo of an old topographic map into today's coordinates, mark the location of the fortress that this map still shows, georeference a reconstruction drawing of the fortress and check it against the terrain.

## Files
| File | Use |
|---|---|
| `geo0241_Georeferencing_Castra_Vetera.qgz` | reference project around the Fürstenberg: DTK (WMS), DTM hillshade (WMS, off), orthophotos (WMS, off), OpenStreetMap |
| `geo0241_DTK25_4304_Xanten_1998_Sheet.jpg` | the whole sheet TK25 4304 Xanten (1998) with cover and legend |
| `geo0241_DTK25_4304_Xanten_1998_Geodetic_Basis.jpg`, `…_Publisher.jpg` | cover and legend: map series, publisher, edition, geodetic basis, coordinates |
| `geo0241_DTK25_4304_Xanten_1998_Corner_SW.jpg` | south-west corner of the sheet: the numbers in the map margin |
| `geo0241_DTK25_4304_Xanten_1998_Fuerstenberg.jpg` | detail around the Fürstenberg – **the photo you georeference** |
| `geo0241_DTK25_4304_Fuerstenberg_Notations.pdf` / `.jpg` | the same detail with the UTM grid crossings circled and numbered (row, column) |
| `geo0241_Vetera_I_Reconstruction.png`, `geo0241_Vetera_I_Floor_Plan.jpg` | reconstruction drawing and partial floor plan of Vetera I (© Dr. Frank Dießenbacher) |

The images are not openly licensed: you get them from the course platform (folder *geo0241*), not from the public repository. Put them into `data/` of this session folder.

## Task
1. **Investigate the map** (sheet, cover and legend photos): type of map and scale, publisher, edition and year, geodetic datum and projection of the map content. Which coordinate grids are printed, and in which CRS?
2. **Read the map margin** (`…_Corner_SW.jpg`): which lines belong to the UTM grid? What do the numbers mean, including the small raised digits? What is the interval between two grid lines, in km and in cm on the map?
3. **Georeference the map photo** (*Layer → Georeferencer…*, target CRS **EPSG:25832**). Use the UTM grid crossings as control points (GCPs). The circles in the Notations file number them (row, column), so everybody talks about the same points. Determine (E, N) of each crossing in metres from the margin numbers. Use at least 12 crossings spread over the whole photo (all 30 are better).
4. Compare *Helmert*, *Polynomial 1*, *Projective* and *Polynomial 2*: note the RMS error, look at the residuals, and switch 3–5 GCPs off as check points. Which transformation do you choose and why? Save the GCPs (*Save GCP Points As…*, `.points`).
5. **Mark the location of Castra Vetera:** the 1998 map shows its approximate location (label and *KD*, cultural monument). Digitise this area as a polygon in a GeoPackage `castra_vetera.gpkg` (EPSG:25832). Compare with today's DTK (WMS) at 1:25 000 and zoomed in: what is still shown today?
6. **Read the DTM hillshade:** switch on *DTM hillshade (NRW, WMS)*. Which pronounced features does it show around your polygon? Describe them. Which of them do you find on the 1998 map, which on today's DTK?
7. **Georeference the reconstruction drawing.** It has no grid: take GCPs from features you can identify both in the drawing and in your georeferenced map or the hillshade. Choose a suitable transformation for a drawing with few GCPs.
8. **Interpret the reconstruction:** overlay it with the hillshade and the DTK. How does it imagine the surroundings of the fortress? Find inconsistencies between the reconstruction and the terrain, and give possible reasons.

**Optional (code):** compute the RMS of Polynomial 1 for your `.points` file with numpy (slide "Georeferencing step by step"), or warp the photo with `gdal_translate -gcp …` and `gdalwarp`.

## Hand in
Report (max. 2 pages):
- answers to 1, 2, 6 and 8 in a few sentences each;
- a table *transformation – number of GCPs – RMS – check error* (metres) and your choice with a reason;
- a map (layout) with the georeferenced map, the reconstruction, your polygon and the hillshade;
- the area of your polygon in hectares (`$area / 10000`), compared with the fortress itself (about 56 ha inside the wall).

Deadline and channel: see the course plan.

## Tutorials
- QGIS user manual, Georeferencer: https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/georeferencer.html
- QGIS Tutorials and Tips, georeferencing basics: https://www.qgistutorials.com/en/docs/georeferencing_basics.html
