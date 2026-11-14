"""DS 建正式相机 + 出第一批静帧。

读取 ds_camera_action/cam_design_draft.json，在 DS_相机动作_v01.mb 里
建立 DS_PRODUCTION_CAMERAS 组和正式透视相机，逐机位 playblast 出图，
并独立用 Maya 的相机矩阵复核投影位置。
"""
import glob
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "cam_design_draft.json")
STILL_DIR = os.path.join(ROOT, "ds_stills", "v01")
GROUP = "DS_PRODUCTION_CAMERAS"

OUT = {"errors": [], "steps": [], "cams": {}, "verify": {}}


def log(m):
    OUT["steps"].append(m)


def project_with_matrix(p, m, focal):
    """用 Maya 返回的世界矩阵做投影，独立复核。"""
    inv = invert_rigid(m)
    v = [p[0] - m[12], p[1] - m[13], p[2] - m[14]]
    # 转到相机局部坐标（行向量：local = world * M^-1）
    x = v[0] * m[0] + v[1] * m[1] + v[2] * m[2]
    y = v[0] * m[4] + v[1] * m[5] + v[2] * m[6]
    z = v[0] * m[8] + v[1] * m[9] + v[2] * m[10]
    if z >= -1.0:
        return None
    fx = 0.5 + 0.5 * (x / -z) / (36.0 / 2.0 / focal)
    fy = 0.5 - 0.5 * (y / -z) / (20.25 / 2.0 / focal)
    return fx, fy, -z


def invert_rigid(m):
    return m  # 只为占位，实际投影用轴向量直接点乘


def axis_dot(v, ax):
    return v[0] * ax[0] + v[1] * ax[1] + v[2] * ax[2]


def project_axes(p, eye, right, up, back, focal):
    """right/up/back 是相机三轴的基向量，back = -forward。"""
    v = (p[0] - eye[0], p[1] - eye[1], p[2] - eye[2])
    x = axis_dot(v, right)
    y = axis_dot(v, up)
    zf = -axis_dot(v, back)
    if zf <= 1.0:
        return None
    fx = 0.5 + 0.5 * (x / zf) / (36.0 / 2.0 / focal)
    fy = 0.5 - 0.5 * (y / zf) / (20.25 / 2.0 / focal)
    return fx, fy, zf


HEADS = {
    "Ma": (0.02, 113.05, -105.24),
    "Huang": (90.39, 123.19, 51.87),
    "Shiye": (-89.20, 123.49, 51.37),
}


def make_cam(name, eye, aim, focal):
    cam = cmds.camera(name=name)[0]
    shape = cmds.listRelatives(cam, shapes=True)[0]
    f = [aim[0] - eye[0], aim[1] - eye[1], aim[2] - eye[2]]
    n = math.sqrt(sum(c * c for c in f))
    f = [c / n for c in f]
    r = [f[1] * 0.0 - f[2] * 1.0, f[2] * 0.0 - f[0] * 0.0, f[0] * 1.0 - f[1] * 0.0]  # cross(f, up)
    n = math.sqrt(sum(c * c for c in r))
    r = [c / n for c in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]  # cross(r, f)
    matrix = [r[0], r[1], r[2], 0.0,
              u[0], u[1], u[2], 0.0,
              -f[0], -f[1], -f[2], 0.0,
              eye[0], eye[1], eye[2], 1.0]
    cmds.xform(cam, ws=True, m=matrix)
    cmds.setAttr(shape + ".focalLength", focal)
    cmds.setAttr(shape + ".horizontalFilmAperture", 36.0)
    cmds.setAttr(shape + ".verticalFilmAperture", 20.25)
    cmds.setAttr(shape + ".filmFit", 1)
    cmds.setAttr(shape + ".nearClipPlane", 5.0)
    cmds.setAttr(shape + ".farClipPlane", 2200.0)
    cmds.setAttr(shape + ".renderable", True)
    cmds.setAttr(shape + ".depthOfField", False)
    return cam, shape, (r, u, [-c for c in f])


try:
    design = json.load(open(DESIGN, encoding="utf-8"))
    os.makedirs(STILL_DIR, exist_ok=True)

    if cmds.objExists(GROUP):
        cmds.delete(GROUP)
    cmds.group(em=True, name=GROUP)

    cam_map = {}
    for item in design:
        sid = item["id"]
        name = "DS_%s_CAM" % sid
        created, shape, axes = make_cam(name, item["eye"], item["aim"], item["focal"])
        cam_map[sid] = created
        OUT["cams"][sid] = {"transform": created, "shape": shape, "focal": item["focal"]}

        # 复核：用实际相机三轴重新投影
        m = cmds.xform(created, q=True, ws=True, m=True)
        eye = (m[12], m[13], m[14])
        right = (m[0], m[1], m[2])
        up = (m[4], m[5], m[6])
        back = (m[8], m[9], m[10])
        chk = {}
        for hname, hp in HEADS.items():
            pr = project_axes(hp, eye, right, up, back, item["focal"])
            if pr:
                chk[hname] = [round(pr[0], 3), round(pr[1], 3), round(pr[2], 1)]
        OUT["verify"][sid] = chk
    for sid, cam in cam_map.items():
        cmds.parent(cam, GROUP, relative=True)
    log("建立相机 %d 台" % len(cam_map))

    panels = cmds.getPanel(type="modelPanel") or []
    visible = [p for p in panels if cmds.control(p, q=True, visible=True)]
    if not visible:
        raise RuntimeError("没有可见 modelPanel")
    panel = visible[0]
    OUT["panel"] = panel
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     wireframeOnShaded=False, backfaceCulling=False, twoSidedLighting=True,
                     selectionHiliteDisplay=False)
    cmds.select(clear=True)

    for item in design:
        sid = item["id"]
        cam = cam_map[sid]
        cmds.setFocus(panel)
        cmds.lookThru(panel, cam)
        actual = cmds.modelEditor(panel, q=True, camera=True)
        OUT["verify"].setdefault(sid, {})["panel_cam"] = actual
        cmds.currentTime(1)
        cmds.refresh(force=True)
        base = os.path.join(STILL_DIR, "DS_%s" % sid)
        for old in glob.glob(base + "*.png"):
            os.remove(old)
        made = cmds.playblast(frame=1, format="image", filename=base, sequenceTime=False,
                              clearCache=True, viewer=False, showOrnaments=False,
                              offScreen=True, percent=100, widthHeight=(960, 540),
                              quality=95, compression="png")
        got = sorted(glob.glob(base + "*.png"))
        OUT["verify"][sid]["file"] = got
        OUT["verify"][sid]["returned"] = made
        log("%s -> %s" % (sid, os.path.basename(got[0]) if got else "NO FILE"))

    # 保存相机映射
    mapping = {"scene": cmds.file(q=True, sn=True), "group": GROUP,
               "cams": cam_map, "panel": panel}
    with open(os.path.join(ROOT, "ds_camera_action", "camera_map_deepseek.json"), "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=1)

    cmds.lookThru(panel, cam_map["S001"])
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["scene_saved"] = cmds.file(q=True, sn=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds5_cams.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "errors": OUT["errors"][:1]}, ensure_ascii=False))
