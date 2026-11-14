import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}

# 复位
for j in ("LeftArm", "RightArm", "LeftForeArm", "RightForeArm",
          "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg",
          "Spine", "Spine1", "Neck", "Head", "Hips"):
    if cmds.objExists(j):
        cmds.setAttr(j + ".rotate", 0, 0, 0)
cmds.refresh(force=True)

chain = ["Root", "Center", "Groove", "Hips", "Spine", "Spine1", "Neck", "Head",
         "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
         "RightShoulder", "RightArm", "RightForeArm", "RightHand",
         "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"]
OUT["world_pos"] = {}
for j in chain:
    if cmds.objExists(j):
        p = cmds.xform(j, q=True, ws=True, t=True)
        OUT["world_pos"][j] = [round(v, 2) for v in p]

# 父级链和变换
OUT["parent"] = {}
for j in chain:
    if cmds.objExists(j):
        par = cmds.listRelatives(j, parent=True)
        OUT["parent"][j] = par[0] if par else None

# 骨长
OUT["bone_len"] = {}
for j in ("LeftArm", "LeftForeArm", "LeftHand", "LeftUpLeg", "LeftLeg"):
    if cmds.objExists(j):
        try:
            OUT["bone_len"][j] = round(cmds.getAttr(j + ".length"), 3)
        except Exception:
            OUT["bone_len"][j] = None

# 蒙皮信息
mesh = "CH_Ma_GEOShape"
if cmds.objExists(mesh):
    sc = cmds.listConnections(mesh, type="skinCluster") or []
    OUT["skinCluster"] = sc
    if sc:
        inf = cmds.skinCluster(sc[0], q=True, influence=True) or []
        OUT["influences"] = len(inf)
        OUT["influence_sample"] = inf[:10]
        # 是否真的有权重：取一个顶点看权重
        try:
            w = cmds.skinPercent(sc[0], mesh + ".vtx[100]", q=True, value=True)
            OUT["vtx100_weights_nonzero"] = [round(x, 3) for x in w if x > 0.001]
        except Exception as e:
            OUT["vtx_err"] = repr(e)
    OUT["mesh_transform"] = {
        "translate": [round(v, 3) for v in cmds.getAttr("CH_Ma_GEO.translate")[0]],
        "rotate": [round(v, 3) for v in cmds.getAttr("CH_Ma_GEO.rotate")[0]],
        "scale": [round(v, 4) for v in cmds.getAttr("CH_Ma_GEO.scale")[0]],
        "parent": cmds.listRelatives("CH_Ma_GEO", parent=True),
    }

# 骨架根节点变换
arm = cmds.listRelatives("Root", parent=True)
OUT["armature_root"] = arm
if arm:
    OUT["armature_transform"] = {
        "translate": [round(v, 3) for v in cmds.getAttr(arm[0] + ".translate")[0]],
        "rotate": [round(v, 3) for v in cmds.getAttr(arm[0] + ".rotate")[0]],
        "scale": [round(v, 4) for v in cmds.getAttr(arm[0] + ".scale")[0]],
    }

with open(os.path.join(ROOT, "logs", "t6_layout.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
