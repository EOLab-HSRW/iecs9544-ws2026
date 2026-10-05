# geo0241 Georeferencing: Castra Vetera near Xanten

**Session:** 8136 S4 (homework 9544 S2) · **Tool:** QGIS Georeferencer · **Time:** demo 45 min + exercise 45 min

Learn how to georeference a scanned or photographed map, or any image with identifiable features, and how to judge the result. The Roman legionary camp *Vetera I* lay on the Fürstenberg hill near Xanten-Birten; you place a photo of an old topographic map and a reconstruction drawing of the camp into today's coordinates.

## Files
| File | Use |
|---|---|
| `geo0241_Georeferencing_Castra_Vetera.qgz` | reference layers around the Fürstenberg: DTK (WMS), orthophotos (WMS, off), districts, OSM |
| images (Moodle, folder *geo0241*) | `Photo_DTK25_4304_Xanten_1998_Detail_Fuerstenberg.jpg` (photographed DTK25 sheet 4304 Xanten, 1998), `…_Notations.pdf`, `Vetera_I_reconstr.png`, `Vetera_I_topo.png` |

Put the images into `data/` of this session folder.

## Task
1. Open `geo0241_Georeferencing_Castra_Vetera.qgz` (topographic map from WMS; switch on the orthophotos or the DTM hillshade as a second reference).
2. Open the **Georeferencer** (*Layer → Georeferencer*) with `Photo_DTK25_4304_Xanten_1998_Detail_Fuerstenberg.jpg`.
3. Set at least 8 well-distributed ground control points (road crossings, buildings, field corners; *From Map Canvas*), target CRS **EPSG:25832**.
4. Compare *Linear*, *Helmert*, *Polynomial 1* and *Thin Plate Spline*: note the RMS error and inspect the residuals. Which one do you choose and why? Save the GCPs (`.points`).
5. Repeat for the reconstruction drawing `Vetera_I_reconstr.png`.
6. Digitize the outline of the camp Vetera I as a polygon layer in a GeoPackage `castra_vetera.gpkg` (see geo0341 for digitizing).

## Homework (present in S5)
Report (½ page): RMS errors of the transformations you tried, the one you chose and why, a map (layout) with both georeferenced images and your polygon, area of the camp in hectares (`$area / 10000`).

## Tutorials
- https://www.qgistutorials.com/en/docs/georeferencing_basics.html
- https://docs.qgis.org/latest/en/docs/user_manual/working_with_raster/georeferencer.html
