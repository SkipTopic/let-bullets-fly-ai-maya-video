import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
def shoot(tag, cam, f=1):
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(f)
    cmds.lookThru(p, cam)
    for old in os.listdir(REV):
        if old.startswith("PB_" + tag + "."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "PB_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=95,
                   compression="png")
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v5_final.mb"), o=True, force=True)
    FACTOR = 1.55
    moved = 0
    cams = [c for c in (cmds.listRelatives("CAMERAS", children=True) or [])]
    for cam in cams:
        t = cmds.getAttr(cam + ".translate")[0]
        cmds.setAttr(cam + ".translate", t[0] * FACTOR, t[1], t[2] * FACTOR)
        moved += 1
    OUT["moved"] = moved
    for cam in cams:
        for ax in ("translateX", "translateZ"):
            keys = cmds.keyframe(cam, attribute=ax, q=True)
            if keys:
                vals = cmds.keyframe(cam, attribute=ax, q=True, valueChange=True)
                times = cmds.keyframe(cam, attribute=ax, q=True)
                for t, v in zip(times, vals):
                    cmds.keyframe(cam, attribute=ax, time=(t, t), value=v * FACTOR)
    shoot("S001", "S001_CAM1", 30)
    shoot("S002", "S002_CAM1", 80)
    shoot("S045", "S045_CAM1", 2340)
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v6.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z7.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
