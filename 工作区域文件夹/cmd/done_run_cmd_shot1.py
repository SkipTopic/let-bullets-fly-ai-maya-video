import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    made = []
    for cam, tag, f in (("S001_CAM1", "SHOT_Ma", 30),
                        ("S002_CAM1", "SHOT_Huang", 80),
                        ("S045_CAM1", "SHOT_Shiye", 2340)):
        if not cmds.objExists(cam):
            OUT.setdefault("missing", []).append(cam); continue
        cmds.currentTime(f)
        cmds.lookThru(p, cam)
        for old in os.listdir(REV):
            if old.startswith(tag + "."):
                try: os.remove(os.path.join(REV, old))
                except Exception: pass
        cmds.playblast(frame=f, format="image", filename=os.path.join(REV, tag),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
        made.append(tag)
    OUT["made"] = made
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r15.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
