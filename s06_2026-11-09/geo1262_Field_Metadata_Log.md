# geo1262 Field data: metadata log (homework)

**Tool:** a text editor or spreadsheet, a file manager · **Time:** about 1 h · **Builds on:** `geo0261_RTK_Field_Practice.md`, `geo1261_Mission_Plan.md`, the field day · **Template:** `data/geo1262/geo1262_flight_log.csv`

A folder of 600 photos called `DJI_202611091034_001_Mapping` is useless in three months: which height, which camera, was the drone on RTK, where are the control points, which CRS has the CSV? Photogrammetry software reads some of this from the photos; most of it exists only in the heads of the people who were in the field. In this homework you write it down while you still remember it, so that someone else (or you, in the project) can process the data.

## 1 Flight log (one row per flight)
Start from `data/geo1262/geo1262_flight_log.csv` (one example row, F1). Your group's flight logger filled in times and app numbers in the field; complete the table:

| Column | What | Example |
|---|---|---|
| `flight_id` | F1, F2, … as named in the field | `F1` |
| `date`, `takeoff_local`, `landing_local` | ISO date, local time `HH:MM` (Europe/Berlin) | `14:05` |
| `mission_type` | `mapping`, `oblique`, `manual` | `mapping` |
| `height_agl_m`, `front_overlap_pct`, `side_overlap_pct` | as set in the app | `25`, `80`, `70` |
| `cameras` | `RGB`, `MS`, `RGB+MS` | `RGB+MS` |
| `drone_rtk` | `on` (with FIX), `off`, `float` | `on` |
| `gimbal_pitch_deg` | −90 = nadir | `-90` |
| `photos_app`, `lines_app`, `line_spacing_app_m`, `flight_time_app_min` | numbers the app showed before take-off | |
| `photos_on_card` | count the files in the folder afterwards (per camera if both) | |
| `battery_start_pct`, `battery_end_pct` | from the app or the flight logger | |
| `wind`, `clouds_light` | short text: `light, gusts`, `overcast, even light`, `sun, shadows` | |
| `reflectance_panel` | `before`, `after`, `before+after`, `none` | |
| `pilot`, `logger` | initials | |
| `folder` | folder name of this flight in the data store | `F1_map25_all` |
| `notes` | anything special: aborted line, people in the area, battery change | |

Keep it a plain CSV (comma, UTF-8, header unchanged): the logs of all groups are merged by a script.

## 2 Compare with your mission plan
Add a short table to your README (below) for F1: your geo1261 numbers next to the app's (line spacing, photo positions, flight time) and next to the photos on the card. Explain each difference in one sentence (e.g. turns at the line ends, the app's own overlap rounding, photos taken on the way to the first line).

## 3 README for the field data
Write `README.md` (one page) that someone who was not there can use:
- **Site and date:** place, flight area (which file), who measured and who flew.
- **Coordinate reference:** CRS of the RTK points (EPSG code), height system (ellipsoidal or above NHN, which one), antenna/pole height and how it was entered.
- **Control:** which points are ground control points, which are check points; file names of the RTK CSVs; number of FIX solutions and anything you noticed (time to first fix, first vs second round).
- **Flights:** reference to the flight log; which flight is the main data set and why.
- **Raw data:** which receiver logged raw data (RINEX), from when to when.
- **Licence and use:** course data, not for publication (people and buildings in the photos).
- **Problems:** what went wrong or could be done better next time.

## Hand in
Upload `groupNN_flight_log.csv` and `groupNN_README.md` to Moodle (one upload per group) before the next session.

## Why this matters
The accuracy check of the drone products compares the orthomosaic and the surface model with your check points: that only works if it is clear which points were control and which were check points, and in which height system they are. The same log is the start of the metadata of your project data.

## Sources
- OpenDroneMap documentation, *Ground control points* (GCP file format), docs.opendronemap.org/gcp.
- DJI Mavic 3M specifications, ag.dji.com/mavic-3-m/specs.
- ISO 19115-1:2014 *Geographic information – Metadata* (the formal standard behind a "metadata log"; here only the idea: who, what, where, when, how).
