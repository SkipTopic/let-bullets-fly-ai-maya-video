import maya.cmds as cmds
import json, os, sys, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib, lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), o=True, force=True)
    j = "Ma_"
    gx, gy, gz = cmds.getAttr("GRP_Ma.translate")[0]
    table = 75.75
    # 目标：桌面正前方
    tgt = (gx, table + 3.0, gz + 28.0)
    sj, ee = j + "LeftArm", j + "LeftHand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVL")[0]
    cmds.setAttr(pv + ".translate", gx + 60, table + 25, gz + 5)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(tgt[0], tgt[1], tgt[2], h, absolute=True)
    chain = []
    cur = ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
        if cur:
            chain.append(cur)
    chain.append(sj)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain}
    got = cmds.xform(ee, q=True, ws=True, t=True)
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    cmds.refresh(force=True)
    after = cmds.xform(ee, q=True, ws=True, t=True)
    OUT["target"] = [round(v, 1) for v in tgt]
    OUT["got"] = [round(v, 1) for v in got]
    OUT["after"] = [round(v, 1) for v in after]
    OUT["err"] = round(sum((after[i]-tgt[i])**2 for i in range(3))**0.5, 2)
    OUT["rot"] = {k: [round(x, 1) for x in v] for k, v in vals.items()}
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","h1.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
