import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
def shoot(tag, cam="OV_front1", w=900, h=560, f=1):
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
        if old.startswith("ISO_" + tag + "."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "ISO_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w, h), quality=95,
                   compression="png")
    return tag
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), o=True, force=True)
    # 1) 只显示布景
    cmds.setAttr("CHARS.visibility", 0)
    OUT["set_only"] = shoot("set_only")
    # 2) 恢复，只隐藏布景
    cmds.setAttr("CHARS.visibility", 1)
    cmds.setAttr("GRP_SET.visibility", 0)
    OUT["chars_only"] = shoot("chars_only")
    cmds.setAttr("GRP_SET.visibility", 1)
    # 3) 检查黄四郎网格是否有飞出顶点
    m = "Huang_AragakiFBXASC032Shinjiro_mesh"
    bb = cmds.xform(m, q=True, ws=True, bb=True)
    OUT["huang_bbox"] = [round(v, 0) for v in bb]
    OUT["set_children"] = cmds.listRelatives("GRP_SET", children=True, type="transform") or []
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z4.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
