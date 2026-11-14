"""DS 离线机位设计器 v3。

思路：给定被摄者、景别（头部占画面高度比例）、前景人物要求，
解出一台能用、不撞人、不把人拍进画面的相机（eye/aim/focal）。

投影约定与 Maya 一致：水平光圈 36mm，16:9 时垂直光圈 20.25mm，filmFit=horizontal。
"""
import json
import math
import os

HAP = 36.0
VAP = 20.25

HEADS = {
    "Ma": {"center": (0.02, 113.05, -105.24), "top": 124.97, "chin": 101.13, "yaw": 0.0},
    "Huang": {"center": (90.39, 123.19, 51.87), "top": 134.38, "chin": 111.99, "yaw": -120.0},
    "Shiye": {"center": (-89.20, 123.49, 51.37), "top": 134.71, "chin": 112.27, "yaw": 120.0},
}
BODIES = {
    "Ma": (0.02, -102.0, 34.0, 128.0),
    "Huang": (88.33, 51.0, 34.0, 138.0),
    "Shiye": (-88.33, 51.0, 32.0, 138.0),
}
TABLE = {"center": (0.0, 0.0), "radius": 88.0, "top": 75.8}


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    n = math.sqrt(dot(a, a)) or 1e-9
    return (a[0] / n, a[1] / n, a[2] / n)


def forward_of(name):
    y = math.radians(HEADS[name]["yaw"])
    return (math.sin(y), 0.0, math.cos(y))


def left_of(name):
    return cross((0.0, 1.0, 0.0), forward_of(name))


def basis(eye, aim):
    f = norm(sub(aim, eye))
    r = norm(cross(f, (0.0, 1.0, 0.0)))
    u = cross(r, f)
    return r, u, f


def project(p, eye, aim, focal):
    r, u, f = basis(eye, aim)
    v = sub(p, eye)
    z = dot(v, f)
    if z <= 1.0:
        return None
    x = dot(v, r)
    y = dot(v, u)
    fx = 0.5 + 0.5 * (x / z) / (HAP / 2.0 / focal)
    fy = 0.5 - 0.5 * (y / z) / (VAP / 2.0 / focal)
    return fx, fy, z


def head_frac(name, eye, aim, focal):
    h = HEADS[name]
    a = project((h["center"][0], h["top"], h["center"][2]), eye, aim, focal)
    b = project((h["center"][0], h["chin"], h["center"][2]), eye, aim, focal)
    if not a or not b:
        return None
    return abs(a[1] - b[1])


def min_head_dist(eye):
    return min(math.dist(eye, HEADS[n]["center"]) for n in HEADS)


def min_body_dist(eye):
    worst = 1e9
    for n, (x, z, r, top) in BODIES.items():
        if eye[1] > top + 6:
            continue
        worst = min(worst, math.hypot(eye[0] - x, eye[2] - z) - r)
    return worst


def cost(cam, spec):
    eye, aim, focal = cam["eye"], cam["aim"], cam["focal"]
    subj = spec["subject"]
    pr = project(HEADS[subj]["center"], eye, aim, focal)
    if pr is None:
        return 1e7
    fx, fy, dist = pr
    hf = head_frac(subj, eye, aim, focal) or 0
    c = 0.0

    c += 80.0 * (fx - spec.get("fx", 0.5)) ** 2
    c += 80.0 * (fy - spec.get("fy", 0.46)) ** 2
    c += 120.0 * (hf - spec["head_frac"]) ** 2
    c += 0.30 * (focal - spec["focal"]) ** 2
    c += 0.020 * (eye[1] - spec["height"]) ** 2

    fwd = forward_of(subj)
    v = norm((eye[0] - HEADS[subj]["center"][0], 0.0, eye[2] - HEADS[subj]["center"][2]))
    ang = math.degrees(math.acos(max(-1.0, min(1.0, dot(v, fwd)))))
    c += 0.03 * (ang - spec["azimuth"]) ** 2

    hd = min_head_dist(eye)
    if hd < 55.0:
        c += 120.0 * (55.0 - hd)
    bd = min_body_dist(eye)
    if bd < 25.0:
        c += 100.0 * (25.0 - bd)

    fg = spec.get("foreground")
    if fg:
        name = fg["name"]
        pr2 = project(HEADS[name]["center"], eye, aim, focal)
        if pr2 is None:
            return 1e7
        gx, gy, gd = pr2
        c += 100.0 * (gx - fg["fx"]) ** 2
        if "dist" in fg:
            c += 0.08 * (gd - fg["dist"]) ** 2
        if gd < 38.0:
            c += 100.0 * (38.0 - gd)
        if abs(gx - fx) < 0.20:
            c += 8.0 * (0.20 - abs(gx - fx)) / 0.20
        if not (-0.25 <= gx <= 1.35):
            c += 40.0
    else:
        for other in HEADS:
            if other == subj:
                continue
            pr3 = project(HEADS[other]["center"], eye, aim, focal)
            if pr3 and -0.05 <= pr3[0] <= 1.05 and -0.05 <= pr3[1] <= 1.05:
                c += 6.0
    return c


def clamp_cam(c, spec):
    subj = spec["subject"]
    sx, sy, sz = HEADS[subj]["center"]
    c["eye"][1] = max(80.0, min(150.0, c["eye"][1]))
    c["focal"] = max(26.0, min(100.0, c["focal"]))
    d = math.hypot(c["eye"][0] - sx, c["eye"][2] - sz)
    lo, hi = spec.get("radius_range", (110.0, 230.0))
    if d < lo or d > hi:
        k = (lo if d < lo else hi) / max(d, 1e-6)
        c["eye"][0] = sx + (c["eye"][0] - sx) * k
        c["eye"][2] = sz + (c["eye"][2] - sz) * k
    ax, ay, az = c["aim"]
    dx, dy, dz = ax - sx, ay - sy, az - sz
    n = math.sqrt(dx * dx + dy * dy + dz * dz)
    if n > 45.0:
        c["aim"] = [sx + dx * 45 / n, sy + dy * 45 / n, sz + dz * 45 / n]
    return c


def refine(spec, cam, iters=900, step=(8.0, 12.0, 5.0, 8.0, 5.0, 6.0)):
    step = list(step)
    best = cost(cam, spec)
    for _ in range(iters):
        improved = False
        for key, ax_list in (("eye", (0, 1, 2)), ("aim", (0, 1, 2)), ("focal", (None,))):
            for axis in ax_list:
                for sign in (1.0, -1.0):
                    trial = {k: (list(v) if isinstance(v, list) else v) for k, v in cam.items()}
                    if axis is None:
                        trial["focal"] += sign * step[5]
                    else:
                        trial[key][axis] += sign * step[axis]
                    trial = clamp_cam(trial, spec)
                    cc = cost(trial, spec)
                    if cc < best - 1e-7:
                        cam, best = trial, cc
                        improved = True
        if not improved:
            step = [s * 0.55 for s in step]
            if step[0] < 0.35:
                break
    return cam, best


def start_from(spec, azimuth, side, dist, focal):
    subj = spec["subject"]
    h = HEADS[subj]
    az = math.radians(azimuth)
    d = norm(add(mul(forward_of(subj), math.cos(az)), mul(left_of(subj), side * math.sin(az))))
    eye = [h["center"][0] + d[0] * dist, spec["height"], h["center"][2] + d[2] * dist]
    aim = [h["center"][0], h["center"][1] - 1.0, h["center"][2]]
    return {"eye": eye, "aim": aim, "focal": focal}


def solve(spec):
    best = None
    for az in (-45, -25, -10, 0, 10, 25, 45):
        for side in (1.0, -1.0):
            for dist in (115.0, 150.0, 190.0, 225.0):
                for focal in (35.0, 45.0, 55.0, 70.0):
                    cam = start_from(spec, az, side, dist, focal)
                    cam = clamp_cam(cam, spec)
                    cam, c = refine(spec, cam, iters=220, step=(12.0, 16.0, 7.0, 12.0, 7.0, 9.0))
                    if best is None or c < best[1]:
                        best = (cam, c)
    cam, c = refine(spec, best[0], iters=1800, step=(4.0, 6.0, 2.5, 4.0, 2.5, 3.0))
    return cam, c


def metrics(cam):
    eye, aim, focal = cam["eye"], cam["aim"], cam["focal"]
    out = {"focal": round(focal, 2), "eye": [round(v, 2) for v in eye], "aim": [round(v, 2) for v in aim]}
    for n in HEADS:
        pr = project(HEADS[n]["center"], eye, aim, focal)
        out[n] = None if not pr else {
            "fx": round(pr[0], 3), "fy": round(pr[1], 3), "dist": round(pr[2], 1),
            "head_frac": round(head_frac(n, eye, aim, focal) or 0, 3),
        }
    out["head_clearance_cm"] = round(min_head_dist(eye), 1)
    out["body_clearance_cm"] = round(min_body_dist(eye), 1)
    return out


SHOTS = [
    {"id": "P_MA", "subject": "Ma", "fx": 0.52, "fy": 0.46, "head_frac": 0.35,
     "height": 108, "focal": 60, "azimuth": 13, "radius_range": (110, 235)},
    {"id": "P_HUANG", "subject": "Huang", "fx": 0.5, "fy": 0.46, "head_frac": 0.35,
     "height": 118, "focal": 58, "azimuth": 16, "radius_range": (110, 235)},
    {"id": "P_SHIYE", "subject": "Shiye", "fx": 0.5, "fy": 0.46, "head_frac": 0.35,
     "height": 118, "focal": 58, "azimuth": 16, "radius_range": (110, 235)},

    {"id": "S001", "subject": "Ma", "fx": 0.54, "fy": 0.45, "head_frac": 0.34,
     "height": 108, "focal": 58, "azimuth": 13, "radius_range": (110, 230)},
    {"id": "S002", "subject": "Huang", "fx": 0.5, "fy": 0.45, "head_frac": 0.34,
     "height": 117, "focal": 56, "azimuth": 13, "radius_range": (110, 230)},
    {"id": "S003", "subject": "Ma", "fx": 0.44, "fy": 0.45, "head_frac": 0.32,
     "height": 113, "focal": 72, "azimuth": 30, "radius_range": (245, 290),
     "foreground": {"name": "Shiye", "fx": 1.04, "dist": 115}},
    {"id": "S004", "subject": "Huang", "fx": 0.56, "fy": 0.45, "head_frac": 0.32,
     "height": 121, "focal": 72, "azimuth": 30, "radius_range": (245, 290),
     "foreground": {"name": "Ma", "fx": -0.04, "dist": 115}},
    {"id": "S005", "subject": "Ma", "fx": 0.5, "fy": 0.46, "head_frac": 0.34,
     "height": 109, "focal": 62, "azimuth": 8, "radius_range": (115, 235)},
    {"id": "S006", "subject": "Huang", "fx": 0.46, "fy": 0.46, "head_frac": 0.34,
     "height": 118, "focal": 60, "azimuth": 9, "radius_range": (115, 235)},
    {"id": "S007", "subject": "Ma", "fx": 0.5, "fy": 0.46, "head_frac": 0.33,
     "height": 110, "focal": 55, "azimuth": 18, "radius_range": (110, 225)},
]

if __name__ == "__main__":
    out = []
    for spec in SHOTS:
        cam, c = solve(spec)
        m = metrics(cam)
        m["id"] = spec["id"]
        m["cost"] = round(c, 3)
        m["spec"] = spec
        out.append(m)
        print(json.dumps(m, ensure_ascii=False))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cam_design_draft.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("written", path)
