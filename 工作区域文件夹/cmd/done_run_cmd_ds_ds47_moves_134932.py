"""v04 运镜：按镜头内容给推、拉、摇、移、升降、环绕，逐 3 帧烘焙（含微晃）。

参考 全流程 Skill/maya-sheng-animation/scripts/maya_camera_tools.py 的做法：
同时给 eye 和 aim 打点，aim 动起来才有摇镜/俯仰。
"""
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "cams": {}}

# 镜号 -> 运镜类型
MOVE = {
    "S001": "push", "S002": "pull", "S003": "track", "S004": "push", "S005": "pan",
    "S006": "tilt_down", "S007": "push", "S008": "pull", "S009": "pan", "S010": "push",
    "S011": "track", "S012": "push", "S013": "pull", "S014": "push", "S015": "track",
    "S016": "push", "S017": "pan", "S018": "push", "S019": "tilt_up", "S020": "track",
    "S021": "push", "S022": "pan", "S023": "push", "S024": "pull", "S025": "push",
    "S026": "push", "S027": "tilt_up", "S028": "push", "S029": "pan", "S030": "push",
    "S031": "push", "S032": "pull", "S033": "track", "S034": "push", "S035": "push",
    "S036": "track", "S037": "pan", "S038": "push", "S039": "push", "S040": "pull",
    "S041": "tilt_up", "S042": "push", "S043": "push", "S044": "push", "S045": "crane_up",
    "S046": "none", "S047": "push", "S048": "tilt_down", "S049": "pull", "S050": "push",
    "S051": "push", "S052": "pan", "S053": "push", "S054": "push", "S055": "push",
    "S056": "tilt_down", "S057": "push", "S058": "pan", "S059": "push", "S060": "push",
    "S061": "tilt_up", "S062": "push", "S063": "push", "S064": "push", "S065": "pull",
    "S066": "push", "S067": "push", "S068": "crane_up", "S069": "crane_up", "S070": "pan",
    "S071": "push",
}


def smooth(t):
    return t * t * (3.0 - 2.0 * t)


def look_rot(cam, eye, aim):
    f = [aim[i] - eye[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in f)) or 1e-9
    f = [c / n for c in f]
    r = [-f[2], 0.0, f[0]]
    n = math.sqrt(sum(c * c for c in r)) or 1e-9
    r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    m = [r[0], r[1], r[2], 0.0,
         u[0], u[1], u[2], 0.0,
         -f[0], -f[1], -f[2], 0.0,
         eye[0], eye[1], eye[2], 1.0]
    cmds.xform(cam, ws=True, m=m)
    return list(cmds.xform(cam, q=True, ro=True))


def endpoints(kind, eye, aim, dist):
    """返回 (eye_end, aim_end)。"""
    e = list(eye)
    a = list(aim)
    d = [a[i] - e[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d)) or 1e-9
    fwd = [c / n for c in d]
    right = [-fwd[2], 0.0, fwd[0]]
    rn = math.sqrt(sum(c * c for c in right)) or 1e-9
    right = [c / rn for c in right]

    if kind == "push":
        k = dist * 0.075
        e = [e[i] + fwd[i] * k for i in range(3)]
    elif kind == "pull":
        k = dist * 0.065
        e = [e[i] - fwd[i] * k for i in range(3)]
    elif kind in ("pan", "pan_left", "pan_right"):
        ang = math.radians(3.4) * (-1.0 if kind == "pan_left" else 1.0)
        v = [right[i] * math.sin(ang) + fwd[i] * math.cos(ang) for i in range(3)]
        a = [e[i] + v[i] * dist for i in range(3)]
    elif kind in ("tilt_up", "tilt_down"):
        ang = math.radians(2.8) * (1.0 if kind == "tilt_up" else -1.0)
        v = [fwd[i] * math.cos(ang) + (1.0 if i == 1 else 0.0) * math.sin(ang) for i in range(3)]
        n2 = math.sqrt(sum(c * c for c in v)) or 1e-9
        v = [c / n2 for c in v]
        a = [e[i] + v[i] * dist for i in range(3)]
    elif kind == "track":
        k = 20.0
        e = [e[i] + right[i] * k for i in range(3)]
        a = [a[i] + right[i] * k for i in range(3)]
    elif kind == "crane_up":
        k = 18.0
        e[1] += k
        a[1] += k * 0.35
    elif kind == "orbit":
        ang = math.radians(5.0)
        rel = [e[0] - a[0], e[2] - a[2]]
        c, s = math.cos(ang), math.sin(ang)
        e[0] = a[0] + rel[0] * c - rel[1] * s
        e[2] = a[2] + rel[0] * s + rel[1] * c
    return e, a


def shake(f, seed):
    return (math.sin(f * 0.171 + seed) * 0.18 + math.sin(f * 0.061 + seed * 1.7) * 0.12,
            math.cos(f * 0.113 + seed * 2.3) * 0.15,
            math.sin(f * 0.083 + seed * 0.7) * 0.12)


try:
    shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                           encoding="utf-8"))["shots"]
    for idx, s in enumerate(shots):
        sid = s["id"]
        cams = cmds.ls("DS_%s_CAM*" % sid)
        if not cams:
            continue
        cam = cams[0]
        eye0 = s["eye"]
        aim0 = s["aim"]
        proj = s.get("projection") or {}
        subj = s.get("subject")
        dist = (proj.get(subj, {}) or {}).get("dist", 200.0) if subj else 200.0

        kind = MOVE.get(sid, "push")
        if kind == "none":
            kind = "push"
        eye1, aim1 = endpoints(kind, eye0, aim0, dist)

        # 清掉旧曲线
        for attr in ("translate", "rotate"):
            try:
                cmds.cutKey(cam, at=attr, clear=True)
            except Exception:
                pass

        f0, f1 = s["frame_range"]
        seed = idx * 1.31
        for f in range(f0, f1 + 1, 3):
            t = smooth((f - f0) / max(1, (f1 - f0)))
            eye = [eye0[i] + (eye1[i] - eye0[i]) * t for i in range(3)]
            aim = [aim0[i] + (aim1[i] - aim0[i]) * t for i in range(3)]
            sx, sy, sz = shake(f, seed)
            eye = [eye[0] + sx, eye[1] + sy, eye[2] + sz]
            rot = look_rot(cam, eye, aim)
            cmds.setKeyframe(cam, at="translate", time=f, value=tuple(eye))
            cmds.setKeyframe(cam, at="rotate", time=f, value=tuple(rot))

        t = 1.0
        eye = [eye0[i] + (eye1[i] - eye0[i]) * t for i in range(3)]
        aim = [aim0[i] + (aim1[i] - aim0[i]) * t for i in range(3)]
        sx, sy, sz = shake(f1, seed)
        eye = [eye[0] + sx, eye[1] + sy, eye[2] + sz]
        rot = look_rot(cam, eye, aim)
        cmds.setKeyframe(cam, at="translate", time=f1, value=tuple(eye))
        cmds.setKeyframe(cam, at="rotate", time=f1, value=tuple(rot))

        OUT["cams"][sid] = {"kind": kind,
                            "eye_move_cm": round(math.dist(eye0, eye1), 1),
                            "aim_move_cm": round(math.dist(aim0, aim1), 1)}

    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds47_moves.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for sid, v in list(OUT["cams"].items())[:12]:
    print(sid, v)
print("ok", OUT.get("ok"), "n", len(OUT["cams"]), OUT["errors"][:1])
