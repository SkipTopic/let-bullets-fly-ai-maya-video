import maya.cmds as cmds
import json, os, glob, shutil, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
RAWS = os.path.join(ROOT, "frames_raw")
FINAL = os.path.join(ROOT, "frames_all")
OUT = {"errors": [], "log": []}

try:
    cmds.file(os.path.join(ROOT, "scenes", "v10_prod.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))

    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)

    os.makedirs(RAWS, exist_ok=True)
    os.makedirs(FINAL, exist_ok=True)

    # 预热一帧，避免首帧黑屏
    cmds.currentTime(shots[0]["start"])
    cmds.lookThru(p, cmap[shots[0]["id"]])
    cmds.playblast(frame=shots[0]["start"], format="image",
                   filename=os.path.join(ROOT, "_审片", "warmup"),
                   sequenceTime=False, clearCache=True, viewer=False,
                   showOrnaments=False, offScreen=True, percent=100,
                   widthHeight=(854, 480), quality=90, compression="png")

    for i, s in enumerate(shots):
        cmds.lookThru(p, cmap[s["id"]])
        cmds.playblast(startTime=s["start"], endTime=s["end"], format="image",
                       filename=os.path.join(RAWS, s["id"]),
                       sequenceTime=False, clearCache=True, viewer=False,
                       showOrnaments=False, offScreen=True, percent=100,
                       widthHeight=(854, 480), quality=90, compression="png")
        OUT["log"].append("%s %d-%d" % (s["id"], s["start"], s["end"]))
        if i % 10 == 0:
            json.dump(OUT, open(os.path.join(ROOT, "logs", "render_progress.json"), "w",
                                encoding="utf-8"), ensure_ascii=False)

    # 重命名为连续帧号
    files = []
    for s in shots:
        fs = sorted(glob.glob(os.path.join(RAWS, s["id"] + ".*.png")))
        files += fs
    OUT["raw_count"] = len(files)
    files = files[:3512]
    for idx, f in enumerate(files, start=1):
        dst = os.path.join(FINAL, "%04d.png" % idx)
        shutil.copyfile(f, dst)
    OUT["final_count"] = len(files)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "f8_render.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
