import maya.cmds as cmds, json, os
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
out = {}
for key in ("Ma", "Huang", "Shiye"):
    shp = [n for n in (cmds.ls(type="mesh") or []) if n.startswith(key + "_") and not cmds.getAttr(n+".intermediateObject")]
    if not shp:
        continue
    sgs = cmds.listConnections(shp[0], type="shadingEngine") or []
    names = []
    for sg in dict.fromkeys(sgs):
        m = cmds.listConnections(sg + ".surfaceShader") or []
        names.append(m[0] if m else sg)
    out[key] = names
json.dump(out, open(os.path.join(ROOT,"logs","r5_mats.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
