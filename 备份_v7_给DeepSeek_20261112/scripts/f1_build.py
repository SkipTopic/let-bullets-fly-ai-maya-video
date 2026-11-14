import maya.cmds as cmds
import json, os, sys, importlib, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}

# 手放腿侧，近景看不见手 → 避免"钢琴手"
POSE = {
    "LeftArm": (-92, 0, -14), "LeftForeArm": 4,
    "RightArm": (92, 0, 14), "RightForeArm": -4,
}


def apply_pose(j):
    cmds.setAttr(j + "LeftArm.rotate", *POSE["LeftArm"])
    cmds.setAttr(j + "LeftForeArm.rotateX", POSE["LeftForeArm"])
    cmds.setAttr(j + "RightArm.rotate", *POSE["RightArm"])
    cmds.setAttr(j + "RightForeArm.rotateX", POSE["RightForeArm"])
    cmds.setAttr(j + "Spine.rotateX", 3)
    cmds.setAttr(j + "Spine1.rotateX", 1)
    cmds.setAttr(j + "Neck.rotateX", -15)
    cmds.setAttr(j + "Head.rotateX", -16)


def light_up():
    cmds.setAttr("LGT_key.intensity", 1.75)
    cmds.setAttr("LGT_rim.intensity", 1.5)
    cmds.setAttr("LGT_amb.intensity", 0.55)
    cmds.setAttr("LGT_fill.intensity", 0.45)
    for i in range(2):
        n = "SET_candle_light_%d" % i
        if cmds.objExists(n):
            cmds.setAttr(n + ".intensity", 2400)


try:
    chars = L.build_all()
    cmds.setAttr("SET_table_top.translateY", 78.0)
    for key, ch in chars.items():
        apply_pose(ch["j"])
    light_up()
    cmds.refresh(force=True)

    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    OUT["head_pos"] = {k: [round(v, 1) for v in p] for k, p in head_pos.items()}

    grp_cam = cmds.group(em=True, name="GRP_CAMERAS")
    cmap = {}
    for s in shots:
        h = head_pos[s["subject"]]
        aim_at = (h[0], h[1] - 4.0, h[2])
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        dist = 138.0 if "近" in s["size"] else 205.0
        ey = h[1] + 11.0
        k = dist / max(s["dist"], 1.0)
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, ey, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", *aim_at)
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp_cam)
        cmds.parent(loc, grp_cam)
        if s["eye0"] != s["eye1"]:
            cmds.setKeyframe(cam, attribute="translateX", time=s["start"], value=s["eye0"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["start"], value=s["eye0"][2] * k)
            cmds.setKeyframe(cam, attribute="translateX", time=s["end"], value=s["eye1"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["end"], value=s["eye1"][2] * k)

    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    # ---------- 动画：每镜头部转向 + 呼吸 + 眨眼 ----------
    KEY = {"Ma": "Ma_", "Huang": "Huang_", "Shiye": "Shiye_"}
    for s in shots:
        j = KEY[s["subject"]]
        st, en = s["start"], s["end"]
        mid = st + max(2, s["dur"] // 2)

        # 头部转向听者
        base_y = cmds.getAttr(j + "Head.rotateY")
        turn = -16 if s["listener"] and s["listener"] in ("Ma", "Shiye") else 12
        cmds.setKeyframe(j + "Head.rotateY", time=st, value=base_y)
        cmds.setKeyframe(j + "Head.rotateY", time=mid, value=base_y + turn)
        cmds.setKeyframe(j + "Head.rotateY", time=en, value=base_y + turn * 0.4)

        # 身体轻微前倾（说话）
        sp0 = cmds.getAttr(j + "Spine.rotateX")
        cmds.setKeyframe(j + "Spine.rotateX", time=st, value=sp0)
        cmds.setKeyframe(j + "Spine.rotateX", time=mid, value=sp0 + 2.5)
        cmds.setKeyframe(j + "Spine.rotateX", time=en, value=sp0)

        # 眨眼
        for f in (st + 6, mid + 9, en - 8):
            if f <= st or f >= en:
                continue
            cmds.setKeyframe(j + "Head.scaleY", time=f, value=1.0)
        # 用 eyeball 骨做眨眼会失真，这里用 head 微点头代替节奏
        cmds.setKeyframe(j + "Neck.rotateX", time=st, value=cmds.getAttr(j + "Neck.rotateX"))
        cmds.setKeyframe(j + "Neck.rotateX", time=mid, value=cmds.getAttr(j + "Neck.rotateX") + 2.0)
        cmds.setKeyframe(j + "Neck.rotateX", time=en, value=cmds.getAttr(j + "Neck.rotateX"))

    # 被摄者以外的角色，给极轻微呼吸
    for key, ch in chars.items():
        j = ch["j"]
        for f, v in ((1, 0), (1800, 1.2), (3512, 0)):
            pass

    cmds.file(os.path.join(ROOT, "scenes", "v7_final.mb"), f=True, type="mayaBinary", ea=True)

    # ---------- 输出目录设定 + 试渲 ----------
    cmds.workspace(os.path.dirname(ROOT), openWorkspace=True)
    try:
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
    except Exception:
        pass

    p = cmds.getPanel(type="modelPanel")[0]
    L.setup_viewport()
    cmds.modelEditor(p, e=True, camera=cmap["S001"], displayLights="default",
                     displayAppearance="smoothShaded", wireframeOnShaded=False)
    cmds.currentTime(shots[0]["start"] + 3)
    cmds.refresh(force=True)
    OUT["test"] = cmds.render(cmap["S001"], x=854, y=480)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "f1_build.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
