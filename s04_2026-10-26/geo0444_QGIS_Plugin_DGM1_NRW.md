# geo0444 Your own QGIS plugin: DGM1 NRW Tile Downloader

**Tool:** QGIS plugin · **Time:** demo 15 min + exercise 20 min · **Files:** `geo0444_DGM1_NRW_Tile_Downloader_QGIS_Plugin.zip` (in this session folder) · **Builds on:** geo0443 (the long console script `geo0443_DGM1_Tiles_QGIS_Console.py`)

In geo0443 you ran a script in the Python console. A **plugin** is the same Python code packed so that QGIS loads it at start-up: with menu entries, toolbar buttons and its own entry in the Plugin Manager. Everybody who installs the zip gets the tool, without opening the console. This plugin does what the long geo0443 script does: tile index of the NRW terrain model DGM1, select tiles, download, virtual raster. In addition, the download runs in the background, so QGIS stays usable.

Data: DGM1 (1 m) of North Rhine-Westphalia from opengeodata.nrw.de, © Geobasis NRW, Datenlizenz Deutschland – Zero – Version 2.0 (dl-de/zero-2-0). The plugin is a teaching example, not an official product of Geobasis NRW.

## 1. Install (once)
1. `geo0444_DGM1_NRW_Tile_Downloader_QGIS_Plugin.zip` is in this session folder. **Do not unzip it**: QGIS needs the zip itself. (If you downloaded the whole Moodle folder as a zip, unzip that one, but leave the plugin zip inside as it is.)
2. QGIS: *Plugins → Manage and Install Plugins… → Install from ZIP* → `…` → choose the zip → *Install Plugin*. Confirm the warning about plugins from outside the official repository (*Yes*): you install code from your course, not from the QGIS plugin repository.
3. The plugin appears under *Plugins → DGM1 NRW Tile Downloader* and as two toolbar buttons. No buttons? *View → Toolbars → Plugins Toolbar*. Check that it is ticked in *Plugins → Manage and Install Plugins… → Installed*.

## 2. Use it
1. Open a project in your session folder (the plugin finds `<course folder>/data/`; otherwise it asks for a data folder once).
2. Button **Load DGM1 tile index** (tiles, one selected): the index appears as layer **DGM1 tiles NRW**, coloured by survey year. It is the same file as in geo0442/geo0443 (`data/derived/dgm1_tile_index.gpkg`).
3. Select tiles (at most 50), button **Download selected tiles** (tiles with red arrow). Watch the status bar at the bottom: progress, and a × to cancel. Pan the map while it downloads. When it is done, a VRT `dgm1_selection_<time>.vrt` is added.
4. *View → Panels → Log Messages*, tab *DGM1 NRW*: one line per tile.
5. Menu *Plugins → DGM1 NRW Tile Downloader*: also *Check server for a new file list* and *Choose data folder…*.

## 3. Look inside: the anatomy of a plugin (demo)
QGIS unpacked the zip into your profile folder: *Settings → User Profiles → Open Active Profile Folder* → `python/plugins/dgm1_nrw_tiles/`. Open the files in a text editor (or VS Code).

| File | What QGIS does with it |
|---|---|
| `metadata.txt` | reads name, version, minimum QGIS version, description, icon for the Plugin Manager |
| `__init__.py` | imports the folder as a Python package and calls `classFactory(iface)` once |
| `plugin.py` | the plugin class: `initGui()` when the plugin is switched on (menu entries, buttons), `unload()` when it is switched off; everything added in `initGui()` must be removed in `unload()` |
| `core.py` | an ordinary module: file list, tile index, download, VRT; no buttons, no message bar |
| `icon.png`, `icon_index.png` | the icons |

Compare with the long geo0443 script:

| Console script | Plugin |
|---|---|
| runs when you press *Run Script*; you type `download_selected()` | runs nothing by itself; buttons and menu entries call methods |
| `iface` exists in the console | `iface` is handed to `classFactory(iface)` and kept as `self.iface` |
| download in the main thread: QGIS waits | download as `QgsTask` in a background thread: QGIS stays usable, progress and cancel in the status bar |
| logic and GUI in one file | `core.py` (logic) and `plugin.py` (GUI) |

**The rule for background tasks:** the function `_download` (bottom of `plugin.py`) runs in another thread. It only writes files and calls `task.setProgress()`. Adding the VRT to the map happens in `_finished`, which QGIS calls in the main thread afterwards. Changing layers or widgets from a background thread can crash QGIS.

## 4. Exercise (pairs): change the plugin
To load your changes without restarting QGIS, install the plugin **Plugin Reloader** (*Manage and Install Plugins… → All*, search "Plugin Reloader"). Its button reloads a plugin: QGIS calls `unload()`, imports the changed code and calls `initGui()` again. Choose `dgm1_nrw_tiles` once in its settings.

1. **Colours.** In `plugin.py`, method `_style`, change the list `colours` (e.g. a colour scale from light to dark for older to newer survey years) and the opacity (`"40"` at the end of the colour is the alpha value in hex). Reload, then *Load DGM1 tile index* again (remove the old layer first). Labels from which scale on? Change `pal.minimumScale`.
2. **A third button: zoom to the selected tiles.** In `initGui()`, add a third toolbar button that calls a new method `zoom_to_selection`. In that method, find the index layer and call `self.iface.mapCanvas().zoomToSelected(layer)`. Use the theme icon `"/mActionZoomToSelected.svg"`. Reload, select some tiles, zoom out, press your button.
3. **Check `unload()`.** Switch the plugin off and on in the Plugin Manager. Does your button disappear and come back exactly once? Why is it not doubled?
4. **Version.** Raise `version=` in `metadata.txt` to `0.1.1` and reload: where in the Plugin Manager do you see it?

If you break something: QGIS shows a Python error window. Read the last line, fix the file, reload. If nothing helps, install the zip again (it replaces your edited copy).

## Check yourself
- Which two functions does every plugin need, and when does QGIS call them?
- Why does the plugin need its own `iface` instead of the global one of the console?
- What would happen if `_download` added the VRT layer to the map itself?
- The zip file can be renamed freely, but the folder inside not. Why? (Hint: profile folder, QgsSettings key.)
- When is a console script enough, when is a plugin worth the extra files?

## Further
- PyQGIS Developer Cookbook, plugins: https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/index.html
- Tasks (`QgsTask`): https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/tasks.html
- Plugin Builder (generates the skeleton of a new plugin): plugin "Plugin Builder 3" in the Plugin Manager
