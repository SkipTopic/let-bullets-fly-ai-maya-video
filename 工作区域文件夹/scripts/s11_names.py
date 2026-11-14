import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
n = cmds.ls("CAM*") or []
out = {"count": len(n), "sample": n[:12], "transforms": [x for x in n if cmds.nodeType(x)=="transform"][:12]}
json.dump(out, open(os.path.join(ROOT,"logs","s11.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
