"""DS 预览灯光 v2：稳定三点光，放在 DS_LIGHTS 组内，重复执行安全。"""
import json
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "lights": [], "steps": []}

SPECS = [
    ("DS_KEY", "spot", (-140.0, 300.0, 260.0), (0.0, 90.0, 0.0), 2.2, (1.0, 0.94, 0.86), 55.0),
    ("DS_FILL", "spot", (220.0, 200.0, 200.0), (0.0, 85.0, 10.0), 0.9, (0.82, 0.88, 1.0), 80.0),
    ("DS_RIM", "spot", (40.0, 260.0, -320.0), (0.0, 110.0, 0.0), 1.4, (1.0, 0.92, 0.8), 70.0),
    ("DS_AMB", "ambient", None, None, 0.55, (0.62, 0.66, 0.72), None),
]

try:
    if cmds.objExists("DS_LIGHTS"):
        cmds.delete("DS_LIGHTS")
    cmds.group(em=True, name="DS_LIGHTS")

    for name, kind, pos, aim, intensity, color, cone in SPECS:
        if kind == "spot":
            node = cmds.spotLight(name=name + "_L", intensity=intensity, rgb=color,
                                  coneAngle=cone, penumbra=0.35, decayRate=0)[0]
            tr = cmds.listRelatives(node, parent=True)[0]
            cmds.xform(tr, ws=True, t=pos)
            tgt = cmds.spaceLocator(name=name + "_AIM")[0]
            cmds.xform(tgt, ws=True, t=aim)
            cmds.aimConstraint(tgt, tr, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                               worldUpType="vector", worldUpVector=(0, 1, 0))
        else:
            node = cmds.ambientLight(name=name + "_L", intensity=intensity, rgb=color)[0]
            tr = cmds.listRelatives(node, parent=True)[0]
        OUT["lights"].append({"name": name, "shape": node, "transform": tr})
        OUT["steps"].append("created " + name)

    for l in OUT["lights"]:
        cmds.parent(l["transform"], "DS_LIGHTS", relative=False)
        if cmds.objExists(l["name"] + "_AIM"):
            cmds.parent(l["name"] + "_AIM", "DS_LIGHTS", relative=False)

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayLights="all", twoSidedLighting=True)
    OUT["panel"] = panel
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds16_lights.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in OUT.items() if k != "errors"}, ensure_ascii=False))
print(OUT["errors"][:1])
