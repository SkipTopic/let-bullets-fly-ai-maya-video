import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    m = "Ma_MakotoFBXASC032Yuki_mesh"
    OUT["mesh_bbox"] = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    OUT["mesh_wscale"] = [round(v, 3) for v in cmds.xform(m, q=True, ws=True, s=True)]
    arm = "Ma_MakotoFBXASC032Yuki_arm"
    OUT["arm_wscale"] = [round(v, 3) for v in cmds.xform(arm, q=True, ws=True, s=True)]
    OUT["grp_wscale"] = [round(v, 3) for v in cmds.xform("CHR_Ma", q=True, ws=True, s=True)]
    OUT["arm_bbox"] = [round(v, 1) for v in cmds.xform(arm, q=True, ws=True, bb=True)]
    panels = cmds.getPanel(type="modelPanel") or []
    vis = [x for x in panels if cmds.control(x, q=True, visible=True)]
    p = vis[0] if vis else "modelPanel4"
    cmds.modelEditor(p, e=True, displayAppearance="smoothShaded", polymeshes=True,
                     displayLights="default", grid=False, joints=False, cameras=False,
                     locators=False, wireframeOnShaded=False, manipulators=False,
                     handles=False, headsUpDisplay=False)
    cmds.currentTime(1)
    cmds.lookThru(p, "persp")
    cmds.playblast(frame=1, format="image",
                   filename=os.path.join(ROOT, "_审片", "DIAG_persp"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=90,
                   compression="png")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r12.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
