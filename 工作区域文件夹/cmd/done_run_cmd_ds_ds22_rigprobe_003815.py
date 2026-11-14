"""摸清三人的手臂骨链与世界坐标，供手部 IK 使用。"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "chars": {}}

ROOTS = {"Ma": "CHR_Ma", "Huang": "CHR_Huang", "Shiye": "CHR_Shiye"}

for name, root in ROOTS.items():
    joints = cmds.listRelatives(root, allDescendents=True, type="joint") or []
    joints = list(reversed(joints))
    info = []
    for j in joints:
        t = cmds.xform(j, q=True, ws=True, t=True)
        info.append({
            "name": j,
            "parent": (cmds.listRelatives(j, parent=True) or [None])[0],
            "world": [round(v, 1) for v in t],
        })
    OUT["chars"][name] = info

with open(os.path.join(ROOT, "logs", "ds22_rig.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for name, info in OUT["chars"].items():
    print("==", name, len(info), "joints")
    for j in info:
        if any(k in j["name"] for k in ("Arm", "Hand", "Shoulder", "Clavicle", "Forearm", "Head", "Neck", "Spine")):
            print("  ", j["name"], "<-", j["parent"], j["world"])
