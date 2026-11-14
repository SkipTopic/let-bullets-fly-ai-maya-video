"""把 DS_S001_CAMShape1 的全部属性倒出来，找影响视场的可疑值。"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
shape = "DS_S001_CAMShape1"
out = {"attrs": {}, "errors": []}

for a in cmds.listAttr(shape) or []:
    try:
        if not cmds.attributeQuery(a, node=shape, writable=True):
            continue
        v = cmds.getAttr(shape + "." + a)
    except Exception:
        continue
    if isinstance(v, (int, float)) or (isinstance(v, list) and len(v) <= 4):
        out["attrs"][a] = v

# 对比一台 Maya 默认新建的相机
tmp = cmds.camera(name="TMP_REF_CAM")[0]
tshape = cmds.listRelatives(tmp, shapes=True)[0]
ref = {}
for a in cmds.listAttr(tshape) or []:
    try:
        v = cmds.getAttr(tshape + "." + a)
    except Exception:
        continue
    if isinstance(v, (int, float)):
        ref[a] = v
diff = {}
for k, v in out["attrs"].items():
    if isinstance(v, (int, float)) and k in ref and abs(float(v) - float(ref[k])) > 1e-9:
        diff[k] = {"ds": v, "default": ref[k]}
out["diff_vs_default"] = diff
cmds.delete(tmp)

path = os.path.join(ROOT, "logs", "ds14_camattrs.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out.get("diff_vs_default"), ensure_ascii=False, indent=1))
