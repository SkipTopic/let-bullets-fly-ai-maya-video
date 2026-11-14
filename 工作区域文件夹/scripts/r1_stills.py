import maya.cmds as cmds
import json, os, shutil, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
os.makedirs(REV, exist_ok=True)
LOG = os.path.join(ROOT, "logs", "r1_stills.json")
OUT = {"errors": []}

PICKS = [
    ("S001", 30, "马县长近景"),
    ("S032", 1650, "马县长近景2"),
    ("S033", 1718, "黄四郎近景"),
    ("S045", 2327, "师爷近景"),
    ("S019", 899, "师爷中景"),
    ("S049", 2471, "黄四郎中景"),
]

try:
    cmds.file(os.path.join(ROOT, "scenes", "v7_final.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
    p = cmds.getPanel(type="modelPanel")[0]
    for attr in ("hardwareRenderingGlobals.multiSampleEnable",
                 "hardwareRenderingGlobals.lineAAEnable"):
        try:
            cmds.setAttr(attr, 1)
        except Exception:
            pass
    for attr in ("hardwareRenderingGlobals.ssaoEnable",
                 "hardwareRenderingGlobals.floatingPointRTEnable"):
        try:
            cmds.setAttr(attr, 0)
        except Exception:
            pass

    made = []
    for sid, f, label in PICKS:
        cam = cmap[sid]
        cmds.modelEditor(p, e=True, camera=cam, displayLights="default",
                         displayAppearance="smoothShaded", wireframeOnShaded=False,
                         grid=False, joints=False, headsUpDisplay=False)
        cmds.currentTime(f)
        cmds.refresh(force=True)
        img = cmds.render(cam, x=854, y=480)
        dst = os.path.join(REV, "%s_%s.png" % (sid, label))
        shutil.copyfile(img, dst)
        made.append(dst)
        OUT.setdefault("each", []).append({"shot": sid, "frame": f, "png": dst})
    OUT["made"] = len(made)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
