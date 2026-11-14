import maya.cmds as cmds
import json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
LOG = os.path.join(ROOT, "logs", "d3.json")
OUT = {"step": "start", "errors": []}
def dump():
    json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def shoot(tag, eye, aim, focal=90):
    cam = cmds.camera(name="DC_" + tag, focalLength=focal)[0]
    cmds.setAttr(cam + ".translate", *eye)
    dx, dy, dz = aim[0]-eye[0], aim[1]-eye[1], aim[2]-eye[2]
    horiz = math.sqrt(dx*dx + dz*dz)
    cmds.setAttr(cam + ".rotate", -math.degrees(math.atan2(dy, horiz)),
                 math.degrees(math.atan2(dx, dz)) + 180.0, 0)
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
        if old.startswith("DC_" + tag + "."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=1, format="image", filename=os.path.join(REV, "DC_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(700, 520), quality=95,
                   compression="png")
    cmds.delete(cam)
try:
    OUT["step"] = "open"; dump()
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    # 删掉另外两个人，省内存
    for x in ("CHR_Huang", "CHR_Shiye", "Huang_AragakiFBXASC032Shinjiro_mesh",
              "Shiye_JunpeiFBXASC032Iori_mesh", "HIDDEN_HELPERS"):
        if cmds.objExists(x):
            try: cmds.delete(x)
            except Exception: pass
    OUT["step"] = "posed"; dump()
    j = "Ma_"
    cmds.setAttr(j + "LeftArm.rotate", -30.8, 33.1, -20.2)
    cmds.setAttr(j + "LeftForeArm.rotate", -66.1, -6.2, 66.3)
    cmds.refresh(force=True)
    OUT["hand"] = [round(v,1) for v in cmds.xform(j+"LeftHand", q=True, ws=True, t=True)]
    OUT["A"] = shoot("A", (62, 96, -52), (12, 84, -95)); dump()
    OUT["step"] = "mush"; dump()
    dm = cmds.deltaMush("Ma_MakotoFBXASC032Yuki_mesh", smoothingIterations=6,
                        smoothingStep=0.5, pinBorderVertices=0, envelope=1.0)
    OUT["dm"] = dm; dump()
    cmds.refresh(force=True)
    OUT["B"] = shoot("B", (62, 96, -52), (12, 84, -95))
    OUT["step"] = "done"; OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
