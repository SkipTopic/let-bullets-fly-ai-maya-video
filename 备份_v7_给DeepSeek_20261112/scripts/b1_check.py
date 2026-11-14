import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}

try:
    cmds.file(new=True, force=True)
    cmds.file(os.path.join(ROOT, "models_fbx2", "CH_Ma.fbx"), i=True, ignoreVersion=True,
              ra=True, mergeNamespacesOnClash=False, namespace=":")

    joints = cmds.ls(type="joint") or []
    OUT["joint_count"] = len(joints)
    OUT["joints_sample"] = joints[:40]

    meshes = [m for m in (cmds.ls(type="mesh", ni=True) or [])
              if cmds.listConnections(m, type="skinCluster")]
    OUT["main_meshes"] = meshes
    m = meshes[0]
    tr = cmds.listRelatives(m, parent=True)[0]
    cmds.rename(tr, "CH_Ma_GEO")

    OUT["geo_scale"] = [round(v, 4) for v in cmds.getAttr("CH_Ma_GEO.scale")[0]]
    OUT["geo_rot"] = [round(v, 3) for v in cmds.getAttr("CH_Ma_GEO.rotate")[0]]

    bb = cmds.exactWorldBoundingBox("CH_Ma_GEO")
    OUT["bbox"] = [round(v, 2) for v in bb]

    key = {}
    for j in ("Head", "Hips", "LeftFoot", "RightFoot", "LeftHand", "RightHand", "LeftArm", "LeftForeArm"):
        if cmds.objExists(j):
            key[j] = [round(v, 2) for v in cmds.xform(j, q=True, ws=True, t=True)]
    OUT["key_ws"] = key

    # 父链检查（确认没有断链）
    chain = []
    n = "LeftHand"
    while n:
        chain.append(n)
        p = cmds.listRelatives(n, parent=True)
        n = p[0] if p else None
        if len(chain) > 30:
            break
    OUT["left_hand_chain"] = chain

    # 灯光 + 相机
    cmds.directionalLight(n="KEY", rotation=(55, -30, 0))
    cmds.setAttr("KEY.intensity", 1.7)
    cmds.ambientLight(n="AMB", intensity=0.45)

    cam_tr = cmds.camera(name="TCAM")[0]
    h = max(1.0, bb[4] - bb[1])
    cmds.setAttr(cam_tr + ".translate", (bb[0] + bb[3]) / 2, h * 0.55, bb[5] + h * 1.7)
    cmds.setAttr(cmds.listRelatives(cam_tr, shapes=True)[0] + ".focalLength", 50)
    cmds.setAttr(cam_tr + ".rotate", -3, 0, 0)
    cmds.lookThru(cam_tr)

    for me in cmds.ls(type="modelEditor") or []:
        try:
            cmds.modelEditor(me, e=True, displayAppearance="smoothShaded",
                             displayTextures=False, wireframeOnShaded=False,
                             grid=False, joints=False, manipulators=False,
                             headsUpDisplay=False, displayLights="default")
        except Exception:
            pass

    base = os.path.join(ROOT, "_接手检查", "b1_check")
    for f in os.listdir(os.path.join(ROOT, "_接手检查")):
        if f.startswith("b1_check"):
            os.remove(os.path.join(ROOT, "_接手检查", f))
    cmds.playblast(frame=1, format="image", filename=base, sequenceTime=0, clearCache=1,
                   viewer=0, showOrnaments=0, fp=4, percent=100,
                   widthHeight=[640, 480], quality=95, compression="png")
    OUT["png"] = [f for f in os.listdir(os.path.join(ROOT, "_接手检查")) if f.startswith("b1_check")]
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "b1_check.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
