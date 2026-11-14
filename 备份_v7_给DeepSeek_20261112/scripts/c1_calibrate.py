import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"calib": []}

# ---------- 干净导入 ----------
cmds.file(new=True, force=True)
cmds.file(os.path.join(ROOT, "models_fbx", "CH_Ma.fbx"), i=True, ignoreVersion=True,
          ra=True, mergeNamespacesOnClash=False, namespace=":")

all_meshes = cmds.ls(type="mesh", ni=True) or []
main = [m for m in all_meshes if cmds.listConnections(m, type="skinCluster")][0]
tr = cmds.listRelatives(main, parent=True)[0]
cmds.rename(tr, "CH_Ma_GEO")

def all_bones():
    return cmds.ls(type="joint") or []

def reset():
    for j in all_bones():
        for a in ("X", "Y", "Z"):
            try:
                cmds.setAttr("%s.rotate%s" % (j, a), 0)
            except Exception:
                pass
    cmds.refresh(force=True)

def wpos(n):
    return cmds.xform(n, q=True, ws=True, t=True)

reset()
REST = {n: [round(v, 3) for v in wpos(n)] for n in
        ("LeftHand", "RightHand", "Head", "LeftFoot", "RightFoot", "Hips", "LeftForeArm", "LeftUpLeg")}
OUT["rest"] = REST

LEAF = {
    "LeftArm": "LeftHand", "LeftForeArm": "LeftHand",
    "RightArm": "RightHand", "RightForeArm": "RightHand",
    "LeftUpLeg": "LeftFoot", "LeftLeg": "LeftFoot",
    "RightUpLeg": "RightFoot", "RightLeg": "RightFoot",
    "Spine": "Head", "Spine1": "Head", "Neck": "Head", "Hips": "Head",
}
DEG = 45

for bone, leaf in LEAF.items():
    if not cmds.objExists(bone):
        continue
    for axis in ("X", "Y", "Z"):
        reset()
        cmds.setAttr("%s.rotate%s" % (bone, axis), DEG)
        cmds.refresh(force=True)
        p = wpos(leaf)
        d = [round(p[i] - REST[leaf][i], 2) for i in range(3)]
        dist = round(sum(x * x for x in d) ** 0.5, 2)
        OUT["calib"].append({"bone": bone, "axis": axis, "deg": DEG,
                             "leaf": leaf, "delta": d, "dist": dist})
reset()

# 面部形态键清单检查
blends = cmds.ls(type="blendShape") or []
OUT["blendShapes"] = blends
if blends:
    OUT["targets"] = cmds.blendShape(blends[0], q=True, target=True)

with open(os.path.join(ROOT, "logs", "c1_calib.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
