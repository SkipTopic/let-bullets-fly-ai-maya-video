"""渲染指定镜号的序列帧（playblast 连续帧），参数在 cmd/ds_seq_param.json。"""
import glob
import json
import os
import time
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PARAM = os.path.join(ROOT, "cmd", "ds_seq_param.json")
OUT = {"errors": [], "done": []}

try:
    p = json.load(open(PARAM, encoding="utf-8"))
    ids = p["ids"]
    outdir = p["outdir"]
    w, h, q = p.get("w", 960), p.get("h", 540), p.get("q", 85)
    os.makedirs(outdir, exist_ok=True)
    shots = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
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
            OUT["errors"].append("missing cam " + sid)
            continue
        s = shots[sid]
        f0, f1 = s["frame_range"]
        cmds.lookThru(panel, cam[0])
        cmds.setFocus(panel)
        cmds.refresh(force=True)
        t0 = time.time()
        base = os.path.join(outdir, sid)
        cmds.playblast(startTime=f0, endTime=f1, filename=base, format="image",
                       sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                       offScreen=True, percent=100, widthHeight=(w, h), quality=q,
                       compression="png")
        n = len(glob.glob(base + "*.png"))
        OUT["done"].append({"id": sid, "frames": n, "sec": round(time.time() - t0, 1),
                            "range": [f0, f1]})
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds27_seq.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "done": OUT["done"], "err": OUT["errors"][:1]}, ensure_ascii=False)[:600])
