import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"tests": []}

def wpos(j):
    p = cmds.xform(j, q=True, ws=True, t=True)
    return [round(v, 2) for v in p]

def reset():
    for j in ("LeftArm", "RightArm", "LeftForeArm", "RightForeArm",
              "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg",
              "Spine", "Spine1", "Neck", "Head"):
        if cmds.objExists(j):
            cmds.setAttr(j + ".rotate", 0, 0, 0)

reset()
base = {j: wpos(j) for j in ("LeftHand", "RightHand", "Head", "LeftFoot", "Hips")}
OUT["base"] = base

def probe(joint, axis, deg):
    reset()
    cur = cmds.getAttr(joint + ".rotate")[0]
    v = list(cur)
    v["XYZ".index(axis)] = deg
    cmds.setAttr(joint + ".rotate", *v)
    cmds.refresh(force=True)
    return wpos("LeftHand" if "Left" in joint else "RightHand")

for joint in ("LeftArm", "RightArm", "LeftUpLeg", "RightUpLeg", "LeftForeArm"):
    row = {"joint": joint, "base": wpos("LeftHand" if "Left" in joint else "RightHand")}
    for axis in ("X", "Y", "Z"):
        row[axis] = probe(joint, axis, 60)
    OUT["tests"].append(row)

reset()
# 坐姿：髋部前抬 + 膝弯
cmds.setAttr("LeftUpLeg.rotateX", 88)
cmds.setAttr("RightUpLeg.rotateX", 88)
cmds.setAttr("LeftLeg.rotateX", -88)
cmds.setAttr("RightLeg.rotateX", -88)
cmds.refresh(force=True)
OUT["sit_test"] = {j: wpos(j) for j in ("Hips", "LeftFoot", "RightFoot", "Head", "LeftHand")}

with open(os.path.join(ROOT, "logs", "t5_pose.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
