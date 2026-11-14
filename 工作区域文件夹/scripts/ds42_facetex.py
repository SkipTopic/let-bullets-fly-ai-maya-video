"""按"正面度+面数"精确判定脸/头发，脸用贴图，头发用贴图或深色，身体保持纯色。"""
import json
import math
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
HEAD = {"Huang": (90.39, 123.19, 51.87, -120.0), "Shiye": (-89.20, 123.49, 51.37, 120.0)}
TEX = {
    "Huang": {"face": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_f1_tex00.png",
              "hair": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_h00_tex00.png"},
    "Shiye": {"face": r"{R}\models_raw\junpei_iori\textures\pc103_f1_tex00.png",
              "hair": r"{R}\models_raw\junpei_iori\textures\pc103_h00_tex00.png"},
}
SKIN = (0.80, 0.62, 0.50)
HAIR = (0.19, 0.15, 0.13)
OUT = {"errors": [], "picked": {}, "mode": {}}


def file_tex(path, name):
    if not os.path.exists(path):
        return None
    ex = cmds.ls(name, type="file")
    if ex:
        cmds.setAttr(ex[0] + ".fileTextureName", path, type="string")
        return ex[0]
    node = cmds.shadingNode("file", asTexture=True, isColorManaged=False, name=name)
    cmds.setAttr(node + ".fileTextureName", path, type="string")
    p2d = cmds.shadingNode("place2dTexture", asUtility=True, name=name + "_p2d")
    for a in ("coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger",
              "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"):
        try:
            cmds.connectAttr(p2d + "." + a, node + "." + a, f=True)
        except Exception:
            pass
    return node


try:
    use_tex = json.load(open(os.path.join(ROOT, "logs", "ds42_mode.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(ROOT, "logs", "ds42_mode.json")) else {}
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]

    for name, (hx, hy, hz, yaw) in HEAD.items():
        fx, fz = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        items = []
        for it in log.get(name, []):
            c = it.get("center")
            if not c:
                continue
            d = math.dist(c, (hx, hy, hz))
            if d > 16.0:
                continue
            fw = (c[0] - hx) * fx + (c[2] - hz) * fz
            items.append({"mat": it["mat"], "faces": it["faces"], "y": c[1], "fwd": fw, "dist": d})

        front = [i for i in items if i["fwd"] > 3.5]
        face = max(front, key=lambda i: i["faces"]) if front else None
        hair_cands = [i for i in items if i is not face and i["fwd"] <= 5.0]
        hair = max(hair_cands, key=lambda i: i["faces"]) if hair_cands else None

        OUT["picked"][name] = {"face": face["mat"][-24:] if face else None,
                               "hair": hair["mat"][-24:] if hair else None,
                               "face_f": face["faces"] if face else 0,
                               "hair_f": hair["faces"] if hair else 0}

        for i in items:
            mat = i["mat"]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            if face and mat == face["mat"]:
                tex = file_tex(TEX[name]["face"].format(R=ROOT), "DS_FACE_%s" % name)
                if tex:
                    cmds.connectAttr(tex + ".outColor", mat + ".color", f=True)
                    OUT["mode"][name + "_face"] = "texture"
                else:
                    cmds.setAttr(mat + ".color", *SKIN)
            elif hair and mat == hair["mat"]:
                tex = file_tex(TEX[name]["hair"].format(R=ROOT), "DS_HAIR_%s" % name)
                if tex:
                    cmds.connectAttr(tex + ".outColor", mat + ".color", f=True)
                    OUT["mode"][name + "_hair"] = "texture"
                else:
                    cmds.setAttr(mat + ".color", *HAIR)
            elif i["y"] > hy + 8.0:
                cmds.setAttr(mat + ".color", *HAIR)
            elif i["y"] > hy - 12.0:
                cmds.setAttr(mat + ".color", *SKIN)

    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds42_facetex.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:700])
