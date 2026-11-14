import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
TABLE = 75.75


def shoot(name, eye, aim, focal=85, frame=1):
    cam_name = "DIAG_" + name
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam = cmds.camera(name=cam_name, focalLength=focal)[0]
    cmds.setAttr(cam + ".translate", *eye)
    loc = cmds.spaceLocator(name=cam_name + "_aim")[0]
    cmds.setAttr(loc + ".translate", *aim)
    k = cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
    m = cmds.xform(cam, q=True, ws=True, m=True)
    cmds.delete(k)
    cmds.delete(loc)
    cmds.xform(cam, ws=True, m=m)

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(frame)
    cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("BRK_" + name + "."):
            try:
                os.remove(os.path.join(REV, old))
            except Exception:
                pass
    cmds.playblast(frame=frame, format="image",
                   filename=os.path.join(REV, "BRK_" + name),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(640, 480), quality=95,
                   compression="png")
    return os.path.join(REV, "BRK_" + name + ".0000.png")


try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    j = "Ma_"

    # ---- 复现：左臂抬到桌面高度（之前 IK 解出的姿势）----
    cmds.setAttr(j + "LeftArm.rotate", -30.8, 33.1, -20.2)
    cmds.setAttr(j + "LeftForeArm.rotate", -66.1, -6.2, 66.3)
    cmds.refresh(force=True)
    hand = cmds.xform(j + "LeftHand", q=True, ws=True, t=True)
    OUT["hand"] = [round(v, 1) for v in hand]

    eye = (78, 96, -58)
    aim = (10, 84, -95)
    OUT["A_before"] = shoot("A_before", eye, aim)

    # ---- 试 Delta Mush ----
    mesh = "Ma_MakotoFBXASC032Yuki_mesh"
    try:
        dm = cmds.deltaMush(mesh, smoothingIterations=10, smoothingStep=0.55,
                            pinBorderVertices=1, envelope=1.0)
        OUT["deltaMush"] = dm
    except Exception as e:
        OUT["deltaMush_err"] = repr(e)
        # 可能名字带数字
        shapes = cmds.listRelatives(mesh, shapes=True) or []
        OUT["shapes"] = shapes

    cmds.refresh(force=True)
    OUT["B_deltaMush"] = shoot("B_deltaMush", eye, aim, frame=1)

    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "d1_break.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
