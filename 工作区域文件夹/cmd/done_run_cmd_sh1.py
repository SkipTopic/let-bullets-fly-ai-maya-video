import maya.cmds as cmds
import json, os, shutil, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v8_outdoor.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    cam = cmap["S001"]
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaHardware2", type="string")
    cmds.setAttr("LGT_sun.useDepthMapShadows", 0)
    cmds.modelEditor(p, e=True, camera=cam, displayLights="all")
    for inten, tag in ((0.5, "S_off_low"), (6.0, "S_off_high")):
        cmds.setAttr("LGT_sun.intensity", inten)
        cmds.currentTime(30)
        cmds.refresh(force=True)
        img = cmds.render(cam, x=854, y=480)
        shutil.copyfile(img, os.path.join(ROOT, "_审片", tag + ".png"))
    OUT["shadow"] = cmds.getAttr("LGT_sun.useDepthMapShadows")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r4.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
