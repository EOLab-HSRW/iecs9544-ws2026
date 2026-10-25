# geo0443 DGM1 tiles in QGIS: select on a tile index, download, virtual raster

**Tool:** QGIS Python console · **Time:** 10 min · **Script:** `geo0443_DGM1_Tiles_QGIS_Console.py` · **Builds on:** geo0442 (the same index, built in a notebook)

In geo0442 you built the index of all NRW terrain tiles in a notebook on the hub. The script does the same in QGIS on your laptop: it puts the 36 000 squares on the map, you select the tiles you need with the mouse, and it downloads them and combines them into one virtual raster (VRT).

## Run the script
1. Open your project, e.g. the one in your session folder (the script finds `<course folder>/data/` from the project's folder; otherwise it asks you for a data folder once and remembers it).
2. *Plugins → Python Console* → *Show Editor* (the notepad icon) → *Open Script…* → `geo0443_DGM1_Tiles_QGIS_Console.py` → *Run Script* (green triangle).
3. The first time, it downloads the file list (3.5 MB) and writes `data/derived/dgm1_tile_index.gpkg` (a few seconds). Later runs only ask the server whether the list has changed.
4. The layer **DGM1 tiles NRW** appears, coloured by survey year. Zoom in to see the tile names.

## Select and download
1. Select tiles on **DGM1 tiles NRW**: *Select Features* tool (click, Shift+click, or drag a rectangle), or *Vector → Research Tools → Select by Location* with a polygon of your area.
2. In the console (lower part), type `download_selected()` and press Enter. At most 50 tiles per call.
3. The tiles go to `data/original/dgm1_tiff/`; tiles already there are skipped. A VRT `dgm1_selection_<date>.vrt` is added to the map. Your own name: `download_selected(vrt_name="my_area")`.

Other commands: `info()` (data folder, index date, tiles on disk), `refresh(force=True)` (check the server now), `set_data_dir()` (choose another data folder).

## Check yourself
- Select the six tiles of the Uedemer Hochwald (geo1041). Do you get the same files as from the geo0442 zip? Same survey years?
- Run `download_selected()` twice. What is different the second time, and why?
- Open `data/original/dgm1_tiff/index.json`. What do `etag` and `last_modified` tell the server when the script asks again?
- Open the VRT in a text editor. Where are the pixels?

Data: DGM1 © Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (dl-de/zero-2-0).
