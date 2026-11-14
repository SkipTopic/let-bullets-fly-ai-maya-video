"""材质普查：每个人物/道具材质的类型、颜色、贴图连接，以及磁盘上的贴图文件。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "materials": {}, "file_textures": [], "disk_textures": []}

MESHES = {
    "Ma": "NH_MaleM_140_LOD0",
    "Huang": "Huang_AragakiFBXASC032Shinjiro_mesh",
    "Shiye": "Shiye_JunpeiFBXASC032Iori_mesh",
}
SET_MESHES = ["SET_table_top", "SET_floor", "SET_house_body", "SET_seat_0", "SET_back_0",
              "SET_bowl_0", "SET_cup_0", "SET_bottle", "SET_sky1"]

seen = set()
for label, mesh in list(MESHES.items()) + [(m, m) for m in SET_MESHES]:
    if not cmds.objExists(mesh):
        continue
    sgs = cmds.listConnections(mesh, type="shadingEngine") or []
    infos = []
    for sg in sgs:
        mats = cmds.listConnections(sg + ".surfaceShader") or []
        for m in mats:
            if m in seen:
                infos.append({"mat": m, "dup": True})
                continue
            seen.add(m)
            d = {"mat": m, "type": cmds.nodeType(m), "sg": sg}
            for attr in ("color", "baseColor", "diffuse", "incandescence", "roughness"):
                if cmds.attributeQuery(attr, node=m, exists=True):
                    try:
                        v = cmds.getAttr(m + "." + attr)
                        d[attr] = [round(c, 3) for c in v[0]] if isinstance(v, list) else v
                    except Exception:
                        pass
            tex = cmds.listConnections(m, type="file") or []
            d["file_nodes"] = tex
            for t in tex:
                try:
                    d.setdefault("textures", []).append(cmds.getAttr(t + ".fileTextureName"))
                except Exception:
                    pass
            infos.append(d)
    OUT["materials"][label] = infos

OUT["file_textures"] = sorted(cmds.ls(type="file") or [])
for base in ("models_raw", "models_new", "models_fbx", "models_fbx2", "assets"):
    p = os.path.join(ROOT, base)
    if os.path.isdir(p):
        for ext in ("png", "jpg", "jpeg", "tga", "bmp"):
            OUT["disk_textures"] += glob.glob(os.path.join(p, "**", "*." + ext), recursive=True)[:400]

with open(os.path.join(ROOT, "logs", "ds31_mat.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for k, v in OUT["materials"].items():
    print("==", k)
    for m in v[:8]:
        if m.get("dup"):
            print("   (dup)", m["mat"])
        else:
            print("   ", m["mat"], m["type"], m.get("color") or m.get("baseColor"), "tex:", m.get("textures"))
print("file nodes", len(OUT["file_textures"]), "disk textures", len(OUT["disk_textures"]))
print(OUT["disk_textures"][:10])
