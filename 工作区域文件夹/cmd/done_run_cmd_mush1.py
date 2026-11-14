import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "d2_mush.json")
OUT = {"step": "start", "errors": []}


def dump():
    json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def shoot(name, eye, aim, focal=90):
    cam_name = "DM_" + name
    cam = cmds.camera(name=cam_name, focalLength=focal)[0]
    cmds.setAttr(cam + ".translate", *eye)
    # 手动算朝向（不建 locator，少建节点）
    dx, dy, dz = aim[0] - eye[0], aim[1] - eye[1], aim[2] - eye[2]
    import math
    horiz = math.sqrt(dx * dx + dz * dz)
    rot_y = math.degrees(math.atan2(dx, dz)) + 180.0
    rot_x = math.degrees(math.atan2(dy, horiz))
    cmds.setAttr(cam + ".rotate", -rot_x, rot_y, 0)

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(1)
    cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("DM_" + name + "."):
            try:
                os.remove(os.path.join(REV, old))
            except Exception:
                pass
    cmds.playblast(frame=1, format="image", filename=os.path.join(REV, "DM_" + name),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(640, 480), quality=95,
                   compression="png")
    cmds.delete(cam)
    return "DM_" + name + ".0000.png"


try:
    OUT["step"] = "open"
    dump()
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)

    OUT["step"] = "pose"
    dump()
    j = "Ma_"
    cmds.setAttr(j + "LeftArm.rotate", -30.8, 33.1, -20.2)
    cmds.setAttr(j + "LeftForeArm.rotate", -66.1, -6.2, 66.3)
    cmds.refresh(force=True)
    OUT["hand"] = [round(v, 1) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)]

    OUT["step"] = "render_A"
    dump()
    OUT["A"] = shoot("A", (62, 96, -52), (12, 84, -95))

    OUT["step"] = "deltaMush"
    dump()
    mesh = "Ma_MakotoFBXASC032Yuki_mesh"
    try:
        dm = cmds.deltaMush(mesh, smoothingIterations=6, smoothingStep=0.5,
                            pinBorderVertices=0, envelope=1.0)
        OUT["dm_node"] = dm
    except Exception as e:
        OUT["dm_err"] = repr(e)
    dump()

    OUT["step"] = "render_B"
    dump()
    cmds.refresh(force=True)
    OUT["B"] = shoot("B", (62, 96, -52), (12, 84, -95))

    OUT["step"] = "done"
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
