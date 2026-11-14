"""建立 71 台正式相机并逐镜出静帧（首轮自检用）。"""
import glob
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json")
STILL_DIR = os.path.join(ROOT, "ds_stills", "v02_71")
GROUP = "DS_PRODUCTION_CAMERAS"

OUT = {"errors": [], "steps": [], "cams": {}, "files": {}}
HEADS = {"Ma": (0.02, 113.05, -105.24), "Huang": (90.39, 123.19, 51.87), "Shiye": (-89.20, 123.49, 51.37)}


def make_cam(name, eye, aim, focal):
    cam = cmds.camera(name=name)[0]
    shape = cmds.listRelatives(cam, shapes=True)[0]
    f = [aim[0] - eye[0], aim[1] - eye[1], aim[2] - eye[2]]
    n = math.sqrt(sum(c * c for c in f))
    f = [c / n for c in f]
    r = [-f[2], 0.0, f[0]]
    n = math.sqrt(sum(c * c for c in r)) or 1e-9
    r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    matrix = [r[0], r[1], r[2], 0.0,
              u[0], u[1], u[2], 0.0,
              -f[0], -f[1], -f[2], 0.0,
              eye[0], eye[1], eye[2], 1.0]
    cmds.xform(cam, ws=True, m=matrix)
    cmds.setAttr(shape + ".focalLength", focal)
    cmds.setAttr(shape + ".horizontalFilmAperture", 36.0 / 25.4)
    cmds.setAttr(shape + ".verticalFilmAperture", 20.25 / 25.4)
    cmds.setAttr(shape + ".filmFit", 1)
    cmds.setAttr(shape + ".nearClipPlane", 5.0)
    cmds.setAttr(shape + ".farClipPlane", 2200.0)
    cmds.setAttr(shape + ".renderable", True)
    return cam, shape


def project(eye, aim, focal, p):
    f = [aim[i] - eye[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in f))
    f = [c / n for c in f]
    r = [-f[2], 0.0, f[0]]
    n = math.sqrt(sum(c * c for c in r)) or 1e-9
    r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    v = [p[i] - eye[i] for i in range(3)]
    z = sum(v[i] * f[i] for i in range(3))
    if z <= 1:
        return None
    x = sum(v[i] * r[i] for i in range(3))
    y = sum(v[i] * u[i] for i in range(3))
    return (0.5 + 0.5 * (x / z) / (36.0 / 2 / focal), 0.5 - 0.5 * (y / z) / (20.25 / 2 / focal), z)


try:
    data = json.load(open(DESIGN, encoding="utf-8"))["shots"]
    os.makedirs(STILL_DIR, exist_ok=True)
    if cmds.objExists(GROUP):
        cmds.delete(GROUP)
    cmds.group(em=True, name=GROUP)

    cam_map = {}
    for s in data:
        cam, shape = make_cam("DS_%s_CAM" % s["id"], s["eye"], s["aim"], s["focal"])
        cam_map[s["id"]] = cam
        cmds.parent(cam, GROUP, relative=True)
    OUT["cam_count"] = len(cam_map)
    OUT["steps"].append("建立 %d 台相机" % len(cam_map))

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="all", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     selectionHiliteDisplay=False)
    cmds.select(clear=True)

    for s in data:
        sid = s["id"]
        cam = cam_map[sid]
        cmds.setFocus(panel)
        cmds.lookThru(panel, cam)
        fr = s["frame_range"][0] + (s["frame_range"][1] - s["frame_range"][0]) // 2
        cmds.currentTime(fr)
        cmds.refresh(force=True)
        base = os.path.join(STILL_DIR, "DS_" + sid)
        for old in glob.glob(base + "*.png"):
            os.remove(old)
        cmds.playblast(frame=fr, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
        got = sorted(glob.glob(base + "*.png"))
        OUT["files"][sid] = got[0] if got else None

    # 复核：用实际相机矩阵投影三人头部
    verify = {}
    for s in data:
        cam = cam_map[s["id"]]
        m = cmds.xform(cam, q=True, ws=True, m=True)
        eye = (m[12], m[13], m[14])
        verify[s["id"]] = {n: (None if not project(eye, s["aim"], s["focal"], p) else
                               [round(project(eye, s["aim"], s["focal"], p)[0], 2),
                                round(project(eye, s["aim"], s["focal"], p)[1], 2)])
                           for n, p in HEADS.items()}
    OUT["verify"] = verify

    mapping = {"scene": cmds.file(q=True, sn=True), "group": GROUP, "cams": cam_map}
    with open(os.path.join(ROOT, "ds_camera_action", "camera_map_deepseek.json"), "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=1)

    cmds.lookThru(panel, cam_map["S001"])
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
    OUT["saved"] = cmds.file(q=True, sn=True)
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds15_build71.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "cams": OUT.get("cam_count"), "err": OUT["errors"][:1]}, ensure_ascii=False))
