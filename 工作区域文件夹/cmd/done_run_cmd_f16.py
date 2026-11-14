import maya.cmds as cmds, json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "f16.json")
OUT = {"errors": []}
TABLE = 75.75
CH = {"Ma": ("CHR_Ma", "Ma_", "Ma_MakotoFBXASC032Yuki_mesh"),
      "Huang": ("CHR_Huang", "Huang_", "Huang_AragakiFBXASC032Shinjiro_mesh"),
      "Shiye": ("CHR_Shiye", "Shiye_", "Shiye_JunpeiFBXASC032Iori_mesh")}
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def hh(m):
    bb = cmds.xform(m, q=True, ws=True, bb=True)
    return round(bb[4]-bb[1], 0)

def ik_arm(j, side, tgt, pole):
    sj, ee = j+side+"Arm", j+side+"Hand"
    hd = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVx")[0]
    cmds.setAttr(pv+".translate", *pole)
    cmds.poleVectorConstraint(pv, hd)
    cmds.move(tgt[0], tgt[1], tgt[2], hd, absolute=True)
    chain, cur = [], ee
    while cur and cur != sj:
        chain.append(cur); p = cmds.listRelatives(cur, parent=True); cur = p[0] if p else None
    chain.append(sj)
    vals = {b: list(cmds.getAttr(b+".rotate")[0]) for b in chain}
    cmds.delete(hd); cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b+".rotate", *v)

def shoot(tag, cam, f=1, w=854, h=480):
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(f); cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("FF_"+tag+"."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV,"FF_"+tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w,h), quality=95,
                   compression="png")
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    for c in (cmds.ls(type="camera") or []):
        try:
            cmds.setAttr(c+".nearClipPlane", 5.0); cmds.setAttr(c+".farClipPlane", 2200.0)
        except Exception: pass

    res = {}
    for key,(grp,j,mesh) in CH.items():
        gx, gy, gz = cmds.getAttr(grp+".translate")[0]
        ang = math.radians(cmds.getAttr(grp+".rotateY"))
        fwd = (math.sin(ang), math.cos(ang)); right = (math.cos(ang), -math.sin(ang))
        rec = {}
        for side, s in (("Left",1), ("Right",-1)):
            tgt = (gx+fwd[0]*25+right[0]*19*s, TABLE+3.0, gz+fwd[1]*25+right[1]*19*s)
            pole = (gx+fwd[0]*2+right[0]*95*s, TABLE-16, gz+fwd[1]*2+right[1]*95*s)
            ik_arm(j, side, tgt, pole)
            got = cmds.xform(j+side+"Hand", q=True, ws=True, t=True)
            rec[side] = round(sum((got[i]-tgt[i])**2 for i in range(3))**0.5, 1)
        cmds.refresh(force=True)
        rec["height"] = hh(mesh)
        res[key] = rec
    OUT["pose"] = res
    dump()
    # 轻量 Delta Mush（pin=1，3 次迭代）
    for key,(grp,j,mesh) in CH.items():
        try:
            cmds.deltaMush(mesh, smoothingIterations=3, smoothingStep=0.4,
                           pinBorderVertices=1, envelope=1.0)
        except Exception as e:
            OUT.setdefault("dm_err", {})[key] = repr(e)[:100]
    cmds.refresh(force=True)
    OUT["heights_after_mush"] = {k: hh(v[2]) for k,v in CH.items()}
    dump()
    for tag, cam, f in (("S001","S001_CAM1",30), ("S002","S002_CAM1",80), ("S045","S045_CAM1",2340)):
        shoot(tag, cam, f)
    shoot("front", "OV_front1", 1, 900, 560)
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v7.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
