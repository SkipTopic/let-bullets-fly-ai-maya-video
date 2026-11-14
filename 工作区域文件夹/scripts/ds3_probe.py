"""DS 场景探查：布景、灯光、材质、渲染设置、观察相机参数、视口面板。"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
d = {"errors": []}


def safe(fn, default=None):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        d["errors"].append(str(exc))
        return default


d["set_children"] = safe(lambda: sorted(cmds.listRelatives("GRP_SET", children=True) or []), [])
d["set_detail"] = {}
for node in d["set_children"]:
    bb = safe(lambda n=node: cmds.exactWorldBoundingBox(n))
    shapes = safe(lambda n=node: cmds.listRelatives(n, shapes=True, type="mesh") or [])
    d["set_detail"][node] = {"bbox": [round(v, 1) for v in bb] if bb else None, "mesh": bool(shapes)}

d["lights"] = []
for lt in safe(lambda: cmds.ls(type="light") or [], []):
    tr = cmds.listRelatives(lt, parent=True) or [lt]
    info = {
        "light": lt,
        "transform": tr[0],
        "type": cmds.nodeType(lt),
        "intensity": safe(lambda l=lt: cmds.getAttr(l + ".intensity")),
        "color": safe(lambda l=lt: [round(c, 3) for c in cmds.getAttr(l + ".color")[0]]),
        "world": safe(lambda t=tr[0]: [round(v, 1) for v in cmds.xform(t, q=True, ws=True, t=True)]),
    }
    d["lights"].append(info)

d["shading"] = {}
for mesh in safe(lambda: cmds.ls(type="mesh", noIntermediate=True) or [], []):
    sgs = safe(lambda m=mesh: cmds.listConnections(m, type="shadingEngine") or [], [])
    mats = []
    for sg in sgs:
        mats += safe(lambda s=sg: cmds.listConnections(s + ".surfaceShader") or [], [])
    d["shading"][mesh] = {"verts": safe(lambda m=mesh: cmds.polyEvaluate(m, v=True)), "materials": mats}

d["render"] = {
    "width": safe(lambda: cmds.getAttr("defaultResolution.width")),
    "height": safe(lambda: cmds.getAttr("defaultResolution.height")),
    "aspect": safe(lambda: cmds.getAttr("defaultResolution.deviceAspectRatio")),
    "engine": safe(lambda: cmds.getAttr("defaultRenderGlobals.currentRenderer")),
}

d["panels"] = safe(lambda: cmds.getPanel(type="modelPanel") or [], [])
d["visible_panel_cam"] = {}
for p in d.get("panels", []):
    d["visible_panel_cam"][p] = safe(lambda pp=p: cmds.modelEditor(pp, q=True, camera=True))

cams = []
for c in safe(lambda: cmds.listCameras() or [], []):
    tr = cmds.listRelatives(c, parent=True) or [c]
    cams.append({
        "shape": c,
        "transform": tr[0],
        "focal": safe(lambda s=c: cmds.getAttr(s + ".focalLength")),
        "haperture": safe(lambda s=c: cmds.getAttr(s + ".horizontalFilmAperture")),
        "vaperture": safe(lambda s=c: cmds.getAttr(s + ".verticalFilmAperture")),
        "fit": safe(lambda s=c: cmds.getAttr(s + ".filmFit")),
        "ortho": safe(lambda s=c: cmds.getAttr(s + ".orthographic")),
        "world": safe(lambda t=tr[0]: [round(v, 1) for v in cmds.xform(t, q=True, ws=True, t=True)]),
        "parent": safe(lambda t=tr[0]: (cmds.listRelatives(t, parent=True) or [None])[0]),
        "near_far": safe(lambda s=c: [cmds.getAttr(s + ".nearClipPlane"), cmds.getAttr(s + ".farClipPlane")]),
    })
d["cameras"] = cams

d["top_level"] = safe(lambda: sorted(cmds.ls(assemblies=True) or []), [])

out = os.path.join(ROOT, "logs", "ds3_probe.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": True, "out": out}, ensure_ascii=False))
