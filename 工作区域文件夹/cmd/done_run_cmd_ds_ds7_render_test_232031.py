"""诊断渲染通道：确认 playblast 到底用了哪台相机。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = os.path.join(ROOT, "ds_stills", "test")
os.makedirs(OUT, exist_ok=True)
res = {"errors": [], "docs": {}}

res["docs"]["ogsRender"] = (cmds.ogsRender.__doc__ or "")[:1500]

panels = cmds.getPanel(type="modelPanel") or []
visible = [p for p in panels if cmds.control(p, q=True, visible=True)]
res["panels"] = panels
res["visible"] = visible
panel = visible[0]
res["panel"] = panel

cam = cmds.ls("DS_S001_CAM*")[0]
shape = cmds.listRelatives(cam, shapes=True)[0]
res["cam"] = cam
res["focal_before"] = cmds.getAttr(shape + ".focalLength")

cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                 displayLights="default", grid=False, joints=False, cameras=False,
                 locators=False, manipulators=False, handles=False, headsUpDisplay=False)
cmds.select(clear=True)
cmds.setFocus(panel)
cmds.lookThru(panel, cam)
res["panel_cam_after_lookthru"] = cmds.modelEditor(panel, q=True, camera=True)
cmds.currentTime(1)
cmds.refresh(force=True)

base = os.path.join(OUT, "pb_58mm")
for f in glob.glob(base + "*.png"):
    os.remove(f)
cmds.playblast(frame=1, format="image", filename=base, sequenceTime=False, clearCache=True,
               viewer=False, showOrnaments=False, offScreen=True, percent=100,
               widthHeight=(960, 540), quality=95, compression="png")
res["pb_58"] = glob.glob(base + "*.png")

# 改焦距，若画面不变说明 playblast 没用这台相机
cmds.setAttr(shape + ".focalLength", 18.0)
cmds.refresh(force=True)
base2 = os.path.join(OUT, "pb_18mm")
for f in glob.glob(base2 + "*.png"):
    os.remove(f)
cmds.playblast(frame=1, format="image", filename=base2, sequenceTime=False, clearCache=True,
               viewer=False, showOrnaments=False, offScreen=True, percent=100,
               widthHeight=(960, 540), quality=95, compression="png")
res["pb_18"] = glob.glob(base2 + "*.png")
cmds.setAttr(shape + ".focalLength", res["focal_before"])
cmds.refresh(force=True)

with open(os.path.join(ROOT, "logs", "ds7_render_test.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "docs"}, ensure_ascii=False, indent=1))
