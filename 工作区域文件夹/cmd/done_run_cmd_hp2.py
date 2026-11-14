import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    helpers = [x for x in (cmds.ls(assemblies=True) or []) if "mmd_sdef" in x]
    if helpers:
        g = cmds.group(em=True, name="HIDDEN_HELPERS")
        cmds.parent("HIDDEN_HELPERS", "SCENE")
        for h in helpers:
            cmds.parent(h, g)
        cmds.setAttr(g + ".visibility", 0)
        try:
            lay = cmds.createDisplayLayer(name="HELPERS_HIDDEN", empty=True)
            cmds.editDisplayLayerMembers(lay, g, noRecurse=True)
            cmds.setAttr(lay + ".visibility", 0)
        except Exception:
            pass
    # 移动测试（确认 sdef 归组后蒙皮还活着）
    m = "Ma_MakotoFBXASC032Yuki_mesh"
    b = cmds.xform(m, q=True, ws=True, bb=True)
    cmds.setAttr("CHR_Ma.translateX", cmds.getAttr("CHR_Ma.translateX") + 30)
    cmds.refresh(force=True)
    a = cmds.xform(m, q=True, ws=True, bb=True)
    OUT["move_dx"] = round(a[0] - b[0], 2)
    cmds.setAttr("CHR_Ma.translateX", cmds.getAttr("CHR_Ma.translateX") - 30)

    OUT["top"] = [x for x in (cmds.ls(assemblies=True) or []) if x not in ("persp","top","front","side")]
    cmds.file(save=True, type="mayaBinary", force=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","s21.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
