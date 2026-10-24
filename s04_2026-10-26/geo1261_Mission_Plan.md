# geo1261 Mission plan for the Green Fab Lab (homework)

**Tool:** Jupyter notebook `geo1261_Mission_Plan.ipynb` · **Time:** about 2–3 h · **Builds on:** slides `geo1260_Drone_Imagery_WebODM` (parts *Photos* and *Plan*) · **Data:** `data/geo1261/gfl_flight_area.gpkg`

The drone flight at the Green Fab Lab is planned in the flight app (DJI Pilot 2). The app computes everything for you – and you should know what it computes. In this homework you plan the flight of the DJI Mavic 3M (RGB and multispectral camera together) yourself: pixel size, flight lines, photo positions, speed and flight time. In the field you compare your numbers with the app's.

## Files
| File | Content |
|---|---|
| `geo1261_Mission_Plan.ipynb` | the workbook: read the text cells, fill in the cells marked `# YOUR CODE HERE` |
| `data/geo1261/gfl_flight_area.gpkg` | layer `flight_area`: the area we may fly over (land use "Bildung und Wissenschaft" around the Green Fab Lab; west and south of the building and above it); layer `building`. EPSG:25832 |

## Tasks
1. **Camera (§1):** derive the ground sampling distance (GSD) of both cameras from the field of view and the image size.
2. **Spacing and speed (§2):** turn height and overlap into line spacing, photo spacing and speed; decide which camera sets which value.
3. **Flight lines (§3):** generate parallel flight lines over the area with Shapely.
4. **Photos and time (§4):** photo positions, path length, flight time.
5. **Map and export (§5):** run the map cell; it saves your plan as `geo1261_plan.gpkg` (open it in QGIS) and the area as `gfl_flight_area.kml` for the flight app.
6. **Heights (§6):** compare 25, 30, 40 and 60 m, all cameras and RGB only; answer the questions.

## Hints
- `np.tan` wants radians. The RGB field of view is given for the **diagonal**, the multispectral one for the width.
- At 100 m the RGB pixel is about 2.7 cm: check your `gsd` with that.
- If a flight line comes out as a `MultiLineString`, the line crosses a concave part of the area: keep the longest piece.
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
