import maya.cmds as cmds
import json, os, sys, importlib, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path: sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v6_cams.mb"), o=True, force=True)
    OUT["panels"] = cmds.getPanel(type="modelPanel")
    cmds.setAttr("CAMX001X1.focalLength", 85)
    p = OUT["panels"][0]
    cmds.modelEditor(p, e=True, camera="CAMX001X1")
    OUT["now_cam"] = cmds.modelEditor(p, q=True, camera=True)
    L.setup_viewport()
    cmds.modelEditor(p, e=True, camera="CAMX001X1", displayLights="default",
                     displayAppearance="smoothShaded")
    OUT["now_cam2"] = cmds.modelEditor(p, q=True, camera=True)
    OUT["lights_mode"] = cmds.modelEditor(p, q=True, displayLights=True)
    cmds.currentTime(3); cmds.refresh(force=True)
    OUT["a"] = L.render_to(os.path.join(ROOT,"_接手检查","s14_a.png"))
    cmds.modelEditor(p, e=True, camera="persp")
    cmds.refresh(force=True)
    OUT["b"] = L.render_to(os.path.join(ROOT,"_接手检查","s14_b.png"))
    OUT["persp_cam"] = cmds.modelEditor(p, q=True, camera=True)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","s14.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
