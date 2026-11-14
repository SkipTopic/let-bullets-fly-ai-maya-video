import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "characters": {}}


def attrs(node):
    data = {}
    for attr in ("translate", "rotate", "scale", "jointOrient"):
        if cmds.attributeQuery(attr, node=node, exists=True):
            try:
                data[attr] = list(cmds.getAttr(node + "." + attr)[0])
            except Exception:
                pass
    data["parent"] = (cmds.listRelatives(node, parent=True) or [None])[0]
    return data


try:
    cmds.loadPlugin("fbxmaya", quiet=True)
    for key in ("Ma", "Huang", "Shiye"):
        cmds.file(new=True, f=True)
        path = os.path.join(ROOT, "models_fbx2", "CH_%s.fbx" % key)
        cmds.file(path, i=True, type="FBX", ignoreVersion=True, options="v=0;", pr=True, ra=True)
        cmds.currentTime(1)
        cmds.refresh(force=True)
        joints = cmds.ls(type="joint") or []
        transforms = {}
        for node in joints + (cmds.ls(assemblies=True) or []):
            if node in ("persp", "top", "front", "side"):
                continue
            transforms[node] = attrs(node)
        meshes = []
        for mesh in (cmds.ls(type="mesh", long=True) or []):
            if cmds.getAttr(mesh + ".intermediateObject"):
                continue
            tr = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
            meshes.append({"shape": mesh, "transform": tr, "bbox": list(cmds.xform(tr, q=True, ws=True, bb=True)), "vertices": cmds.polyEvaluate(mesh, vertex=True)})
        key_positions = {}
        for bone in ("Root", "Center", "Groove", "Bone", "LowerBody", "Spine", "Spine1", "Neck", "Head", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"):
            if cmds.objExists(bone):
                key_positions[bone] = {"world": list(cmds.xform(bone, q=True, ws=True, t=True)), "world_rotate": list(cmds.xform(bone, q=True, ws=True, ro=True))}
        OUT["characters"][key] = {"transforms": transforms, "joints": joints, "meshes": meshes, "key_positions": key_positions}
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "q2_rest.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
