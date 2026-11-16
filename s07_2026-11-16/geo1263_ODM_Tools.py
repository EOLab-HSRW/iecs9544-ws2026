"""geo1263_ODM_Tools - given tools for the exercise geo1263 (WebODM results and accuracy).

Import in the notebook:  import geo1263_ODM_Tools as ot   (keep this file next to the notebook)

* read_emlid(...)        Emlid Flow CSV export(s) -> GeoDataFrame (EPSG:25832, H = DHHN2016)
* to_ellipsoidal / to_dhhn   DHHN2016 height H <-> ellipsoidal height h (quasigeoid GCG2016, PROJ)
* write_geo_txt(...)     camera positions (e.g. after PPK) -> ODM image geolocation file geo.txt
* WebODM                 small client for the WebODM REST API (login, project, task, wait, download)
* read_points(...)       RTK points of the field day (GeoPackage with the layers of WebODM) -> one table
* sample_dsm(...)        height of a DSM/DTM at points (median in a small window)
* sample_bilinear(...)   height of a coarse grid (e.g. DGM1, 1 m) at points, bilinear interpolation
* nrw_tile(...)          DGM1/DOM1 tile of Geobasis NRW, downloaded once
* stats(...)             mean, std, RMSE, n of a column, optionally per group
* check_points, check_heights, check_stats, check_errors   checks for your answers

Sources: OpenDroneMap docs (docs.opendronemap.org: gcp, geo, arguments), WebODM API docs
(docs.webodm.org/api), PROJ grid de_bkg_gcg2016.tif (BKG, via cdn.proj.org), Geobasis NRW
(opengeodata.nrw.de, dl-de/zero-2-0). R. Becker, EOLab-HSRW, CC BY-SA 4.0.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

CRS = "EPSG:25832"                       # ETRS89 / UTM zone 32N
CRS_H = "EPSG:25832+7837"                # + DHHN2016 height (what Emlid Flow gives us)
CRS_h = "EPSG:4937"                      # ETRS89 geographic 3D (ellipsoidal height)
GRID = "de_bkg_gcg2016.tif"              # German quasigeoid GCG2016 (BKG), PROJ CDN

# Emlid Flow CSV export: our names -> possible column names (first match wins).
# Checked against the Emlid community docs; compare with your own export.
EMLID_COLS = {
    "name": ["Name"], "E": ["Easting"], "N": ["Northing"], "H": ["Elevation"],
    "h": ["Ellipsoidal height"], "status": ["Solution status"], "correction": ["Correction type"],
    "rms_E": ["Easting RMS"], "rms_N": ["Northing RMS"], "rms_H": ["Elevation RMS"],
    "antenna": ["Antenna height"], "start": ["Averaging start"],
}

# ODM options we keep the same for every task of the comparison (docs.opendronemap.org/arguments)
OPTIONS = {"dsm": True, "dtm": True, "auto-boundary": True}


# ---------------------------------------------------------------------------------------------
# RTK points
# ---------------------------------------------------------------------------------------------
def read_emlid(paths):
    """One or more Emlid Flow CSV exports -> GeoDataFrame with the columns name, E, N, H (+ the
    optional ones of EMLID_COLS that exist) and file; geometry in EPSG:25832.
    Names are kept as text (G1, C2, B1b, ...)."""
    import geopandas as gpd
    if isinstance(paths, (str, Path)):
        paths = [paths]
    frames = []
    for p in paths:
        raw = pd.read_csv(p, dtype={"Name": str})
        out = pd.DataFrame()
        for key, cands in EMLID_COLS.items():
            col = next((c for c in cands if c in raw.columns), None)
            if col is not None:
                out[key] = raw[col]
            elif key in ("name", "E", "N", "H"):
                raise KeyError(f"{Path(p).name}: no column {cands} - is this an Emlid Flow CSV export?")
        out["file"] = Path(p).name
        frames.append(out)
    df = pd.concat(frames, ignore_index=True)
    df["name"] = df["name"].astype(str).str.strip()
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["E"], df["N"]), crs=CRS)


def fix_only(gdf):
    """Keep the points with solution status FIX (if the column exists)."""
    if "status" not in gdf:
        return gdf
    keep = gdf["status"].astype(str).str.upper().str.startswith("FIX")
    if (~keep).any():
        print("left out (no FIX):", ", ".join(gdf.loc[~keep, "name"]))
    return gdf[keep].copy()


# ---------------------------------------------------------------------------------------------
# heights
# ---------------------------------------------------------------------------------------------
def _grid_ready():
    """Make sure PROJ has the GCG2016 grid: network on, else download it once into the PROJ user dir."""
    import pyproj
    folder = Path(pyproj.datadir.get_user_data_dir(True))
    f = folder / GRID
    if not f.exists():
        try:
            urllib.request.urlretrieve("https://cdn.proj.org/" + GRID, f)
        except OSError as e:
            raise RuntimeError(f"PROJ grid {GRID} missing and not downloadable ({e}); "
                               "ask your teacher for the file") from e
    return f


def to_ellipsoidal(E, N, H):
    """DHHN2016 heights H at E, N (EPSG:25832) -> ellipsoidal heights h (ETRS89, GRS80)."""
    from pyproj import Transformer
    _grid_ready()
    t = Transformer.from_crs(CRS_H, CRS_h, always_xy=True)
    _, _, h = t.transform(np.asarray(E, float), np.asarray(N, float), np.asarray(H, float))
    if not np.all(np.isfinite(h)):
        raise RuntimeError("height transformation failed (PROJ grid not found?)")
    return h


def to_dhhn(E, N, h):
    """Ellipsoidal heights h at E, N (EPSG:25832) -> DHHN2016 heights H."""
    from pyproj import Transformer
    _grid_ready()
    lon, lat = Transformer.from_crs(CRS, "EPSG:4258", always_xy=True).transform(E, N)
    t = Transformer.from_crs(CRS_h, CRS_H, always_xy=True)
    _, _, H = t.transform(lon, lat, np.asarray(h, float))
    if not np.all(np.isfinite(H)):
        raise RuntimeError("height transformation failed (PROJ grid not found?)")
    return H


# ---------------------------------------------------------------------------------------------
# ODM input files
# ---------------------------------------------------------------------------------------------
def write_geo_txt(path, images, E, N, z, crs=CRS, acc_h=None, acc_v=None):
    """ODM image geolocation file (docs.opendronemap.org/geo): first line the CRS, then
    image_name geo_x geo_y geo_z [yaw pitch roll horz_accuracy vert_accuracy] (accuracies in m;
    angles are written as 0, ODM uses them only for radiometric calibration)."""
    lines = [crs]
    for k, img in enumerate(images):
        row = f"{img} {E[k]:.3f} {N[k]:.3f} {z[k]:.3f}"
        if acc_h is not None:
            row += f" 0 0 0 {acc_h:.3f} {acc_v if acc_v is not None else acc_h:.3f}"
        lines.append(row)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return Path(path)


def read_gcp_list(path):
    """gcp_list.txt (header + geo_x geo_y geo_z im_x im_y image [name]) -> (crs, DataFrame)."""
    txt = Path(path).read_text(encoding="utf-8").strip().splitlines()
    rows = [ln.split() for ln in txt[1:] if ln.strip()]
    df = pd.DataFrame([r[:7] + [""] * (7 - len(r[:7])) for r in rows],
                      columns=["E", "N", "H", "im_x", "im_y", "image", "name"])
    for c in ("E", "N", "H", "im_x", "im_y"):
        df[c] = df[c].astype(float)
    return txt[0].strip(), df


# ---------------------------------------------------------------------------------------------
# WebODM REST API (docs.webodm.org/api; partial upload + commit as in the WebODM web interface)
# ---------------------------------------------------------------------------------------------
STATUS = {10: "queued", 20: "running", 30: "failed", 40: "completed", 50: "cancelled"}


class WebODM:
    """Minimal WebODM client.

        odm = WebODM("https://odm.eolab.de")
        odm.login(user)                        # asks for the password (getpass)
        pid = odm.project("group03")
        tid = odm.task(pid, files, name="F2a_gcp", options=OPTIONS)
        odm.wait(pid, tid)
        odm.download(pid, tid, folder)
    """

    def __init__(self, url="https://odm.eolab.de"):
        self.url = url.rstrip("/") + "/api"
        self.headers = {}

    def login(self, user, password=None):
        import getpass
        import requests
        password = password or getpass.getpass(f"WebODM password for {user}: ")
        r = requests.post(self.url + "/token-auth/", data={"username": user, "password": password}, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"login failed ({r.status_code}): {r.text[:200]}")
        self.headers = {"Authorization": "JWT " + r.json()["token"]}
        return self

    def _get(self, path, **kw):
        import requests
        r = requests.get(self.url + path, headers=self.headers, timeout=120, **kw)
        r.raise_for_status()
        return r

    def _post(self, path, **kw):
        import requests
        r = requests.post(self.url + path, headers=self.headers, timeout=600, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"POST {path}: {r.status_code} {r.text[:300]}")
        return r.json()

    def project(self, name):
        """Id of the project `name` (created if it does not exist)."""
        for p in self._get("/projects/", params={"name": name}).json():
            if p["name"] == name:
                return p["id"]
        return self._post("/projects/", data={"name": name})["id"]

    def tasks(self, pid):
        """Tasks of a project as a DataFrame (id, name, status, images, created)."""
        rows = [dict(id=t["id"], name=t["name"], status=STATUS.get(t["status"], t["status"]),
                     images=t.get("images_count"), created=t.get("created_at"))
                for t in self._get(f"/projects/{pid}/tasks/").json()]
        return pd.DataFrame(rows)

    def task(self, pid, files, name, options=None, batch=10):
        """Create a task from image files (+ gcp_list.txt / geo.txt) and start it.
        Uploads in batches of `batch` files (partial task, upload, commit), so that large photo
        sets do not hit the upload limit of the web server. Returns the task id."""
        opts = [{"name": k, "value": v} for k, v in (options or OPTIONS).items()]
        files = [Path(f) for f in files]
        t = self._post(f"/projects/{pid}/tasks/",
                       data={"name": name, "options": json.dumps(opts), "partial": "true"})
        for i in range(0, len(files), batch):
            part = files[i:i + batch]
            handles = [("images", (f.name, open(f, "rb"))) for f in part]
            try:
                self._post(f"/projects/{pid}/tasks/{t['id']}/upload/", files=handles)
            finally:
                for _, (_, fh) in handles:
                    fh.close()
            print(f"uploaded {min(i + batch, len(files))}/{len(files)}", end="\r")
        self._post(f"/projects/{pid}/tasks/{t['id']}/commit/")
        print(f"\ntask {name} ({t['id']}) started")
        return t["id"]

    def info(self, pid, tid):
        return self._get(f"/projects/{pid}/tasks/{tid}/").json()

    def wait(self, pid, tid, every=30):
        """Poll until the task is completed (returns the task info) or failed/cancelled (error)."""
        while True:
            t = self.info(pid, tid)
            st = t["status"]
            print(f"{t['name']}: {STATUS.get(st, st)}, {t.get('running_progress', 0) * 100:.0f} %   ", end="\r")
            if st == 40:
                print()
                return t
            if st in (30, 50):
                raise RuntimeError(f"task {t['name']} {STATUS[st]}: {t.get('last_error')}")
            time.sleep(every)

    def download(self, pid, tid, folder, assets=("orthophoto.tif", "dsm.tif", "dtm.tif", "report.pdf")):
        """Download the assets that exist for this task into `folder`; returns the paths."""
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        have = set(self.info(pid, tid).get("available_assets", []))
        out = []
        for a in assets:
            if have and a not in have:
                print("not available:", a)
                continue
            r = self._get(f"/projects/{pid}/tasks/{tid}/download/{a}", stream=True)
            with open(folder / a, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
            out.append(folder / a)
            print("saved", folder / a)
        return out


# ---------------------------------------------------------------------------------------------
# rasters
# ---------------------------------------------------------------------------------------------
def sample_dsm(path, E, N, radius=0.15):
    """Median of the raster `path` in a square of +- radius (m) around each point (E, N in the
    raster CRS, EPSG:25832 for ODM results with GCPs). NaN where the raster has no data."""
    import rasterio
    from rasterio.windows import from_bounds
    out = []
    with rasterio.open(path) as src:
        for e, n in zip(np.atleast_1d(E), np.atleast_1d(N)):
            w = from_bounds(e - radius, n - radius, e + radius, n + radius, src.transform).round_offsets().round_lengths()
            a = src.read(1, window=w, masked=True, boundless=True)
            out.append(float(np.ma.median(a)) if a.count() else np.nan)
    return np.array(out)


def nrw_tile(product, e_km, n_km, folder="data/original/nrw"):
    """DGM1 or DOM1 tile (product "dgm1" / "dom1") with lower left corner e_km, n_km (EPSG:25832, km),
    downloaded once from opengeodata.nrw.de (Geobasis NRW, dl-de/zero-2-0)."""
    base = f"https://www.opengeodata.nrw.de/produkte/geobasis/hm/{product}_tiff/{product}_tiff/"
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    hit = sorted(folder.glob(f"{product}_32_{e_km}_{n_km}_1_nw_*.tif"))
    if hit:
        return hit[-1]
    index = urllib.request.urlopen(base, timeout=60).read().decode("utf-8")
    name = re.search(rf'name="({product}_32_{e_km}_{n_km}_1_nw_\d{{4}}\.tif)"', index).group(1)
    urllib.request.urlretrieve(base + name, folder / name)
    return folder / name


def read_points(path):
    """RTK points of the field day: GeoPackage with one layer per point set (e.g. the WebODM
    overlays permanent_ground_markers and student_gcps) -> one GeoDataFrame (EPSG:25832) with
    id (P1.. / S3..), set, E, N, h (ellipsoidal), surface, solution, rms_lat, rms_h."""
    import geopandas as gpd
    import pyogrio
    parts = []
    for layer in pyogrio.list_layers(path)[:, 0]:
        g = gpd.read_file(path, layer=layer)
        prefix = "P" if layer.startswith("perm") else "S"
        parts.append(gpd.GeoDataFrame({
            "id": prefix + g["name"].astype(str), "set": layer, "E": g["E"], "N": g["N"],
            "h": g["h_ellipsoidal_m"], "surface": g.get("surface", "unknown"),
            "solution": g["solution"], "rms_lat": g["rms_lat_m"], "rms_h": g["rms_h_m"]},
            geometry=gpd.points_from_xy(g["E"], g["N"]), crs=CRS))
    return pd.concat(parts, ignore_index=True)


def sample_bilinear(path, E, N):
    """Bilinear interpolation of a raster (band 1) at points E, N (raster CRS). Use it for coarse
    grids like DGM1 (1 m), where the nearest cell can be 0.7 m away. NaN outside or at nodata."""
    import rasterio
    out = []
    with rasterio.open(path) as src:
        a = src.read(1, masked=True).astype(float).filled(np.nan)
        inv = ~src.transform
        shift = 0.5        # cell centres; GDAL reports corner-based transforms also for PixelIsPoint files
        for e, n in zip(np.atleast_1d(E), np.atleast_1d(N)):
            c, r = inv * (e, n)
            c, r = c - shift, r - shift
            c0, r0 = int(np.floor(c)), int(np.floor(r))
            if not (0 <= c0 < a.shape[1] - 1 and 0 <= r0 < a.shape[0] - 1):
                out.append(np.nan)
                continue
            fc, fr = c - c0, r - r0
            q = a[r0:r0 + 2, c0:c0 + 2]
            out.append(q[0, 0] * (1 - fc) * (1 - fr) + q[0, 1] * fc * (1 - fr)
                       + q[1, 0] * (1 - fc) * fr + q[1, 1] * fc * fr)
    return np.array(out)


def stats(df, col, by=None):
    """mean, std, RMSE = sqrt(mean(x^2)) and n of df[col], for all rows or per group `by`."""
    def one(x):
        x = x.dropna()
        return pd.Series({"n": len(x), "mean": x.mean(), "std": x.std(), "RMSE": np.sqrt((x ** 2).mean())})
    if by is None:
        return one(df[col]).to_frame("all").T
    return df.groupby(by)[col].apply(one).unstack()


# ---------------------------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------------------------
def _ok(cond, msg_ok, msg_bad):
    print(("OK: " + msg_ok) if cond else ("Not yet: " + msg_bad))
    return bool(cond)


def check_split(gcps, cps):
    """GCPs = G1..G5 (first round), check points = C1..C3, no overlap."""
    g, c = set(gcps["name"]), set(cps["name"])
    return (_ok(g == {f"G{i}" for i in range(1, 6)}, "5 GCPs", f"GCPs are {sorted(g)}, expected G1-G5 (round 1)")
            & _ok(c == {"C1", "C2", "C3"}, "3 check points", f"check points are {sorted(c)}, expected C1-C3")
            & _ok(not (g & c), "no point in both lists", "a point is in both lists"))


def check_errors(err, measured, rtk):
    """err: DataFrame with task, name, dE, dN, dH (map - RTK)."""
    m = measured.merge(rtk[["name", "E", "N", "H"]], on="name")
    ref = pd.DataFrame({"task": m["task"], "name": m["name"], "dE": m["E_map"] - m["E"],
                        "dN": m["N_map"] - m["N"], "dH": m["H_map"] - m["H"]})
    mine = err.set_index(["task", "name"]).sort_index()
    ref = ref.set_index(["task", "name"]).sort_index()
    if not _ok(mine.index.equals(ref.index), "one row per task and check point", "rows do not match: merge on 'name'"):
        return False
    d = (mine[["dE", "dN", "dH"]] - ref[["dE", "dN", "dH"]]).abs().to_numpy().max()
    return _ok(d < 1e-6, "differences map - RTK", "sign or columns: map minus RTK, E_map - E ...")


def check_points(pts):
    """31 points, ids unique, all FIX, lateral RMS below 3 cm."""
    return (_ok(len(pts) == 31, "31 points", f"{len(pts)} points, expected 31 (21 permanent + 10 students)")
            & _ok(pts["id"].is_unique, "ids unique", "ids not unique: use the prefix P / S")
            & _ok((pts["solution"] == "FIX").all() and (pts["rms_lat"] < 0.03).all(),
                  "all FIX, lateral RMS < 3 cm", "a point is not FIX or has RMS >= 3 cm"))


def check_heights(pts):
    """H = DHHN2016 from h with GCG2016, N_qg = h - H about 44.9 m at the Green Fab Lab."""
    ok = {"H", "N_qg"} <= set(pts.columns)
    if not _ok(ok, "columns H and N_qg", "add the columns H and N_qg"):
        return False
    ref = to_dhhn(pts["E"].to_numpy(), pts["N"].to_numpy(), pts["h"].to_numpy())
    return (_ok(np.allclose(pts["H"], ref, atol=1e-3), "H from to_dhhn", "H: use ot.to_dhhn(E, N, h)")
            & _ok(np.allclose(pts["N_qg"], pts["h"] - pts["H"]), "N_qg = h - H", "N_qg = h - H"))


def check_stats(table, df, col, by):
    """table from your own function: columns n, mean, std, RMSE per group."""
    ref = stats(df, col, by)
    try:
        a = table[["n", "mean", "std", "RMSE"]].sort_index().to_numpy(float)
        b = ref.sort_index().to_numpy(float)
    except (KeyError, TypeError, ValueError):
        return _ok(False, "", "columns n, mean, std, RMSE, one row per group")
    same = a.shape == b.shape and np.allclose(a, b, atol=1e-9, equal_nan=True)
    return _ok(same, "statistics per group", "compare RMSE = sqrt(mean(x**2)) and std (pandas: ddof=1)")

