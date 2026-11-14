import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    for key, arm, mesh in (
        ("Ma", "Ma_MakotoFBXASC032Yuki_arm", "Ma_MakotoFBXASC032Yuki_mesh"),
        ("Huang", "Huang_AragakiFBXASC032Shinjiro_arm", "Huang_AragakiFBXASC032Shinjiro_mesh"),
        ("Shiye", "Shiye_JunpeiFBXASC032Iori_arm", "Shiye_JunpeiFBXASC032Iori_mesh"),
    ):
        if cmds.objExists(mesh) and cmds.objExists(arm):
            cmds.parent(mesh, arm)      # 挂到骨架下，蒙皮不受影响
    cmds.refresh(force=True)
    OUT["ma_bbox"] = [round(v, 1) for v in cmds.xform("Ma_MakotoFBXASC032Yuki_mesh", q=True, ws=True, bb=True)]
    OUT["ma_parent"] = cmds.listRelatives("Ma_MakotoFBXASC032Yuki_mesh", parent=True)
    # 移动测试
    b = cmds.xform("Ma_MakotoFBXASC032Yuki_mesh", q=True, ws=True, bb=True)
    cmds.setAttr("CHR_Ma.translateX", 20)
    cmds.refresh(force=True)
    a = cmds.xform("Ma_MakotoFBXASC032Yuki_mesh", q=True, ws=True, bb=True)
    OUT["move_dx"] = round(a[0] - b[0], 2)
    cmds.setAttr("CHR_Ma.translateX", 0)
    cmds.file(save=True, type="mayaBinary", force=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","s22.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
