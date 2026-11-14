import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    REV = os.path.join(ROOT, "_审片")
    for cam, name in (("S001_CAM1", "FINAL_Ma"), ("S045_CAM45", "FINAL_Shiye")):
        if not cmds.objExists(cam):
            OUT.setdefault("missing", []).append(cam)
            continue
        cmds.currentTime(30)
        cmds.lookThru(p, cam)
        for old in os.listdir(REV):
            if old.startswith(name + "."):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=30, format="image", filename=os.path.join(REV, name),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r11.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
