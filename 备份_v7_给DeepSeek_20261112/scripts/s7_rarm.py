import maya.cmds as cmds
import json, os, sys, importlib, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}


def d3(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


try:
    chars = L.build_all()
    ch = chars["Ma"]
    j = ch["j"]
    gx, gz = 0.0, -118.0
    tgtL = (17.0, 80.0, -88.0)
    tgtR = (-17.0, 80.0, -88.0)

    resL = None
    for ax in (-95, -85, -75, -65):
        for az in (-25, 0, 25):
            for fx in (70, 90, 110):
                cmds.setAttr(j + "LeftArm.rotate", ax, 0, az)
                cmds.setAttr(j + "LeftForeArm.rotateX", fx)
                cmds.refresh(force=True)
                p = cmds.xform(j + "LeftHand", q=True, ws=True, t=True)
                e = d3(p, tgtL)
                if resL is None or e < resL[0]:
                    resL = (e, ax, az, fx, [round(v, 1) for v in p])
    OUT["left_best"] = resL

    resR = None
    for ax in (0, 20, 40, 60):
        for az in (-40, 0, 40):
            for fx in (-110, -90, -45, 45, 90):
                cmds.setAttr(j + "RightArm.rotate", ax, 0, az)
                cmds.setAttr(j + "RightForeArm.rotateX", fx)
                cmds.refresh(force=True)
                p = cmds.xform(j + "RightHand", q=True, ws=True, t=True)
                e = d3(p, tgtR)
                if resR is None or e < resR[0]:
                    resR = (e, ax, az, fx, [round(v, 1) for v in p])
    OUT["right_best"] = resR

    # 应用最优并渲染
    eL, axL, azL, fxL, _ = resL
    eR, axR, azR, fxR, _ = resR
    cmds.setAttr(j + "LeftArm.rotate", axL, 0, azL)
    cmds.setAttr(j + "LeftForeArm.rotateX", fxL)
    cmds.setAttr(j + "RightArm.rotate", axR, 0, azR)
    cmds.setAttr(j + "RightForeArm.rotateX", fxR)
    cmds.refresh(force=True)

    OUT["left_hand"] = [round(v, 1) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)]
    OUT["right_hand"] = [round(v, 1) for v in cmds.xform(j + "RightHand", q=True, ws=True, t=True)]

    ang = math.radians(ch["theta"] + 180)
    cam = L.make_cam("CAM_t", (math.cos(ang) * 200, 125, math.sin(ang) * 200),
                     cmds.xform(j + "Head", q=True, ws=True, t=True), 85)
    cmds.lookThru(cam)
    OUT["png"] = L.render_to(os.path.join(ROOT, "_接手检查", "s7_test.png"))
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s7.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
