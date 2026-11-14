"""定位测试：列出所有 DS 相机，并在关键点放临时标记球渲染，确认相机实际看到什么。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUTDIR = os.path.join(ROOT, "ds_stills", "test")
os.makedirs(OUTDIR, exist_ok=True)
out = {"errors": [], "cams": [], "markers": []}

try:
    # 1) 列出所有 DS 相机及其实世界位置
    for c in cmds.ls("DS_*", type="camera") or []:
        tr = (cmds.listRelatives(c, parent=True) or [c])[0]
        m = cmds.xform(tr, q=True, ws=True, m=True)
        out["cams"].append({
            "shape": c,
            "transform": tr,
            "world": [round(m[12], 1), round(m[13], 1), round(m[14], 1)],
            "focal": round(cmds.getAttr(c + ".focalLength"), 2),
            "parent": (cmds.listRelatives(tr, parent=True) or [None])[0],
        })

    # 2) 临时标记
    markers = [
        ("M_MaHead", (0.02, 113.05, -105.24), 6.0, (1, 0, 0)),
        ("M_TableC", (0.0, 75.8, 0.0), 8.0, (0, 1, 0)),
        ("M_Aim", (2.02, 110.05, -140.0), 5.0, (0, 0, 1)),
    ]
    for name, pos, r, col in markers:
        sp = cmds.polySphere(name=name, radius=r, sx=12, sy=8)[0]
        cmds.xform(sp, ws=True, t=pos)
        sh = cmds.listRelatives(sp, shapes=True)[0]
        mat = cmds.shadingNode("lambert", asShader=True, name=name + "_M")
        cmds.setAttr(mat + ".color", col[0], col[1], col[2])
        cmds.setAttr(mat + ".incandescence", col[0] * 0.8, col[1] * 0.8, col[2] * 0.8)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name + "_SG")
        cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", f=True)
        cmds.sets(sp, e=True, forceElement=sg)
        out["markers"].append(name)

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cam = "DS_S001_CAM1"
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False)
    cmds.select(clear=True)
    cmds.setFocus(panel)
    cmds.lookThru(panel, cam)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    base = os.path.join(OUTDIR, "marker_S001")
    for f in glob.glob(base + "*.png"):
        os.remove(f)
    cmds.playblast(frame=1, format="image", filename=base, sequenceTime=False, clearCache=True,
                   viewer=False, showOrnaments=False, offScreen=True, percent=100,
                   widthHeight=(960, 540), quality=95, compression="png")
    out["file"] = glob.glob(base + "*.png")

    # 3) 清理标记
    for name in out["markers"]:
        if cmds.objExists(name):
            cmds.delete(name)
        for n in (name + "_M", name + "_SG"):
            if cmds.objExists(n):
                cmds.delete(n)
    out["ok"] = True
except Exception as exc:  # noqa: BLE001
    out["errors"].append(repr(exc))

with open(os.path.join(ROOT, "logs", "ds11_marker.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
