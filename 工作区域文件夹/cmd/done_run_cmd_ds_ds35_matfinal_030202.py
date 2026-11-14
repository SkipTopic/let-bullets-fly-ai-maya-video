"""最终材质：MMD 两人按高度分区纯色（避免 UV 错位），Ma 保留贴图；同时压低相机光。"""
import json, os, traceback
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
HEAD_Y = {"Huang": 123.2, "Shiye": 123.5}
SKIN = (0.80, 0.62, 0.50)
HAIR = (0.20, 0.16, 0.14)
CAP = (0.30, 0.28, 0.28)
COAT = (0.66, 0.62, 0.55)
TROUSER = (0.22, 0.20, 0.22)
OUT = {"errors": [], "by": {}}

try:
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]
    for name in ("Huang", "Shiye"):
        items = [i for i in log.get(name, []) if i.get("center")]
        for it in items:
            mat = it["mat"]
            cy = it["center"][1]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            if abs(cy - HEAD_Y[name]) < 16.0:
                if cy > HEAD_Y[name] + 3.0:
                    col = CAP if (name == "Shiye" and cy > HEAD_Y[name] + 9.0) else HAIR
                else:
                    col = SKIN
            elif cy < 62.0:
                col = TROUSER
            else:
                col = COAT
            cmds.setAttr(mat + ".color", col[0], col[1], col[2])
            it["flat"] = col
        OUT["by"][name] = len(items)

    for lt in cmds.ls("DS_*_LGT", type="pointLight") or []:
        cmds.setAttr(lt + ".intensity", 0.42)
    if cmds.objExists("DS_AMB_LShape"):
        cmds.setAttr("DS_AMB_LShape.intensity", 0.34)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds35_matfinal.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:400])
