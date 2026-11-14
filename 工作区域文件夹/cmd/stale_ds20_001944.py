"""最终机位 + 稳定预览光（v06）：71 台相机，每台带跟随光，外加环境光与补光。"""
import glob
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json")
STILL_DIR = os.path.join(ROOT, "ds_stills", "v06_71")
GROUP = "DS_PRODUCTION_CAMERAS"
OUT = {"errors": [], "files": {}}


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
    cmds.setAttr(shape + ".farClipPlane", 3000.0)
    cmds.setAttr(shape + ".renderable", True)
    return cam


try:
    data = json.load(open(DESIGN, encoding="utf-8"))["shots"]
    os.makedirs(STILL_DIR, exist_ok=True)
    for g in (GROUP, "DS_LIGHTS"):
        if cmds.objExists(g):
            cmds.delete(g)
    cmds.group(em=True, name=GROUP)

    cam_map = {}
    for s in data:
        cam = make_cam("DS_%s_CAM" % s["id"], s["eye"], s["aim"], s["focal"])
        cmds.parent(cam, GROUP, relative=True)
        r = cmds.pointLight(name="DS_%s_LGT" % s["id"], intensity=0.55, decayRate=0,
                            rgb=(1.0, 0.97, 0.93))
        lt = r[0] if isinstance(r, (list, tuple)) else r
        ltr = cmds.listRelatives(lt, parent=True)[0]
        cmds.parent(ltr, cam, relative=True)
        cmds.setAttr(ltr + ".translate", 0.0, 8.0, -14.0)
        cam_map[s["id"]] = cam

    # 环境 + 背景补光（不带阴影，避免死黑）
    cmds.group(em=True, name="DS_LIGHTS")
    amb_res = cmds.ambientLight(name="DS_AMB_L", intensity=0.42, rgb=(0.70, 0.74, 0.82))
    amb = amb_res[0] if isinstance(amb_res, (list, tuple)) else amb_res
    cmds.parent(cmds.listRelatives(amb, parent=True)[0], "DS_LIGHTS", relative=False)

    d_res = cmds.directionalLight(name="DS_BGFILL_L", intensity=0.55, rgb=(0.92, 0.94, 1.0))
    dfill = d_res[0] if isinstance(d_res, (list, tuple)) else d_res
    dtr = cmds.listRelatives(dfill, parent=True)[0]
    cmds.parent(dtr, "DS_LIGHTS", relative=False)
    cmds.xform(dtr, ws=True, ro=(-28.0, 8.0, 0.0))
    try:
        cmds.setAttr(dfill + ".useDepthMapShadows", 0)
    except Exception:
        pass

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
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds20_v06.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "n": sum(1 for v in OUT["files"].values() if v),
                  "err": OUT["errors"][:1]}, ensure_ascii=False))
