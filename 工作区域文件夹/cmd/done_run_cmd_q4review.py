import maya.cmds as cmds
import json, os, math, traceback, glob

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT_DIR = os.path.join(ROOT, "_摆姿验收", "v4")
OUT = {"errors": [], "images": {}}
os.makedirs(OUT_DIR, exist_ok=True)


def make_camera(name, eye, aim, width, up=(0.0, 1.0, 0.0)):
    cam = cmds.camera(name=name)[0]
    shape = cmds.listRelatives(cam, shapes=True)[0]
    cmds.setAttr(shape + ".orthographic", True)
    cmds.setAttr(shape + ".orthographicWidth", width)
    cmds.setAttr(shape + ".nearClipPlane", 1.0)
    cmds.setAttr(shape + ".farClipPlane", 2200.0)
    cmds.setAttr(shape + ".renderable", False)
    cmds.setAttr(cam + ".translate", *eye)
    target = cmds.spaceLocator(name=name + "_AIM")[0]
    cmds.setAttr(target + ".translate", *aim)
    constraint = cmds.aimConstraint(target, cam, aimVector=(0.0, 0.0, -1.0), upVector=up, worldUpType="vector", worldUpVector=up)
    matrix = cmds.xform(cam, q=True, ws=True, m=True)
    cmds.delete(constraint)
    cmds.delete(target)
    cmds.xform(cam, ws=True, m=matrix)
    cmds.parent(cam, "POSE_REVIEW_CAMERAS")
    return cam


def character_frame(group):
    center = list(cmds.getAttr(group + ".translate")[0])
    yaw = math.radians(cmds.getAttr(group + ".rotateY"))
    fwd = [math.sin(yaw), 0.0, math.cos(yaw)]
    right = [math.cos(yaw), 0.0, -math.sin(yaw)]
    return center, fwd, right


def add(a, b, scale=1.0):
    return [a[i] + b[i] * scale for i in range(3)]


try:
    cmds.file(os.path.join(ROOT, "scenes", "摆姿重建_v4.mb"), o=True, f=True)
    cmds.currentTime(1)
    if cmds.objExists("POSE_REVIEW_CAMERAS"):
        cmds.delete("POSE_REVIEW_CAMERAS")
    cmds.group(em=True, name="POSE_REVIEW_CAMERAS")

    specs = [
        ("Scene_front", (0.0, 100.0, 400.0), (0.0, 65.0, 0.0), 360.0, (0.0, 1.0, 0.0)),
        ("Scene_left", (-400.0, 100.0, 0.0), (0.0, 65.0, 0.0), 360.0, (0.0, 1.0, 0.0)),
        ("Scene_right", (400.0, 100.0, 0.0), (0.0, 65.0, 0.0), 360.0, (0.0, 1.0, 0.0)),
        ("Scene_top", (0.0, 450.0, 0.01), (0.0, 50.0, 0.0), 340.0, (0.0, 0.0, -1.0)),
    ]
    for key, group in (("Ma", "CHR_Ma"), ("Huang", "CHR_Huang"), ("Shiye", "CHR_Shiye")):
        center, fwd, right = character_frame(group)
        target = add(center, [0.0, 1.0, 0.0], 68.0)
        specs.extend([
            (key + "_front", add(add(target, fwd, 250.0), [0.0, 1.0, 0.0], 25.0), target, 200.0, (0.0, 1.0, 0.0)),
            (key + "_left", add(add(target, right, 250.0), [0.0, 1.0, 0.0], 25.0), target, 200.0, (0.0, 1.0, 0.0)),
            (key + "_right", add(add(target, right, -250.0), [0.0, 1.0, 0.0], 25.0), target, 200.0, (0.0, 1.0, 0.0)),
            (key + "_top", add(target, [0.0, 1.0, 0.0], 300.0), target, 160.0, fwd),
        ])
    for name, eye, aim, width, up in specs:
        make_camera("REVIEW_" + name, eye, aim, width, up)

    panels = cmds.getPanel(type="modelPanel") or []
    visible = [p for p in panels if cmds.control(p, q=True, visible=True)]
    if not visible:
        raise RuntimeError("No visible modelPanel")
    panel = visible[0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=False,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     wireframeOnShaded=False, backfaceCulling=False, twoSidedLighting=True,
                     selectionHiliteDisplay=False)
    cmds.select(clear=True)
    for name, _eye, _aim, _width, _up in specs:
        cam = "REVIEW_" + name
        cmds.lookThru(panel, cam)
        cmds.currentTime(1)
        cmds.refresh(force=True)
        base = os.path.join(OUT_DIR, name)
        made = cmds.playblast(frame=1, format="image", filename=base, sequenceTime=False,
                              clearCache=True, viewer=False, showOrnaments=False,
                              offScreen=True, percent=100, widthHeight=(960, 720),
                              quality=95, compression="png")
        matches = glob.glob(base + "*.png")
        OUT["images"][name] = {"returned": made, "matches": matches}
    cmds.lookThru(panel, "REVIEW_Scene_front")
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "q4_review.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
