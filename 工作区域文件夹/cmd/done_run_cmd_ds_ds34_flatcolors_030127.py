"""MMD 三人改成按部位纯色材质（贴图 UV 不可靠时的稳妥做法），Ma 保留贴图。"""
import json, os, traceback
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
HEAD_Y = {"Huang": 123.2, "Shiye": 123.5}
SKIN = (0.87, 0.72, 0.61)
HAIR = (0.24, 0.20, 0.18)
CAP = (0.32, 0.30, 0.30)
COAT = (0.88, 0.85, 0.74)
VEST = (0.55, 0.12, 0.16)
TROUSER = (0.28, 0.26, 0.28)
DARK = (0.18, 0.16, 0.15)
OUT = {"errors": [], "by": {}}

try:
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]
    for name in ("Huang", "Shiye"):
        items = [i for i in log.get(name, []) if i.get("center")]
        head = sorted([i for i in items if abs(i["center"][1] - HEAD_Y[name]) < 16.0],
                      key=lambda x: -x["faces"])
        main_face = head[0]["mat"] if head else None
        for it in items:
            mat = it["mat"]
            cy = it["center"][1]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            if mat == main_face:
                col = SKIN
            elif abs(cy - HEAD_Y[name]) < 16.0:
                col = CAP if name == "Shiye" and cy > HEAD_Y[name] + 7 else HAIR
            elif cy < 62.0:
                col = TROUSER
            elif cy < 72.0:
                col = DARK
            else:
                col = COAT
            cmds.setAttr(mat + ".color", col[0], col[1], col[2])
            it["flat"] = col
        OUT["by"][name] = len(items)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds34_flat.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:400])
