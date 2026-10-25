# geo0443 DGM1 tiles in QGIS: select on a tile index, download, virtual raster

**Tool:** QGIS Python console · **Time:** 10 min (run the tool) + 30 min (walkthrough and comparison) · **Scripts:** `geo0443_DGM1_Tiles_QGIS_Basic.py` (short, 116 lines), `geo0443_DGM1_Tiles_QGIS_Console.py` (long, 391 lines) · **Builds on:** geo0442 (the same index, built in a notebook)

In geo0442 you built the index of all NRW terrain tiles in a notebook on the hub. Two scripts do the same in QGIS on your laptop: they put the 36 000 squares on the map, you select the tiles you need with the mouse, and the script downloads them and combines them into one virtual raster (VRT). Both scripts work. The short one is written to be read; the long one is written to be used by many people on many computers. What the extra 275 lines buy is the subject of the comparison.

Both use the same files (as geo0442): `data/original/dgm1_tiff/` (file list `index.xml`, `index.json`, tiles, VRT) and `data/derived/dgm1_tile_index.gpkg` (layer `dgm1_tiles`).

## 1. Use it: the long version
1. Open your project in your session folder (the script finds `<course folder>/data/` from the project's folder; otherwise it asks you for a data folder once and remembers it).
2. *Plugins → Python Console* → *Show Editor* (notepad icon) → *Open Script…* → `geo0443_DGM1_Tiles_QGIS_Console.py` → *Run Script* (green triangle).
3. The first time, it downloads the file list (3.5 MB) and writes the tile index (a few seconds). Later runs only ask the server whether the list has changed. The layer **DGM1 tiles NRW** appears, coloured by survey year; zoom in to see the tile names.
4. Select tiles on **DGM1 tiles NRW**: *Select Features* tool (click, Shift+click, drag a rectangle), or *Vector → Research Tools → Select by Location* with a polygon of your area.
5. In the console, type `download_selected()` and press Enter (at most 50 tiles). Tiles already there are skipped. A VRT `dgm1_selection_<date>.vrt` is added to the map; your own name: `download_selected(vrt_name="my_area")`.

Other commands: `info()`, `refresh(force=True)` (check the server now), `set_data_dir()`.

## 2. Look inside: the console first
Before you read any script, ask the layer yourself. Click **DGM1 tiles NRW** in the *Layers* panel, select a few tiles and type line by line:
```python
layer = iface.activeLayer()
layer.featureCount(), [f.name() for f in layer.fields()]
sel = layer.selectedFeatures()
[f["file"] for f in sel]
sum(f["size_mb"] for f in sel)
```
This is what `download_selected()` starts with: the selected features and their attributes.

## 3. Walkthrough: the short version
Save the project, open `geo0443_DGM1_Tiles_QGIS_Basic.py` in the console editor, run it, select tiles, `download_selected()`. Then read it along its four parts:

| Part | Lines to look at | Question |
|---|---|---|
| Setup | `DATA = Path(home).parent / "data"` | Where do the files go? What happens if the project is not saved? |
| 1 `fetch_listing` | `If-None-Match`, `e.code == 304` | What does the script send the second time, what does the server answer, how many bytes come back? |
| 2 `build_index` | `NAME.match`, `QgsRectangle(e * 1000, …)`, `writeAsVectorFormatV3` | How does a file name become a square? Why does the script stop on an unexpected name instead of skipping it? |
| 3 `download_selected` | `selectedFeatures()`, `st_size == f["size_bytes"]`, `gdal.BuildVRT` | When is a tile downloaded again? Where are the pixels of the VRT? |

## 4. Compare: what do the extra 275 lines buy?
Work in pairs. For each row, find the code in both scripts and try the experiment.

| Topic | Experiment | Short version | Long version |
|---|---|---|---|
| Data folder | run with an unsaved project; run on a second computer | ? | ? |
| Server check | run the script three times in a row; look at `index.json` | ? | ? |
| No network | switch off Wi-Fi, run the script | ? | ? |
| Interrupted download | pull the network during `download_selected()`, then run it again | ? | ? |
| File list changed | a tile was surveyed again: its name in `index.json` changed, your index is a week old | ? | ? |
| While downloading | try to pan the map during a download of 10 tiles | ? | ? |
| VRT | make two selections one after the other; move the course folder; look into the `.vrt` files with a text editor | ? | ? |
| Provenance | open `dgm1_tile_index.gpkg` in the *Browser*: which layers? Where is written how old the index is? | ? | ? |
| Map | how does the index look, can you read the tile names? | ? | ? |

Then discuss:
- Which differences are **robustness** (the result is right or a clear error appears), which are **user experience** (the user knows what happens and what to do), which are **convenience**?
- Which three additions would you take into the short version first, and why?
- The long version is harder to read. Who pays for that, and when is it worth it?

## 5. The same as a QGIS plugin: DGM1 NRW Tile Downloader
The long script, turned into a plugin: menu and toolbar buttons instead of the console, and the download runs in the background (QGIS stays usable, progress and a cancel button in the status bar). How a script becomes a plugin is shown in class.

**Install (once):**
1. The file `dgm1_nrw_tiles.zip` is in this session folder. **Do not unzip it**: QGIS needs the zip itself. (If you downloaded the whole Moodle folder as a zip, unzip that one, but leave `dgm1_nrw_tiles.zip` inside as it is.)
2. QGIS: *Plugins → Manage and Install Plugins… → Install from ZIP* → `…` → choose `dgm1_nrw_tiles.zip` → *Install Plugin*. Confirm the warning about plugins from outside the official repository (*Yes*): you install code from your course, not from the QGIS plugin repository.
3. The plugin appears under *Plugins → DGM1 NRW Tile Downloader* and as two toolbar buttons. If you do not see the buttons: *View → Toolbars → Plugins Toolbar*. Check that it is ticked in *Plugins → Manage and Install Plugins… → Installed*.

**Use:**
1. Open a project in your session folder (the plugin finds `<course folder>/data/`; otherwise it asks for a data folder once).
2. Button **Load DGM1 tile index** (tiles, one selected): the index appears, coloured by survey year.
3. Select tiles on **DGM1 tiles NRW** (at most 50), button **Download selected tiles** (tiles with red arrow). A VRT `dgm1_selection_<time>.vrt` is added when the download is done.
4. Messages in detail: *View → Panels → Log Messages*, tab *DGM1 NRW*.

**Update or remove:** install a newer zip the same way (it replaces the old version); remove it in *Manage and Install Plugins… → Installed → Uninstall Plugin*. Data and tiles stay in your data folder.

## Check yourself
- Select the six tiles of the Uedemer Hochwald (geo1041). Do you get the same files as from the geo0442 zip? Same survey years?
- Why does each script ask the server before it rebuilds the index, and the long one also before a download?
- Run the long version after the short one on the same data folder: it rebuilds the index although the file list has not changed. Why? (Look for `index_info`.)

Data: DGM1 © Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (dl-de/zero-2-0).
