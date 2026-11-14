import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
CONFIG = {
    "Ma": {
        "group": "CHR_Ma", "mesh": "NH_MaleM_140_LOD0",
        "joints": ["Bip001", "Bip001Pelvis", "Bip001Spine", "Bip001Spine1", "Bip001Spine2", "Bip001Neck", "Bip001Head", "Bip001LClavicle", "Bip001LUpperArm", "Bip001LForearm", "Bip001LHand", "Bip001RClavicle", "Bip001RUpperArm", "Bip001RForearm", "Bip001RHand", "Bip001LThigh", "Bip001LCalf", "Bip001LFoot", "Bip001RThigh", "Bip001RCalf", "Bip001RFoot"],
    },
    "Huang": {
        "group": "CHR_Huang", "mesh": "Huang_AragakiFBXASC032Shinjiro_mesh",
        "joints": ["Huang_Root", "Huang_Center", "Huang_Groove", "Huang_Bone", "Huang_Spine", "Huang_Spine1", "Huang_Neck", "Huang_Head", "Huang_LeftShoulder", "Huang_LeftArm", "Huang_LeftArmTwist", "Huang_LeftForeArm", "Huang_LeftHandTwist", "Huang_LeftHand", "Huang_RightShoulder", "Huang_RightArm", "Huang_RightArmTwist", "Huang_RightForeArm", "Huang_RightHandTwist", "Huang_RightHand", "Huang_LeftUpLeg", "Huang_LeftLeg", "Huang_LeftFoot", "Huang_RightUpLeg", "Huang_RightLeg", "Huang_RightFoot"],
    },
    "Shiye": {
        "group": "CHR_Shiye", "mesh": "Shiye_JunpeiFBXASC032Iori_mesh",
        "joints": ["Shiye_Root", "Shiye_Center", "Shiye_Groove", "Shiye_Bone", "Shiye_Spine", "Shiye_Spine1", "Shiye_Neck", "Shiye_Head", "Shiye_LeftShoulder", "Shiye_LeftArm", "Shiye_LeftArmTwist", "Shiye_LeftForeArm", "Shiye_LeftHandTwist", "Shiye_LeftHand", "Shiye_RightShoulder", "Shiye_RightArm", "Shiye_RightArmTwist", "Shiye_RightForeArm", "Shiye_RightHandTwist", "Shiye_RightHand", "Shiye_LeftUpLeg", "Shiye_LeftLeg", "Shiye_LeftFoot", "Shiye_RightUpLeg", "Shiye_RightLeg", "Shiye_RightFoot"],
    },
}


def vector(node, attr):
    try:
        return list(cmds.getAttr(node + "." + attr)[0])
    except Exception:
        return None


def joint_record(node):
    if not cmds.objExists(node):
        return None
    return {
        "parent": (cmds.listRelatives(node, parent=True) or [None])[0],
        "local_translate": vector(node, "translate"),
        "local_rotate": vector(node, "rotate"),
        "local_scale": vector(node, "scale"),
        "joint_orient": vector(node, "jointOrient"),
        "rotate_order": cmds.getAttr(node + ".rotateOrder"),
        "world_translate": list(cmds.xform(node, q=True, ws=True, t=True)),
        "world_rotate": list(cmds.xform(node, q=True, ws=True, ro=True)),
        "world_matrix": cmds.xform(node, q=True, ws=True, m=True),
        "rotate_connections": cmds.listConnections(node + ".rotate", s=True, d=False) or [],
    }


try:
    path = os.path.join(ROOT, "scenes", "摆姿重建_v7.mb")
    cmds.file(path, o=True, f=True)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    OUT["scene"] = cmds.file(q=True, sn=True)
    OUT["maya_version"] = cmds.about(version=True)
    OUT["linear_unit"] = cmds.currentUnit(q=True, linear=True)
    OUT["time_unit"] = cmds.currentUnit(q=True, time=True)
    OUT["playback"] = {"min": cmds.playbackOptions(q=True, min=True), "max": cmds.playbackOptions(q=True, max=True), "animation_start": cmds.playbackOptions(q=True, animationStartTime=True), "animation_end": cmds.playbackOptions(q=True, animationEndTime=True)}
    OUT["modified"] = cmds.file(q=True, modified=True)
    OUT["references"] = cmds.file(q=True, reference=True) or []
    OUT["file_texture_nodes"] = cmds.ls(type="file") or []
    OUT["unknown_nodes"] = cmds.ls(type="unknown") or []
    OUT["blend_shapes"] = cmds.ls(type="blendShape") or []
    OUT["animation_curves"] = cmds.ls(type="animCurve") or []
    OUT["ik_handles"] = cmds.ls(type="ikHandle") or []
    OUT["delta_mush"] = cmds.ls(type="deltaMush") or []
    OUT["camera_shapes"] = cmds.ls(type="camera", long=True) or []
    OUT["assemblies"] = cmds.ls(assemblies=True) or []
    OUT["scene_children"] = cmds.listRelatives("SCENE", children=True) or []
    OUT["chars_children"] = cmds.listRelatives("CHARS", children=True) or []
    OUT["characters"] = {}
    for key, cfg in CONFIG.items():
        group = cfg["group"]
        mesh = cfg["mesh"]
        shape = cmds.listRelatives(mesh, shapes=True, ni=True, fullPath=True)[0]
        OUT["characters"][key] = {
            "group": {"local_translate": vector(group, "translate"), "local_rotate": vector(group, "rotate"), "world_matrix": cmds.xform(group, q=True, ws=True, m=True)},
            "mesh": {"shape": shape, "parent": cmds.listRelatives(mesh, parent=True) or [], "visible": cmds.getAttr(mesh + ".visibility"), "bbox": list(cmds.xform(mesh, q=True, ws=True, bb=True)), "vertices": cmds.polyEvaluate(shape, vertex=True), "skin_clusters": cmds.listConnections(shape, type="skinCluster") or []},
            "joints": {name: joint_record(name) for name in cfg["joints"] if cmds.objExists(name)},
        }
    props = {}
    for node in cmds.ls(type="transform", long=True) or []:
        short = node.split("|")[-1].lower()
        if any(word in short for word in ("cup", "bottle", "plate", "bowl", "chop", "wine", "glass", "candle", "seat", "table")):
            props[node] = {"parent": cmds.listRelatives(node, parent=True, fullPath=True) or [], "world_translate": list(cmds.xform(node, q=True, ws=True, t=True)), "world_bbox": list(cmds.xform(node, q=True, ws=True, bb=True))}
    OUT["props"] = props
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds0_scene_snapshot.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
