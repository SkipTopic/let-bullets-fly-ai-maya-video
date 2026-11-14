import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}

names = ["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"]

def dump(tag):
    d = {"tag": tag}
    for n in names:
        d[n] = {
            "ws": [round(v, 2) for v in cmds.xform(n, q=True, ws=True, t=True)],
            "rot": [round(v, 2) for v in cmds.getAttr(n + ".rotate")[0]],
        }
    d["rootLock"] = [cmds.getAttr("LeftArm.rotateX", lock=True),
                     cmds.getAttr("LeftArm.rotateY", lock=True),
                     cmds.getAttr("LeftArm.rotateZ", lock=True)]
    d["jointOrient"] = [round(v, 2) for v in cmds.getAttr("LeftArm.jointOrient")[0]]
    d["rotateOrder"] = cmds.getAttr("LeftArm.rotateOrder")
    return d

OUT["before"] = dump("before")
cmds.setAttr("LeftArm.rotateZ", 75)
cmds.refresh(force=True)
OUT["after"] = dump("after")
cmds.setAttr("LeftArm.rotateZ", 0)
cmds.refresh(force=True)

# 父级世界矩阵
m = cmds.xform("LeftArm", q=True, ws=True, matrix=True)
OUT["leftArm_matrix"] = [round(v, 4) for v in m]

with open(os.path.join(ROOT, "logs", "t9_decisive.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
