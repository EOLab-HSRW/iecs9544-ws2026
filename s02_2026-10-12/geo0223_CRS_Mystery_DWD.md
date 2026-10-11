# geo0223 CRS mystery with DWD stations (homework)

**Tool:** QGIS (notebook geo0221 optional) · **Time:** about 2 h · **Data:** `data/geo0223_DWD_Stations_NRW_CRS_1.csv` … `_5.csv`

Same task as in class, new data and no help from rivers: 83 climate stations of the Deutscher Wetterdienst (DWD) in North Rhine-Westphalia, stored in five files with five different coordinate reference systems. The files are numbered 1–5. Their CRSs are **not** in the same order as the gauge files A–E from class.

## Files
| File | Use |
|---|---|
| `data/geo0223_DWD_Stations_NRW_CRS_1.csv` … `_5.csv` | the five mystery files (source: Deutscher Wetterdienst, coordinates converted) |
| `geo0222_CRS_Mystery_QGIS.qgz` (if your session folder has it) | start project (NRW boundaries + OpenStreetMap, EPSG:25832); otherwise any new QGIS project with OpenStreetMap and project CRS EPSG:25832 |
| `geo0221_CRS_in_Code.ipynb` | optional: check your answer in metres |

## Task
1. Identify the CRS (EPSG code) of **all five files**. For each file justify your answer in 2–3 sentences: value ranges, units, number of digits, zone prefix, axis order. Not the same separator and column names everywhere: read the files in a text editor first.
2. Prove it: load all five files into your QGIS project with your CRSs. Add **one screenshot** at a large scale (about 1:2 000) of one station where all five layers coincide. Write the station name and the scale into the caption.
3. One file needs a datum transformation. Which one? Measure in QGIS how far its points lie from the others, and explain in one sentence why the offset is not exactly zero.

**Optional (code check):** in `geo0221_CRS_in_Code.ipynb` set `PATTERN = "geo0223_DWD_Stations_NRW_CRS_*.csv"`, `REF` = the number of your degree file, `PAIR = (216, 389)` and fill `GUESS` with your five answers. Then run §1–§4. All offsets in §3 should be (almost) zero.

## Hand in
One PDF (max. 2 pages): table *file – EPSG code – justification*, the screenshot, the answer to step 3. Deadline and channel: see the course plan.

## Check yourself
- Which two files contain exactly the same northing values? What does that tell you?
- Why would measuring the distance between two stations in file *x* give a result about 1.6 times too long?
