import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
cams = cmds.ls(type="camera")
trs = [c for c in (cmds.listRelatives(cams, parent=True) or [])]
json.dump({"camera_shapes": cams[:8], "count_shape": len(cams), "transforms": trs[:8],
           "count_tr": len(trs), "scene": cmds.file(q=True, sn=True)},
          open(os.path.join(ROOT,"logs","s13.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
