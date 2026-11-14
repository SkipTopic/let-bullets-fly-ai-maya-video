import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = {"errors": []}
REV = os.path.join(ROOT, "_审片")
TABLE = 75.75

ARM_CHAIN = ["Arm", "ArmTwist", "ForeArm", "HandTwist", "Hand"]
CHARS = {
    "Ma": ("CHR_Ma", "Ma_"),
    "Huang": ("CHR_Huang", "Huang_"),
    "Shiye": ("CHR_Shiye", "Shiye_"),
}


def reset_pose(j):
    for sd in ("Left", "Right"):
        for b in ARM_CHAIN:
            if cmds.objExists(j + sd + b):
                cmds.setAttr(j + sd + b + ".rotate", 0, 0, 0)
    # 躯干坐直，只留极轻的前倾
    cmds.setAttr(j + "Spine.rotateX", 1.5)
    cmds.setAttr(j + "Spine1.rotateX", 1.0)
    cmds.setAttr(j + "Neck.rotateX", -9)
    cmds.setAttr(j + "Head.rotateX", -7)
    for b in ("LeftUpLeg", "RightUpLeg"):
        cmds.setAttr(j + b + ".rotateX", -92)
    for b in ("LeftLeg", "RightLeg"):
        cmds.setAttr(j + b + ".rotateX", 92)
    for b in ("LeftFoot", "RightFoot"):
        cmds.setAttr(j + b + ".rotateX", -6)


def put_hand(j, side, target, pole):
    sj, ee = j + side + "Arm", j + side + "Hand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVt")[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    chain, cur = [ee], ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
        if cur:
            chain.append(cur)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain}
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    cmds.refresh(force=True)
    return list(cmds.xform(ee, q=True, ws=True, t=True))


try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)

    # ---------- 扶正 + 手放桌面 ----------
    report = {}
    for key, (grp, j) in CHARS.items():
        reset_pose(j)
    cmds.refresh(force=True)

    for key, (grp, j) in CHARS.items():
        gx, gy, gz = cmds.getAttr(grp + ".translate")[0]
        ang = math.radians(cmds.getAttr(grp + ".rotateY"))
        # 角色本地 +Z 朝向（rotateY 后）
        fwd = (math.sin(ang), math.cos(ang))
        right = (math.cos(ang), -math.sin(ang))
        rec = {"body": [round(gx, 1), round(gz, 1)], "fwd": [round(f, 2) for f in fwd]}
        for side, s in (("Left", 1), ("Right", -1)):
            tgt = (gx + fwd[0] * 26 + right[0] * 17 * s, TABLE + 3.0,
                   gz + fwd[1] * 26 + right[1] * 17 * s)
            pole = (gx + fwd[0] * 6 + right[0] * 85 * s, TABLE + 22,
                    gz + fwd[1] * 6 + right[1] * 85 * s)
            got = put_hand(j, side, tgt, pole)
            # 手的横向偏移（离身体中轴多远）
            dx = got[0] - gx
            dz = got[1 - 1] * 0 + (got[2] - gz)
            rec[side] = {
                "target": [round(v, 1) for v in tgt],
                "got": [round(v, 1) for v in got],
                "err": round(sum((got[i] - tgt[i]) ** 2 for i in range(3)) ** 0.5, 2),
                "y_above_table": round(got[1] - TABLE, 1),
            }
        rec["head_y"] = round(cmds.xform(j + "Head", q=True, ws=True, t=True)[1], 1)
        rec["shoulder_y"] = round(cmds.xform(j + "LeftArm", q=True, ws=True, t=True)[1], 1)
        report[key] = rec
    OUT["pose"] = report

    # ---------- 观察摄像机（不参与渲染） ----------
    obs = {
        "OV_front": ((0, 175, 330), (0, 80, -30), 45),
        "OV_left": ((-330, 165, 120), (0, 78, -30), 45),
        "OV_right": ((330, 165, 120), (0, 78, -30), 45),
        "OV_top": ((0, 360, 40), (0, 55, -40), 40),
    }
    grp_ov = cmds.group(em=True, name="OBSERVATION_CAMERAS")
    if cmds.objExists("SCENE"):
        cmds.parent(grp_ov, "SCENE")
    made = []
    for nm, (eye, aim, focal) in obs.items():
        cam = cmds.camera(name=nm, focalLength=focal)[0]
        cmds.setAttr(cam + ".translate", *eye)
        loc = cmds.spaceLocator(name=nm + "_aim")[0]
        cmds.setAttr(loc + ".translate", *aim)
        k = cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                               worldUpType="vector", worldUpVector=(0, 1, 0))
        m = cmds.xform(cam, q=True, ws=True, m=True)
        cmds.delete(k)
        cmds.delete(loc)
        cmds.xform(cam, ws=True, m=m)
        shp = cmds.listRelatives(cam, shapes=True)[0]
        try:
            cmds.setAttr(shp + ".renderable", 0)     # 不参与渲染
        except Exception:
            pass
        cmds.parent(cam, grp_ov)
        made.append(cam)
    OUT["obs_cams"] = made

    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), f=True, type="mayaBinary", ea=True)

    # ---------- 出观察图 ----------
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    for nm in ("OV_front", "OV_left", "OV_right", "OV_top"):
        cmds.currentTime(1)
        cmds.lookThru(p, nm)
        for old in os.listdir(REV):
            if old.startswith(nm + "."):
                try:
                    os.remove(os.path.join(REV, old))
                except Exception:
                    pass
        cmds.playblast(frame=1, format="image", filename=os.path.join(REV, nm),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(960, 540), quality=90, compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f13_pose.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
