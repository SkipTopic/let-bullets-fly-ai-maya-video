import maya.cmds as cmds
import json, os, sys, importlib, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}

TABLE_Y = 80.0          # 桌面高度（抬高以便手能落在桌面）
TABLE_R = 92.0


def ik_pose(j, sj, ee, target, pole):
    h = cmds.ikHandle(sj=j + sj, ee=j + ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PV_" + ee)[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    vals = {}
    for b in (sj, ee):
        vals[b] = list(cmds.getAttr(j + b + ".rotate")[0])
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(j + b + ".rotate", *v)
    return vals


try:
    chars = L.build_all()

    # 桌面高度重设
    cmds.setAttr("SET_table_top.translateY", TABLE_Y - 2.25)

    result = {}
    for key, ch in chars.items():
        j = ch["j"]
        gx, gy, gz = cmds.getAttr(ch["grp"] + ".translate")[0]
        ang = math.radians(ch["theta"])
        fwd = (-math.cos(ang), -math.sin(ang))
        right = (-fwd[1], fwd[0])

        head = cmds.xform(j + "Head", q=True, ws=True, t=True)
        info = {"head": [round(v, 1) for v in head]}

        for side, s in (("Left", 1), ("Right", -1)):
            sj = side + "Arm"
            ee = side + "ForeArm"
            tx = gx + fwd[0] * 33 + right[0] * 17 * s
            tz = gz + fwd[1] * 33 + right[1] * 17 * s
            target = (tx, TABLE_Y + 6.0, tz)
            pole = (gx + fwd[0] * 5 + right[0] * 70 * s,
                    TABLE_Y + 10, gz + fwd[1] * 5 + right[1] * 70 * s)
            vals = ik_pose(j, sj, ee, target, pole)
            hand = cmds.xform(j + side + "Hand", q=True, ws=True, t=True)
            info[side] = {"target": [round(v, 1) for v in target],
                          "hand": [round(v, 1) for v in hand],
                          "rot": {k: [round(x, 1) for x in v] for k, v in vals.items()}}

        # 腿：脚落到地面、略往前
        for side, s in (("Left", 1), ("Right", -1)):
            sj, ee = side + "UpLeg", side + "Leg"
            tx = gx + fwd[0] * 18 + right[0] * 17 * s
            tz = gz + fwd[1] * 18 + right[1] * 17 * s
            target = (tx, 6.0, tz)
            pole = (gx + fwd[0] * 90, 90, gz + fwd[1] * 90)
            vals = ik_pose(j, sj, ee, target, pole)
            info[side + "_leg"] = {k: [round(x, 1) for x in v] for k, v in vals.items()}

        result[key] = info

    OUT["pose"] = result

    for key, ch in chars.items():
        ang = math.radians(ch["theta"] + 180)
        eye = (math.cos(ang) * 200, 125, math.sin(ang) * 200)
        aim = cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
        cam = L.make_cam("CAM_s_" + key, eye, aim, 85)
        cmds.lookThru(cam)
        L.render_to(os.path.join(ROOT, "_接手检查", "s6_" + key + ".png"))

    cmds.file(os.path.join(ROOT, "scenes", "v5_ik.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s6_ik.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
