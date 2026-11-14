import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), f=True, type="mayaBinary", ea=True)
    OUT["saved"] = "手工摆位_v3_mush.mb"
    OUT["dm"] = [x for x in (cmds.ls(type="deltaMush") or [])]
    OUT["ok"] = True
except Exception as e:
    OUT["err"] = repr(e)
json.dump(OUT, open(os.path.join(ROOT,"logs","s30.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
