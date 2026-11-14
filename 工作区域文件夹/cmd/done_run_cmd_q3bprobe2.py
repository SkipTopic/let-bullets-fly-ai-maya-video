import maya.cmds as cmds
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}


def state(bone):
    data = {"world": list(cmds.xform(bone, q=True, ws=True, t=True)), "rotate": list(cmds.getAttr(bone + ".rotate")[0])}
    for attr in ("translate", "rotate", "scale", "jointOrient", "preferredAngle", "stiffness", "minRotLimit", "maxRotLimit", "minRotLimitEnable", "maxRotLimitEnable", "segmentScaleCompensate"):
        if cmds.attributeQuery(attr, node=bone, exists=True):
            try:
                data[attr] = cmds.getAttr(bone + "." + attr)
            except Exception as exc:
                data[attr] = repr(exc)
    data["locked"] = {a: cmds.getAttr(bone + "." + a, lock=True) for a in ("rotateX", "rotateY", "rotateZ")}
    data["connections"] = cmds.listConnections(bone + ".rotate", s=True, d=False) or []
    return data


def probe(start, end, target, pole, solver):
    before = {b: state(b) for b in (start, end)}
    handle = cmds.ikHandle(sj=start, ee=end, sol=solver, forceSolver=True)[0]
    loc = None
    if solver == "ikRPsolver":
        loc = cmds.spaceLocator()[0]
        cmds.setAttr(loc + ".translate", *pole)
        cmds.poleVectorConstraint(loc, handle)
    cmds.move(target[0], target[1], target[2], handle, absolute=True, worldSpace=True)
    if cmds.attributeQuery("ikBlend", node=handle, exists=True):
        cmds.setAttr(handle + ".ikBlend", 1.0)
    if cmds.attributeQuery("ikEnabled", node=handle, exists=True):
        cmds.setAttr(handle + ".ikEnabled", True)
    cmds.dgdirty(all=True)
    cmds.currentTime(2)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    handle_attrs = {}
    for attr in ("ikBlend", "ikEnabled", "solver", "priority", "weight", "poWeight"):
        if cmds.attributeQuery(attr, node=handle, exists=True):
            handle_attrs[attr] = cmds.getAttr(handle + "." + attr)
    effectors = cmds.listConnections(handle + ".endEffector", s=True, d=False) or []
    data = {
        "handle": list(cmds.xform(handle, q=True, ws=True, t=True)),
        "end": list(cmds.xform(end, q=True, ws=True, t=True)),
        "start": list(cmds.xform(start, q=True, ws=True, t=True)),
        "handle_attrs": handle_attrs,
        "effectors": [{"name": e, "world": list(cmds.xform(e, q=True, ws=True, t=True))} for e in effectors],
        "handle_connections": cmds.listConnections(handle, s=True, d=True) or [],
        "before": before,
        "after_start": state(start),
        "after_end": state(end),
    }
    parents = cmds.listRelatives(end, parent=True)
    if parents:
        data["middle"] = state(parents[0])
    cmds.delete(handle)
    if loc:
        cmds.delete(loc)
    return data


try:
    cmds.file(os.path.join(ROOT, "scenes", "摆姿重建_v1.mb"), o=True, f=True)
    OUT["rp"] = probe("Bip001LThigh", "Bip001LFoot", [6.7814, 10.1, -67.2828], [6.7814, 62.0, -35.0], "ikRPsolver")
    OUT["sc"] = probe("Bip001RThigh", "Bip001RFoot", [-6.7814, 10.1, -67.2828], None, "ikSCsolver")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "q3b_ik_probe.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
