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

# 实测过的稳妥手臂角度：手落在 y≈84.7，桌面抬到 80 → 手掌正好压桌面
POSE_L_ARM = (-88, 0, -8)
POSE_L_FORE = 10
POSE_R_ARM = (88, 0, 8)
POSE_R_FORE = -10
TABLE_Y = 75.75


def build():
    chars = L.build_all()
    cmds.setAttr("SET_table_top.translateY", TABLE_Y - 2.25)
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "LeftArm.rotate", *POSE_L_ARM)
        cmds.setAttr(j + "LeftForeArm.rotateX", POSE_L_FORE)
        cmds.setAttr(j + "RightArm.rotate", *POSE_R_ARM)
        cmds.setAttr(j + "RightForeArm.rotateX", POSE_R_FORE)
        cmds.setAttr(j + "Spine.rotateX", 6)
        cmds.setAttr(j + "Spine1.rotateX", 3)
        cmds.setAttr(j + "Neck.rotateX", -13)
        cmds.setAttr(j + "Head.rotateX", -11)
    cmds.refresh(force=True)
    return chars


def cameras(chars):
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
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, h[1] + 6.0, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 4.0, h[2])
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
    return shots, cmap


def animate(chars, shots):
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

        cmds.setKeyframe(j + "Neck.rotateX", time=st, value=-13)
        cmds.setKeyframe(j + "Neck.rotateX", time=mid, value=-10)
        cmds.setKeyframe(j + "Neck.rotateX", time=en, value=-13)

        cmds.setKeyframe(j + "Spine.rotateX", time=st, value=6)
        cmds.setKeyframe(j + "Spine.rotateX", time=mid, value=8.5)
        cmds.setKeyframe(j + "Spine.rotateX", time=en, value=6)

        if any(w in s["action"] for w in WORD):
            side = "Left" if idx % 2 == 0 else "Right"
            lift = -16 if side == "Left" else 16
            ax = cmds.getAttr(j + side + "Arm.rotateX")
            fx = cmds.getAttr(j + side + "ForeArm.rotateX")
            cmds.setKeyframe(j + side + "Arm.rotateX", time=st, value=ax)
            cmds.setKeyframe(j + side + "Arm.rotateX", time=mid, value=ax + lift)
            cmds.setKeyframe(j + side + "Arm.rotateX", time=en, value=ax)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=st, value=fx)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=mid, value=fx - lift * 0.8)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=en, value=fx)


def reload_scene():
    """把刚建好的场景重新打开，清掉扫描残留的状态"""
    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), o=True, force=True)
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaHardware2", type="string") \
        if cmds.objExists("defaultRenderGlobals") else None


try:
    chars = build()
    shots, cmap = cameras(chars)
    animate(chars, shots)
    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), f=True, type="mayaBinary", ea=True)

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    made = []
    for sid, f, name in (("S001", 30, "Ma"), ("S033", 1718, "Huang"), ("S045", 2327, "Shiye")):
        cmds.currentTime(f)
        cmds.lookThru(p, cmap[sid])
        for old in os.listdir(REV):
            if old.startswith("F_%s." % name):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "F_" + name),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
        made.append(name)
    OUT["made"] = made
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f7.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
