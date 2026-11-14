import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
def shoot(tag, cam, w=900, h=560):
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
        if old.startswith("CLIP_" + tag + "."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=1, format="image", filename=os.path.join(REV, "CLIP_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w, h), quality=95,
                   compression="png")
    return tag
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), o=True, force=True)
    cams = [c for c in (cmds.ls(type="camera") or [])]
    OUT["cam_count"] = len(cams)
    for c in cams:
        try:
            cmds.setAttr(c + ".nearClipPlane", 5.0)
            cmds.setAttr(c + ".farClipPlane", 2200.0)
        except Exception:
            pass
    OUT["before"] = shoot("before", "OV_front1")
    # 再把假阴影盘删掉、确认
    for x in ("SET_contact_shadow",):
        if cmds.objExists(x):
            cmds.delete(x)
            OUT["deleted"] = x
    OUT["after"] = shoot("after", "OV_front1")
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z3.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
