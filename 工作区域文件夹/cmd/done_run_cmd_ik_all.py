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
TABLE = 73.5 + 2.25


def chain_to(sj, ee):
    out = [ee]
    cur = ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
        if cur:
            out.append(cur)
    return out


def put_hand(j, side, target, pole):
    sj, ee = j + side + "Arm", j + side + "Hand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PV_%s_%s" % (j, side))[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    bones = chain_to(sj, ee)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in bones}
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    cmds.refresh(force=True)
    got = cmds.xform(ee, q=True, ws=True, t=True)
    return vals, round(sum((got[i] - target[i]) ** 2 for i in range(3)) ** 0.5, 2)


try:
    chars = L.build_all()
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "Spine.rotateX", 8)
        cmds.setAttr(j + "Spine1.rotateX", 4)
        cmds.setAttr(j + "Neck.rotateX", -14)
        cmds.setAttr(j + "Head.rotateX", -12)
    cmds.refresh(force=True)

    info = {}
    for key, ch in chars.items():
        j = ch["j"]
        gx, gy, gz = cmds.getAttr(ch["grp"] + ".translate")[0]
        ang = math.radians(ch["theta"])
        fwd = (-math.cos(ang), -math.sin(ang))
        right = (-fwd[1], fwd[0])
        rec = {}
        for side, s in (("Left", 1), ("Right", -1)):
            tgt = (gx + fwd[0] * 27 + right[0] * 16 * s, TABLE + 3.0,
                   gz + fwd[1] * 27 + right[1] * 16 * s)
            pole = (gx + fwd[0] * 4 + right[0] * 82 * s, TABLE + 26,
                    gz + fwd[1] * 4 + right[1] * 82 * s)
            vals, err = put_hand(j, side, tgt, pole)
            rec[side] = {"err": err, "hand": [round(v, 1) for v in
                                              cmds.xform(j + side + "Hand", q=True, ws=True, t=True)]}
        info[key] = rec
    OUT["hands"] = info

    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    grp = cmds.group(em=True, name="GRP_CAMERAS")
    cmap = {}
    for s in shots:
        h = head_pos[s["subject"]]
        dist = 132.0 if "近" in s["size"] else 198.0
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        k = dist / max(s["dist"], 1.0)
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, h[1] + 8.0, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 12.0, h[2])
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp)
        cmds.parent(loc, grp)
        if s["eye0"] != s["eye1"]:
            cmds.setKeyframe(cam, attribute="translateX", time=s["start"], value=s["eye0"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["start"], value=s["eye0"][2] * k)
            cmds.setKeyframe(cam, attribute="translateX", time=s["end"], value=s["eye1"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["end"], value=s["eye1"][2] * k)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    # 表演：转头 + 抬手（幅度小，手不离桌太远）
    KEY = {"Ma": "Ma_", "Huang": "Huang_", "Shiye": "Shiye_"}
    WORD = ("指", "举", "端", "拿", "比", "挥", "伸", "扶", "放", "拍", "推", "倒")
    for idx, s in enumerate(shots):
        j = KEY[s["subject"]]
        st, en = s["start"], s["end"]
        mid = st + max(2, s["dur"] // 2)
        hy = cmds.getAttr(j + "Head.rotateY")
        turn = -17 if s.get("listener") in ("Ma", "Shiye") else 13
        cmds.setKeyframe(j + "Head.rotateY", time=st, value=hy)
        cmds.setKeyframe(j + "Head.rotateY", time=mid, value=hy + turn)
        cmds.setKeyframe(j + "Head.rotateY", time=en, value=hy + turn * 0.45)
        cmds.setKeyframe(j + "Neck.rotateX", time=st, value=-14)
        cmds.setKeyframe(j + "Neck.rotateX", time=mid, value=-11)
        cmds.setKeyframe(j + "Neck.rotateX", time=en, value=-14)
        cmds.setKeyframe(j + "Spine.rotateX", time=st, value=8)
        cmds.setKeyframe(j + "Spine.rotateX", time=mid, value=10.5)
        cmds.setKeyframe(j + "Spine.rotateX", time=en, value=8)
        if any(w in s["action"] for w in WORD):
            side = "Left" if idx % 2 == 0 else "Right"
            ax = cmds.getAttr(j + side + "Arm.rotateX")
            cmds.setKeyframe(j + side + "Arm.rotateX", time=st, value=ax)
            cmds.setKeyframe(j + side + "Arm.rotateX", time=mid,
                             value=ax + (-7 if side == "Left" else 7))
            cmds.setKeyframe(j + side + "Arm.rotateX", time=en, value=ax)

    cmds.file(os.path.join(ROOT, "scenes", "v11_handfix.mb"), f=True, type="mayaBinary", ea=True)

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(30)
    cmds.lookThru(p, cmap["S001"])
    cmds.playblast(frame=30, format="image", filename=os.path.join(REV, "IK_warm"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=90,
                   compression="png")
    for sid, f, name in (("S001", 30, "Ma"), ("S033", 1718, "Huang"), ("S045", 2327, "Shiye")):
        cmds.currentTime(f)
        cmds.lookThru(p, cmap[sid])
        for old in os.listdir(REV):
            if old.startswith("IK_%s." % name):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "IK_" + name),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f10.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
