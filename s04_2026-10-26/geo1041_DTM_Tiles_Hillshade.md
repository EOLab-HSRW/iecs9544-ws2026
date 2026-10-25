# geo1041 Terrain tiles in QGIS: virtual raster, hillshade, profile

**Tool:** QGIS (raster tools, Elevation Profile) · **Time:** demo 40 min + exercise 20 min · **Slides:** `geo1040_DTM_Processing_Tiles.pdf` · **Data:** the zip `dgm1_uedemer_hochwald.zip` from notebook geo0442 (§6.2)

The NRW terrain model DGM1 comes in tiles of 1 km × 1 km. You combine six tiles of the *Uedemer Hochwald* (a forest between Marienbaum and Uedem) into one seamless layer without copying any data, make the relief visible with a hillshade, and measure heights along a profile. The forest hides a field of prehistoric **burial mounds**, about one metre high: on the orthophoto you see only trees, in the 1 m terrain model you see every mound.

## Files
| File | Use |
|---|---|
| `geo1041_DTM_Tiles_Hillshade.qgz` | start project: ABK basic map (on), DTK, orthophotos, DTM hillshade of Geobasis NRW (WMS, off), OpenStreetMap (off); spatial bookmarks *Uedemer Hochwald (6 tiles)* and *Burial mound field* (*View → Panels → Spatial Bookmarks Manager*) |
| `geo1041_DTM_Tiles_Hillshade_checkpoint.qgz` | catch-up project: the same plus the tile index and the six tiles with a hillshade renderer |
| `../data/dgm1_uedemer_hochwald/` | six DGM1 GeoTIFFs and `dgm1_uedemer_hochwald.gpkg` (tile index of the six tiles), unzipped from the geo0442 zip |

**Before you start:** download `data/derived/geo0442/dgm1_uedemer_hochwald.zip` from your hub folder (right-click → *Download*) and unzip it into the `data/` folder of your course folder on the laptop, so that the GeoTIFFs are in `<course folder>/data/dgm1_uedemer_hochwald/`. The projects find them there (`../data/` seen from this session folder). No hub access? Download the six files from https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_tiff/dgm1_tiff/ (names in the table below).

| Key | File | Survey year |
|---|---|---|
| `dgm1_32_316_5729_1_nw` | `dgm1_32_316_5729_1_nw_2025.tif` | 2025 |
| `dgm1_32_317_5729_1_nw` | `dgm1_32_317_5729_1_nw_2025.tif` | 2025 |
| `dgm1_32_318_5729_1_nw` | `dgm1_32_318_5729_1_nw_2025.tif` | 2025 |
| `dgm1_32_316_5730_1_nw` | `dgm1_32_316_5730_1_nw_2024.tif` | 2024 |
| `dgm1_32_317_5730_1_nw` | `dgm1_32_317_5730_1_nw_2024.tif` | 2024 |
| `dgm1_32_318_5730_1_nw` | `dgm1_32_318_5730_1_nw_2024.tif` | 2024 |

The years are those of the index of October 2026; after a new survey the year in the name changes (geo0442).

Data: DGM1, ABK, DTK, DOP, DTM hillshade: © Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (dl-de/zero-2-0). OpenStreetMap: © OpenStreetMap contributors, ODbL.

## Guided demo
1. **Load the tiles.** Open `geo1041_DTM_Tiles_Hillshade.qgz`. Drag `dgm1_uedemer_hochwald.gpkg` and the six `.tif` files from the *Browser* panel into the map (or *Layer → Add Layer → Add Raster Layer…*, select all six). Label the tile index with `year`.
   *Layer Properties → Information* of one tile: CRS, size in pixels, pixel size, data type, *NoData* value. What do the pixel values mean, in which unit?
2. **Predict:** each tile is drawn with its own grey stretch (min/max of that tile). What do you see at the tile borders? Look, then explain.
3. **One layer from six files: virtual raster.** *Raster → Miscellaneous → Build Virtual Raster…*: input the six tiles, keep *Place each input file into a separate band* **off**, save as `../data/dgm1_uedemer_hochwald/dgm1_uedemer_hochwald.vrt` (in the same folder as the tiles). Remove the six single tiles from the project (*Remove Layer*), keep the VRT.
   A **VRT** (*virtual raster*) is a small XML file that only *points* to the tiles: no pixel is copied. Compare its size with the alternative *Raster → Miscellaneous → Merge…* (one new GeoTIFF; do not run it, estimate: 3000 × 2000 pixels × 4 bytes).
4. **Hillshade as a renderer (display only).** VRT → *Layer Properties → Symbology → Render type: Hillshade*. Try *Z Factor* 1 and 3, *Azimuth* 315° and 135°, *Multidirectional* on/off. Zoom to the bookmark *Burial mound field*. Which settings show the mounds best? Why does the illumination direction change which mounds you see?
5. **Hillshade as a raster file.** *Raster → Analysis → Hillshade…*: input the VRT, *Z factor* 2, *Multidirectional shading* on, save as `../data/dgm1_uedemer_hochwald/hillshade_uedem.tif`. Unlike the renderer, this is a new raster with values 0–255 that you can use in a layout, another program, or the Raster Calculator.
6. **Colour over shade.** Duplicate the VRT (*Duplicate Layer*), *Singleband pseudocolor* (e.g. *Viridis*, min/max from the current canvas), *Blending mode* *Multiply* or opacity 50 %, above the hillshade. Compare with the hillshade of Geobasis NRW (WMS layer): same data?
7. **Profile.** VRT → *Layer Properties → Elevation*: *Represents Elevation Surface* on. *View → Elevation Profile*, draw a line across three or four mounds (*Capture Curve*), *Tolerance* small. Read the height of a mound above its surroundings and its diameter. Compare with the height differences of the whole forest.
8. **Save** the project in your session folder (*Project → Save As…*, `uedem.qgz`).

## Exercise (pairs)
Explore the six tiles with the hillshade (renderer or file) and the DTK/ABK and answer briefly:
1. **Mound field:** where is it (bookmark), how large is it (*Measure Area*), roughly how many mounds? Which map (ABK, DTK, OSM) marks the field, and how?
2. **The steep edge in the east:** how high is it (profile)? What has cut the narrow valleys into it? The ridge is part of the Lower Rhine hills, pushed up by the ice sheet of the Saale glaciation.
3. **Round pits:** in the north-east part of the forest you find small round *depressions*, some with a rim. Positive or negative features, how deep, how large? What could they be? Compare with the mounds.
4. **Tile seam:** the northern row of tiles was surveyed in 2024, the southern row in 2025. Can you see the border at N 5 730 000 in the hillshade? What would a step there mean?

## Check yourself
- Why does a VRT not need more disk space, and when would you still use *Merge*?
- A hillshade is not a height: what does a grey value of a hillshade mean? Why can you not compute a slope or a height difference from it?
- The mounds are 1 m high, the forest floor varies by more than 30 m. Why are they visible in the hillshade but not in the pseudocolour layer?
- Which illumination direction would hide a ditch running from north-west to south-east?

## Tutorials
- QGIS user manual, raster properties (hillshade renderer, elevation): https://docs.qgis.org/latest/en/docs/user_manual/working_with_raster/raster_properties.html
- QGIS user manual, Elevation Profile: https://docs.qgis.org/latest/en/docs/user_manual/map_views/elevation_profile.html
- GDAL `gdalbuildvrt`: https://gdal.org/programs/gdalbuildvrt.html
