import maya.cmds as cmds
import json, os, time, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
CHK = os.path.join(ROOT, "_接手检查")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "v6_cams.mb"), o=True, force=True)
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, camera="CAMX001X1", displayLights="default",
                     displayAppearance="smoothShaded", wireframeOnShaded=False)
    cmds.currentTime(4)
    cmds.refresh(force=True)
    time.sleep(0.5)

    # A) 离屏 playblast
    base = os.path.join(CHK, "s15_off")
    for f in os.listdir(CHK):
        if f.startswith("s15_off"):
            os.remove(os.path.join(CHK, f))
    t0 = time.time()
    cmds.playblast(frame=4, format="image", filename=base, sequenceTime=0,
                   clearCache=1, viewer=0, showOrnaments=0, offScreen=True,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100,
                   compression="png")
    OUT["off_time"] = round(time.time() - t0, 2)
    OUT["off_files"] = [f for f in os.listdir(CHK) if f.startswith("s15_off")]

    # B) 硬件渲染
    cmds.setAttr("defaultRenderGlobals.renopt_hwRender", 1) if cmds.objExists("defaultRenderGlobals.renopt_hwRender") else None
    t0 = time.time()
    try:
        img = cmds.render("CAMX001X1", x=854, y=480)
        OUT["hw"] = img
    except Exception as e:
        OUT["hw_err"] = repr(e)
    OUT["hw_time"] = round(time.time() - t0, 2)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e)); OUT["trace"] = traceback.format_exc()
json.dump(OUT, open(os.path.join(ROOT,"logs","s15.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
