"""姿势可用性测试：抬手 / 举到嘴 / 前伸指人，各出一张，看手臂变形。"""
import json
import math
import os
import sys

import maya.cmds as cmds

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
import ds_animlib as A  # noqa: E402

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "poses": {}}

JOINTS = [j for n in ("Ma", "Huang", "Shiye") for j in (A.ARM[n]["L"] + A.ARM[n]["R"] + A.ARM[n]["head"])]

try:
    snap = A.snapshot(JOINTS)
    A.restore(snap)

    hp = A.HEAD["Ma"]
    f = A.fwd("Ma")
    l = A.left("Ma")
    hR = A.pos("Bip001RHand")
    hL = A.pos("Bip001LHand")

    poses = {
        "lift": (hR[0], hR[1] + 12.0, hR[2] + 4.0),
        "cup": (hp[0] - 2.0, 104.0, hp[2] + 14.0),
        "point": (hR[0] + f[0] * 34.0, 92.0, hR[2] + f[2] * 34.0),
        "thumb": (hR[0] + 4.0, 100.0, hR[2] + 10.0),
    }

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.lookThru(panel, cmds.ls("DS_S001_CAM*")[0])
    outdir = os.path.join(ROOT, "ds_stills", "posetest")
    os.makedirs(outdir, exist_ok=True)

    for name, tgt in poses.items():
        A.restore(snap)
        cmds.currentTime(1)
        A.two_bone_ik("Ma", "R", tgt)
        reached = A.pos("Bip001RHand")
        OUT["poses"][name] = {"target": [round(v, 1) for v in tgt],
                              "reached": [round(v, 1) for v in reached],
                              "err": round(math.dist(tgt, reached), 2)}
        cmds.refresh(force=True)
        cmds.playblast(frame=1, format="image", filename=os.path.join(outdir, name),
                       sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                       offScreen=True, percent=100, widthHeight=(960, 540), quality=90,
                       compression="png")
    A.restore(snap)
    OUT["ok"] = True
except Exception:  # noqa: BLE001
    import traceback
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds25_posetest.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "poses": OUT["poses"], "err": OUT["errors"][:1]}, ensure_ascii=False))
