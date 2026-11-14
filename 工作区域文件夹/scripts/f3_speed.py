import maya.cmds as cmds
import json, os, time, shutil, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v7_final.mb"), o=True, force=True)
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    p = cmds.getPanel(type="modelPanel")[0]
    for a in ("hardwareRenderingGlobals.multiSampleEnable",
              "hardwareRenderingGlobals.shadowMapEnable",
              "hardwareRenderingGlobals.ssaoEnable",
              "hardwareRenderingGlobals.floatingPointRTEnable",
              "hardwareRenderingGlobals.lineAAEnable"):
        try:
            cmds.setAttr(a, 0)
        except Exception as e:
            OUT.setdefault("attr_err", []).append(a)
    OUT["aa"] = cmds.getAttr("hardwareRenderingGlobals.multiSampleEnable")
    s = shots[0]
    cam = cmap[s["id"]]
    cmds.modelEditor(p, e=True, camera=cam, displayLights="default")
    t0 = time.time()
    for i in range(12):
        cmds.currentTime(s["start"] + i)
        img = cmds.render(cam, x=854, y=480)
    OUT["no_aa_per_frame"] = round((time.time() - t0) / 12, 2)
    OUT["last"] = img
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","f3_speed.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
