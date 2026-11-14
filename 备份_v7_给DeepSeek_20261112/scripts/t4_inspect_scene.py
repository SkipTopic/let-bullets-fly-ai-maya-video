import maya.cmds as cmds
import json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}

joints = cmds.ls(type="joint") or []
OUT["joint_count"] = len(joints)
OUT["joints"] = joints

# 只保留主角色的关键骨（有名字意义的）
key = [j for j in joints if any(k in j for k in
       ["Root", "Center", "Groove", "Hips", "Spine", "Neck", "Head",
        "Arm", "ForeArm", "Hand", "Shoulder", "UpLeg", "Leg", "Foot", "Toe",
        "Thumb", "Index", "Middle", "Ring", "Pinky", "Eye"])]
OUT["key_joints"] = key

OUT["materials"] = cmds.ls(type="material") or []
OUT["file_nodes"] = cmds.ls(type="file") or []
sg = cmds.ls(type="shadingEngine") or []
OUT["sg_count"] = len(sg)

# 每个材质的颜色
cols = {}
for m in (cmds.ls(type="lambert") or []) + (cmds.ls(type="blinn") or []) + (cmds.ls(type="phong") or []):
    try:
        cols[m] = [round(v, 3) for v in cmds.getAttr(m + ".color")[0]]
    except Exception:
        pass
OUT["material_colors"] = cols

with open(os.path.join(ROOT, "logs", "t4_scene.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
