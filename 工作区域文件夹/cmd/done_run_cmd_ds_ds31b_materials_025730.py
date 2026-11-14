"""材质普查 v2：从 shape 查材质，列出颜色/贴图/UV 与磁盘贴图对应关系。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "by_mesh": {}, "materials": {}, "disk": {}}

chars = {"Ma": "NH_MaleM_140_LOD0Shape", "Huang": "Huang_AragakiFBXASC032Shinjiro_meshShape",
         "Shiye": "Shiye_JunpeiFBXASC032Iori_meshShape"}
sets = ["SET_table_topShape", "SET_floorShape", "SET_house_bodyShape", "SET_seat_0Shape",
        "SET_back_0Shape", "SET_bowl_0Shape", "SET_cup_0Shape", "SET_bottleShape", "SET_sky1Shape",
        "SET_col_0Shape", "SET_tree_0Shape", "SET_roofShape", "SET_lowwall_LShape", "SET_stepShape"]

for label, shape in list(chars.items()) + [(s.replace("Shape", ""), s) for s in sets]:
    if not cmds.objExists(shape):
        continue
    sgs = cmds.listConnections(shape, type="shadingEngine") or []
    mats = []
    for sg in sgs:
        for m in (cmds.listConnections(sg + ".surfaceShader") or []):
            if m not in mats:
                mats.append(m)
    OUT["by_mesh"][label] = {"shape": shape, "materials": mats, "sg": sgs}

for m in (cmds.ls(type="lambert") or []) + (cmds.ls(type="phong") or []) + \
         (cmds.ls(type="blinn") or []) + (cmds.ls(type="standardSurface") or []):
    d = {"type": cmds.nodeType(m)}
    for attr in ("color", "base", "baseColor", "diffuse", "ambientColor", "incandescence"):
        if cmds.attributeQuery(attr, node=m, exists=True):
            try:
                v = cmds.getAttr(m + "." + attr)
                d[attr] = [round(c, 3) for c in v[0]] if isinstance(v, list) else round(v, 3)
            except Exception:
                pass
    tex = cmds.listConnections(m, type="file") or []
    if tex:
        d["textures"] = [cmds.getAttr(t + ".fileTextureName") for t in tex]
    OUT["materials"][m] = d

for base in ("models_raw", "models_new", "models_fbx", "models_fbx2"):
    p = os.path.join(ROOT, base)
    if not os.path.isdir(p):
        continue
    files = []
    for ext in ("png", "jpg", "jpeg", "tga", "bmp", "dds"):
        files += glob.glob(os.path.join(p, "**", "*." + ext), recursive=True)
    OUT["disk"][base] = sorted(files)

with open(os.path.join(ROOT, "logs", "ds31_mat.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for k, v in OUT["by_mesh"].items():
    print("==", k, "->", v["materials"][:6])
print("--- distinct materials", len(OUT["materials"]))
for m, d in list(OUT["materials"].items())[:25]:
    print("  ", m, d.get("type"), d.get("color") or d.get("base"), d.get("textures"))
print("--- disk")
for b, f in OUT["disk"].items():
    print("  ", b, len(f))
    for x in f[:6]:
        print("     ", os.path.relpath(x, ROOT))
