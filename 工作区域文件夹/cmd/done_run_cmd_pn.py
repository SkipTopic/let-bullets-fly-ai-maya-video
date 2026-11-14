import maya.cmds as cmds
import json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v9_classic.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    panels = cmds.getPanel(type="modelPanel")
    OUT["panels"] = panels
    OUT["visible"] = {p: cmds.control(p, q=True, visible=True) for p in panels}
    for p in panels:
        try:
            cmds.modelEditor(p, e=True, displayLights="default",
                             displayAppearance="smoothShaded", wireframeOnShaded=False,
                             grid=False, joints=False, cameras=False, locators=False,
                             headsUpDisplay=False)
            cmds.currentTime(30)
            cmds.lookThru(p, cmap["S001"])
            base = os.path.join(REV, "PN_%s" % p)
            for old in os.listdir(REV):
                if old.startswith("PN_%s." % p):
                    os.remove(os.path.join(REV, old))
            cmds.playblast(frame=30, format="image", filename=base, sequenceTime=False,
                           clearCache=True, viewer=False, showOrnaments=False,
                           offScreen=True, percent=100, widthHeight=(640, 360),
                           quality=90, compression="png")
            fs = [x for x in os.listdir(REV) if x.startswith("PN_%s." % p)]
            OUT[p] = fs
        except Exception as e:
            OUT[p] = repr(e)[:120]
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r6.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
