import maya.cmds as cmds
import json, os, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "f14_mush_all.json")
OUT = {"step": "start", "errors": []}
TABLE = 75.75


def dump():
    json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def shoot(tag, eye, aim, focal=90, w=760, h=560):
    cam = cmds.camera(name="MV_" + tag, focalLength=focal)[0]
    cmds.setAttr(cam + ".translate", *eye)
    loc = cmds.spaceLocator(name="MVLOC")[0]
    cmds.setAttr(loc + ".translate", *aim)
    k = cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
    m = cmds.xform(cam, q=True, ws=True, m=True)
    cmds.delete(k)
    cmds.delete(loc)
    cmds.xform(cam, ws=True, m=m)
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(1)
    cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("MV_" + tag + "."):
            try:
                os.remove(os.path.join(REV, old))
            except Exception:
                pass
    cmds.playblast(frame=1, format="image", filename=os.path.join(REV, "MV_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w, h), quality=95,
                   compression="png")
    cmds.delete(cam)
    return tag


def put_hand(j, side, target, pole):
    sj, ee = j + side + "Arm", j + side + "Hand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PVm")[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    chain, cur = [ee], ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
        if cur:
            chain.append(cur)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain}
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)
    cmds.refresh(force=True)
    return list(cmds.xform(ee, q=True, ws=True, t=True))


CHARS = {"Ma": ("CHR_Ma", "Ma_", "Ma_MakotoFBXASC032Yuki_mesh"),
         "Huang": ("CHR_Huang", "Huang_", "Huang_AragakiFBXASC032Shinjiro_mesh"),
         "Shiye": ("CHR_Shiye", "Shiye_", "Shiye_JunpeiFBXASC032Iori_mesh")}

try:
    OUT["step"] = "open"; dump()
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)

    OUT["step"] = "deltaMush"; dump()
    for key, (grp, j, mesh) in CHARS.items():
        try:
            if not cmds.objExists("dm_" + key):
                n = cmds.deltaMush(mesh, smoothingIterations=8, smoothingStep=0.5,
                                   pinBorderVertices=0, envelope=1.0)
                try:
                    cmds.rename(n[0], "dm_" + key)
                except Exception:
                    pass
                OUT.setdefault("dm", {})[key] = "ok"
        except Exception as e:
            OUT.setdefault("dm_err", {})[key] = repr(e)[:120]
    dump()

    OUT["step"] = "pose"; dump()
    for key, (grp, j, mesh) in CHARS.items():
        gx, gy, gz = cmds.getAttr(grp + ".translate")[0]
        ang = math.radians(cmds.getAttr(grp + ".rotateY"))
        fwd = (math.sin(ang), math.cos(ang))
        right = (math.cos(ang), -math.sin(ang))
        rec = {}
        for side, s in (("Left", 1), ("Right", -1)):
            tgt = (gx + fwd[0] * 25 + right[0] * 19 * s, TABLE + 3.0,
                   gz + fwd[1] * 25 + right[1] * 19 * s)
            pole = (gx + fwd[0] * 2 + right[0] * 95 * s, TABLE - 16,
                    gz + fwd[1] * 2 + right[1] * 95 * s)
            got = put_hand(j, side, tgt, pole)
            rec[side] = {"err": round(sum((got[i] - tgt[i]) ** 2 for i in range(3)) ** 0.5, 1),
                         "got": [round(v, 1) for v in got]}
        OUT.setdefault("pose", {})[key] = rec
    dump()

    OUT["step"] = "render"; dump()
    OUT["front"] = shoot("front", (0, 175, 300), (0, 78, -30), 45, 900, 560)
    cmds.currentTime(30)
    OUT["ma"] = shoot("ma", (52, 96, -58), (8, 84, -92), 85, 760, 560)
    OUT["step"] = "done"; OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
