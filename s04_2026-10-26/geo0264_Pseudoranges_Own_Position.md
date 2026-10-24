# geo0264 Pseudoranges: compute your own GNSS position (optional)

**Tool:** Jupyter notebook `geo0264_Pseudoranges_Own_Position.ipynb` · **Time:** about 2 h for §1–§3, 1–2 h more for the stretch tasks §4–§5 · **Builds on:** slides `geo0260_GNSS` (*GNSS*, *DGNSS / RTK*, *SAPOS*) · **Data:** `data/geo0264/` or your group's field data

This is an **optional** task for everyone who wants to look inside a GNSS receiver. It is not graded and not needed for the next sessions.

A receiver does not measure positions. It measures **pseudoranges**: signal travel times multiplied by the speed of light, spoiled by its own clock error. You write the solver that turns pseudoranges into a position and check it against a position you know. Step by step you remove the errors and see how large each one is.

## Three data sources
You choose the source in §0 of the notebook (`SOURCE = …`); the rest of the notebook is the same for all three.

| `SOURCE` | What it is | Truth |
|---|---|---|
| `"sapos"` (default) | SAPOS reference stations Viersen and Wesel, 21 October 2026, one epoch every 5 minutes | station coordinates (ETRS89) |
| `"synthetic"` | invented pseudoranges on the real GPS orbits of that day; you switch each error (receiver clock, noise, multipath, ionosphere, troposphere, satellite orbit/clock) on or off | exact |
| `"own"` | your own raw data from the field session at the Green Fab Lab | your RTK fix plus the pole height |

Start with `"sapos"`, then try `"synthetic"` to see which correction removes which error, and `"own"` once your group's data are available.

## Files
| File | Content |
|---|---|
| `geo0264_Pseudoranges_Own_Position.ipynb` | the workbook: read the text cells, fill in the cells marked `# YOUR CODE HERE` |
| `geo0264_gnss_prep.py` | helper module (do not edit for the tasks): reads RINEX files, computes satellite positions and clocks from the broadcast ephemeris, makes the three data sources |
| `data/geo0264/geo0264_sapos_2026-10-21.csv` | GPS pseudoranges of SAPOS stations 2578 Wesel and 2579 Viersen with satellite positions and clocks |
| `data/geo0264/geo0264_sapos_2026-10-21_reference.csv` | their known coordinates (ETRS89, geocentric X, Y, Z) |
| your group's data (after the field session) | `~/shared/data/opengeo/geo0264/<group>/geo0264_<group>.csv` and `…_reference.csv` on the hub (also in Moodle); set `OWN_FILE` and, if you like, `POINT` in §0 |

The columns are explained in the notebook (§2.1).

## Tasks
1. **Warm-up (§1):** write `solve_position(sat, rho)`, a least-squares solver with four unknowns (X, Y, Z, receiver clock). Test it with invented pseudoranges on real orbits; change the clock error, the noise, the number of satellites and the geometry, and explain what happens.
2. **Your data source (§2):** solve one epoch and express the error in east, north and up.
3. **All epochs (§3):** solve all epochs, then add an elevation mask and a troposphere model. Which component improves most, and why?
4. **Stretch, ionosphere (§4):** use both frequencies (ionosphere-free combination). Explain the offset of about one metre that remains with real data.
5. **Stretch, DGNSS (§5):** use the reference station to correct the rover. Where did the offset go?
6. **Wrap-up (§6):** answer the questions; compare at least two sources.

## Hints
- Predict before you run. Compare your numbers with the slides (*Where the metres come from*, *Geometry matters: DOP*, *What coordinates does SAPOS give you?*).
- The satellite clock correction is large (tens of kilometres): add it, do not subtract it.
- If your solution is thousands of kilometres off, print the first iterations of your solver.
- Own data: the reference is the **antenna** position (RTK point + pole height). If your height error is about 1.8 m, you compared with the ground point.

## For the curious: make the data yourself
`geo0264_gnss_prep.py` also runs on its own, e.g. with another SAPOS station or day, or with your raw file:

```
python geo0264_gnss_prep.py sapos --date 2026-10-21 --stations 2578 2582 --step 60 --out my_data
python geo0264_gnss_prep.py own --rinex <raw file>.obs --emlid <group>_emlid.csv --group mygroup --tz Europe/Berlin --base 2578 --out my_data
```
SAPOS files need `pip install --user hatanaka` (compressed RINEX) and download the daily archive (~190 MB) once. Read the code: the satellite positions follow the GPS interface specification IS-GPS-200, as in every GPS receiver.

## Hand in
Nothing. If you want feedback, upload the notebook (with outputs) to Moodle and say which result surprised you.

## Sources
- SAPOS NRW, GPPS archive (RINEX observations and broadcast navigation): Bezirksregierung Köln, Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0, https://www.opengeodata.nrw.de/produkte/geobasis/rb/sapos/gpps_archiv/
- Broadcast navigation for own data: IGS daily file BRDC00WRD (BKG, igs.bkg.bund.de) or the SAPOS archive.
- IS-GPS-200 (GPS interface specification): satellite position and clock from the broadcast ephemeris.
- Wikipedia: *GNSS positioning calculation*, *Pseudorange*, *Dilution of precision*.
