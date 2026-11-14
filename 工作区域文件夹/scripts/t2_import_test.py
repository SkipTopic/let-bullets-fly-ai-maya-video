import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"step": "t2_import_test", "errors": []}

try:
    cmds.file(new=True, force=True)
    fbx = os.path.join(ROOT, "models_fbx", "CH_Ma.fbx")
    cmds.file(fbx, i=True, ignoreVersion=True, ra=True,
              mergeNamespacesOnClash=False, namespace=":")

    meshes = cmds.ls(type="mesh", ni=True) or []
    arms = cmds.ls(type="joint", ni=True) or []
    OUT["meshes"] = meshes
    OUT["joint_count"] = len(arms)

    shapes = [m for m in meshes]
    OUT["poly_counts"] = {m: cmds.polyEvaluate(m, f=True) for m in shapes}

    # 世界包围盒
    bb = None
    for m in shapes:
        b = cmds.exactWorldBoundingBox(m)
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), min(bb[2], b[2]),
                                   max(bb[3], b[3]), max(bb[4], b[4]), max(bb[5], b[5])]
    OUT["world_bbox"] = [round(v, 3) for v in bb] if bb else None

    # 变换链检查
    info = []
    for m in shapes:
        tr = cmds.listRelatives(m, parent=True)[0]
        info.append({
            "transform": tr,
            "translate": [round(v, 3) for v in cmds.getAttr(tr + ".translate")[0]],
            "scale": [round(v, 4) for v in cmds.getAttr(tr + ".scale")[0]],
            "rotate": [round(v, 3) for v in cmds.getAttr(tr + ".rotate")[0]],
            "visibility": cmds.getAttr(tr + ".visibility"),
            "lodVisibility": cmds.getAttr(tr + ".lodVisibility"),
            "overrideEnabled": cmds.getAttr(tr + ".overrideEnabled"),
            "overrideDisplayType": cmds.getAttr(tr + ".overrideDisplayType"),
            "shadingGroups": [cmds.listConnections(m, type="shadingEngine") or []],
            "displayLayer": cmds.listConnections(tr, type="displayLayer"),
            "intermediate": cmds.getAttr(m + ".intermediateObject"),
        })
    OUT["mesh_info"] = info

    # 灯光 + 相机
    cmds.directionalLight(n="KEY", rotation=(45, 35, 0))
    cmds.setAttr("KEY.intensity", 1.6)
    cmds.ambientLight(n="AMB", intensity=0.35)

    # 取包围盒中心/高度
    cx = (bb[0] + bb[3]) / 2.0
    cy = (bb[1] + bb[4]) / 2.0
    cz = (bb[2] + bb[5]) / 2.0
    h = bb[5] - bb[2]
    OUT["center"] = [round(cx, 2), round(cy, 2), round(cz, 2)]
    OUT["height"] = round(h, 2)

    cam = cmds.camera()
    cam_tr, cam_sh = cam[0], cam[1]
    cmds.setAttr(cam_tr + ".translate", cx + h * 1.4, cy + h * 0.15, cz + h * 2.2)
    cmds.setAttr(cam_sh + ".focalLength", 85)
    tgt = cmds.spaceLocator(n="AIM")[0]
    cmds.setAttr(tgt + ".translate", cx, cy, cz)
    cmds.pointConstraint(tgt, cam_tr, mo=False)
    cmds.setAttr(cam_tr + ".rotateX", -8)

    # 背景改成浅灰，方便判断有没有东西
    cmds.setAttr("hardwareRenderingGlobals.backgroundColorR", 0.55)
    cmds.setAttr("hardwareRenderingGlobals.backgroundColorG", 0.57)
    cmds.setAttr("hardwareRenderingGlobals.backgroundColorB", 0.62)

    png = os.path.join(ROOT, "_接手检查", "t2_char_test.png")
    os.makedirs(os.path.dirname(png), exist_ok=True)
    for f in (png, os.path.splitext(png)[0] + ".0001.png"):
        if os.path.exists(f):
            os.remove(f)

    cmds.playblast(frame=1, format="image", filename=png.replace(".png", ""),
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480],
                   quality=100, compression="png")
    OUT["png"] = png
    OUT["png_exists"] = os.path.exists(png) or os.path.exists(png.replace(".png", ".0001.png"))

    # 也存一份场景
    cmds.file(os.path.join(ROOT, "scenes", "t2_test.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "t2_import_test.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
