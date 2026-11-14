import maya.cmds as cmds
import json, os, sys, importlib, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path: sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}
try:
    cam = "CAMX001X"
    OUT["pos"] = [round(v,1) for v in cmds.getAttr(cam+".translate")[0]]
    OUT["rot"] = [round(v,1) for v in cmds.getAttr(cam+".rotate")[0]]
    OUT["focal"] = cmds.getAttr(cam+".focalLength")
    # 相机世界矩阵的前方向
    m = cmds.xform(cam, q=True, ws=True, matrix=True)
    OUT["matrix"] = [round(v,3) for v in m]
    L.setup_viewport()
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.setAttr(cam+".focalLength", 20)
    cmds.modelEditor(p, e=True, camera=cam, displayLights="default")
    cmds.currentTime(3); cmds.refresh(force=True)
    OUT["wide"] = L.render_to(os.path.join(ROOT,"_接手检查","s12_wide.png"))
    cmds.modelEditor(p, e=True, camera="persp")
    cmds.refresh(force=True)
    OUT["persp"] = L.render_to(os.path.join(ROOT,"_接手检查","s12_persp.png"))
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","s12.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
