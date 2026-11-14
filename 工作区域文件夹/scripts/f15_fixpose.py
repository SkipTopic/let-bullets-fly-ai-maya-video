import maya.cmds as cmds, json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "f15.json")
OUT = {"errors": []}
TABLE = 75.75
CHARS = {"Ma": ("CHR_Ma", "Ma_", "Ma_MakotoFBXASC032Yuki_mesh"),
         "Huang": ("CHR_Huang", "Huang_", "Huang_AragakiFBXASC032Shinjiro_mesh"),
         "Shiye": ("CHR_Shiye", "Shiye_", "Shiye_JunpeiFBXASC032Iori_mesh")}
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)

def put_hand(j, side, target, pole):
    sj, ee = j + side + "Arm", j + side + "Hand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVf")[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    chain, cur = [ee], ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True); cur = p[0] if p else None
        if cur: chain.append(cur)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain}
    cmds.delete(h); cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    # 扭转变形骨清零，避免个别顶点被甩飞
    for b in (side + "ArmTwist", side + "HandTwist"):
        if cmds.objExists(j + b):
            cmds.setAttr(j + b + ".rotate", 0, 0, 0)
    cmds.refresh(force=True)
    return list(cmds.xform(ee, q=True, ws=True, t=True))

try:
    OUT["step"]="open"; dump()
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), o=True, force=True)
    res = {}
    for key,(grp,j,mesh) in CHARS.items():
        gx,gy,gz = cmds.getAttr(grp+".translate")[0]
        ang = math.radians(cmds.getAttr(grp+".rotateY"))
        fwd = (math.sin(ang), math.cos(ang)); right = (math.cos(ang), -math.sin(ang))
        rec = {}
        for side,s in (("Left",1),("Right",-1)):
            tgt = (gx+fwd[0]*25+right[0]*19*s, TABLE+3.0, gz+fwd[1]*25+right[1]*19*s)
            pole = (gx+fwd[0]*2+right[0]*95*s, TABLE-16, gz+fwd[1]*2+right[1]*95*s)
            got = put_hand(j, side, tgt, pole)
            rec[side] = round(sum((got[i]-tgt[i])**2 for i in range(3))**0.5, 1)
        bb = cmds.xform(mesh, q=True, ws=True, bb=True)
        rec["bbox_y"] = [round(bb[1],0), round(bb[4],0)]
        rec["height"] = round(bb[4]-bb[1], 0)
        res[key] = rec
    OUT["pose"]=res
    OUT["step"]="saved"
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v4.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"]=True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
