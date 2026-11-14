"""诊断：三人网格与骨架的真实世界包围盒，和 S001 相机的相对关系。"""
import json
import math
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
MESHES = {"Ma": "NH_MaleM_140_LOD0", "Huang": "Huang_AragakiFBXASC032Shinjiro_mesh",
          "Shiye": "Shiye_JunpeiFBXASC032Iori_mesh"}
GROUPS = {"Ma": "CHR_Ma", "Huang": "CHR_Huang", "Shiye": "CHR_Shiye"}

out = {"meshes": {}, "groups": {}, "cams": {}}
for k, m in MESHES.items():
    bb = cmds.exactWorldBoundingBox(m)
    out["meshes"][k] = {
        "bbox": [round(v, 1) for v in bb],
        "center": [round((bb[0] + bb[3]) / 2, 1), round((bb[1] + bb[4]) / 2, 1), round((bb[2] + bb[5]) / 2, 1)],
        "size": [round(bb[3] - bb[0], 1), round(bb[4] - bb[1], 1), round(bb[5] - bb[2], 1)],
        "transform": [round(v, 2) for v in cmds.xform(m, q=True, ws=True, t=True)],
        "parent": (cmds.listRelatives(m, parent=True) or [None])[0],
        "scale": [round(v, 3) for v in cmds.xform(m, q=True, ws=True, s=True)],
    }
for k, g in GROUPS.items():
    out["groups"][k] = {
        "translate": [round(v, 2) for v in cmds.xform(g, q=True, ws=True, t=True)],
        "rotate": [round(v, 2) for v in cmds.xform(g, q=True, ws=True, ro=True)],
        "scale": [round(v, 3) for v in cmds.xform(g, q=True, ws=True, s=True)],
    }

for cid in ("S001", "P_MA", "S003"):
    cam = cmds.ls("DS_%s_CAM*" % cid)[0]
    m = cmds.xform(cam, q=True, ws=True, m=True)
    eye = (m[12], m[13], m[14])
    bb = cmds.exactWorldBoundingBox(MESHES["Ma"])
    center = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
    out["cams"][cid] = {"eye": [round(v, 1) for v in eye],
                        "dist_to_Ma_center": round(math.dist(eye, center), 1),
                        "dist_to_Ma_mesh_bbox_corner": round(math.dist(eye, (bb[0], bb[1], bb[2])), 1)}

with open(os.path.join(ROOT, "logs", "ds8_meshcheck.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
