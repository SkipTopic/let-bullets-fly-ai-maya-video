"""建/重建 71 台正式相机与预览光，保存场景（不渲染）。"""
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json")
GROUP = "DS_PRODUCTION_CAMERAS"
OUT = {"errors": []}


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
    m = [r[0], r[1], r[2], 0.0, u[0], u[1], u[2], 0.0,
         -f[0], -f[1], -f[2], 0.0, eye[0], eye[1], eye[2], 1.0]
    cmds.xform(cam, ws=True, m=m)
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
    for g in (GROUP, "DS_LIGHTS"):
        if cmds.objExists(g):
            cmds.delete(g)
    cmds.group(em=True, name=GROUP)
    cmds.group(em=True, name="DS_LIGHTS")

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

    a = cmds.ambientLight(name="DS_AMB_L", intensity=0.42, rgb=(0.70, 0.74, 0.82))
    amb = a[0] if isinstance(a, (list, tuple)) else a
    cmds.parent(cmds.listRelatives(amb, parent=True)[0], "DS_LIGHTS", relative=False)

    d = cmds.directionalLight(name="DS_BGFILL_L", intensity=0.55, rgb=(0.92, 0.94, 1.0))
    dfill = d[0] if isinstance(d, (list, tuple)) else d
    dtr = cmds.listRelatives(dfill, parent=True)[0]
    cmds.parent(dtr, "DS_LIGHTS", relative=False)
    cmds.xform(dtr, ws=True, ro=(-28.0, 8.0, 0.0))

    with open(os.path.join(ROOT, "ds_camera_action", "camera_map_deepseek.json"), "w", encoding="utf-8") as fh:
        json.dump({"group": GROUP, "cams": cam_map, "scene": cmds.file(q=True, sn=True)},
                  fh, ensure_ascii=False, indent=1)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
    OUT["cams"] = len(cam_map)
    OUT["scene"] = cmds.file(q=True, sn=True)
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds20_build.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:500])
