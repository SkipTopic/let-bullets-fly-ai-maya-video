"""给每块材质上唯一纯色并渲染，用于肉眼定位"哪块是脸/头发/衣服"。"""
import json
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PALETTE = [
    (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 0.0),
    (1.0, 0.0, 1.0), (0.0, 1.0, 1.0), (1.0, 0.5, 0.0), (0.5, 0.0, 1.0),
    (0.0, 0.45, 0.0), (1.0, 0.6, 0.7), (0.5, 0.25, 0.0), (0.5, 0.5, 0.5),
    (1.0, 1.0, 1.0), (0.05, 0.05, 0.05), (0.4, 0.6, 1.0), (0.6, 0.6, 0.0),
    (0.0, 0.5, 0.5), (0.9, 0.4, 0.4), (0.3, 0.1, 0.1), (0.7, 0.9, 0.3),
]
CHARS = {"Huang": "Huang_AragakiFBXASC032Shinjiro_meshShape",
         "Shiye": "Shiye_JunpeiFBXASC032Iori_meshShape"}
OUT = {"errors": [], "map": {}}

try:
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]
    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    os.makedirs(os.path.join(ROOT, "ds_stills", "ident"), exist_ok=True)

    for name, shape in CHARS.items():
        items = [i for i in log.get(name, []) if i.get("center")]
        items.sort(key=lambda x: -x["faces"])
        OUT["map"][name] = []
        for idx, it in enumerate(items):
            col = PALETTE[idx % len(PALETTE)]
            mat = it["mat"]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            cmds.setAttr(mat + ".color", col[0], col[1], col[2])
            cmds.setAttr(mat + ".incandescence", 0, 0, 0)
            OUT["map"][name].append({"idx": idx, "color": col, "mat": mat[-28:],
                                     "faces": it["faces"], "y": it["center"][1]})

    cam = {"Huang": "DS_S002_CAM*", "Shiye": "DS_S010_CAM*"}
    for name, pat in cam.items():
        cams = cmds.ls(pat)
        if not cams:
            continue
        cmds.lookThru(panel, cams[0])
        cmds.currentTime(400 if name == "Shiye" else 80)
        cmds.refresh(force=True)
        cmds.playblast(frame=(610 if name == "Shiye" else 80), format="image",
                       filename=os.path.join(ROOT, "ds_stills", "ident", name),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(960, 540), quality=90, compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds41_ident.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for n, rows in OUT["map"].items():
    print("==", n)
    for r in rows:
        print("  %2d %-24s faces=%-5d y=%.1f color=%s" % (r["idx"], r["mat"], r["faces"], r["y"], r["color"]))
