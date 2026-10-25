"""geo0443 DGM1 tiles in QGIS, short version: read it from top to bottom.

Save your project first (in your session folder), then: Python Console -> Show Editor ->
Open Script... (this file) -> Run Script. Select tiles on the layer "DGM1 tiles NRW",
then type  download_selected()  in the console.

The long version geo0443_DGM1_Tiles_QGIS_Console.py does the same with more care
(data folder, refresh once a day, offline, progress bar, style, relative VRT). Compare them.
Data: DGM1 (c) Geobasis NRW, dl-de/zero-2-0.
"""
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from osgeo import gdal
from qgis.core import (QgsFeature, QgsGeometry, QgsProject, QgsRasterLayer, QgsRectangle,
                       QgsVectorFileWriter, QgsVectorLayer)

URL = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_tiff/dgm1_tiff/"
HEADERS = {"User-Agent": "opengeo teaching script geo0443 basic (QGIS)"}
NAME = re.compile(r"^dgm1_32_(\d{3})_(\d{4})_1_nw_(\d{4})\.tif$")   # east km, north km, survey year
LAYER = "DGM1 tiles NRW"
MAX_TILES = 50

home = QgsProject.instance().homePath()            # the folder of the saved project
if not home:
    raise RuntimeError("save the project first: the data go to ../data next to the session folder")
DATA = Path(home).parent / "data"                  # or write your own path here
ORIGINAL = DATA / "original" / "dgm1_tiff"         # file list and tiles, as sent by the server
GPKG = DATA / "derived" / "dgm1_tile_index.gpkg"   # the tile index (same file as geo0442)
ORIGINAL.mkdir(parents=True, exist_ok=True)
GPKG.parent.mkdir(parents=True, exist_ok=True)


# 1. The file list: download it, or only ask "has it changed?" ------------------------------
def fetch_listing():
    """True if a new file list was downloaded, False if our copy is still current (HTTP 304)."""
    xml_file, info_file = ORIGINAL / "index.xml", ORIGINAL / "index.json"
    info = json.loads(info_file.read_text()) if info_file.exists() else {}
    headers = dict(HEADERS)
    if xml_file.exists() and info.get("etag"):
        headers["If-None-Match"] = info["etag"]    # "send it only if it differs from this version"
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, headers=headers), timeout=60) as r:
            xml_file.write_bytes(r.read())
            info = {"url": URL, "etag": r.headers.get("ETag"), "last_modified": r.headers.get("Last-Modified")}
    except urllib.error.HTTPError as e:
        if e.code == 304:                          # Not Modified: no body, keep our copy
            print("file list unchanged (304)")
            return False
        raise
    info_file.write_text(json.dumps(info, indent=1))
    print("file list downloaded, Last-Modified", info["last_modified"])
    return True


# 2. The tile index: one 1 km square per file name ------------------------------------------
def build_index():
    """Read index.xml, make a polygon layer in memory, save it as GeoPackage."""
    root = ET.parse(ORIGINAL / "index.xml").getroot()
    mem = QgsVectorLayer("Polygon?crs=EPSG:25832&field=key:string&field=file:string&field=year:integer"
                         "&field=e_km:integer&field=n_km:integer&field=size_mb:double"
                         "&field=size_bytes:long&field=timestamp:string", "tiles", "memory")
    features = []
    for tag in root.iter("file"):                  # <file name="..." size="..." timestamp="..."/>
        m = NAME.match(tag.get("name"))
        if m is None:
            raise ValueError(f"unexpected file name {tag.get('name')}")
        e, n, year = (int(v) for v in m.groups())
        f = QgsFeature(mem.fields())
        f.setAttributes([f"dgm1_32_{e}_{n}_1_nw", tag.get("name"), year, e, n,
                         round(int(tag.get("size")) / 1e6, 2), int(tag.get("size")), tag.get("timestamp")])
        f.setGeometry(QgsGeometry.fromRect(QgsRectangle(e * 1000, n * 1000, (e + 1) * 1000, (n + 1) * 1000)))
        features.append(f)
    mem.dataProvider().addFeatures(features)
    opts = QgsVectorFileWriter.SaveVectorOptions()
    opts.driverName, opts.layerName = "GPKG", "dgm1_tiles"
    QgsVectorFileWriter.writeAsVectorFormatV3(mem, str(GPKG), QgsProject.instance().transformContext(), opts)
    print(len(features), "tiles written to", GPKG)


# 3. Download the selected tiles, combine them in a virtual raster --------------------------
def download_selected():
    layer = QgsProject.instance().mapLayersByName(LAYER)[0]
    selected = layer.selectedFeatures()
    if not 0 < len(selected) <= MAX_TILES:
        print(f"select 1 to {MAX_TILES} tiles on the layer '{LAYER}' ({len(selected)} selected)")
        return
    files = []
    for f in selected:
        target = ORIGINAL / f["file"]
        if target.exists() and target.stat().st_size == f["size_bytes"]:
            print(f["file"], "already there")
        else:
            with urllib.request.urlopen(urllib.request.Request(URL + f["file"], headers=HEADERS), timeout=60) as r:
                target.write_bytes(r.read())
            if target.stat().st_size != f["size_bytes"]:
                raise IOError(f"{f['file']}: incomplete download")
            print(f["file"], "downloaded")
        files.append(str(target))
    vrt = ORIGINAL / "dgm1_selection.vrt"
    gdal.BuildVRT(str(vrt), files).FlushCache()    # a small XML file that points to the tiles
    QgsProject.instance().addMapLayer(QgsRasterLayer(str(vrt), "DGM1 selection"))
    print(len(files), "tiles in", vrt)


# Run: refresh the index if needed, show it -------------------------------------------------
for old in QgsProject.instance().mapLayersByName(LAYER):
    QgsProject.instance().removeMapLayer(old.id())  # release the GeoPackage before rewriting it
if fetch_listing() or not GPKG.exists():
    build_index()
QgsProject.instance().addMapLayer(QgsVectorLayer(f"{GPKG}|layername=dgm1_tiles", LAYER, "ogr"))
print(f"Select tiles on '{LAYER}', then type:  download_selected()")
