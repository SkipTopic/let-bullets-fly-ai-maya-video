import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), o=True, force=True)
    OUT["all_meshes"] = len(cmds.ls(type="mesh") or [])
    sets = [x for x in (cmds.listRelatives("GRP_SET", children=True) or [])]
    OUT["set_children"] = sets
    rows = []
    for tr in sets:
        shapes = cmds.listRelatives(tr, shapes=True, ni=True) or []
        for sh in shapes:
            bb = cmds.xform(sh, q=True, ws=True, bb=True)
            rows.append({"tr": tr, "y": [round(bb[1], 2), round(bb[4], 2)],
                         "x": [round(bb[0], 0), round(bb[3], 0)], "z": [round(bb[2], 0), round(bb[5], 0)]})
    OUT["set_rows"] = rows
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z2.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
