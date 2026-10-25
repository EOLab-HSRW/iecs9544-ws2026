# geo0741 Map algebra on the terrain: a local relief model finds burial mounds

**Tool:** QGIS Raster Calculator, GRASS `r.neighbors`, Polygonize, Zonal statistics · **Time:** demo 30 min + exercise 20 min · **Slides:** `geo0740_Raster_Map_Algebra.pdf`, `geo1040_DTM_Processing_Tiles.pdf` · **Builds on:** geo1041 (virtual raster `dgm1_uedemer_hochwald.vrt`)

A burial mound is about 1 m high, the forest floor around it rises and falls by 30 m. To see the mound you have to take away the large-scale terrain and keep only the small bumps: **local relief = terrain − smoothed terrain**. That is map algebra with a *focal* operation (the smoothing: a moving window) and a *local* one (the difference, cell by cell). Then you turn the bumps into polygons and count them.

## Files
| File | Use |
|---|---|
| your geo1041 project (`uedem.qgz`) or `geo1041_DTM_Tiles_Hillshade_checkpoint.qgz` | the six tiles of the Uedemer Hochwald |
| `../data/dgm1_uedemer_hochwald/dgm1_uedemer_hochwald.vrt` | virtual raster from geo1041 step 3 (if you work with the checkpoint project: build it first) |

Save all new rasters in `../data/dgm1_uedemer_hochwald/` (they are large: 24 MB each), vector results in `uedem.gpkg` in your session folder.

## Guided demo
1. **Focal: smooth the terrain.** *Processing → Toolbox → GRASS → Raster → r.neighbors*: input the VRT, *Neighborhood operation* `average`, *Neighborhood size* `31`, output `dtm_mean31.tif`.
   Each output cell is the mean of the 31 × 31 cells (31 m × 31 m) around it. **Predict:** what happens to a mound of 15 m diameter, what to the 30 m high slope in the east?
   *No GRASS in your QGIS?* *Raster → Projections → Warp (Reproject)…* with *Output file resolution* 15 and *Resampling method* `Average` gives a coarse smoothed terrain (blocky, but it works for the next step).
2. **Local: subtract.** *Raster → Raster Calculator…*:
   ```
   "dgm1_uedemer_hochwald@1" - "dtm_mean31@1"
   ```
   Output `lrm.tif` (local relief model). Style it: *Singleband pseudocolor*, colour ramp *RdBu* inverted (red = above the surroundings), *Min* −0.6, *Max* 0.6, mode *Continuous*. Put the hillshade below it at 50 % opacity.
3. **Look** at the bookmark *Burial mound field* and then at the whole area: what is red, what is blue? Paths, ditches, banks, the mounds, the round pits of geo1041 exercise 3. Why are the edges of the steep slope red and blue stripes?
4. **Local: threshold.** Raster Calculator:
   ```
   "lrm@1" > 0.3
   ```
   Output `mask.tif`: 1 where the ground is more than 30 cm above its surroundings, else 0.
5. **Raster → vector.** *Raster → Conversion → Polygonize (Raster to Vector)…*: input `mask.tif`, field name `DN`, output layer `bumps` in `uedem.gpkg`.
6. **Select plausible mounds.** *Processing → Toolbox → Vector selection → Extract by expression*:
   ```
   "DN" = 1 AND $area >= 40 AND $area <= 600
   ```
   (a round area of 40 m² has a diameter of 7 m, 600 m² of 28 m). Output `candidates` in `uedem.gpkg`. *Show Feature Count*.
7. **Zonal: how high?** *Processing → Toolbox → Raster analysis → Zonal statistics*: input `candidates`, raster `lrm.tif`, statistics *Maximum*, prefix `lrm_`. Open the attribute table, sort by `lrm_max`.

## Exercise (pairs)
1. How many candidates are there in the whole area, and how many inside the burial mound field (*Select by Location* with a rectangle or polygon you digitize around the field)? Why are there so many outside the field? Look at five of them.
2. Typical height (`lrm_max`) and diameter of the candidates in the field? Compare with your profile from geo1041: is `lrm_max` the full height of a mound? Why not?
3. Change the window: `r.neighbors` with size 15 and 61. Which window shows the mounds best? Which features appear or disappear? Rule of thumb: how large must the window be compared with the objects you look for?
4. Map algebra vocabulary: write each step of 1–7 as *local*, *focal*, *zonal* or *global* (Tomlin), and say which steps a tool did that the Raster Calculator cannot do.

## Check yourself
- Why is the local relief model better than the hillshade for *measuring* the mounds, and the hillshade better for *seeing* them?
- The threshold 0.3 m and the area limits are your choices. What happens to the result if you change them? How would you choose them less arbitrarily?
- A local relief model is a *difference* of two rasters. Which conditions must the two rasters fulfil (grid, cell size, CRS, extent) for the Raster Calculator to subtract them cell by cell?

## Tutorials
- QGIS user manual, Raster Calculator: https://docs.qgis.org/latest/en/docs/user_manual/working_with_raster/raster_analysis.html
- GRASS manual, r.neighbors: https://grass.osgeo.org/grass-stable/manuals/r.neighbors.html
- Local relief model in archaeology: Hesse, R. (2010): LiDAR-derived Local Relief Models – a new tool for archaeological prospection. *Archaeological Prospection* 17, 67–72, https://doi.org/10.1002/arp.374
