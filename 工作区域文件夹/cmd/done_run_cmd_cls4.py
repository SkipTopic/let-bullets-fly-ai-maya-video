import maya.cmds as cmds
import json, os, sys, shutil, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}
REV = os.path.join(ROOT, "_审片")
os.makedirs(REV, exist_ok=True)


def stills(cmap, picks, tag):
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    made = []
    for sid, f, name in picks:
        cmds.currentTime(f)
        cmds.lookThru(p, cmap[sid])
        base = os.path.join(REV, "%s_%s" % (tag, name))
        for old in os.listdir(REV):
            if old.startswith("%s_%s" % (tag, name)):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=f, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False,
                       offScreen=True, percent=100, widthHeight=(854, 480),
                       quality=95, compression="png")
        fs = sorted([x for x in os.listdir(REV) if x.startswith("%s_%s." % (tag, name))])
        if fs:
            made.append(os.path.join(REV, fs[0]))
    return made


try:
    chars = L.build_all()
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "LeftArm.rotate", -65, 0, -25)
        cmds.setAttr(j + "LeftForeArm.rotateX", 70)
        cmds.setAttr(j + "RightArm.rotate", 40, 0, -40)
        cmds.setAttr(j + "RightForeArm.rotateX", -110)
        cmds.setAttr(j + "Spine.rotateX", 6)
        cmds.setAttr(j + "Spine1.rotateX", 3)
        cmds.setAttr(j + "Neck.rotateX", -12)
        cmds.setAttr(j + "Head.rotateX", -10)

    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    grp_cam = cmds.group(em=True, name="GRP_CAMERAS")
    cmap = {}
    for s in shots:
        h = head_pos[s["subject"]]
        dist = 132.0 if "近" in s["size"] else 198.0
        ey = h[1] + 12.0
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        k = dist / max(s["dist"], 1.0)
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, ey, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 4.0, h[2])
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp_cam)
        cmds.parent(loc, grp_cam)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    cmds.file(os.path.join(ROOT, "scenes", "v9_classic.mb"), f=True, type="mayaBinary", ea=True)

    OUT["made"] = stills(cmap, [("S001", 30, "Ma"), ("S033", 1718, "Huang"), ("S045", 2327, "Shiye")], "CL")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f5_classic.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
