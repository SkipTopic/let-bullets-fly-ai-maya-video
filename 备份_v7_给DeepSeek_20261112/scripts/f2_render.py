import maya.cmds as cmds
import json, os, sys, shutil, time, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
JOB = os.path.join(ROOT, "logs", "render_job.json")
OUT = {"errors": []}
a, b = 0, 0

def main():
    global a, b
    job = json.load(open(JOB, encoding="utf-8"))
    a, b = job["start"], job["end"]
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    cmds.file(os.path.join(ROOT, "scenes", "v7_final.mb"), o=True, force=True)
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, displayLights="all", displayAppearance="smoothShaded",
                     wireframeOnShaded=False, grid=False, joints=False, headsUpDisplay=False)
    for attr in ("hardwareRenderingGlobals.multiSampleEnable",
                 "hardwareRenderingGlobals.ssaoEnable",
                 "hardwareRenderingGlobals.floatingPointRTEnable",
                 "hardwareRenderingGlobals.lineAAEnable"):
        try:
            cmds.setAttr(attr, 0)
        except Exception:
            pass
    os.makedirs(os.path.join(ROOT, "frames"), exist_ok=True)
    t0 = time.time()
    last_cam = None
    done = 0
    for f in range(a, b + 1):
        s = next((x for x in shots if x["start"] <= f <= x["end"]), shots[0])
        cam = cmap[s["id"]]
        if cam != last_cam:
            cmds.modelEditor(p, e=True, camera=cam)
            last_cam = cam
        cmds.currentTime(f)
        img = cmds.render(cam, x=854, y=480)
        dst = os.path.join(ROOT, "frames", "%04d.png" % f)
        shutil.copyfile(img, dst)
        done += 1
    OUT["rendered"] = done
    OUT["seconds"] = round(time.time() - t0, 1)
    OUT["per_frame"] = round((time.time() - t0) / max(done, 1), 2)

try:
    main()
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT, "logs", "f2_%d_%d.json" % (a, b)), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
