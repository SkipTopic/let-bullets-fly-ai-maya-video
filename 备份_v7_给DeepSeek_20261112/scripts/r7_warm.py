import maya.cmds as cmds
import json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    for tag in ("warm", "real"):
        cmds.currentTime(30)
        cmds.lookThru(p, cmap["S001"])
        for old in os.listdir(REV):
            if old.startswith("W_%s." % tag):
                os.remove(os.path.join(REV, old))
        cmds.playblast(frame=30, format="image", filename=os.path.join(REV, "W_" + tag),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=95, compression="png")
    OUT["cam"] = cmap["S001"]
    OUT["pos"] = [round(v, 1) for v in cmds.getAttr(cmap["S001"] + ".translate")[0]]
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r7.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
