"""诊断：核对 DS 正式相机的实际世界位置、朝向与实际投影。"""
import json
import math
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "cam_design_draft.json")
HEADS = {"Ma": (0.02, 113.05, -105.24), "Huang": (90.39, 123.19, 51.87), "Shiye": (-89.20, 123.49, 51.37)}

design = {d["id"]: d for d in json.load(open(DESIGN, encoding="utf-8"))}
out = {"cams": {}}

for sid, spec in design.items():
    cam = "DS_%s_CAM" % sid
    if not cmds.objExists(cam):
        cands = cmds.ls("DS_%s_CAM*" % sid)
        cam = cands[0] if cands else None
    if not cam:
        out["cams"][sid] = {"missing": True}
        continue
    m = cmds.xform(cam, q=True, ws=True, m=True)
    eye = [round(m[12], 2), round(m[13], 2), round(m[14], 2)]
    zaxis = [m[8], m[9], m[10]]
    fwd = [-zaxis[0], -zaxis[1], -zaxis[2]]
    aim = spec["aim"]
    d = [aim[0] - eye[0], aim[1] - eye[1], aim[2] - eye[2]]
    n = math.sqrt(sum(c * c for c in d))
    d = [c / n for c in d]
    cosang = sum(fwd[i] * d[i] for i in range(3))
    shape = cmds.listRelatives(cam, shapes=True)[0]
    out["cams"][sid] = {
        "node": cam,
        "eye_actual": eye,
        "eye_wanted": [round(v, 2) for v in spec["eye"]],
        "fwd_actual": [round(v, 3) for v in fwd],
        "fwd_to_aim": [round(v, 3) for v in d],
        "angle_to_aim_deg": round(math.degrees(math.acos(max(-1, min(1, cosang)))), 2),
        "focal": cmds.getAttr(shape + ".focalLength"),
        "hfa": cmds.getAttr(shape + ".horizontalFilmAperture"),
        "vfa": cmds.getAttr(shape + ".verticalFilmAperture"),
        "filmfit": cmds.getAttr(shape + ".filmFit"),
        "dist_to_Ma": round(math.dist(eye, HEADS["Ma"]), 1),
    }

path = os.path.join(ROOT, "logs", "ds6_camcheck.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
