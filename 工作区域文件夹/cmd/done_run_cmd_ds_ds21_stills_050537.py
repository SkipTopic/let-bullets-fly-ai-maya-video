"""分块渲染指定镜号的静帧，参数写在 cmd/ds_still_param.json。"""
import glob
import json
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PARAM = os.path.join(ROOT, "cmd", "ds_still_param.json")
OUT = {"errors": [], "files": {}}

try:
    p = json.load(open(PARAM, encoding="utf-8"))
    ids = p["ids"]
    outdir = p["outdir"]
    os.makedirs(outdir, exist_ok=True)
    data = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                                               encoding="utf-8"))["shots"]}

    panel = [x for x in cmds.getPanel(type="modelPanel") if cmds.control(x, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="all", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     selectionHiliteDisplay=False, lights=False)
    cmds.select(clear=True)

    for sid in ids:
        cam = cmds.ls("DS_%s_CAM*" % sid)
        if not cam:
            OUT["errors"].append("missing " + sid)
            continue
        cmds.setFocus(panel)
        cmds.lookThru(panel, cam[0])
        s = data[sid]
        fr = s["frame_range"][0] + (s["frame_range"][1] - s["frame_range"][0]) // 2
        cmds.currentTime(fr)
        cmds.refresh(force=True)
        base = os.path.join(outdir, "DS_" + sid)
        cmds.playblast(frame=fr, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
        got = sorted(glob.glob(base + "*.png"))
        OUT["files"][sid] = got[0] if got else None
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds21_stills.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "n": sum(1 for v in OUT["files"].values() if v),
                  "err": OUT["errors"][:1]}, ensure_ascii=False))
