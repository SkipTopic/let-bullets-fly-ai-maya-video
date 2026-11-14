import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    meshes = ["Ma_MakotoFBXASC032Yuki_mesh", "Huang_AragakiFBXASC032Shinjiro_mesh",
              "Shiye_JunpeiFBXASC032Iori_mesh"]
    m = meshes[0]
    before = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    for x in meshes:
        if cmds.objExists(x):
            cmds.parent(x, "CHARS")
    cmds.refresh(force=True)
    after = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    OUT["bbox_before"] = before
    OUT["bbox_after"] = after
    OUT["same"] = before == after
    # 再测一次移动
    cmds.setAttr("CHR_Ma.translateX", 15)
    cmds.refresh(force=True)
    mv = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    OUT["dx"] = round(mv[0] - after[0], 2)
    cmds.setAttr("CHR_Ma.translateX", 0)
    cmds.refresh(force=True)
    OUT["top"] = [x for x in (cmds.ls(assemblies=True) or []) if x not in ("persp","top","front","side")]
    OUT["chars_children"] = cmds.listRelatives("CHARS", children=True) or []
    cmds.file(save=True, type="mayaBinary", force=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","s23.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
