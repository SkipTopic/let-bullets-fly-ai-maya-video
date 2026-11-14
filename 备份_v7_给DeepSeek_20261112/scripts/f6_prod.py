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


def hand(j, side):
    return cmds.xform(j + side + "Hand", q=True, ws=True, t=True)


def solve(j, side, target, ax_range, fx_range):
    best = None
    for ax in ax_range:
        for az in (-30, 0, 30):
            cmds.setAttr(j + side + "Arm.rotate", ax, 0, az)
            for fx in fx_range:
                cmds.setAttr(j + side + "ForeArm.rotateX", fx)
                p = hand(j, side)
                e = sum((p[i] - target[i]) ** 2 for i in range(3)) ** 0.5
                if best is None or e < best[0]:
                    best = (round(e, 2), ax, az, fx, [round(v, 1) for v in p])
    return best


try:
    chars = L.build_all()
    j = chars["Ma"]["j"]
    gx, gy, gz = cmds.getAttr(chars["Ma"]["grp"] + ".translate")[0]
    ang = math.radians(chars["Ma"]["theta"])
    fwd = (-math.cos(ang), -math.sin(ang))
    right = (-fwd[1], fwd[0])

    # 目标：手放在桌面上，身体正前方 30cm，左右各 16cm
    tL = (gx + fwd[0] * 30 + right[0] * 16, TABLE_Y + 4.0, gz + fwd[1] * 30 + right[1] * 16)
    tR = (gx + fwd[0] * 30 - right[0] * 16, TABLE_Y + 4.0, gz + fwd[1] * 30 - right[1] * 16)
    OUT["targets"] = {"L": [round(v, 1) for v in tL], "R": [round(v, 1) for v in tR]}
    OUT["shoulder"] = [round(v, 1) for v in cmds.xform(j + "LeftArm", q=True, ws=True, t=True)]

    OUT["left"] = solve(j, "Left", tL, (-100, -85, -70, -55, -40), (40, 70, 100, 130))
    OUT["right"] = solve(j, "Right", tR, (0, 20, 40, 60, 80), (-130, -100, -70, -40))

    # 应用
    e1, ax1, az1, fx1, _ = OUT["left"]
    e2, ax2, az2, fx2, _ = OUT["right"]
    for key, ch in chars.items():
        jj = ch["j"]
        cmds.setAttr(jj + "LeftArm.rotate", ax1, 0, az1)
        cmds.setAttr(jj + "LeftForeArm.rotateX", fx1)
        cmds.setAttr(jj + "RightArm.rotate", ax2, 0, az2)
        cmds.setAttr(jj + "RightForeArm.rotateX", fx2)
        cmds.setAttr(jj + "Spine.rotateX", 6)
        cmds.setAttr(jj + "Spine1.rotateX", 3)
        cmds.setAttr(jj + "Neck.rotateX", -12)
        cmds.setAttr(jj + "Head.rotateX", -10)
    OUT["applied"] = {"L": [ax1, 0, az1, fx1], "R": [ax2, 0, az2, fx2]}
    cmds.refresh(force=True)

    # 相机
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    grp_cam = cmds.group(em=True, name="GRP_CAMERAS")
    cmap = {}
    for s in shots:
        h = head_pos[s["subject"]]
        dist = 132.0 if "近" in s["size"] else 198.0
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        k = dist / max(s["dist"], 1.0)
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, h[1] + 12.0, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 4.0, h[2])
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp_cam)
        cmds.parent(loc, grp_cam)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), f=True, type="mayaBinary", ea=True)

    # 试渲一张
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(30)
    cmds.lookThru(p, cmap["S001"])
    cmds.playblast(frame=30, format="image", filename=os.path.join(REV, "PR_Ma"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=95,
                   compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f6.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
