import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"step": "t3_render_test", "errors": []}

def world_bbox(shapes):
    bb = None
    for m in shapes:
        b = cmds.exactWorldBoundingBox(m)
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), min(bb[2], b[2]),
                                   max(bb[3], b[3]), max(bb[4], b[4]), max(bb[5], b[5])]
    return bb

try:
    cmds.file(new=True, force=True)
    fbx = os.path.join(ROOT, "models_fbx", "CH_Ma.fbx")
    cmds.file(fbx, i=True, ignoreVersion=True, ra=True,
              mergeNamespacesOnClash=False, namespace=":")

    # 只取"可见的主网格"：有 skinCluster 的那个
    all_meshes = cmds.ls(type="mesh", ni=True) or []
    main = [m for m in all_meshes if cmds.listConnections(m, type="skinCluster")]
    OUT["main_meshes"] = main
    OUT["hidden_count"] = len(all_meshes) - len(main)

    # 重命名成干净名字（只改 transform，shape 会自动跟着改）
    clean = []
    for i, m in enumerate(main):
        tr = cmds.listRelatives(m, parent=True)[0]
        new_tr = cmds.rename(tr, "CH_Ma_GEO")
        shp = cmds.listRelatives(new_tr, shapes=True, ni=True)[0]
        clean.append(shp)
    main = clean
    OUT["renamed"] = main

    bb = world_bbox(main)
    OUT["bbox"] = [round(v, 2) for v in bb]
    W = bb[3] - bb[0]; H = bb[4] - bb[1]; D = bb[5] - bb[2]
    OUT["size_xyz"] = [round(W, 2), round(H, 2), round(D, 2)]

    # 灯光
    key = cmds.directionalLight(n="KEY", rotation=(50, -35, 0))
    cmds.setAttr(key + ".intensity", 1.5)
    cmds.ambientLight(n="AMB", intensity=0.45)

    # 相机：正面，高度取人物胸口，距离按身高
    cam_tr = cmds.camera(name="TCAM")[0]
    cm_y = bb[1] + H * 0.55
    cm_z = bb[2] + D * 0.5
    dist = H * 1.8
    cmds.setAttr(cam_tr + ".translate", (bb[0] + bb[3]) / 2.0, cm_y, cm_z + dist)
    cmds.setAttr(cam_tr + ".rotate", -2, 0, 0)
    cmds.setAttr(cmds.listRelatives(cam_tr, shapes=True)[0] + ".focalLength", 50)
    cmds.lookThru(cam_tr)
    OUT["camera"] = [round(v, 2) for v in cmds.getAttr(cam_tr + ".translate")[0]]

    # 视口显示设置
    for me in cmds.ls(type="modelEditor") or []:
        try:
            cmds.modelEditor(me, e=True, displayAppearance="smoothShaded",
                             displayTextures=False, displayLights="default",
                             wireframeOnShaded=False, grid=False, joints=False,
                             manipulators=False, headsUpDisplay=False)
        except Exception:
            pass

    os.makedirs(os.path.join(ROOT, "_接手检查"), exist_ok=True)
    base = os.path.join(ROOT, "_接手检查", "t3_char")
    for f in os.listdir(os.path.join(ROOT, "_接手检查")):
        if f.startswith("t3_char") and f.endswith(".png"):
            os.remove(os.path.join(ROOT, "_接手检查", f))

    cmds.playblast(frame=1, format="image", filename=base,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480],
                   quality=100, compression="png")
    OUT["pngs"] = [f for f in os.listdir(os.path.join(ROOT, "_接手检查")) if f.startswith("t3_char")]
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "t3_render_test.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
