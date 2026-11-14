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
    OUT["table_edge_z"] = -88.0

    def hand(n):
        return [round(v, 2) for v in cmds.xform(j + n, q=True, ws=True, t=True)]

    rows = []
    for lean in (0, -8, -14, -20):
        cmds.setAttr(j + "Spine.rotateX", lean)
        cmds.setAttr(j + "Spine1.rotateX", lean * 0.4)
        cmds.refresh(force=True)
        rows.append({"lean": lean, "L": hand("LeftHand"), "R": hand("RightHand"),
                     "head": hand("Head")})
    OUT["lean"] = rows

    # 采用 -14，配合手臂参数
    cmds.setAttr(j + "Spine.rotateX", -14)
    cmds.setAttr(j + "Spine1.rotateX", -6)
    combos = []
    for ax, fx in ((-75, 90), (-85, 100), (-70, 110), (-60, 100)):
        cmds.setAttr(j + "LeftArm.rotateX", ax)
        cmds.setAttr(j + "LeftForeArm.rotateX", fx)
        cmds.refresh(force=True)
        combos.append({"armX": ax, "foreX": fx, "L": hand("LeftHand")})
    OUT["left_combos"] = combos

    combos_r = []
    for ax, fx in ((20, 90), (10, 80), (30, 100), (40, 90)):
        cmds.setAttr(j + "RightArm.rotateX", ax)
        cmds.setAttr(j + "RightForeArm.rotateX", fx)
        cmds.refresh(force=True)
        combos_r.append({"armX": ax, "foreX": fx, "R": hand("RightHand")})
    OUT["right_combos"] = combos_r
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s4_lean.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
