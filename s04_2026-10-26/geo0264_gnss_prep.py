#!/usr/bin/env python
"""geo0264_gnss_prep – GPS pseudoranges as small tables for the geo0264 notebook.

All three data sources of geo0264 produce the SAME table (one row per satellite and epoch):

    time         epoch (GPS time, ISO text)          prn          satellite, G01 … G32
    x_m, y_m, z_m  satellite position at transmission, Earth-fixed frame at reception (ECEF, WGS 84)
    sat_clock_m  satellite clock error × c [m]: ADD it to the pseudorange
    tgd_m        group delay × c [m]: SUBTRACT it for single-frequency L1
    C1_m         pseudorange on L1 (C/A code) [m]
    C2_m         pseudorange on L2 [m] (code in column c2_code: C2W = P(Y), C2L = L2C)
    site         station / point name

and a reference table (site, X_m, Y_m, Z_m, frame, note) with the "true" antenna position.

Sources
-------
* ``sapos(date, stations)``  SAPOS NRW reference stations from the GPPS archive (open data,
  Geobasis NRW, dl-de/zero-2-0); truth = station coordinates (ETRS89).
* ``own(rinex, emlid_csv)``   your own raw data (RINEX 3) of an Emlid Reach RS2+, cut into one
  segment per surveyed point with the "Averaging start/end" times of the Emlid Flow CSV export;
  truth = the RTK fix of the point (ETRS89 with SAPOS) plus the antenna (pole) height.
* ``synthetic(orbits, …)``   artificial pseudoranges on REAL GPS orbits (taken from a sapos/own
  table) for a point you choose, with error terms you switch on and off; truth known exactly.

Navigation (broadcast ephemeris) for sapos/own: the receiver's own RINEX navigation file if you have
one, else the IGS daily file of the BKG (igs.bkg.bund.de, ~1.3 MB), else the SAPOS NRW daily
archive (~190 MB, contains BRDM00NRW).

Command line (teacher / curious students):
    python geo0264_gnss_prep.py sapos --date 2026-10-21 --stations 2578 2579 --step 300
    python geo0264_gnss_prep.py own --rinex group03.obs --emlid group03_emlid.csv --group group03 \
        --tz Europe/Berlin --base 2578 --out ~/shared/data/opengeo/geo0264/group03
Needs numpy, pandas, pyproj; `hatanaka` (pip) only for SAPOS files (Hatanaka-compressed RINEX).
Orbits and clocks: IS-GPS-200, Table 20-IV (as in every GPS receiver). R. Becker, CC BY-SA 4.0.
"""
import argparse
import gzip
import shutil
import urllib.request
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

C = 299_792_458.0
F1, F2 = 1575.42e6, 1227.60e6
MU = 3.986005e14            # GM for GPS (IS-GPS-200)
OMEGA_E = 7.2921151467e-5   # Earth rotation rate [rad/s]
F_REL = -4.442807633e-10    # relativistic clock constant [s/m^0.5]
GPS_EPOCH = datetime(1980, 1, 6)
GPS_UTC = 18                # leap seconds: GPS time = UTC + 18 s (since 2017)

HERE = Path(__file__).resolve().parent
CACHE = Path.home() / ".cache" / "geo0264"            # downloads (navigation, SAPOS archive)
SAPOS_URL = "https://www.opengeodata.nrw.de/produkte/geobasis/rb/sapos/gpps_archiv/{date}_NW.zip"
BKG_URL = "https://igs.bkg.bund.de/root_ftp/IGS/BRDC/{y}/{doy:03d}/BRDC00WRD_S_{y}{doy:03d}0000_01D_MN.rnx.gz"
COLUMNS = ["site", "time", "prn", "x_m", "y_m", "z_m", "sat_clock_m", "tgd_m", "C1_m", "C2_m", "c2_code"]


# ============================================================================================
# RINEX 3 readers (GPS only, minimal)
# ============================================================================================
def _f(s):
    s = s.strip().replace("D", "E").replace("d", "e")
    return float(s) if s else np.nan


def read_nav_gps(path):
    """GPS broadcast ephemerides of a RINEX 3 navigation file (plain or .gz) -> DataFrame."""
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", errors="replace") as fh:
        lines = fh.read().splitlines()
    i = next(k for k, l in enumerate(lines) if "END OF HEADER" in l) + 1
    names = ["af0", "af1", "af2", "IODE", "Crs", "dn", "M0", "Cuc", "e", "Cus", "sqrtA", "Toe", "Cic",
             "Omega0", "Cis", "i0", "Crc", "omega", "OmegaDot", "IDOT", "codes", "week", "L2P", "acc",
             "health", "TGD", "IODC", "ttm", "fit", "spare"]
    rec = []
    while i < len(lines):
        l = lines[i]
        if l.startswith("G") and len(l) > 23 and l[3] == " ":
            b = lines[i:i + 8]
            toc = datetime(int(b[0][4:8]), int(b[0][9:11]), int(b[0][12:14]), int(b[0][15:17]),
                           int(b[0][18:20]), int(b[0][21:23]))
            v = [_f(b[0][23 + 19 * k:42 + 19 * k]) for k in range(3)]
            for row in b[1:]:
                v += [_f(row[4 + 19 * k:23 + 19 * k]) for k in range(4)]
            d = dict(zip(names, v))
            d["sv"], d["toc"] = b[0][:3], toc
            rec.append(d)
            i += 8
        else:
            i += 1
    nav = pd.DataFrame(rec)
    return nav[nav["health"] == 0].reset_index(drop=True)


def read_obs_gps(path, step=None, t_from=None, t_to=None):
    """GPS pseudoranges of a RINEX 3 observation file -> DataFrame (time, prn, C1_m, C2_m, c2_code).
    step: keep epochs whose second of day is a multiple of step; t_from/t_to: GPS-time window."""
    with open(path, errors="replace") as fh:
        hdr, types, cur = [], {}, None
        for line in fh:
            if "SYS / # / OBS TYPES" in line:
                if line[0] != " ":
                    cur = line[0]
                    types[cur] = line[7:60].split()
                else:
                    types[cur] += line[7:60].split()
            if "END OF HEADER" in line:
                break
        g = types.get("G", [])
        if "C1C" not in g:
            raise ValueError(f"{path}: no GPS L1 C/A pseudoranges (C1C) in the file")
        c2 = next((c for c in ("C2W", "C2L", "C2X", "C2S") if c in g), None)
        k1, k2 = g.index("C1C"), (g.index(c2) if c2 else None)
        rows, take, skip, t = [], False, 0, None
        for line in fh:
            if skip:                                        # header records inside the file
                skip -= 1
                continue
            if line.startswith(">"):
                flag, n = int(line[31]), int(line[32:35])
                if flag > 1:
                    take, skip = False, n
                    continue
                f = line[2:29].split()
                sec = float(f[5])
                t = datetime(*(int(x) for x in f[:5])) + timedelta(seconds=sec)
                sod = t.hour * 3600 + t.minute * 60 + sec
                take = (flag == 0 and (step is None or abs(sod / step - round(sod / step)) < 1e-6)
                        and (t_from is None or t >= t_from) and (t_to is None or t <= t_to))
                continue
            if take and line.startswith("G"):
                def val(k):
                    s = line[3 + 16 * k:3 + 16 * k + 14] if k is not None else ""
                    return float(s) if s.strip() else np.nan
                rows.append(dict(time=t, prn=line[:3], C1_m=val(k1), C2_m=val(k2), c2_code=c2 or ""))
    return pd.DataFrame(rows)


def read_header(path):
    """Marker name and APPROX POSITION XYZ of a RINEX observation file."""
    name, xyz = None, None
    with open(path, errors="replace") as fh:
        for line in fh:
            if "MARKER NAME" in line:
                name = line[:60].strip()
            if "APPROX POSITION XYZ" in line:
                xyz = [float(x) for x in line[:42].split()]
            if "END OF HEADER" in line:
                break
    return name, xyz


# ============================================================================================
# satellite position and clock from the broadcast ephemeris (IS-GPS-200, Table 20-IV)
# ============================================================================================
def gps_sow(t):
    dt = t - GPS_EPOCH
    return (dt.days % 7) * 86400 + dt.seconds + dt.microseconds * 1e-6


def _wrap(tk):
    return tk - 604800 if tk > 302400 else tk + 604800 if tk < -302400 else tk


def sat_pos_clock(e, t_tx):
    """ECEF position at t_tx (seconds of GPS week) and clock offset [s] without TGD."""
    A = e["sqrtA"] ** 2
    n = np.sqrt(MU / A ** 3) + e["dn"]
    tk = _wrap(t_tx - e["Toe"])
    M = e["M0"] + n * tk
    E = M
    for _ in range(10):
        E = M + e["e"] * np.sin(E)
    nu = np.arctan2(np.sqrt(1 - e["e"] ** 2) * np.sin(E), np.cos(E) - e["e"])
    phi = nu + e["omega"]
    s2, c2 = np.sin(2 * phi), np.cos(2 * phi)
    u = phi + e["Cus"] * s2 + e["Cuc"] * c2
    r = A * (1 - e["e"] * np.cos(E)) + e["Crs"] * s2 + e["Crc"] * c2
    i = e["i0"] + e["Cis"] * s2 + e["Cic"] * c2 + e["IDOT"] * tk
    x, y = r * np.cos(u), r * np.sin(u)
    Om = e["Omega0"] + (e["OmegaDot"] - OMEGA_E) * tk - OMEGA_E * e["Toe"]
    pos = np.array([x * np.cos(Om) - y * np.cos(i) * np.sin(Om),
                    x * np.sin(Om) + y * np.cos(i) * np.cos(Om), y * np.sin(i)])
    tc = _wrap(t_tx - gps_sow(e["toc"]))
    dts = e["af0"] + e["af1"] * tc + e["af2"] * tc ** 2 + F_REL * e["e"] * e["sqrtA"] * np.sin(E)
    return pos, dts


def add_satellites(obs, nav):
    """Pseudorange table (time, prn, C1_m, C2_m, c2_code) -> full geo0264 table."""
    by_sv = {sv: g for sv, g in nav.groupby("sv")}
    out = []
    for o in obs.itertuples():
        if np.isnan(o.C1_m) or o.prn not in by_sv:
            continue
        sub = by_sv[o.prn]
        k = (sub["toc"] - o.time).abs().idxmin()
        if abs((sub.loc[k, "toc"] - o.time).total_seconds()) > 7200:
            continue
        e = sub.loc[k]
        t_rx = gps_sow(o.time)
        t_tx = t_rx - o.C1_m / C
        for _ in range(3):                                  # satellite clock -> GPS transmission time
            pos, dts = sat_pos_clock(e, t_tx)
            t_tx = t_rx - o.C1_m / C - dts
        pos, dts = sat_pos_clock(e, t_tx)
        a = OMEGA_E * o.C1_m / C                            # Earth rotation during the travel time
        out.append(dict(time=o.time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4], prn=o.prn,
                        x_m=round(np.cos(a) * pos[0] + np.sin(a) * pos[1], 3),
                        y_m=round(-np.sin(a) * pos[0] + np.cos(a) * pos[1], 3), z_m=round(pos[2], 3),
                        sat_clock_m=round(C * dts, 3), tgd_m=round(C * e["TGD"], 3),
                        C1_m=o.C1_m, C2_m=o.C2_m, c2_code=o.c2_code))
    return pd.DataFrame(out)


# ============================================================================================
# navigation files
# ============================================================================================
def navigation(day, nav=None):
    """Broadcast ephemeris for a day (datetime.date or 'YYYY-MM-DD'): own file, BKG, SAPOS."""
    if nav:
        return read_nav_gps(nav)
    day = pd.Timestamp(day)
    doy = day.dayofyear
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"BRDC00WRD_S_{day.year}{doy:03d}0000_01D_MN.rnx.gz"
    try:
        if not f.exists():
            urllib.request.urlretrieve(BKG_URL.format(y=day.year, doy=doy), f)
        return read_nav_gps(f)
    except Exception as err:                                # BKG not reachable: SAPOS archive
        print("BKG navigation not available (", err, "), using the SAPOS archive")
        z = sapos_zip(day.strftime("%Y-%m-%d"))
        name = f"BRDM00NRW_S_{day.year}{doy:03d}0000_01D_MN.rnx"
        with zipfile.ZipFile(z) as zf:
            zf.extract(name, CACHE)
        return read_nav_gps(CACHE / name)


def sapos_zip(date):
    CACHE.mkdir(parents=True, exist_ok=True)
    z = CACHE / f"{date}_NW.zip"
    if not z.exists():
        print("downloading", z.name, "(~190 MB, once)")
        urllib.request.urlretrieve(SAPOS_URL.format(date=date), z)
    return z


# ============================================================================================
# the three sources
# ============================================================================================
def sapos(date="2026-10-21", stations=("2578", "2579"), step=300, out=None, t_from=None, t_to=None):
    """SAPOS NRW stations -> (table, reference). Writes CSVs to out if given."""
    import hatanaka
    doy = pd.Timestamp(date).dayofyear
    stem = f"{date[:4]}{doy:03d}0000_01D"
    z = sapos_zip(date)
    tabs, refs = [], []
    with zipfile.ZipFile(z) as zf:
        navname = f"BRDM00NRW_S_{stem}_MN.rnx"               # navigation of the archive itself
        zf.extract(navname, CACHE)
        nav = read_nav_gps(CACHE / navname)
        for st in stations:
            name = f"{st}00DEU_S_{stem}_15S_MO.crx"
            rnx = CACHE / name.replace(".crx", ".rnx")
            if not rnx.exists():
                zf.extract(name, CACHE)
                hatanaka.decompress_on_disk(CACHE / name)
            _, xyz = read_header(rnx)
            df = add_satellites(read_obs_gps(rnx, step=step, t_from=t_from, t_to=t_to), nav)
            df.insert(0, "site", st)
            tabs.append(df)
            refs.append(dict(site=st, X_m=xyz[0], Y_m=xyz[1], Z_m=xyz[2], frame="ETRS89",
                             note="SAPOS station coordinates (ARP)"))
    tab, ref = pd.concat(tabs, ignore_index=True)[COLUMNS], pd.DataFrame(refs)
    if out:
        _write(tab, ref, out, f"geo0264_sapos_{date}")
    return tab, ref


def read_emlid(path, tz_default="UTC"):
    """Emlid Flow CSV export ('All columns') -> points with ETRS89 position and averaging window in
    GPS time. Times like '2026-11-02 10:21:33.4 UTC+01:00'; without an offset tz_default is used."""
    pts = pd.read_csv(path, sep=None, engine="python", dtype={"Name": str})

    def to_gps(s):
        s = str(s).replace(" UTC", "").replace("UTC", "").strip()
        t = pd.Timestamp(s)
        t = t.tz_localize(tz_default) if t.tzinfo is None else t
        return (t.tz_convert("UTC").tz_localize(None) + pd.Timedelta(seconds=GPS_UTC)).to_pydatetime()
    pts["start_gps"] = pts["Averaging start"].map(to_gps)
    pts["end_gps"] = pts["Averaging end"].map(to_gps)
    return pts


def own(rinex, emlid_csv, nav=None, step=1, tz_default="UTC", out=None, group="own", base=None):
    """Own Reach RS2+ raw data + Emlid Flow CSV -> (table, reference), one site per surveyed point.
    Reference = RTK point (ground) + antenna height along the ellipsoid normal (antenna position).
    base: SAPOS station number (e.g. "2578" Wesel) added as a reference station for the same times
    (needs the SAPOS archive of the day, ~190 MB, and `hatanaka`)."""
    from pyproj import Transformer
    pts = read_emlid(emlid_csv, tz_default)
    to_xyz = Transformer.from_crs(4937, 4936, always_xy=True)   # ETRS89 lon/lat/h -> X/Y/Z
    t0, t1 = pts["start_gps"].min(), pts["end_gps"].max()
    navdf = navigation(t0.date(), nav)
    obs = read_obs_gps(rinex, step=step, t_from=t0, t_to=t1)
    tab = add_satellites(obs, navdf)
    tab["t"] = pd.to_datetime(tab["time"])
    tabs, refs = [], []
    for p in pts.itertuples():
        seg = tab[(tab["t"] >= p.start_gps) & (tab["t"] <= p.end_gps)].drop(columns="t").copy()
        if seg.empty:
            print(f"point {p.Name}: no raw epochs between {p.start_gps} and {p.end_gps} (GPS time) – "
                  "check the time zone (tz_default) and that the raw log covers the point")
            continue
        seg.insert(0, "site", str(p.Name))
        tabs.append(seg)
        hant = float(pts.loc[p.Index, "Antenna height"])          # pole height (metres in Emlid Flow)
        lon, lat, h = (float(pts.loc[p.Index, c]) for c in ("Longitude", "Latitude", "Ellipsoidal height"))
        X, Y, Z = to_xyz.transform(lon, lat, h + hant)
        refs.append(dict(site=str(p.Name), X_m=X, Y_m=Y, Z_m=Z, frame="ETRS89",
                         note=f"RTK {pts.loc[p.Index, 'Solution status']}, antenna height {hant:.3f} m added"))
    if base:
        date = t0.strftime("%Y-%m-%d")
        btab, bref = sapos(date, [str(base)], step=None, t_from=t0, t_to=t1)
        tabs.append(btab)
        refs += bref.to_dict("records")
    tab, ref = pd.concat(tabs, ignore_index=True)[COLUMNS], pd.DataFrame(refs)
    if out:
        _write(tab, ref, out, f"geo0264_{group}")
    return tab, ref


ERRORS = {   # defaults of synthetic(): size of each error term (0 switches it off)
    "receiver_clock_us": 0.1,     # receiver clock offset [µs]
    "noise_m": 0.5,               # code noise (1 sigma) [m]
    "multipath_m": 1.0,           # multipath at 10° elevation (1 sigma), falls off towards the zenith [m]
    "iono_zenith_m": 3.0,         # ionospheric delay on L1 at the zenith [m]
    "tropo_zenith_m": 2.3,        # tropospheric delay at the zenith [m]
    "orbit_clock_m": 1.0,         # satellite orbit + clock error (1 sigma per satellite) [m]
}


def elevation(sat, X):
    los = sat - X
    up = X / np.linalg.norm(X)
    return np.degrees(np.arcsin((los @ up) / np.linalg.norm(los, axis=1)))


def synthetic(orbits, lon=6.548, lat=51.493, h=80.0, errors=None, base=None, seed=1, mask=0.0):
    """Artificial pseudoranges on real orbits.
    orbits: a geo0264 table (satellite positions and clocks are reused, its pseudoranges are not).
    errors: dict overriding ERRORS; base: optional (lon, lat, h) of a second, 'reference' point that
    shares the satellite errors (orbit/clock, atmosphere) but has its own clock, noise, multipath.
    Returns (table, reference) like the other sources; sites 'rover' (and 'base')."""
    from pyproj import Transformer
    err = {**ERRORS, **(errors or {})}
    rng = np.random.default_rng(seed)
    to_xyz = Transformer.from_crs(4937, 4936, always_xy=True)
    orb = orbits.drop_duplicates(["time", "prn"]).copy()
    sat_err = {p: rng.normal(0, 1) * err["orbit_clock_m"] for p in orb["prn"].unique()}
    epochs = sorted(orb["time"].unique())
    tabs, refs = [], []
    for site, (lo, la, hh) in [("rover", (lon, lat, h))] + ([("base", base)] if base else []):
        X = np.array(to_xyz.transform(lo, la, hh))
        refs.append(dict(site=site, X_m=X[0], Y_m=X[1], Z_m=X[2], frame="synthetic (exact)",
                         note=f"lon {lo}, lat {la}, h {hh} m"))
        clk = err["receiver_clock_us"] * 1e-6 * C * rng.choice([-1, 1])
        rows = []
        for k, t in enumerate(epochs):
            g = orb[orb["time"] == t]
            sat = g[["x_m", "y_m", "z_m"]].to_numpy()
            el = elevation(sat, X)
            keep = el > mask
            r = np.linalg.norm(sat - X, axis=1)
            sinel = np.sin(np.radians(np.clip(el, 3, 90)))
            iono_map = 1 / np.sqrt(1 - (0.94 * np.cos(np.radians(el))) ** 2)   # thin-shell obliquity
            I1 = err["iono_zenith_m"] * iono_map * (1 + 0.3 * np.sin(2 * np.pi * k / max(len(epochs), 1)))
            T = err["tropo_zenith_m"] / sinel
            mp = err["multipath_m"] * np.sin(np.radians(10)) / sinel * rng.normal(0, 1, len(g))
            common = r + clk - g["sat_clock_m"].to_numpy() + np.array([sat_err[p] for p in g["prn"]]) + T + mp
            c1 = common + I1 + rng.normal(0, err["noise_m"], len(g))
            c2 = common + I1 * (F1 / F2) ** 2 + rng.normal(0, err["noise_m"], len(g))
            rows.append(pd.DataFrame(dict(site=site, time=t, prn=g["prn"].to_numpy(), x_m=g["x_m"].to_numpy(),
                                          y_m=g["y_m"].to_numpy(), z_m=g["z_m"].to_numpy(),
                                          sat_clock_m=g["sat_clock_m"].to_numpy(), tgd_m=0.0,
                                          C1_m=np.round(c1, 3), C2_m=np.round(c2, 3), c2_code="synthetic"))[keep])
        tabs.append(pd.concat(rows, ignore_index=True))
    return pd.concat(tabs, ignore_index=True)[COLUMNS], pd.DataFrame(refs)


def _write(tab, ref, out, stem):
    out = Path(out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    tab.to_csv(out / f"{stem}.csv", index=False)
    ref.to_csv(out / f"{stem}_reference.csv", index=False)
    print(f"wrote {out / (stem + '.csv')} ({tab['time'].nunique()} epochs, {tab['site'].nunique()} sites) "
          f"and {stem}_reference.csv")


def load(path):
    """Read a geo0264 table and its reference file (…_reference.csv next to it)."""
    path = Path(path)
    tab = pd.read_csv(path, dtype={"site": str})
    ref = pd.read_csv(path.with_name(path.stem + "_reference.csv"), dtype={"site": str})
    return tab, ref


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("sapos")
    a.add_argument("--date", default="2026-10-21")
    a.add_argument("--stations", nargs="+", default=["2578", "2579"])
    a.add_argument("--step", type=int, default=300)
    a.add_argument("--out", default=str(HERE / "data" / "geo0264"))
    b = sub.add_parser("own")
    b.add_argument("--rinex", required=True)
    b.add_argument("--emlid", required=True)
    b.add_argument("--nav")
    b.add_argument("--step", type=int, default=1)
    b.add_argument("--tz", default="UTC", help="time zone of Emlid times without offset, e.g. Europe/Berlin")
    b.add_argument("--group", default="own")
    b.add_argument("--base", help="SAPOS station number as reference station, e.g. 2578 (Wesel)")
    b.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "sapos":
        sapos(args.date, args.stations, args.step, args.out)
    else:
        own(args.rinex, args.emlid, args.nav, args.step, args.tz, args.out, args.group, args.base)
