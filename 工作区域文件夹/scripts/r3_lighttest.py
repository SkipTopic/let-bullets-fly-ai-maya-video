import maya.cmds as cmds
import json, os, shutil
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v8_outdoor.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    cam = cmap["S001"]
    p = cmds.getPanel(type="modelPanel")[0]
    try:
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaHardware2", type="string")
    except Exception as e:
        OUT["renderer_err"] = repr(e)
    OUT["renderer"] = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    cmds.setAttr("LGT_sun.intensity", 1.0)
    cmds.modelEditor(p, e=True, camera=cam, displayLights="all")
    cmds.currentTime(30); cmds.refresh(force=True)
    a = cmds.render(cam, x=854, y=480)
    shutil.copyfile(a, os.path.join(ROOT, "_审片", "LT_low.png"))
    cmds.setAttr("LGT_sun.intensity", 12.0)
    cmds.refresh(force=True)
    b = cmds.render(cam, x=854, y=480)
    shutil.copyfile(b, os.path.join(ROOT, "_审片", "LT_high.png"))
    OUT["lights"] = cmds.ls(type="directionalLight")
    OUT["renderers"] = cmds.renderer(q=True, list=True) if hasattr(cmds,"renderer") else None
    OUT["ok"] = True
except Exception:
    import traceback; OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r3.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
