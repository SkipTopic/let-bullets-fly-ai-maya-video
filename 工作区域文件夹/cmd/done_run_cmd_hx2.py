import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
import lib_scene as _L
L = importlib.reload(_L)

OUT = {"errors": []}
REV = os.path.join(ROOT, "_审片")
os.makedirs(REV, exist_ok=True)
TABLE_Y = 73.5 + 2.25


def sweep(j, side, target, axs, fxs, azs=(0,)):
    best = None
    for ax in axs:
        for az in azs:
            cmds.setAttr(j + side + "Arm.rotate", ax, 0, az)
            for fx in fxs:
                cmds.setAttr(j + side + "ForeArm.rotateX", fx)
                cmds.refresh(force=True)
                p = cmds.xform(j + side + "Hand", q=True, ws=True, t=True)
                e = sum((p[i] - target[i]) ** 2 for i in range(3)) ** 0.5
                if best is None or e < best[0]:
                    best = (round(e, 2), ax, az, fx, [round(v, 1) for v in p])
    return best


try:
    chars = L.build_all()
    # 上身更前倾，让肩膀靠近桌面
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "Spine.rotateX", 8)
        cmds.setAttr(j + "Spine1.rotateX", 4)
        cmds.setAttr(j + "Neck.rotateX", -18)
        cmds.setAttr(j + "Head.rotateX", -12)
    cmds.refresh(force=True)

    j = chars["Ma"]["j"]
    gx, gy, gz = cmds.getAttr(chars["Ma"]["grp"] + ".translate")[0]
    ang = math.radians(chars["Ma"]["theta"])
    fwd = (-math.cos(ang), -math.sin(ang))
    right = (-fwd[1], fwd[0])
    OUT["geo"] = {
        "shoulder": [round(v, 1) for v in cmds.xform(j + "LeftArm", q=True, ws=True, t=True)],
        "table": TABLE_Y,
        "hand_before": [round(v, 1) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)],
    }

    tL = (gx + fwd[0] * 26 + right[0] * 17, TABLE_Y + 3.5, gz + fwd[1] * 26 + right[1] * 17)
    tR = (gx + fwd[0] * 26 - right[0] * 17, TABLE_Y + 3.5, gz + fwd[1] * 26 - right[1] * 17)

    OUT["left"] = sweep(j, "Left", tL, (-85, -75, -65), (60, 80, 100), (0, -20))
    OUT["right"] = sweep(j, "Right", tR, (85, 75, 65), (-100, -80, -60), (0, 20))

    e1, ax1, az1, fx1, _ = OUT["left"]
    e2, ax2, az2, fx2, _ = OUT["right"]
    for key, ch in chars.items():
        jj = ch["j"]
        cmds.setAttr(jj + "LeftArm.rotate", ax1, 0, az1)
        cmds.setAttr(jj + "LeftForeArm.rotateX", fx1)
        cmds.setAttr(jj + "RightArm.rotate", ax2, 0, az2)
        cmds.setAttr(jj + "RightForeArm.rotateX", fx2)
        for sd, sg in (("Left", 1), ("Right", -1)):
            try:
                cmds.setAttr(jj + sd + "Hand.rotateX", 38 * sg)
            except Exception:
                pass
    cmds.refresh(force=True)
    OUT["applied"] = {"L": [ax1, az1, fx1], "R": [ax2, az2, fx2]}
    OUT["hand_after"] = {
        "L": [round(v, 1) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)],
        "R": [round(v, 1) for v in cmds.xform(j + "RightHand", q=True, ws=True, t=True)],
    }

    # 相机
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    OUT["heads"] = {k: [round(v, 1) for v in p] for k, p in head_pos.items()}
    grp = cmds.group(em=True, name="GRP_CAMERAS")
    cmap = {}
    for s in shots:
        h = head_pos[s["subject"]]
        dist = 132.0 if "近" in s["size"] else 198.0
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        k = dist / max(s["dist"], 1.0)
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, h[1] + 6.0, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 6.0, h[2])
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp)
        cmds.parent(loc, grp)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    cmds.file(os.path.join(ROOT, "scenes", "v11_handfix.mb"), f=True, type="mayaBinary", ea=True)

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    # 预热
    cmds.currentTime(30)
    cmds.lookThru(p, cmap["S001"])
    cmds.playblast(frame=30, format="image", filename=os.path.join(REV, "HX_warm"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=90,
                   compression="png")
    for sid, f, name in (("S001", 30, "Ma"), ("S033", 1718, "Huang"), ("S045", 2327, "Shiye")):
        cmds.currentTime(f)
        cmds.lookThru(p, cmap[sid])
        for old in os.listdir(REV):
            if old.startswith("HX_%s." % name):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "HX_" + name),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f9.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
