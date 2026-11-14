import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "scenes": {}}


def vec(node, attr):
    try:
        return [round(v, 4) for v in cmds.getAttr(node + "." + attr)[0]]
    except Exception:
        return None


def joint_info(name):
    if not cmds.objExists(name):
        return None
    data = {
        "rotate": vec(name, "rotate"),
        "jointOrient": vec(name, "jointOrient"),
        "world_translate": [round(v, 4) for v in cmds.xform(name, q=True, ws=True, t=True)],
        "world_rotate": [round(v, 4) for v in cmds.xform(name, q=True, ws=True, ro=True)],
        "parents": cmds.listRelatives(name, parent=True, fullPath=True) or [],
    }
    anim = cmds.listConnections(name + ".rotate", type="animCurve", s=True, d=False) or []
    data["rotate_animation"] = anim
    return data


def mesh_info(mesh):
    tr = cmds.listRelatives(mesh, parent=True, fullPath=True) or [mesh]
    return {
        "shape": mesh,
        "transform": tr[0],
        "bbox": [round(v, 3) for v in cmds.xform(tr[0], q=True, ws=True, bb=True)],
        "vertices": cmds.polyEvaluate(mesh, vertex=True),
        "skins": cmds.listConnections(mesh, type="skinCluster") or [],
    }


def inspect_scene(path, mode):
    cmds.file(path, o=True, f=True)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    data = {
        "file": cmds.file(q=True, sn=True),
        "roots": cmds.ls(assemblies=True),
        "chars_children": cmds.listRelatives("CHARS", children=True) if cmds.objExists("CHARS") else [],
        "meshes": [mesh_info(m) for m in (cmds.ls(type="mesh", long=True) or []) if not cmds.getAttr(m + ".intermediateObject")],
        "delta_mush": cmds.ls(type="deltaMush") or [],
        "cameras": cmds.ls(type="camera", long=True) or [],
        "groups": {},
        "joints": {},
    }
    if mode == "old":
        for group in ("CHR_Ma", "CHR_Huang", "CHR_Shiye", "GRP_Ma", "GRP_Huang", "GRP_Shiye"):
            if cmds.objExists(group):
                data["groups"][group] = {"translate": vec(group, "translate"), "rotate": vec(group, "rotate"), "scale": vec(group, "scale")}
        for prefix in ("Ma_", "Huang_", "Shiye_"):
            for bone in ("Root", "Hips", "Spine", "Spine1", "Neck", "Head", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"):
                info = joint_info(prefix + bone)
                if info:
                    data["joints"][prefix + bone] = info
    else:
        for bone in ("Bip001", "Bip001Pelvis", "Bip001Spine", "Bip001Spine1", "Bip001Spine2", "Bip001Neck", "Bip001Head", "Bip001LUpperArm", "Bip001LForearm", "Bip001LHand", "Bip001RUpperArm", "Bip001RForearm", "Bip001RHand", "Bip001LThigh", "Bip001LCalf", "Bip001LFoot", "Bip001RThigh", "Bip001RCalf", "Bip001RFoot"):
            info = joint_info(bone)
            if info:
                data["joints"][bone] = info
        data["joint_count"] = len(cmds.ls(type="joint") or [])
        data["joint_names"] = cmds.ls(type="joint") or []
    return data


try:
    OUT["scenes"]["hand_v2"] = inspect_scene(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), "old")
    OUT["scenes"]["new_ma"] = inspect_scene(os.path.join(ROOT, "scenes", "NEWM_test.mb"), "new")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "q1_inspect.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
