"""上材质：把磁盘上的贴图接到对应材质，按面片平均位置判断脸/头发/身体。"""
import json
import os
import traceback

import maya.api.OpenMaya as om
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "assign": {}}

TEX = {
    "Huang": {
        "face": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_f1_tex00.png",
        "hair": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_h00_tex00.png",
        "body": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_26_SEES00.png",
    },
    "Shiye": {
        "face": r"{R}\models_raw\junpei_iori\textures\pc103_f1_tex00.png",
        "hair": r"{R}\models_raw\junpei_iori\textures\pc103_h00_tex00.png",
        "body": r"{R}\models_raw\junpei_iori\textures\pc103_26_SEES00.png",
    },
}
MA_TEX = {
    "Face": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Face_D.png",
    "Hair": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Hair_D.png",
    "Eye": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Eye_D.png",
    "Up": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Up_D.png",
    "Down": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Down_D.png",
    "Hand": r"{R}\models_new\NH_MaleM_140\Model\T_NH_MaleM_140Hand_D.png",
}
MESH = {"Ma": "NH_MaleM_140_LOD0Shape", "Huang": "Huang_AragakiFBXASC032Shinjiro_meshShape",
        "Shiye": "Shiye_JunpeiFBXASC032Iori_meshShape"}
HEAD_Y = {"Ma": 113.0, "Huang": 123.2, "Shiye": 123.5}


def make_file_tex(path, name):
    if not os.path.exists(path):
        return None
    node = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name=name)
    cmds.setAttr(node + ".fileTextureName", path, type="string")
    place = cmds.shadingNode("place2dTexture", asUtility=True, name=name + "_p2d")
    for a in ("coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", "stagger",
              "wrapU", "wrapV", "repeatUV", "offset", "rotateUV", "noiseUV"):
        if cmds.attributeQuery(a, node=place, exists=True) and cmds.isConnected(place + "." + a, node + "." + a) is False:
            try:
                cmds.connectAttr(place + "." + a, node + "." + a, f=True)
            except Exception:
                pass
    return node


def sg_faces(shape, sg):
    try:
        return cmds.sets(sg, q=True) or []
    except Exception:
        return []


def face_center(shape, faces):
    """用 MFnMesh 求一组面的平均世界坐标。"""
    sel = om.MSelectionList()
    sel.add(shape)
    dag = sel.getDagPath(0)
    fn = om.MFnMesh(dag)
    pts = fn.getPoints(om.MSpace.kWorld)
    acc = om.MVector(0, 0, 0)
    n = 0
    for f in faces:
        try:
            idx = int(str(f).split("[")[-1].rstrip("]").split(":")[0])
        except Exception:
            continue
        verts = fn.getPolygonVertices(idx)
        if not verts:
            continue
        c = om.MVector(0, 0, 0)
        for v in verts:
            c += pts[v]
        acc += c / len(verts)
        n += 1
    return (acc / n) if n else None


try:
    for name, shape in MESH.items():
        if not cmds.objExists(shape):
            OUT["errors"].append("missing " + shape)
            continue
        sgs = cmds.listConnections(shape, type="shadingEngine") or []
        info = []
        for sg in sgs:
            mats = cmds.listConnections(sg + ".surfaceShader") or []
            if not mats:
                continue
            mat = mats[0]
            faces = sg_faces(shape, sg)
            c = face_center(shape, faces)
            info.append({"sg": sg, "mat": mat, "faces": len(faces),
                         "center": [round(c.x, 1), round(c.y, 1), round(c.z, 1)] if c else None})
        OUT["assign"][name] = info

    # --- 按类别贴图 ---
    for name, items in OUT["assign"].items():
        hy = HEAD_Y[name]
        for it in items:
            mat = it["mat"]
            cy = it["center"][1] if it["center"] else 0.0
            if name == "Ma":
                part = None
                for k in MA_TEX:
                    if k in mat:
                        part = k
                if not part:
                    continue
                path = MA_TEX[part].format(R=ROOT)
            else:
                if cy > hy + 4.0:
                    kind = "hair"
                elif cy > hy - 9.0:
                    kind = "face"
                else:
                    kind = "body"
                path = TEX[name][kind].format(R=ROOT)
                it["kind"] = kind
            tex = make_file_tex(path, "DS_TEX_%s_%s" % (name, mat.replace(":", "_")[-20:]))
            if not tex:
                OUT["errors"].append("tex missing " + path)
                continue
            try:
                cmds.connectAttr(tex + ".outColor", mat + ".color", f=True)
                it["texture"] = os.path.basename(path)
            except Exception as exc:  # noqa: BLE001
                OUT["errors"].append("connect %s: %r" % (mat, exc))

    # 视口开贴图
    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayTextures=True)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds32_materials.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for n, items in OUT["assign"].items():
    print("==", n)
    for i in items[:20]:
        print("  ", i["mat"][-28:], i["faces"], i["center"], i.get("kind"), i.get("texture"))
print("errors", OUT["errors"][:3])
