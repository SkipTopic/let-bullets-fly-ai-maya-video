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
        if old.startswith("FN_" + tag + "."):
            try: os.remove(os.path.join(REV, old))
            except Exception: pass
    cmds.playblast(frame=f, format="image", filename=os.path.join(REV, "FN_" + tag),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(854, 480), quality=95,
                   compression="png")
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    # 只做两件事：收紧裁剪面 + 删掉共面的假阴影盘
    for c in (cmds.ls(type="camera") or []):
        try:
            cmds.setAttr(c + ".nearClipPlane", 5.0)
            cmds.setAttr(c + ".farClipPlane", 2200.0)
        except Exception: pass
    for x in ("SET_contact_shadow",):
        if cmds.objExists(x):
            cmds.delete(x)
    bbs = {}
    for k, m in (("Ma","Ma_MakotoFBXASC032Yuki_mesh"),
                 ("Huang","Huang_AragakiFBXASC032Shinjiro_mesh"),
                 ("Shiye","Shiye_JunpeiFBXASC032Iori_mesh")):
        bb = cmds.xform(m, q=True, ws=True, bb=True)
        bbs[k] = round(bb[4]-bb[1], 0)
    OUT["heights"] = bbs
    shoot("S001", "S001_CAM1", 30)
    shoot("S002", "S002_CAM1", 80)
    shoot("S045", "S045_CAM1", 2340)
    cmds.file(os.path.join(ROOT,"scenes","手工摆位_v5_final.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z6.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
