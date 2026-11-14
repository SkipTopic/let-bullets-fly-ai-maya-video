import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
j = [n for n in (cmds.ls(type="joint") or []) if n.startswith("Ma_")]
keep = [n for n in j if any(k in n for k in ("Root","Center","Groove","Bone","Spine","Neck","Head","Arm","Fore","Hand","UpLeg","Leg","Foot","Shoulder","Eye"))]
json.dump({"n": len(j), "keep": keep}, open(os.path.join(ROOT,"logs","_diag2.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
