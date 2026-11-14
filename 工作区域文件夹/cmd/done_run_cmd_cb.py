import maya.cmds as cmds, json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(ROOT, "logs", "e4.json")
OUT = {"runs": [], "errors": []}
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def hh(mesh):
    bb = cmds.xform(mesh, q=True, ws=True, bb=True)
    return round(bb[4]-bb[1], 0)

def run(tag, dm_first=False, iters=3, step=0.4, pin=1):
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    mesh = "Huang_AragakiFBXASC032Shinjiro_mesh"; j = "Huang_"
    if dm_first:
        cmds.deltaMush(mesh, smoothingIterations=iters, smoothingStep=step,
                       pinBorderVertices=pin, envelope=1.0)
    gx, gy, gz = cmds.getAttr("CHR_Huang.translate")[0]
    ang = math.radians(cmds.getAttr("CHR_Huang.rotateY"))
    fwd = (math.sin(ang), math.cos(ang)); right = (math.cos(ang), -math.sin(ang))
    for s in (1, -1):
        tgt = (gx + fwd[0]*25 + right[0]*19*s, 78.75, gz + fwd[1]*25 + right[1]*19*s)
        pole = (gx + fwd[0]*2 + right[0]*95*s, 59.75, gz + fwd[1]*2 + right[1]*95*s)
        hd = cmds.ikHandle(sj=j+("LeftArm" if s>0 else "RightArm"),
                           ee=j+("LeftHand" if s>0 else "RightHand"), sol="ikRPsolver")[0]
        pv = cmds.spaceLocator(name="PVc")[0]
        cmds.setAttr(pv+".translate", *pole)
        cmds.poleVectorConstraint(pv, hd)
        cmds.move(tgt[0], tgt[1], tgt[2], hd, absolute=True)
        chain, cur = [], (j+("LeftHand" if s>0 else "RightHand"))
        sj = j+("LeftArm" if s>0 else "RightArm")
        while cur and cur != sj:
            chain.append(cur); p = cmds.listRelatives(cur, parent=True); cur = p[0] if p else None
        chain.append(sj)
        vals = {b: list(cmds.getAttr(b+".rotate")[0]) for b in chain}
        cmds.delete(hd); cmds.delete(pv)
        for b, v in vals.items():
            cmds.setAttr(b+".rotate", *v)
    if not dm_first:
        cmds.deltaMush(mesh, smoothingIterations=iters, smoothingStep=step,
                       pinBorderVertices=pin, envelope=1.0)
    cmds.refresh(force=True)
    rec = {"tag": tag, "dm_first": dm_first, "pin": pin, "iters": iters,
           "h": hh(mesh)}
    OUT["runs"].append(rec); dump()
    return rec

try:
    run("A 无DM", dm_first=False, iters=0)          # 先跑一次不带 DM 的基准
    cmds.delete(cmds.ls(type="deltaMush") or [])
    run("B IK后加DM pin1 i3", dm_first=False, iters=3, pin=1)
    run("C IK后加DM pin0 i3", dm_first=False, iters=3, pin=0)
    run("D DM先加 pin1 i8", dm_first=True, iters=8, pin=1)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
