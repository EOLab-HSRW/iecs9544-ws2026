
## s01 – geo0641 DWD station pipeline (2026-10-17)
The station id was read as a number, so `00044` became `44`. Ids are identifiers and stay text in this course.
Run `s01_2026-10-05/geo0641_DWD_Station_Pipeline_fix1.ipynb` once **before session 3**: it converts `station_id`
in your `data/derived/dwd_stations.gpkg` to 5-character text. If you run geo0641 again, use
`dtype={"station_id": str, "date_from": str, "date_to": str}` in section 3.2.
