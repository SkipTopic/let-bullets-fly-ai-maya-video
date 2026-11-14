import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
j = cmds.ls(type="joint") or []
d = {"count": len(j), "sample": j[:30], "has_MaHips": [n for n in j if "Hips" in n][:5],
     "roots": cmds.ls("Ma_*", type="joint")[:5]}
json.dump(d, open(os.path.join(ROOT, "logs", "_diag.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
