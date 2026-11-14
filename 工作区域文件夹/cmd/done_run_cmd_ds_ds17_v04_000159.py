"""DS 相机光 + 正式相机重建 + 71 镜静帧（v04）。

每台相机自带一支 point light（跟随镜头），视口用场景灯光但隐藏灯光图标，
这样任何机位都不会出现死黑的脸，也不会拍到灯光图标。
"""
import glob
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json")
STILL_DIR = os.path.join(ROOT, "ds_stills", "v04_71")
GROUP = "DS_PRODUCTION_CAMERAS"
OUT = {"errors": [], "files": {}, "cams": {}}
HEADS = {"Ma": (0.02, 113.05, -105.24), "Huang": (90.39, 123.19, 51.87), "Shiye": (-89.20, 123.49, 51.37)}


def make_cam(name, eye, aim, focal):
    res = cmds.camera(name=name)
    cam = res[0] if isinstance(res, (list, tuple)) else res
    shape = cmds.listRelatives(cam, shapes=True)[0]
    f = [aim[0] - eye[0], aim[1] - eye[1], aim[2] - eye[2]]
    n = math.sqrt(sum(c * c for c in f)) or 1e-9
    f = [c / n for c in f]
    r = [-f[2], 0.0, f[0]]
    n = math.sqrt(sum(c * c for c in r)) or 1e-9
    r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    matrix = [r[0], r[1], r[2], 0.0, u[0], u[1], u[2], 0.0,
              -f[0], -f[1], -f[2], 0.0, eye[0], eye[1], eye[2], 1.0]
    cmds.xform(cam, ws=True, m=matrix)
    cmds.setAttr(shape + ".focalLength", focal)
    cmds.setAttr(shape + ".horizontalFilmAperture", 36.0 / 25.4)
    cmds.setAttr(shape + ".verticalFilmAperture", 20.25 / 25.4)
    cmds.setAttr(shape + ".filmFit", 1)
    cmds.setAttr(shape + ".nearClipPlane", 5.0)
    cmds.setAttr(shape + ".farClipPlane", 2200.0)
    cmds.setAttr(shape + ".renderable", True)
    return cam, shape


def add_cam_light(cam, sid):
    res = cmds.pointLight(name="DS_%s_LGT" % sid, intensity=1.15, decayRate=0,
                          rgb=(1.0, 0.97, 0.93))
    node = res[0] if isinstance(res, (list, tuple)) else res
    tr = cmds.listRelatives(node, parent=True)[0]
    cmds.parent(tr, cam, relative=True)
    cmds.setAttr(tr + ".translate", 0.0, 9.0, -16.0)
    try:
        cmds.setAttr(node + ".useDepthMapShadows", 0)
    except Exception:
        pass
    return tr


try:
    data = json.load(open(DESIGN, encoding="utf-8"))["shots"]
    os.makedirs(STILL_DIR, exist_ok=True)
    if cmds.objExists(GROUP):
        cmds.delete(GROUP)
    if cmds.objExists("DS_LIGHTS"):
        cmds.delete("DS_LIGHTS")
    cmds.group(em=True, name=GROUP)

    cam_map = {}
    for s in data:
        cam, shape = make_cam("DS_%s_CAM" % s["id"], s["eye"], s["aim"], s["focal"])
        cmds.parent(cam, GROUP, relative=True)
        add_cam_light(cam, s["id"])
        cam_map[s["id"]] = cam
    OUT["cams"] = cam_map

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="all", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     selectionHiliteDisplay=False, lights=False)
    cmds.select(clear=True)

    for s in data:
        sid = s["id"]
        cmds.setFocus(panel)
        cmds.lookThru(panel, cam_map[sid])
        fr = s["frame_range"][0] + (s["frame_range"][1] - s["frame_range"][0]) // 2
        cmds.currentTime(fr)
        cmds.refresh(force=True)
        base = os.path.join(STILL_DIR, "DS_" + sid)
        cmds.playblast(frame=fr, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
        got = sorted(glob.glob(base + "*.png"))
        OUT["files"][sid] = got[0] if got else None

    with open(os.path.join(ROOT, "ds_camera_action", "camera_map_deepseek.json"), "w", encoding="utf-8") as fh:
        json.dump({"group": GROUP, "cams": cam_map, "scene": cmds.file(q=True, sn=True)},
                  fh, ensure_ascii=False, indent=1)
    cmds.lookThru(panel, cam_map["S001"])
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["saved"] = cmds.file(q=True, sn=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds17_v04.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "files": sum(1 for v in OUT["files"].values() if v),
                  "err": OUT["errors"][:1]}, ensure_ascii=False))
