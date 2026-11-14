"""逐人隐藏渲染，定位画面里的大块白色物体属于谁。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUTDIR = os.path.join(ROOT, "ds_stills", "isolate")
os.makedirs(OUTDIR, exist_ok=True)
MESHES = {"Ma": "NH_MaleM_140_LOD0", "Huang": "Huang_AragakiFBXASC032Shinjiro_mesh",
          "Shiye": "Shiye_JunpeiFBXASC032Iori_mesh"}
out = {"errors": [], "files": {}}

panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                 displayLights="default", grid=False, joints=False, cameras=False,
                 locators=False, manipulators=False, handles=False, headsUpDisplay=False)
cmds.setFocus(panel)
cmds.lookThru(panel, "DS_S001_CAM1")
cmds.currentTime(1)


def shot(tag):
    cmds.refresh(force=True)
    base = os.path.join(OUTDIR, tag)
    for f in glob.glob(base + "*.png"):
        os.remove(f)
    cmds.playblast(frame=1, format="image", filename=base, sequenceTime=False, clearCache=True,
                   viewer=False, showOrnaments=False, offScreen=True, percent=100,
                   widthHeight=(960, 540), quality=95, compression="png")
    out["files"][tag] = glob.glob(base + "*.png")


try:
    shot("all")
    for key, mesh in MESHES.items():
        cmds.setAttr(mesh + ".visibility", False)
        shot("no_" + key)
        cmds.setAttr(mesh + ".visibility", True)
    for key, mesh in MESHES.items():
        for other, m2 in MESHES.items():
            cmds.setAttr(m2 + ".visibility", other == key)
        shot("only_" + key)
    for mesh in MESHES.values():
        cmds.setAttr(mesh + ".visibility", True)
    out["ok"] = True
except Exception as exc:  # noqa: BLE001
    out["errors"].append(repr(exc))

with open(os.path.join(ROOT, "logs", "ds12_isolate.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
