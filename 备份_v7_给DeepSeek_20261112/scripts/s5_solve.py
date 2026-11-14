import maya.cmds as cmds
import json, os, sys, importlib, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}


def hand(j, side):
    return cmds.xform(j + side + "Hand", q=True, ws=True, t=True)


def dist(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def solve(j, side, target):
    """粗搜 + 细化，返回 (armXYZ, foreX, err)"""
    best = None
    for ax in (-90, -45, 0, 45, 90):
        for ay in (-30, 0, 30):
            for az in (-30, 0, 30):
                cmds.setAttr(j + side + "Arm.rotate", ax, ay, az)
                for fx in (-90, -45, 0, 45, 90):
                    cmds.setAttr(j + side + "ForeArm.rotateX", fx)
                    e = dist(hand(j, side), target)
                    if best is None or e < best[0]:
                        best = (e, ax, ay, az, fx)
    # 细化
    e0, ax, ay, az, fx = best
    for dax in (-20, -10, 0, 10, 20):
        for day in (-15, 0, 15):
            for daz in (-15, 0, 15):
                for dfx in (-25, -10, 0, 10, 25):
                    cmds.setAttr(j + side + "Arm.rotate", ax + dax, ay + day, az + daz)
                    cmds.setAttr(j + side + "ForeArm.rotateX", fx + dfx)
                    e = dist(hand(j, side), target)
                    if e < e0:
                        e0 = e
                        best = (e, ax + dax, ay + day, az + daz, fx + dfx)
    return best


try:
    chars = L.build_all()
    result = {}
    for key, ch in chars.items():
        j = ch["j"]
        gx, gy, gz = cmds.getAttr(ch["grp"] + ".translate")[0]
        ang = math.radians(ch["theta"])
        fwd = (-math.cos(ang), -math.sin(ang))          # 指向圆心
        right = (-fwd[1], fwd[0])
        info = {"pos": [round(gx, 1), round(gz, 1)]}
        for side, s in (("Left", 1), ("Right", -1)):
            tx = gx + fwd[0] * 30 + right[0] * 16 * s
            tz = gz + fwd[1] * 30 + right[1] * 16 * s
            target = (tx, 78.0, tz)
            e, ax, ay, az, fx = solve(j, side, target)
            cmds.setAttr(j + side + "Arm.rotate", ax, ay, az)
            cmds.setAttr(j + side + "ForeArm.rotateX", fx)
            cmds.refresh(force=True)
            info[side] = {"target": [round(v, 1) for v in target],
                          "err": round(e, 2), "arm": [ax, ay, az], "foreX": fx,
                          "got": [round(v, 1) for v in hand(j, side)]}
        result[key] = info
    OUT["solve"] = result

    # 用解出的姿势渲一张
    for key, ch in chars.items():
        ang = math.radians(ch["theta"] + 180)
        eye = (math.cos(ang) * 200, 118, math.sin(ang) * 200)
        aim = cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
        cam = L.make_cam("CAM_s_" + key, eye, aim, 85)
        cmds.lookThru(cam)
        L.render_to(os.path.join(ROOT, "_接手检查", "s5_" + key + ".png"))

    cmds.file(os.path.join(ROOT, "scenes", "v4_pose.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s5_solve.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
