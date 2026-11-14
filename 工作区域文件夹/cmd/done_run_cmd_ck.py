import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}
cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
OUT["grp_tx"] = round(cmds.getAttr("CHR_Ma.translateX"), 2)
m = "Ma_MakotoFBXASC032Yuki_mesh"
h = "Ma_Head"
OUT["a_mesh"] = [round(v, 2) for v in cmds.xform(m, q=True, ws=True, t=True)]
OUT["a_head"] = [round(v, 2) for v in cmds.xform(h, q=True, ws=True, t=True)]
cmds.setAttr("CHR_Ma.translateX", 10)
cmds.refresh(force=True)
OUT["b_mesh"] = [round(v, 2) for v in cmds.xform(m, q=True, ws=True, t=True)]
OUT["b_head"] = [round(v, 2) for v in cmds.xform(h, q=True, ws=True, t=True)]
OUT["mesh_dx"] = round(OUT["b_mesh"][0] - OUT["a_mesh"][0], 2)
OUT["head_dx"] = round(OUT["b_head"][0] - OUT["a_head"][0], 2)
OUT["mesh_parent"] = cmds.listRelatives(m, parent=True)
OUT["mesh_local"] = [round(v, 2) for v in cmds.getAttr(m + ".translate")[0]]
OUT["mesh_scale"] = [round(v, 3) for v in cmds.getAttr(m + ".scale")[0]]
json.dump(OUT, open(os.path.join(ROOT,"logs","r10.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
