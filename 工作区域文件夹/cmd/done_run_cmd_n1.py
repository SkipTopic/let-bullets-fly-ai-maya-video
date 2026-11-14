import maya.cmds as cmds
import json, os, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "n1.json")
OUT = {"errors": []}
TABLE = 75.75
SEAT_R = 102.0
SEAT_Y = 46.5


def dump():
    json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def ik_bake(sj, ee, target, pole=None):
    hd = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = None
    if pole:
        pv = cmds.spaceLocator(name="PVn")[0]
        cmds.setAttr(pv + ".translate", *pole)
        cmds.poleVectorConstraint(pv, hd)
    cmds.move(target[0], target[1], target[2], hd, absolute=True)
    chain, cur = [], ee
    while cur and cur != sj:
        chain.append(cur)
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
    chain.append(sj)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain}
    cmds.delete(hd)
    if pv:
        cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    cmds.refresh(force=True)


def shoot(tag, cam, f=1, w=800, h=600):
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(f)
    cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("NEW_" + tag + "."):
            try:
                os.remove(os.path.join(REV, old))
            except Exception:
                pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "NEW_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w, h), quality=95,
                   compression="png")


try:
    OUT["step"] = "open"; dump()
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)

    # 1) 删掉旧的马县长
    OUT["step"] = "purge_old"; dump()
    old = [x for x in (cmds.listRelatives("CHARS", children=True) or []) if "Ma_" in x]
    old += ["CHR_Ma"] if cmds.objExists("CHR_Ma") else []
    if old:
        try:
            cmds.delete(old)
        except Exception as e:
            OUT["purge_err"] = repr(e)[:120]
    OUT["left_in_chars"] = cmds.listRelatives("CHARS", children=True) or []

    # 2) 导入新模型 + 删表情
    OUT["step"] = "import"; dump()
    fbx = os.path.join(ROOT, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")
    cmds.file(fbx, i=True, ignoreVersion=True, namespace="MA")
    meshes = [m for m in (cmds.ls(type="mesh") or []) if not cmds.getAttr(m + ".intermediateObject")]
    base = None
    for m in meshes:
        if cmds.listConnections(m, type="skinCluster"):
            base = m
            break
    OUT["base_mesh"] = base
    bss = cmds.ls(type="blendShape") or []
    if bss:
        try:
            cmds.delete(bss)
        except Exception:
            pass
    kill = []
    for m in meshes:
        if m == base:
            continue
        p = cmds.listRelatives(m, parent=True)
        if p:
            kill.append(p[0])
    kill = list(dict.fromkeys(kill))
    if kill:
        try:
            cmds.delete(kill)
        except Exception:
            pass
    OUT["meshes_left"] = len([x for x in (cmds.ls(type="mesh") or [])
                              if not cmds.getAttr(x + ".intermediateObject")])
    dump()

    # 3) 摆坐姿
    OUT["step"] = "pose_legs"; dump()
    hip = cmds.xform("Bip001LThigh", q=True, ws=True, t=True)
    for s, sgn in (("L", 1), ("R", -1)):
        thigh = "Bip001%sThigh" % s
        calf = "Bip001%sCalf" % s
        foot = "Bip001%sFoot" % s
        hpos = cmds.xform(thigh, q=True, ws=True, t=True)
        ik_bake(thigh, calf, (hpos[0], hpos[1] + 2, hpos[2] + 36),
                pole=(hpos[0] + 30 * sgn, hpos[1] + 30, hpos[2] + 18))
        kpos = cmds.xform(calf, q=True, ws=True, t=True)
        ik_bake(calf, foot, (kpos[0], 8.0, kpos[2] + 14),
                pole=(kpos[0] + 20 * sgn, kpos[1] - 20, kpos[2] + 30))

    # 4) 坐到位：髋骨落到椅面高度
    OUT["step"] = "seat"; dump()
    pelvis_y = cmds.xform("Bip001Pelvis", q=True, ws=True, t=True)[1]
    dz = SEAT_Y - pelvis_y
    root_tr = cmds.listRelatives(cmds.ls(type="joint")[0], parent=True)
    OUT["root"] = root_tr
    for r in (root_tr or []):
        cmds.setAttr(r + ".translateY", cmds.getAttr(r + ".translateY") + dz)
    cmds.refresh(force=True)
    OUT["pelvis_after"] = round(cmds.xform("Bip001Pelvis", q=True, ws=True, t=True)[1], 1)

    # 5) 转到马县长的位置
    ang = 270.0
    gx = math.cos(math.radians(ang)) * SEAT_R
    gz = math.sin(math.radians(ang)) * SEAT_R
    grp = cmds.group(em=True, name="CHR_Ma")
    root_tr = (cmds.listRelatives(cmds.ls(type="joint")[0], parent=True) or [None])[0]
    if root_tr:
        cmds.parent(root_tr, grp)
    cmds.parent(grp, "CHARS")
    cmds.setAttr(grp + ".translate", gx, 0, gz)
    cmds.setAttr(grp + ".rotateY", 0)
    # 网格跟随骨架，保持原地级别
    if base:
        mt = cmds.listRelatives(base, parent=True)[0]
        cmds.parent(mt, "CHARS")
    cmds.refresh(force=True)
    OUT["ma_head"] = [round(v, 1) for v in cmds.xform("Bip001Head", q=True, ws=True, t=True)]
    dump()

    # 6) 手放桌面
    OUT["step"] = "pose_arms"; dump()
    ang_r = math.radians(270.0)
    fwd = (math.sin(ang_r), math.cos(ang_r))
    right = (math.cos(ang_r), -math.sin(ang_r))
    errs = {}
    for s, sgn in (("L", 1), ("R", -1)):
        tgt = (gx + fwd[0] * 24 + right[0] * 20 * sgn, TABLE + 4.0,
               gz + fwd[1] * 24 + right[1] * 20 * sgn)
        pole = (gx + fwd[0] * 2 + right[0] * 90 * sgn, TABLE - 10,
                gz + fwd[1] * 2 + right[1] * 90 * sgn)
        ik_bake("Bip001%sUpperArm" % s, "Bip001%sHand" % s, tgt, pole)
        got = cmds.xform("Bip001%sHand" % s, q=True, ws=True, t=True)
        errs[s] = round(sum((got[i] - tgt[i]) ** 2 for i in range(3)) ** 0.5, 1)
    OUT["arm_err"] = errs
    OUT["head_after"] = [round(v, 1) for v in cmds.xform("Bip001Head", q=True, ws=True, t=True)]
    OUT["mesh_bb"] = [round(v, 0) for v in cmds.xform(base, q=True, ws=True, bb=True)]
    dump()

    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v9_newma.mb"), f=True,
              type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
