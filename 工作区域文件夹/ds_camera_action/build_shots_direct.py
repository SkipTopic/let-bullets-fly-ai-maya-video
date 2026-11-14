"""71 镜机位直算版：先定机位（方位/距离/高度/焦距），再解瞄准点命中构图。

比搜索式求解更可控：每镜机位由参数显式决定，不会所有镜头塌到同一点。
"""
import csv
import hashlib
import json
import math
import os

HAP = 36.0
VAP = 20.25

HEAD = {
    "Ma": {"c": (0.02, 113.05, -105.24), "top": 124.97, "chin": 101.13, "yaw": 0.0},
    "Huang": {"c": (90.39, 123.19, 51.87), "top": 134.38, "chin": 111.99, "yaw": -120.0},
    "Shiye": {"c": (-89.20, 123.49, 51.37), "top": 134.71, "chin": 112.27, "yaw": 120.0},
}
BASE_H = {"Ma": 109.0, "Huang": 119.0, "Shiye": 119.0}


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


def fwd(name):
    y = math.radians(HEAD[name]["yaw"])
    return (math.sin(y), 0.0, math.cos(y))


def leftv(name):
    return cross((0.0, 1.0, 0.0), fwd(name))


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
    return (0.5 + 0.5 * (x / z) / (HAP / 2 / focal),
            0.5 - 0.5 * (y / z) / (VAP / 2 / focal), z)


def head_frac(name, eye, aim, focal):
    h = HEAD[name]
    a = project((h["c"][0], h["top"], h["c"][2]), eye, aim, focal)
    b = project((h["c"][0], h["chin"], h["c"][2]), eye, aim, focal)
    if not a or not b:
        return 0.0
    return abs(a[1] - b[1])


def aim_for(eye, target, focal, fx, fy, iters=6):
    """求瞄准点，使 target 落在画面 (fx, fy)。"""
    aim = target
    for _ in range(iters):
        pr = project(target, eye, aim, focal)
        if not pr:
            return aim
        r, u, f = basis(eye, aim)
        R = math.dist(eye, target)
        dx = (pr[0] - fx) * 2.0 * math.atan(HAP / 2 / focal) * R
        dy = (pr[1] - fy) * 2.0 * math.atan(VAP / 2 / focal) * R
        aim = add(aim, add(mul(r, dx), mul(u, -dy)))
    return aim


def rnd(seed, lo, hi):
    h = int(hashlib.md5(seed.encode("utf-8")).hexdigest()[:8], 16)
    return lo + (hi - lo) * ((h % 10000) / 10000.0)


BODY = {
    "Ma": (0.02, -102.0, 34.0, 128.0),
    "Huang": (88.33, 51.0, 34.0, 138.0),
    "Shiye": (-88.33, 51.0, 32.0, 138.0),
}


def seg_hits_circle(p0, p1, c, r):
    ax, az = p0[0], p0[2]
    bx, bz = p1[0], p1[2]
    dx, dz = bx - ax, bz - az
    L2 = dx * dx + dz * dz
    if L2 < 1e-6:
        return False
    t = ((c[0] - ax) * dx + (c[1] - az) * dz) / L2
    if t <= 0.08 or t >= 0.94:
        return False
    cx, cz = ax + t * dx, az + t * dz
    return math.hypot(cx - c[0], cz - c[1]) < r


def blocked(eye, target, skip):
    for n, (bx, bz, r, top) in BODY.items():
        if n in skip:
            continue
        if math.hypot(eye[0] - bx, eye[2] - bz) < r:
            continue
        if seg_hits_circle(eye, target, (bx, bz), r):
            y = eye[1] + (target[1] - eye[1]) * 0.5
            if y < top:
                return n
    return None


def clearance_ok(eye, skip):
    for n, (bx, bz, r, top) in BODY.items():
        if n in skip:
            continue
        if eye[1] < top + 5 and math.hypot(eye[0] - bx, eye[2] - bz) < r + 26.0:
            return False
        if math.dist(eye, HEAD[n]["c"]) < 45.0:
            return False
    return True


def frame_ok(eye, aim, focal, name, fx_range=(0.24, 0.76), fy_range=(0.20, 0.78)):
    pr = project(HEAD[name]["c"], eye, aim, focal)
    if not pr:
        return False
    return fx_range[0] <= pr[0] <= fx_range[1] and fy_range[0] <= pr[1] <= fy_range[1]


def singles_cam(subj, seed):
    """带校验的机位：不撞人、不被别人挡住、主体在画内。"""
    for attempt in range(30):
        sd = seed if attempt == 0 else "%s_%d" % (seed, attempt)
        az = math.radians(rnd(sd + "az", 4.0, 42.0))
        side = 1.0 if int(hashlib.md5((sd + "s").encode()).hexdigest(), 16) % 2 else -1.0
        R = rnd(sd + "R", 165.0, 255.0)
        h = BASE_H[subj] + rnd(sd + "h", -10.0, 10.0)
        frac = rnd(sd + "f", 0.30, 0.35)
        fx = rnd(sd + "x", 0.46, 0.54)
        fy = rnd(sd + "y", 0.44, 0.47)

        hd = HEAD[subj]["c"]
        d = norm(add(mul(fwd(subj), math.cos(az)), mul(leftv(subj), side * math.sin(az))))
        eye = (hd[0] + d[0] * R, h, hd[2] + d[2] * R)
        R3 = math.dist(eye, hd)
        size = HEAD[subj]["top"] - HEAD[subj]["chin"]
        focal = frac * VAP * R3 / size
        aim = aim_for(eye, hd, focal, fx, fy)

        if not clearance_ok(eye, {subj}):
            continue
        if blocked(eye, hd, {subj}):
            continue
        if not frame_ok(eye, aim, focal, subj):
            continue
        return eye, aim, focal
    raise RuntimeError("no valid single camera for %s" % subj)


def ots_cam(subj, fg, seed, right_side):
    """机位在前景人物外侧，朝主体回看；横向偏移控制前景在画框边缘。"""
    d_fg = rnd(seed + "d", 150.0, 205.0)
    e_frac = rnd(seed + "e", 0.55, 0.85)
    frac = rnd(seed + "f", 0.27, 0.33)
    fx = rnd(seed + "x", 0.40, 0.50) if right_side else rnd(seed + "x", 0.50, 0.60)
    fy = rnd(seed + "y", 0.43, 0.48)
    h = BASE_H[subj] + rnd(seed + "h", -4.0, 8.0)

    a = HEAD[fg]["c"]
    b = HEAD[subj]["c"]
    ax = math.hypot(b[0] - a[0], b[2] - a[2])
    ux = (b[0] - a[0]) / ax
    uz = (b[2] - a[2]) / ax
    px = uz
    pz = -ux
    sgn = 1.0 if right_side else -1.0

    # 解横向偏移：让前景人物的头落在 fx=±1.02
    target_fg_fx = 1.16 if right_side else -0.16
    best = None
    for i in range(41):
        ef = 0.12 + i * 0.012
        eye = (a[0] - ux * d_fg + px * ef * d_fg * sgn, h, a[2] - uz * d_fg + pz * ef * d_fg * sgn)
        R3 = math.dist(eye, b)
        size = HEAD[subj]["top"] - HEAD[subj]["chin"]
        focal = frac * VAP * R3 / size
        aim = aim_for(eye, b, focal, fx, fy)
        pr = project(a, eye, aim, focal)
        if not pr:
            continue
        err = abs(pr[0] - target_fg_fx)
        if best is None or err < best[0]:
            best = (err, eye, aim, focal, ef)
    if best is None:
        return None
    return best[1], best[2], best[3]


def metrics(eye, aim, focal):
    out = {}
    for n in HEAD:
        pr = project(HEAD[n]["c"], eye, aim, focal)
        out[n] = None if not pr else {"fx": round(pr[0], 3), "fy": round(pr[1], 3),
                                      "dist": round(pr[2], 1),
                                      "head_frac": round(head_frac(n, eye, aim, focal), 3)}
    return out


SHOTS = [
    ("S001", "Ma", "single", None), ("S002", "Huang", "single", None),
    ("S003", "Ma", "ots", "Shiye"), ("S004", "Huang", "ots", "Ma"),
    ("S005", "Ma", "single", None), ("S006", "Huang", "single", None),
    ("S007", "Ma", "single", None), ("S008", "Huang", "single", None),
    ("S009", "Ma", "single", None), ("S010", "Shiye", "single", None),
    ("S011", "Huang", "single", None), ("S012", "Ma", "single", None),
    ("S013", "Shiye", "medium", None), ("S014", "Ma", "ots", "Shiye"),
    ("S015", "Huang", "medium", None), ("S016", "Ma", "ots", "Shiye"),
    ("S017", "Ma", "single", None), ("S018", "Shiye", "single", None),
    ("S019", "Huang", "medium", None), ("S020", "Shiye", "ots", "Huang"),
    ("S021", "Huang", "ots", "Ma"), ("S022", "Shiye", "single", None),
    ("S023", "Ma", "ots", "Shiye"), ("S024", "Shiye", "single", None),
    ("S025", "Ma", "single", None), ("S026", "Shiye", "single", None),
    ("S027", "Ma", "single", None), ("S028", "Huang", "single", None),
    ("S029", "Ma", "ots", "Shiye"), ("S030", "Huang", "single", None),
    ("S031", "Ma", "single", None), ("S032", "Huang", "single", None),
    ("S033", "Shiye", "ots", "Huang"), ("S034", "Huang", "single", None),
    ("S035", "Ma", "ots", "Shiye"), ("S036", "Huang", "ots", "Shiye"),
    ("S037", "Ma", "ots", "Shiye"), ("S038", "Huang", "ots", "Shiye"),
    ("S039", "Ma", "ots", "Huang"), ("S040", "Shiye", "medium", None),
    ("S041", "Huang", "single", None), ("S042", "Huang", "close", None),
    ("S043", None, "title", None), ("S044", "Shiye", "single", None),
    ("S045", "Shiye", "single", None), ("S046", None, "title", None),
    ("S047", "Ma", "single", None), ("S048", "Huang", "single", None),
    ("S049", "Shiye", "medium", None), ("S050", "Ma", "single", None),
    ("S051", "Ma", "single", None), ("S052", "Huang", "single", None),
    ("S053", "Huang", "single", None), ("S054", None, "title", None),
    ("S055", "Shiye", "single", None), ("S056", "Ma", "single", None),
    ("S057", "Huang", "single", None), ("S058", "Ma", "single", None),
    ("S059", "Shiye", "single", None), ("S060", "Ma", "single", None),
    ("S061", "Huang", "single", None), ("S062", "Ma", "single", None),
    ("S063", "Huang", "single", None), ("S064", "Ma", "single", None),
    ("S065", "Shiye", "single", None), ("S066", "Huang", "single", None),
    ("S067", "Ma", "single", None), ("S068", "Shiye", "single", None),
    ("S069", "Ma", "ots", "Shiye"), ("S070", "Shiye", "single", None),
    ("S071", "Ma", "single", None),
]

TITLES = {
    "S043": ((-30.0, 62.0, 118.0), (10.0, 74.0, -35.0), 70.0, "低机位贴桌面，看瓶子与桌面剪影"),
    "S046": ((0.0, 120.0, 120.0), (0.0, 70.0, 0.0), 50.0, "黑场+镜号，机位仅占位"),
    "S054": ((10.0, 120.0, 150.0), (-20.0, 90.0, -60.0), 55.0, "窗格光影暗转，机位仅占位"),
}


def build():
    out = []
    for sid, subj, kind, fg in SHOTS:
        if kind == "title":
            eye, aim, focal, note = TITLES[sid]
            out.append({"id": sid, "type": "title", "eye": list(eye), "aim": list(aim),
                        "focal": focal, "note": note, "projection": {}})
            continue
        if kind == "ots":
            right_side = fg in ("Shiye", "Huang")
            eye, aim, focal = ots_cam(subj, fg, sid + "ots", right_side)
        else:
            if kind == "medium":
                got = None
                for attempt in range(30):
                    sd = sid if attempt == 0 else "%s_m%d" % (sid, attempt)
                    az = math.radians(rnd(sd + "az", 4.0, 26.0))
                    side = 1.0 if int(hashlib.md5((sd + "s").encode()).hexdigest(), 16) % 2 else -1.0
                    R = rnd(sd + "R", 225.0, 300.0)
                    h = BASE_H[subj] + rnd(sd + "h", -8.0, 8.0)
                    frac = rnd(sd + "f", 0.17, 0.23)
                    fx = rnd(sd + "x", 0.44, 0.56)
                    fy = 0.46
                    hd = HEAD[subj]["c"]
                    d = norm(add(mul(fwd(subj), math.cos(az)), mul(leftv(subj), side * math.sin(az))))
                    eye = (hd[0] + d[0] * R, h, hd[2] + d[2] * R)
                    R3 = math.dist(eye, hd)
                    size = HEAD[subj]["top"] - HEAD[subj]["chin"]
                    focal = frac * VAP * R3 / size
                    aim = aim_for(eye, hd, focal, fx, fy)
                    if clearance_ok(eye, {subj}) and not blocked(eye, hd, {subj}) and frame_ok(eye, aim, focal, subj):
                        got = (eye, aim, focal)
                        break
                if got is None:
                    raise RuntimeError("no valid medium camera for " + sid)
                eye, aim, focal = got
            elif kind == "close":
                eye, aim, focal = singles_cam(subj, sid + "c")
                focal *= 1.55
                hd = HEAD[subj]["c"]
                aim = aim_for(eye, hd, focal, 0.5, 0.47)
            else:
                eye, aim, focal = singles_cam(subj, sid)

        m = metrics(eye, aim, focal)
        out.append({"id": sid, "type": kind, "subject": subj, "foreground": fg,
                    "eye": [round(v, 2) for v in eye], "aim": [round(v, 2) for v in aim],
                    "focal": round(focal, 2), "projection": m})
    return out


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    shots = build()
    rows = {r["shot_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "shotlist.csv"), encoding="utf-8-sig"))}

    # 重复机位检查
    import itertools
    dups = []
    for a, b in itertools.combinations([s for s in shots if s["type"] != "title"], 2):
        d = math.dist(a["eye"], b["eye"])
        if d < 22 and abs(a["focal"] - b["focal"]) < 6:
            dups.append((a["id"], b["id"], round(d, 1), round(abs(a["focal"] - b["focal"]), 1)))

    for s in shots:
        r = rows[s["id"]]
        s["frame_range"] = [int(r["start_frame"]), int(r["end_frame"])]
        s["shot_size_text"] = r["shot_size"]
        s["dialogue"] = r["dialogue"]
        s["film_action"] = r["action"]
        s["film_camera_move"] = r["camera_move"]

    with open(os.path.join(HERE, "shots_deepseek.json"), "w", encoding="utf-8") as fh:
        json.dump({"version": 2, "method": "direct-placement + aim solve",
                   "near_duplicates": dups, "shots": shots}, fh, ensure_ascii=False, indent=1)
    print("shots", len(shots), "near-duplicates", len(dups))
    for d in dups[:20]:
        print("  dup", d)
    print("unique positions", len({(round(s["eye"][0], 1), round(s["eye"][2], 1)) for s in shots if s["type"] != "title"}))
