import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}
CHK = os.path.join(ROOT, "_接手检查")
os.makedirs(CHK, exist_ok=True)

def shot(tag):
    base = os.path.join(CHK, "t7_" + tag)
    cmds.playblast(frame=1, format="image", filename=base, sequenceTime=0,
                   clearCache=1, viewer=0, showOrnaments=0, fp=4, percent=100,
                   widthHeight=[640, 360], quality=90, compression="png")
    return [f for f in os.listdir(CHK) if f.startswith("t7_" + tag)]

# 相机（正面全身）
if cmds.objExists("TCAM"):
    cmds.lookThru("TCAM")

for j in ("LeftArm", "RightArm", "LeftForeArm", "RightForeArm",
          "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg"):
    if cmds.objExists(j):
        cmds.setAttr(j + ".rotate", 0, 0, 0)
cmds.refresh(force=True)

OUT["rest"] = shot("rest")

# 极端测试：左臂 Z +75
cmds.setAttr("LeftArm.rotateZ", 75)
cmds.refresh(force=True)
OUT["armZ75"] = shot("armZ75")
OUT["armZ75_hand"] = [round(v, 2) for v in cmds.xform("LeftHand", q=True, ws=True, t=True)]

cmds.setAttr("LeftArm.rotateZ", 0)
cmds.setAttr("LeftArm.rotateX", 75)
cmds.refresh(force=True)
OUT["armX75"] = shot("armX75")
OUT["armX75_hand"] = [round(v, 2) for v in cmds.xform("LeftHand", q=True, ws=True, t=True)]

cmds.setAttr("LeftArm.rotateX", 0)
cmds.setAttr("LeftArm.rotateY", 75)
cmds.refresh(force=True)
OUT["armY75"] = shot("armY75")
OUT["armY75_hand"] = [round(v, 2) for v in cmds.xform("LeftHand", q=True, ws=True, t=True)]

cmds.setAttr("LeftArm.rotate", 0, 0, 0)
cmds.refresh(force=True)

with open(os.path.join(ROOT, "logs", "t7_move.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
