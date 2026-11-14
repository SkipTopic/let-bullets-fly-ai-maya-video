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

    # 躯干与头归零，先看基准
    for b in ("Spine", "Spine1", "Neck", "Head"):
        try:
            cmds.setAttr(j + b + ".rotateX", 0)
        except Exception:
            pass
    cmds.refresh(force=True)

    def hp():
        return [round(v, 2) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)]

    def fp():
        return [round(v, 2) for v in cmds.xform(j + "LeftFoot", q=True, ws=True, t=True)]

    def hd():
        return [round(v, 2) for v in cmds.xform(j + "Head", q=True, ws=True, t=True)]

    OUT["base"] = {"hand": hp(), "foot": fp(), "head": hd()}

    # 手臂扫描（左臂：Arm X 负=下垂；ForeArm 决定前臂）
    arm_rows = []
    for ax in (-75, -60, -45, -30):
        for fx in (0, 30, 60, 90, 120):
            cmds.setAttr(j + "LeftArm.rotateX", ax)
            cmds.setAttr(j + "LeftArm.rotateZ", 0)
            cmds.setAttr(j + "LeftForeArm.rotateX", fx)
            cmds.refresh(force=True)
            arm_rows.append({"armX": ax, "foreX": fx, "hand": hp()})
    OUT["arm_sweep"] = arm_rows

    # 复位手臂
    cmds.setAttr(j + "LeftArm.rotateX", 0)
    cmds.setAttr(j + "LeftForeArm.rotateX", 0)

    # 腿部扫描
    leg_rows = []
    for ux in (80, 88, 96):
        for lx in (-96, -88, -80, -72):
            cmds.setAttr(j + "LeftUpLeg.rotateX", ux)
            cmds.setAttr(j + "LeftLeg.rotateX", lx)
            cmds.refresh(force=True)
            leg_rows.append({"upLegX": ux, "legX": lx, "foot": fp()})
    OUT["leg_sweep"] = leg_rows

    # 颈部/头部 pitch 扫描（看头是否水平）
    neck_rows = []
    for nx in (-15, -8, 0, 8):
        cmds.setAttr(j + "Neck.rotateX", nx)
        cmds.refresh(force=True)
        neck_rows.append({"neckX": nx, "head": hd()})
    OUT["neck_sweep"] = neck_rows

    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s1_sweep.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
