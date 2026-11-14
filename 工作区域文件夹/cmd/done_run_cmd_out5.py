import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
import lib_scene as _L
L = importlib.reload(_L)

OUT = {"errors": []}
TABLE_TOP = 75.75


def chain_between(sj, ee):
    """从 sj 到 ee 的关节链（含两端）"""
    out = [ee]
    cur = ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        if not p:
            break
        cur = p[0]
        out.append(cur)
    return list(reversed(out))


def ik_put_hand(j, side, target, pole_side):
    sj, ee = j + side + "Arm", j + side + "Hand"
    bones = chain_between(sj, ee)
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PV_" + side)[0]
    cmds.setAttr(pv + ".translate", *pole_side)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    vals = {}
    for b in bones:
        vals[b] = list(cmds.getAttr(b + ".rotate")[0])
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    return vals


try:
    chars = L.build_all()

    # ---------- 双手放到桌面（IK 反解后回写旋转） ----------
    rest = {}
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "LeftArm.rotate", -65, 0, -25)
        cmds.setAttr(j + "LeftForeArm.rotateX", 70)
        cmds.setAttr(j + "RightArm.rotate", 40, 0, -40)
        cmds.setAttr(j + "RightForeArm.rotateX", -110)
        rest[key] = {
            "L": [round(v, 1) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)],
            "R": [round(v, 1) for v in cmds.xform(j + "RightHand", q=True, ws=True, t=True)],
        }

        # 躯干与头
        cmds.setAttr(j + "Spine.rotateX", 4)
        cmds.setAttr(j + "Spine1.rotateX", 2)
        cmds.setAttr(j + "Neck.rotateX", -13)
        cmds.setAttr(j + "Head.rotateX", -14)
    OUT["hand_err"] = rest
    cmds.refresh(force=True)

    # ---------- 71 台相机 ----------
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
        if s["eye0"] != s["eye1"]:
            cmds.setKeyframe(cam, attribute="translateX", time=s["start"], value=s["eye0"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["start"], value=s["eye0"][2] * k)
            cmds.setKeyframe(cam, attribute="translateX", time=s["end"], value=s["eye1"][0] * k)
            cmds.setKeyframe(cam, attribute="translateZ", time=s["end"], value=s["eye1"][2] * k)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)

    # ---------- 表演：转头 + 手臂动作（不碰手指） ----------
    KEY = {"Ma": "Ma_", "Huang": "Huang_", "Shiye": "Shiye_"}
    GESTURE_WORDS = ("指", "举", "端", "拿", "比", "挥", "伸", "扶", "放", "拍", "推", "倒")
    for idx, s in enumerate(shots):
        j = KEY[s["subject"]]
        st, en = s["start"], s["end"]
        mid = st + max(2, s["dur"] // 2)

        hy = cmds.getAttr(j + "Head.rotateY")
        turn = -17 if (s.get("listener") in ("Ma", "Shiye")) else 13
        cmds.setKeyframe(j + "Head.rotateY", time=st, value=hy)
        cmds.setKeyframe(j + "Head.rotateY", time=mid, value=hy + turn)
        cmds.setKeyframe(j + "Head.rotateY", time=en, value=hy + turn * 0.45)

        cmds.setKeyframe(j + "Neck.rotateX", time=st, value=-13)
        cmds.setKeyframe(j + "Neck.rotateX", time=mid, value=-10)
        cmds.setKeyframe(j + "Neck.rotateX", time=en, value=-13)

        if any(w in s["action"] for w in GESTURE_WORDS):
            side = "Left" if idx % 2 == 0 else "Right"
            ax, ay, az = cmds.getAttr(j + side + "Arm.rotate")[0]
            fx = cmds.getAttr(j + side + "ForeArm.rotateX")
            lift = -14 if side == "Left" else 14
            cmds.setKeyframe(j + side + "Arm.rotateX", time=st, value=ax)
            cmds.setKeyframe(j + side + "Arm.rotateX", time=mid, value=ax + lift)
            cmds.setKeyframe(j + side + "Arm.rotateX", time=en, value=ax)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=st, value=fx)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=mid, value=fx - lift * 0.7)
            cmds.setKeyframe(j + side + "ForeArm.rotateX", time=en, value=fx)

        cmds.setKeyframe(j + "Spine.rotateX", time=st, value=4)
        cmds.setKeyframe(j + "Spine.rotateX", time=mid, value=6.2)
        cmds.setKeyframe(j + "Spine.rotateX", time=en, value=4)

    cmds.file(os.path.join(ROOT, "scenes", "v8_outdoor.mb"), f=True, type="mayaBinary", ea=True)

    # 试渲一张
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, camera=cmap["S001"], displayLights="default",
                     displayAppearance="smoothShaded", wireframeOnShaded=False,
                     grid=False, joints=False, headsUpDisplay=False)
    cmds.currentTime(30)
    cmds.refresh(force=True)
    OUT["test"] = cmds.render(cmap["S001"], x=854, y=480)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f4_outdoor.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
