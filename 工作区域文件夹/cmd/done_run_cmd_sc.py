import maya.cmds as cmds, json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(ROOT, "logs", "e3.json")
OUT = {"errors": []}
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def h(mesh):
    bb = cmds.xform(mesh, q=True, ws=True, bb=True)
    return round(bb[4]-bb[1], 0)
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    mesh = "Huang_AragakiFBXASC032Shinjiro_mesh"; j = "Huang_"
    gx, gy, gz = cmds.getAttr("CHR_Huang.translate")[0]
    ang = math.radians(cmds.getAttr("CHR_Huang.rotateY"))
    fwd = (math.sin(ang), math.cos(ang)); right = (math.cos(ang), -math.sin(ang))
    OUT["rest_h"] = h(mesh)

    tgt = (gx + fwd[0]*25 + right[0]*19, 78.75, gz + fwd[1]*25 + right[1]*19)
    pole = (gx + fwd[0]*2 + right[0]*95, 59.75, gz + fwd[1]*2 + right[1]*95)
    hd = cmds.ikHandle(sj=j+"LeftArm", ee=j+"LeftHand", sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVe")[0]
    cmds.setAttr(pv+".translate", *pole)
    cmds.poleVectorConstraint(pv, hd)
    cmds.move(tgt[0], tgt[1], tgt[2], hd, absolute=True)
    cmds.refresh(force=True)
    OUT["after_ik_h"] = h(mesh)

    # 检查链上骨骼的缩放
    chain, cur = [], j+"LeftHand"
    while cur and cur != j+"LeftArm":
        chain.append(cur)
        p = cmds.listRelatives(cur, parent=True); cur = p[0] if p else None
    chain.append(j+"LeftArm")
    scales = {}
    for b in chain:
        try:
            scales[b] = [round(v,4) for v in cmds.getAttr(b+".scale")[0]]
        except Exception:
            pass
    OUT["scales_after_ik"] = scales
    dump()

    # 把缩放全部归 1
    for b in chain:
        for ax in ("scaleX","scaleY","scaleZ"):
            try: cmds.setAttr(b+"."+ax, 1.0)
            except Exception: pass
    cmds.refresh(force=True)
    OUT["after_reset_scale_h"] = h(mesh)
    dump()
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
