import maya.cmds as cmds
import json, os, sys, importlib, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path: sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}

def shoot(cam, path, frame):
    L.setup_viewport()
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, camera=cam, displayLights="default")
    cmds.currentTime(frame)
    cmds.refresh(force=True)
    return L.render_to(path)

try:
    cmds.file(os.path.join(ROOT, "scenes", "v6_cams.mb"), o=True, force=True)
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    by = {s["id"]: s for s in shots}
    for tid in ("S001", "S020", "S045", "S060"):
        s = by[tid]
        OUT[tid] = shoot(cmap[tid], os.path.join(ROOT, "_接手检查", "s9_" + tid + ".png"),
                         s["start"] + 2)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","s9.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
