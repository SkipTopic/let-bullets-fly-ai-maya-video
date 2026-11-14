"""调平相机光并重渲 71 镜静帧（v05）。"""
import glob
import json
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
DESIGN = os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json")
STILL_DIR = os.path.join(ROOT, "ds_stills", "v05_71")
OUT = {"errors": [], "files": {}}

try:
    for lt in cmds.ls("DS_*_LGT", type="pointLight") or []:
        cmds.setAttr(lt + ".intensity", 0.62)

    data = json.load(open(DESIGN, encoding="utf-8"))["shots"]
    os.makedirs(STILL_DIR, exist_ok=True)
    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="all", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     selectionHiliteDisplay=False, lights=False)
    cmds.select(clear=True)
    for s in data:
        sid = s["id"]
        cam = cmds.ls("DS_%s_CAM*" % sid)
        if not cam:
            OUT["errors"].append("missing cam " + sid)
            continue
        cmds.setFocus(panel)
        cmds.lookThru(panel, cam[0])
        fr = s["frame_range"][0] + (s["frame_range"][1] - s["frame_range"][0]) // 2
        cmds.currentTime(fr)
        cmds.refresh(force=True)
        base = os.path.join(STILL_DIR, "DS_" + sid)
        cmds.playblast(frame=fr, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
        got = sorted(glob.glob(base + "*.png"))
        OUT["files"][sid] = got[0] if got else None
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds18_v05.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "n": sum(1 for v in OUT["files"].values() if v),
                  "err": OUT["errors"][:1]}, ensure_ascii=False))
