# geo0921 Web services from GDI NRW in QGIS (WMS, WMTS, WFS, WCS)

**Tool:** QGIS as OGC client · **Time:** 45 min

Instead of downloading files you can ask a server for exactly the map section you are looking at. The standards of the **Open Geospatial Consortium (OGC)** make this work between any client and server:

| Service | Returns | Example from Geobasis NRW |
|---|---|---|
| **WMS** Web Map Service | a picture of the map (PNG/JPEG) for your extent | topographic maps (DTK), orthophotos (DOP) |
| **WMTS** Web Map Tile Service | pre-rendered tiles, fast | DOP, DTK collection |
| **WFS** Web Feature Service / OGC API Features | the vector features with attributes | administrative boundaries (DVG), buildings, parcels |
| **WCS** Web Coverage Service | raster *data* (values), e.g. elevation | digital terrain model |

## Files
| File | Use |
|---|---|
| `geo0921_NRW_WMS_Connections.xml`, `…_WFS_…`, `…_WCS_…` | connection lists of Geobasis NRW (state 2025) to import into QGIS |
| `geo0921_NRW_Web_Services_checkpoint.qgz` | districts + DTK (WMS) + DOP (WMS, switched off) + OSM |

## Steps
1. **Import the connections.** The connection lists are also on the Geobasis NRW site: [Webdienste](https://www.bezreg-koeln.nrw.de/geobasis-nrw/webdienste) ▸ [Geodatendienste](https://www.bezreg-koeln.nrw.de/geobasis-nrw/webdienste/geodatendienste) ▸ Downloads ▸ *Dateien zur Befüllung von Auswahllisten in QGIS* ([ZIP](https://www.bezreg-koeln.nrw.de/system/files/media/document/file/geobasis_geodatendienste_qgis_auswahl.zip)); the copies in this folder are `geo0921_NRW_*_Connections.xml`.
   *Layer ▸ Data Source Manager ▸ WMS/WMTS ▸ Load* → `geo0921_NRW_WMS_Connections.xml` → tick only what you need (below). Same for the tabs *WFS / OGC API - Features* and *WCS*. (Alternative: *Browser ▸ WMS/WMTS ▸ right-click ▸ Load Connections…*)
2. **Set the project CRS** to EPSG:25832 (*Project ▸ Properties ▸ CRS*).
3. **WMS – three background maps.** Select a connection ▸ *Connect* ▸ select the layer ▸ *Add*:
   - *NW Digitale Orthophotos (DOP) [WMS]* → *DOP Farbe*
   - *NW Digitale Topographische Karten; DTK Sammeldienst [WMS]* → *DTK Farbe*. Zoom in and out: the map changes its content with the scale.
   - *NW Digitales Geländemodell – Schummerung (DGM-Schummerung)* → *DGM Schummerung Graustufen NW*

   *Checkpoint:* `geo0921_NRW_Web_Services_checkpoint.qgz`.
4. Use *Identify* on the hillshade: what do you get back? Compare with *Identify* on a vector layer.
5. **Zoom in before you switch on WFS or WCS layers** (2–3 km across is enough): they send objects or values for the whole view, and a county-wide view means hundreds of thousands of buildings.
6. **WFS:** add *NW Topographische Sonderkarten; Verwaltungsgrenzen* (DVG via WFS), layer *Kreise*. Open the attribute table: these are real features. Compare with your downloaded DVG1 layer. Then try the ALKIS buildings around the campus; tick *Only request features overlapping the view extent*.
7. **WCS:** add the terrain model *NW Digitales Geländemodell (DGM); Höhenmodell des Landes NRW* and *Identify* a cell value (metres above sea level). Compare with the hillshade at the same spot.
8. Write down the **GetCapabilities** URL of one service and open it in a browser: what is in it?
9. *(Optional)* Save the WCS terrain model for a 2 km × 2 km area: right-click ▸ *Export ▸ Save As…* ▸ extent *Map Canvas Extent* ▸ GeoTIFF. Note the download date.

**Help:** QGIS manual, [19 Working with OGC / ISO protocols](https://docs.qgis.org/latest/en/docs/user_manual/working_with_ogc/ogc_client_support.html) · Geobasis NRW guides (German): [WMS](https://www.bezreg-koeln.nrw.de/system/files/media/document/file/geobasis_webdienste_anleitung_wms.pdf) · [WFS](https://www.bezreg-koeln.nrw.de/system/files/media/document/file/geobasis_webdienste_anleitung_wfs.pdf) · [WCS](https://www.bezreg-koeln.nrw.de/system/files/media/document/file/geobasis_webdienste_anleitung_wcs.pdf)

## Exercise
For your homework district: which services would you use for (a) a background map in a report, (b) counting buildings, (c) the elevation of a weather station? Justify with the table above.

## Check yourself
- Why can't you calculate an NDVI or an average elevation from a WMS layer – not even from the hillshade?
- What are the advantages and risks of using a service instead of a downloaded file in a project you have to hand in?
