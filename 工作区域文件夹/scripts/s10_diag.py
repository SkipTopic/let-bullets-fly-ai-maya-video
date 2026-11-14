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
    OUT["meshes"] = len(cmds.ls(type="mesh") or [])
    OUT["cams"] = len(cmds.ls("CAM_*", type="transform") or [])
    OUT["lights"] = cmds.ls(type="directionalLight") or []
    cam = "CAM_S001"
    OUT["cam_pos"] = [round(v,1) for v in cmds.getAttr(cam + ".translate")[0]]
    OUT["cam_rot"] = [round(v,1) for v in cmds.getAttr(cam + ".rotate")[0]]
    OUT["cam_focal"] = cmds.getAttr(cam + ".focalLength")
    # 广角看同一位置
    cmds.setAttr(cam + ".focalLength", 18)
    L.setup_viewport()
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, camera=cam, displayLights="default")
    cmds.currentTime(3)
    cmds.refresh(force=True)
    OUT["wide"] = L.render_to(os.path.join(ROOT, "_接手检查", "s10_wide.png"))
    # persp
    cmds.modelEditor(p, e=True, camera="persp")
    cmds.refresh(force=True)
    OUT["persp"] = L.render_to(os.path.join(ROOT, "_接手检查", "s10_persp.png"))
    # 场景里所有东西的世界包围盒
    OUT["bbox_all"] = [round(v,1) for v in cmds.exactWorldBoundingBox(cmds.ls(type="mesh"))]
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","s10.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
