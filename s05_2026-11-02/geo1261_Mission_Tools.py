"""Tools for geo1261 Mission plan (DJI Mavic 3M over the Green Fab Lab).

You do not have to write these functions: they are the reference implementation the notebook
uses from section 3 on, so that a mistake in an earlier exercise does not stop you. Read them
if you like - the stretch task asks you to write `flight_lines` yourself.

Same algorithm as `common.mission()` of the geo1260 slides.
"""
import numpy as np
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, Point, box

# DJI Mavic 3M specifications (ag.dji.com/mavic-3-m/specs)
CAMERAS = {
    "RGB": dict(px=(5280, 3956), fov=84.0, fov_over="diagonal", interval=0.7),
    "MS": dict(px=(2592, 1944), fov=61.2, fov_over="width", interval=2.0),
}
V_MAX = 15.0     # m/s, top speed used for mapping
TURN_S = 10.0    # s per turn between two lines (assumption)


def gsd(cam, height):
    """Ground sampling distance in metres: the ground one pixel covers."""
    c = CAMERAS[cam]
    w, h = c["px"]
    n = np.hypot(w, h) if c["fov_over"] == "diagonal" else w
    return 2 * height * np.tan(np.radians(c["fov"] / 2)) / n


def plan_numbers(cam, height, front=0.8, side=0.7):
    """GSD, footprint (across, along), line spacing, photo spacing (base) and speed for one camera."""
    g = gsd(cam, height)
    across, along = CAMERAS[cam]["px"][0] * g, CAMERAS[cam]["px"][1] * g   # long side across
    base = along * (1 - front)
    return dict(gsd=g, across=across, along=along, spacing=across * (1 - side), base=base,
                v=min(V_MAX, base / CAMERAS[cam]["interval"]))


def combined(height, cams=("RGB", "MS"), front=0.8, side=0.7):
    """Spacing, base and speed when several cameras record together: the smallest value wins."""
    ps = [plan_numbers(c, height, front, side) for c in cams]
    return {k: min(p[k] for p in ps) for k in ("spacing", "base", "v")}


def heading_of(area):
    """Direction of the long side of the area (minimum rotated rectangle), degrees from east."""
    rr = list(area.minimum_rotated_rectangle.exterior.coords)
    edges = [(rr[i], rr[i + 1]) for i in range(4)]
    (x0, y0), (x1, y1) = max(edges, key=lambda e: np.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
    return float(np.degrees(np.arctan2(y1 - y0, x1 - x0)))


def rectangle_size(area):
    """Length (along the heading) and width (across) of the minimum rotated rectangle, metres."""
    rr = list(area.minimum_rotated_rectangle.exterior.coords)
    a = np.hypot(rr[1][0] - rr[0][0], rr[1][1] - rr[0][1])
    b = np.hypot(rr[2][0] - rr[1][0], rr[2][1] - rr[1][1])
    return float(max(a, b)), float(min(a, b))


def flight_lines(area, spacing, heading):
    """Parallel lines `spacing` apart over the area, centred across it, every second one reversed.

    1 rotate the area so that the flight direction becomes the x axis,
    2 draw horizontal lines `spacing` apart, centred between the lowest and highest point,
    3 cut each line with the rotated area (keep the longest piece if it falls apart),
    4 reverse every second line (back and forth) and rotate everything back.
    """
    c0 = area.centroid
    rot = affinity.rotate(area, -heading, origin=c0)
    x0, y0, x1, y1 = rot.bounds
    n = max(1, int(np.ceil((y1 - y0) / spacing)))
    ys = (y0 + y1) / 2 + (np.arange(n) - (n - 1) / 2) * spacing
    lines = []
    for k, y in enumerate(ys):
        seg = LineString([(x0 - 1, y), (x1 + 1, y)]).intersection(rot)
        if seg.is_empty:
            continue
        if isinstance(seg, MultiLineString):
            seg = max(seg.geoms, key=lambda q: q.length)
        if k % 2:
            seg = LineString(list(seg.coords)[::-1])
        lines.append(affinity.rotate(seg, heading, origin=c0))
    return lines


def photo_positions(lines, base):
    """A photo every `base` metres along each line, starting at its start."""
    photos = []
    for ln in lines:
        m = int(np.floor(ln.length / base)) + 1
        photos += [ln.interpolate(min(i * base, ln.length)) for i in range(m)]
    return photos


def path_length(lines):
    """All lines plus the short connections from the end of one line to the start of the next."""
    return sum(ln.length for ln in lines) + sum(
        Point(lines[i].coords[-1]).distance(Point(lines[i + 1].coords[0])) for i in range(len(lines) - 1))


def flight_minutes(length, v, n_lines, turn_s=TURN_S):
    return (length / v + turn_s * (n_lines - 1)) / 60


def mission(area, height, cams=("RGB", "MS"), front=0.8, side=0.7):
    """The whole plan for one height and camera set, as one table row."""
    c = combined(height, cams, front, side)
    ls = flight_lines(area, c["spacing"], heading_of(area))
    return dict(height=height, cams="+".join(cams), gsd_rgb_cm=gsd("RGB", height) * 100,
                gsd_ms_cm=gsd("MS", height) * 100, spacing_m=c["spacing"], base_m=c["base"],
                v_ms=c["v"], lines=len(ls), photos=len(photo_positions(ls, c["base"])),
                minutes=flight_minutes(path_length(ls), c["v"], len(ls)))


def footprint(p, cam, height, heading):
    """Ground rectangle of one photo taken at point p (long side across the flight direction)."""
    n = plan_numbers(cam, height)
    r = box(p.x - n["along"] / 2, p.y - n["across"] / 2, p.x + n["along"] / 2, p.y + n["across"] / 2)
    return affinity.rotate(r, heading, origin=p)


# ---- checks for the exercises ------------------------------------------------------------------
def _ok(name, mine, ref, tol=1e-3):
    good = mine is not None and np.isclose(mine, ref, rtol=tol)
    print(f"{'OK ' if good else 'NOT YET'}  {name}: yours {mine if mine is None else round(float(mine), 4)}"
          + ("" if good else "  (check units, radians and which pixel count goes with the angle)"))
    return good


def check_gsd(f):
    """Compare your gsd(cam, height) with the reference at 100 m."""
    for cam in CAMERAS:
        try:
            mine = f(cam, 100)
        except Exception as e:                       # noqa: BLE001
            print(f"NOT YET  gsd('{cam}', 100): {type(e).__name__}: {e}")
            continue
        _ok(f"gsd('{cam}', 100) in m", mine, gsd(cam, 100))


def check_plan_numbers(f, height=25):
    """Compare your plan_numbers(cam, height) with the reference."""
    for cam in CAMERAS:
        try:
            mine = f(cam, height)
        except Exception as e:                       # noqa: BLE001
            print(f"NOT YET  plan_numbers('{cam}', {height}): {type(e).__name__}: {e}")
            continue
        ref = plan_numbers(cam, height)
        for k in ref:
            _ok(f"{cam} {k}", mine.get(k) if isinstance(mine, dict) else None, ref[k])


def same_lines(mine, ref, tol=0.05):
    """True if two lists of flight lines agree (number, direction and position within tol metres)."""
    if len(mine) != len(ref):
        print(f"NOT YET  {len(mine)} lines, reference {len(ref)}")
        return False
    worst = max(max(Point(a.coords[0]).distance(Point(b.coords[0])),
                    Point(a.coords[-1]).distance(Point(b.coords[-1]))) for a, b in zip(mine, ref))
    print(("OK " if worst < tol else "NOT YET") + f"  largest end point difference {worst:.2f} m")
    return worst < tol
