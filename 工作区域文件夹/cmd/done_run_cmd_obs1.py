import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    ovs = [c for c in (cmds.ls(type="camera") or []) if c.startswith("OV_")]
    OUT["ov_shapes"] = ovs
    trs = {}
    for s in ovs:
        p = cmds.listRelatives(s, parent=True)
        if p:
            trs[p[0]] = s
    OUT["ov_transforms"] = list(trs.keys())
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    made = []
    for tr in trs:
        cmds.currentTime(1)
        cmds.lookThru(p, tr)
        tgt = os.path.join(REV, tr)
        for old in os.listdir(REV):
            if old.startswith(tr + "."):
                try: os.remove(os.path.join(REV, old))
                except Exception: pass
        cmds.playblast(frame=1, format="image", filename=tgt, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
        made.append(tr)
    OUT["made"] = made
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r14.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
