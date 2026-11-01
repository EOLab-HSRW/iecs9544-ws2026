# geo1261 Mission plan for the Green Fab Lab (homework)

**Tool:** Jupyter notebook `geo1261_Mission_Plan.ipynb` · **Time:** about 2 h (+ 1 h stretch) · **Builds on:** slides `geo1260_Drone_Imagery_WebODM` (parts *Photos* and *Plan*) · **Data:** `data/geo1261/gfl_flight_area.gpkg`

The drone flight at the Green Fab Lab is planned in the flight app (DJI Pilot 2). The app computes everything for you – and you should know what it computes. In this homework you plan the flight of the DJI Mavic 3M (RGB and multispectral camera together) yourself: pixel size, footprint, line and photo spacing, speed and flight time. You estimate the plan by hand first; the flight lines over the real area are drawn by given tools. In the field you compare your numbers with the app's.

## Files
| File | Content |
|---|---|
| `geo1261_Mission_Plan.ipynb` | the workbook: read the text cells, fill in the cells marked `# YOUR CODE HERE` |
| `geo1261_Mission_Tools.py` | given tools (imported as `mt`): reference functions, flight lines, photo positions, checks for your answers. Keep it next to the notebook |
| `data/geo1261/gfl_flight_area.gpkg` | layer `flight_area`: the area we may fly over (land use "Bildung und Wissenschaft" around the Green Fab Lab; west and south of the building and above it); layer `building`. EPSG:25832 |

## Tasks
1. **Camera (§1):** derive the ground sampling distance (GSD) of both cameras from the field of view and the image size; `mt.check_gsd` tells you if it is right.
2. **Footprint, spacing and speed (§2):** turn height and overlap into footprint, line spacing, photo spacing and speed; decide which camera sets which value (`mt.check_plan_numbers`).
3. **Estimate (§3):** estimate lines, photos, path and flight time by hand on the rectangle around the area – before you run §4.
4. **Plan, map and export (§4–5):** run the given cells: flight lines over the real area, comparison with your estimate, map; the plan is saved as `geo1261_plan.gpkg` (open it in QGIS) and the area as `gfl_flight_area.kml` for the flight app.
5. **Heights (§6):** make a table for 25, 30, 40 and 60 m, all cameras and RGB only, with `mt.mission`; answer the questions.
6. **Stretch (§7):** write the flight lines yourself with Shapely and compare them with `mt.flight_lines`.

## Hints
- `np.tan` wants radians. The RGB field of view is given for the **diagonal**, the multispectral one for the width.
- At 100 m the RGB pixel is about 2.7 cm: check your `gsd` with that.
- GSD = one pixel on the ground; footprint = the whole photo on the ground (GSD × number of pixels).
- From §3 on the notebook uses the reference functions in `mt`, so a mistake in §1–2 does not stop you.
- Stretch: if a flight line comes out as a `MultiLineString`, the line crosses a concave part of the area: keep the longest piece.
- The plan is a model: the app adds margins and turns of its own. The comparison is part of the task.

## In the field
Write down the numbers DJI Pilot 2 shows for the same height and overlap (line spacing, number of photos, flight time) and bring them to the session after the flights.

## Hand in
Upload the notebook (with outputs) and a screenshot of your plan in QGIS to Moodle before the next session.

## Sources
- Flight area and building: ALKIS (simplified WFS), Bezirksregierung Köln, Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0, extracted 2026-10-24.
- Camera: DJI Mavic 3M specifications, ag.dji.com/mavic-3-m/specs.
- Overlap: OpenDroneMap documentation, *Flying tips*, docs.opendronemap.org/flying.
- Wikipedia: *Ground sample distance*, *Photogrammetry*.
