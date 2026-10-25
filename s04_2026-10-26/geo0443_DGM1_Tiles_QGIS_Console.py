"""geo0443 DGM1 tiles of NRW in QGIS: tile index, select, download, virtual raster.

Run in the QGIS Python console: Plugins -> Python Console -> "Show Editor" ->
"Open Script..." (this file) -> "Run Script". Then:

  1. The layer "DGM1 tiles NRW" (about 36 000 squares of 1 km) appears in the map.
     The first time, the script downloads the file list (3.5 MB) and builds the index
     (a few seconds); afterwards it only asks the server whether the list has changed.
  2. Select tiles on that layer (Select Features tool, or Select by Location with a polygon).
  3. Type in the console:   download_selected()
     The tiles are downloaded (tiles already there are skipped) and combined into a
     virtual raster (VRT) that is added to the map.

Other commands:  refresh(force=True)  ->  check the server now (otherwise at most once a day)
                 set_data_dir()        ->  choose the data folder again
                 info()                ->  data folder, index date, number of tiles

Same file layout and GeoPackage schema as notebook geo0442, so both can use the same data folder:
  <data>/original/dgm1_tiff/index.xml, index.json   file list as sent by the server, HTTP info
  <data>/original/dgm1_tiff/dgm1_32_*.tif          the downloaded tiles (and the VRTs)
  <data>/derived/dgm1_tile_index.gpkg              layers dgm1_tiles, index_info
Only the Python standard library, GDAL/OGR and the QGIS API: nothing to install.

Data: DGM1 (c) Geobasis NRW, Datenlizenz Deutschland - Zero - Version 2.0 (dl-de/zero-2-0).
"""
import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from osgeo import gdal, ogr, osr
from qgis.core import (Qgis, QgsApplication, QgsCategorizedSymbolRenderer, QgsFillSymbol,
                       QgsPalLayerSettings, QgsProject, QgsRasterLayer, QgsRendererCategory,
                       QgsSettings, QgsTextFormat, QgsVectorLayer, QgsVectorLayerSimpleLabeling)

try:
    from qgis.utils import iface            # None outside the QGIS desktop (tests)
except ImportError:
    iface = None

# ---- settings you may change ------------------------------------------------------------
DATA_DIR = ""              # "" = find it: OPENGEO_DATA, saved choice, <course folder>/data, or ask
MAX_AGE_HOURS = 24         # ask the server again after this time
MAX_TILES = 50             # per download_selected() call: be polite to the server
# -----------------------------------------------------------------------------------------

DGM1_URL = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_tiff/dgm1_tiff/"
HEADERS = {"User-Agent": "opengeo teaching script geo0443 (QGIS)"}
EPSG = 25832
TILE = 1000
NAME = re.compile(r"^dgm1_32_(?P<e_km>\d{3})_(?P<n_km>\d{4})_1_nw_(?P<year>\d{4})\.tif$")
LAYER_NAME = "DGM1 tiles NRW"
SETTINGS_KEY = "opengeo/data_dir"
LICENCE = "Geobasis NRW, dl-de/zero-2-0"


# ---- where the data go ------------------------------------------------------------------
def _ask_folder(start):
    if iface is None:
        return ""
    from qgis.PyQt.QtWidgets import QFileDialog
    return QFileDialog.getExistingDirectory(iface.mainWindow(), "Data folder for DGM1 tiles "
                                            "(the data/ folder of your course folder)", str(start))


def _course_data_folder():
    """data/ next to or above the project file (session folder -> ../data)."""
    home = QgsProject.instance().homePath()
    if not home:
        return None
    p = Path(home)
    for folder in (p, *p.parents[:3]):
        if (folder / "data").is_dir():
            return folder / "data"
    return None


def data_dir():
    """The data folder: setting, environment, saved choice, course folder, ask, ~/tmp/opengeo/data."""
    for candidate in (DATA_DIR, os.environ.get("OPENGEO_DATA", ""), QgsSettings().value(SETTINGS_KEY, "")):
        if candidate and Path(candidate).expanduser().is_dir():
            return Path(candidate).expanduser()
    folder = _course_data_folder()
    if folder is None:
        chosen = _ask_folder(Path.home())
        folder = Path(chosen) if chosen else Path.home() / "tmp" / "opengeo" / "data"
        if not chosen:
            _say(f"no data folder chosen, using {folder}", Qgis.Warning)
    folder.mkdir(parents=True, exist_ok=True)
    QgsSettings().setValue(SETTINGS_KEY, str(folder))
    return folder


def set_data_dir():
    """Choose the data folder again (saved in the QGIS settings)."""
    chosen = _ask_folder(QgsSettings().value(SETTINGS_KEY, str(Path.home())))
    if chosen:
        QgsSettings().setValue(SETTINGS_KEY, chosen)
    print("data folder:", data_dir())


def paths():
    root = data_dir()
    original = root / "original" / "dgm1_tiff"
    derived = root / "derived"
    for folder in (original, derived):
        folder.mkdir(parents=True, exist_ok=True)
    return {"original": original, "xml": original / "index.xml", "json": original / "index.json",
            "gpkg": derived / "dgm1_tile_index.gpkg"}


def _say(text, level=Qgis.Info, seconds=6):
    print(text)
    if iface is not None:
        iface.messageBar().pushMessage("DGM1", text, level, seconds)


# ---- 1. the file list: download once, then only ask "changed?" -------------------------
def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def fetch_listing(force=False):
    """(xml bytes, info dict, changed?) of the DGM1 file list.

    Local copy younger than MAX_AGE_HOURS: no request. Otherwise a *conditional* GET:
    the server answers 304 Not Modified (no body) if the list has not changed since our copy."""
    p = paths()
    info = json.loads(p["json"].read_text(encoding="utf-8")) if p["json"].exists() else {}
    have = p["xml"].exists()
    if have and not force:
        checked = datetime.strptime(info.get("checked", info.get("downloaded", "2000-01-01 00:00")), "%Y-%m-%d %H:%M")
        if datetime.now() - checked < timedelta(hours=MAX_AGE_HOURS):
            return p["xml"].read_bytes(), info, False
    headers = dict(HEADERS)
    if have and info.get("etag"):
        headers["If-None-Match"] = info["etag"]
    if have and info.get("last_modified"):
        headers["If-Modified-Since"] = info["last_modified"]
    try:
        with urllib.request.urlopen(urllib.request.Request(DGM1_URL, headers=headers), timeout=60) as r:
            body = r.read()
            info = {"url": DGM1_URL, "downloaded": _now(), "checked": _now(),
                    "last_modified": r.headers.get("Last-Modified"), "etag": r.headers.get("ETag")}
    except urllib.error.HTTPError as e:
        if e.code != 304:
            raise
        info["checked"] = _now()                              # 304: our copy is current
        p["json"].write_text(json.dumps(info, indent=1), encoding="utf-8")
        return p["xml"].read_bytes(), info, False
    except (urllib.error.URLError, TimeoutError) as e:
        if have:                                              # offline: work with what we have
            _say(f"server not reachable ({e}); using the local file list of {info.get('downloaded')}", Qgis.Warning)
            return p["xml"].read_bytes(), info, False
        raise
    p["xml"].write_bytes(body)
    p["json"].write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"file list downloaded: {len(body) / 1e6:.1f} MB, Last-Modified {info['last_modified']}")
    return body, info, True


def parse_listing(xml_bytes):
    """One dict per tile: key, file, year, e_km, n_km, size_bytes, timestamp. Stops on unknown names."""
    root = ET.fromstring(xml_bytes)
    rows, bad = [], []
    for f in root.iter("file"):
        name = f.get("name")
        m = NAME.match(name)
        if m is None:
            bad.append(name)
            continue
        e_km, n_km, year = (int(v) for v in m.group("e_km", "n_km", "year"))
        rows.append({"key": f"dgm1_32_{e_km}_{n_km}_1_nw", "file": name, "year": year, "e_km": e_km,
                     "n_km": n_km, "size_bytes": int(f.get("size")), "timestamp": f.get("timestamp")})
    if bad:
        raise ValueError(f"{len(bad)} names do not fit the DGM1 pattern, e.g. {bad[:3]}: has the server changed?")
    keys = [r["key"] for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("a tile appears twice in the file list")
    return rows


# ---- 2. the tile index (GeoPackage, same schema as geo0442) -----------------------------
def _index_info(gpkg):
    if not gpkg.exists():
        return {}
    ds = ogr.Open(str(gpkg))
    lyr = ds.GetLayerByName("index_info") if ds else None
    if lyr is None:
        return {}
    feat = lyr.GetNextFeature()
    return {} if feat is None else {k: feat.GetField(k) for k in feat.keys()}


def build_index(rows, info, gpkg):
    """Write layers dgm1_tiles (one 1 km square per tile) and index_info (where and when from)."""
    for suffix in ("", "-wal", "-shm"):
        Path(str(gpkg) + suffix).unlink(missing_ok=True)
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(str(gpkg))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(EPSG)
    lyr = ds.CreateLayer("dgm1_tiles", srs, ogr.wkbPolygon, options=["SPATIAL_INDEX=YES"])
    for name, kind in (("key", ogr.OFTString), ("file", ogr.OFTString), ("year", ogr.OFTInteger),
                       ("e_km", ogr.OFTInteger), ("n_km", ogr.OFTInteger), ("size_mb", ogr.OFTReal),
                       ("size_bytes", ogr.OFTInteger64), ("timestamp", ogr.OFTDateTime)):
        lyr.CreateField(ogr.FieldDefn(name, kind))
    defn = lyr.GetLayerDefn()
    lyr.StartTransaction()
    for r in rows:
        x0, y0 = r["e_km"] * TILE, r["n_km"] * TILE
        feat = ogr.Feature(defn)
        for k in ("key", "file", "year", "e_km", "n_km", "size_bytes", "timestamp"):
            feat.SetField(k, r[k])
        feat.SetField("size_mb", round(r["size_bytes"] / 1e6, 2))
        feat.SetGeometry(ogr.CreateGeometryFromWkt(
            f"POLYGON(({x0} {y0},{x0 + TILE} {y0},{x0 + TILE} {y0 + TILE},{x0} {y0 + TILE},{x0} {y0}))"))
        lyr.CreateFeature(feat)
    lyr.CommitTransaction()
    tab = ds.CreateLayer("index_info", None, ogr.wkbNone)
    fields = {"source": DGM1_URL, "last_modified": info.get("last_modified") or "", "etag": info.get("etag") or "",
              "downloaded": info.get("downloaded") or "", "tiles": len(rows), "licence": LICENCE}
    for k, v in fields.items():
        tab.CreateField(ogr.FieldDefn(k, ogr.OFTInteger if isinstance(v, int) else ogr.OFTString))
    feat = ogr.Feature(tab.GetLayerDefn())
    for k, v in fields.items():
        feat.SetField(k, v)
    tab.CreateFeature(feat)
    ds = None
    print(f"tile index written: {gpkg} ({len(rows)} tiles, {gpkg.stat().st_size / 1e6:.1f} MB)")


def refresh(force=False):
    """Check the file list (at most once per MAX_AGE_HOURS, or now with force=True); rebuild the index if needed.
    Returns the tiles as {key: row}."""
    p = paths()
    xml_bytes, info, changed = fetch_listing(force)
    rows = parse_listing(xml_bytes)
    old = _index_info(p["gpkg"])
    stale = (changed or not old or old.get("tiles") != len(rows)
             or (old.get("last_modified") or "") != (info.get("last_modified") or ""))
    if stale:
        layer = _find_layer()
        if layer is not None:                       # release the file before rewriting it
            QgsProject.instance().removeMapLayer(layer.id())
        build_index(rows, info, p["gpkg"])
    else:
        print(f"tile index is current ({len(rows)} tiles, file list of {info.get('last_modified')})")
    return {r["key"]: r for r in rows}


# ---- 3. the layer in QGIS ---------------------------------------------------------------
def _find_layer():
    gpkg = str(paths()["gpkg"])
    for layer in QgsProject.instance().mapLayers().values():
        if isinstance(layer, QgsVectorLayer) and layer.source().split("|")[0] == gpkg:
            return layer
    return None


def _style(layer):
    """Squares coloured by survey year, labels with the key when zoomed in."""
    years = sorted({int(v) for v in layer.uniqueValues(layer.fields().indexOf("year"))})
    colours = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725", "#f89540", "#cc4778"]
    cats = []
    for i, year in enumerate(years):
        sym = QgsFillSymbol.createSimple({"color": colours[i % len(colours)] + "40",
                                          "outline_color": "#555555", "outline_width": "0.1"})
        cats.append(QgsRendererCategory(year, sym, str(year)))
    layer.setRenderer(QgsCategorizedSymbolRenderer("year", cats))
    pal = QgsPalLayerSettings()
    pal.fieldName = "key"
    pal.placement = Qgis.LabelPlacement.OverPoint if hasattr(Qgis, "LabelPlacement") else QgsPalLayerSettings.OverPoint
    fmt = QgsTextFormat()
    fmt.setSize(8)
    pal.setFormat(fmt)
    pal.scaleVisibility = True
    pal.maximumScale = 1                          # QGIS: "maximum" = most zoomed in
    pal.minimumScale = 60000                      # labels only at 1:60 000 or closer
    layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))
    layer.setLabelsEnabled(True)


def index_layer():
    """The tile index layer in the current project (loaded and styled if it is not there yet)."""
    layer = _find_layer()
    if layer is None:
        layer = QgsVectorLayer(f"{paths()['gpkg']}|layername=dgm1_tiles", LAYER_NAME, "ogr")
        if not layer.isValid():
            raise RuntimeError(f"cannot open {paths()['gpkg']}")
        _style(layer)
        QgsProject.instance().addMapLayer(layer)
    return layer


# ---- 4. download the selected tiles -----------------------------------------------------
def download_tile(file, size_bytes, folder, progress=None):
    """Download one tile into `folder`: skip it if it is there with the right size; .part file, size check."""
    target = folder / file
    if target.exists() and target.stat().st_size == size_bytes:
        return "exists"
    part = target.with_name(target.name + ".part")
    req = urllib.request.Request(DGM1_URL + file, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r, open(part, "wb") as f:
        while chunk := r.read(1 << 16):                      # 64 KB pieces
            f.write(chunk)
            if progress:
                progress()
    if part.stat().st_size != size_bytes:
        raise IOError(f"{file}: {part.stat().st_size} bytes, the index says {size_bytes}")
    part.replace(target)
    return "downloaded"


def download_selected(layer=None, vrt_name=None, add_to_map=True):
    """Download the selected tiles of the index layer and add a VRT of them to the map. Returns the VRT path."""
    layer = layer or _find_layer() or index_layer()
    keys = sorted({f["key"] for f in layer.selectedFeatures()})
    if not keys:
        _say("no tiles selected: select tiles on the layer 'DGM1 tiles NRW' first", Qgis.Warning)
        return None
    if len(keys) > MAX_TILES:
        _say(f"{len(keys)} tiles selected, at most {MAX_TILES} per call (MAX_TILES)", Qgis.Warning)
        return None
    current = refresh()                                       # the names in the index may be outdated
    missing = [k for k in keys if k not in current]
    if missing:
        _say(f"not in the current file list: {missing}", Qgis.Warning)
    rows = [current[k] for k in keys if k in current]
    folder = paths()["original"]
    total = sum(r["size_bytes"] for r in rows) / 1e6
    print(f"{len(rows)} tiles, {total:.1f} MB -> {folder}")
    bar = None
    if iface is not None:
        from qgis.PyQt.QtWidgets import QProgressBar
        msg = iface.messageBar().createMessage("DGM1", f"downloading {len(rows)} tiles ({total:.0f} MB) ...")
        bar = QProgressBar()
        bar.setMaximum(len(rows))
        msg.layout().addWidget(bar)
        iface.messageBar().pushWidget(msg, Qgis.Info)
    files = []
    try:
        for i, r in enumerate(rows, 1):
            status = download_tile(r["file"], r["size_bytes"], folder, progress=QgsApplication.processEvents)
            print(f"  {r['file']}  {r['size_bytes'] / 1e6:5.2f} MB  {status}")
            files.append(str(folder / r["file"]))
            if bar is not None:
                bar.setValue(i)
            QgsApplication.processEvents()
    finally:
        if iface is not None:
            iface.messageBar().clearWidgets()
    if not files:
        return None
    vrt = folder / (vrt_name or f"dgm1_selection_{datetime.now():%Y%m%d_%H%M%S}.vrt")
    if not vrt.suffix:
        vrt = vrt.with_suffix(".vrt")
    cwd = os.getcwd()
    try:
        os.chdir(folder)                                      # relative paths in the VRT: the folder can move
        gdal.BuildVRT(vrt.name, [Path(f).name for f in files]).FlushCache()
    finally:
        os.chdir(cwd)
    if add_to_map:
        QgsProject.instance().addMapLayer(QgsRasterLayer(str(vrt), vrt.stem))
    _say(f"{len(files)} tiles ready, virtual raster {vrt.name} added", Qgis.Success)
    return vrt


def info():
    """Data folder, index date and size."""
    p = paths()
    meta = _index_info(p["gpkg"])
    print("data folder :", data_dir())
    print("tile index  :", p["gpkg"], "|", meta.get("tiles"), "tiles | file list of", meta.get("last_modified"))
    tifs = sorted(p["original"].glob("dgm1_32_*.tif"))
    print("tiles here  :", len(tifs), f"({sum(t.stat().st_size for t in tifs) / 1e6:.1f} MB)")


def main():
    refresh()
    layer = index_layer()
    if iface is not None:
        iface.setActiveLayer(layer)
    print("\nSelect tiles on the layer 'DGM1 tiles NRW', then type:  download_selected()")


main()      # runs when the console editor executes the file ("Run Script")
