import maya.cmds as cmds
import json, os, sys, importlib, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}
try:
    chars = L.build_all()
    ch = chars["Ma"]
    j = ch["j"]

    def pos(n):
        return [round(v, 2) for v in cmds.xform(j + n, q=True, ws=True, t=True)]

    OUT["target"] = {"note": "身体在 z=-118，桌面 y=75.75，想要手在 y≈78 z≈-90 x≈±16"}

    rows = []
    for ax in (-75, -40, 20, 75):
        for fx in (-90, 90):
            cmds.setAttr(j + "RightArm.rotateX", ax)
            cmds.setAttr(j + "RightForeArm.rotateX", fx)
            cmds.refresh(force=True)
            rows.append({"armX": ax, "foreX": fx, "hand": pos("RightHand")})
    OUT["right_arm"] = rows

    # 左臂微调 y：ArmX 从 -75 到 -95
    lrows = []
    for ax in (-75, -85, -95):
        for fx in (75, 90, 105):
            cmds.setAttr(j + "LeftArm.rotateX", ax)
            cmds.setAttr(j + "LeftForeArm.rotateX", fx)
            cmds.refresh(force=True)
            lrows.append({"armX": ax, "foreX": fx, "hand": pos("LeftHand")})
    OUT["left_arm"] = lrows

    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s3_arms.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
