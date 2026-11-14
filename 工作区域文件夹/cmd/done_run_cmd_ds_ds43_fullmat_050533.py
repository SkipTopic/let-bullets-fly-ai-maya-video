"""一次性重建 MMD 材质：身体按部位纯色，脸/头发用贴图（可切换）。"""
import json, math, os, traceback
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
CAP = (0.30, 0.28, 0.28)
COAT = (0.66, 0.62, 0.55)
TROUSER = (0.22, 0.20, 0.22)
DARK = (0.16, 0.14, 0.13)
OUT = {"errors": [], "picked": {}, "applied": {}}

FACE_TEX = os.environ.get("DS_FACE_TEX", "1") == "1"


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
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]
    for name, (hx, hy, hz, yaw) in HEAD.items():
        fx, fz = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
        seen = set()
        items = []
        for it in log.get(name, []):
            c = it.get("center")
            if not c or it["mat"] in seen:
                continue
            seen.add(it["mat"])
            d = math.dist(c, (hx, hy, hz))
            fw = (c[0] - hx) * fx + (c[2] - hz) * fz
            items.append({"mat": it["mat"], "faces": it["faces"], "c": c, "fwd": fw, "dist": d})
        head = [i for i in items if i["dist"] < 16.0]
        front = [i for i in head if i["fwd"] > 3.5]
        face = max(front, key=lambda i: i["faces"]) if front else None
        hair = max([i for i in head if i is not face and i["fwd"] <= 5.0],
                   key=lambda i: i["faces"], default=None)
        OUT["picked"][name] = {"face": (face["mat"] if face else None),
                               "hair": (hair["mat"] if hair else None)}

        for i in items:
            mat = i["mat"]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            y = i["c"][1]
            if face and mat == face["mat"] and FACE_TEX:
                tex = file_tex(TEX[name]["face"].format(R=ROOT), "DS_FACE_%s" % name)
                if tex:
                    cmds.connectAttr(tex + ".outColor", mat + ".color", f=True)
                    OUT["applied"].setdefault(name, []).append("face_tex")
                    continue
            if face and mat == face["mat"]:
                cmds.setAttr(mat + ".color", *SKIN)
            elif hair and mat == hair["mat"]:
                cmds.setAttr(mat + ".color", *HAIR)
            elif i["dist"] < 16.0:
                col = CAP if (name == "Shiye" and y > hy + 8.0) else HAIR
                cmds.setAttr(mat + ".color", *col)
            elif y < 62.0:
                cmds.setAttr(mat + ".color", *TROUSER)
            elif y < 72.0:
                cmds.setAttr(mat + ".color", *DARK)
            else:
                cmds.setAttr(mat + ".color", *COAT)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds43_fullmat.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:500])
