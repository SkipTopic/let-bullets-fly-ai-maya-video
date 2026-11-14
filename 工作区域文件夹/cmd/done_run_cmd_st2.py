import maya.cmds as cmds
import json, os, shutil, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
os.makedirs(REV, exist_ok=True)
LOG = os.path.join(ROOT, "logs", "r2_stills.json")
OUT = {"errors": []}

PICKS = [
    ("S001", 30, "S001_马县长近景"),
    ("S033", 1718, "S033_黄四郎近景"),
    ("S045", 2327, "S045_师爷近景"),
    ("S019", 899, "S019_师爷中景"),
]


def render(cam, frame, name):
    p = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(p, e=True, camera=cam, displayLights="default",
                     displayAppearance="smoothShaded", wireframeOnShaded=False,
                     grid=False, joints=False, headsUpDisplay=False)
    cmds.currentTime(frame)
    cmds.refresh(force=True)
    img = cmds.render(cam, x=854, y=480)
    dst = os.path.join(REV, name + ".png")
    shutil.copyfile(img, dst)
    return dst


try:
    cmds.file(os.path.join(ROOT, "scenes", "v8_outdoor.mb"), o=True, force=True)
    cmap = json.load(open(os.path.join(ROOT, "logs", "cam_map.json"), encoding="utf-8"))
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
    for sid, f, name in PICKS:
        made.append(render(cmap[sid], f, name))

    # 全景：看整个场景和房子
    wc = cmds.camera(name="CAM_WIDE", focalLength=28)[0]
    cmds.setAttr(wc + ".translate", 0, 210, 430)
    loc = cmds.spaceLocator()[0]
    cmds.setAttr(loc + ".translate", 0, 90, -120)
    cmds.aimConstraint(loc, wc, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                       worldUpType="vector", worldUpVector=(0, 1, 0))
    cmds.delete(loc)
    made.append(render(wc, 30, "WIDE_全景"))

    OUT["made"] = made
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
