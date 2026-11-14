import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    m = "Ma_MakotoFBXASC032Yuki_mesh"
    OUT["bbox_before"] = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    cmds.setAttr("CHR_Ma.translateX", 20)
    cmds.refresh(force=True)
    OUT["bbox_moved"] = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    OUT["dx"] = round(OUT["bbox_moved"][0] - OUT["bbox_before"][0], 2)
    cmds.setAttr("CHR_Ma.translateX", 0)
    cmds.refresh(force=True)
    OUT["bbox_back"] = [round(v, 1) for v in cmds.xform(m, q=True, ws=True, bb=True)]
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r13.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
