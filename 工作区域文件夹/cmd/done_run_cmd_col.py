import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    fixed = 0
    for m in (cmds.ls(type="lambert") or []):
        try:
            c = cmds.getAttr(m + ".color")[0]
        except Exception:
            continue
        # 深色（鞋子色）统一改成中性布料灰
        if max(c) < 0.36:
            cmds.setAttr(m + ".color", 0.62, 0.60, 0.56, type="double3")
            cmds.setAttr(m + ".ambientColor", 0.22, 0.21, 0.20, type="double3")
            fixed += 1
    OUT["fixed"] = fixed
    cmds.file(save=True, type="mayaBinary", force=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","s24.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
