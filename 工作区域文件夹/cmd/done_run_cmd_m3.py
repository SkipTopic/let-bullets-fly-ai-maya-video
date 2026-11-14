import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    allm = cmds.ls(type="mesh") or []
    OUT["all_meshes"] = len(allm)
    rows = []
    for m in allm:
        try:
            inter = cmds.getAttr(m + ".intermediateObject")
        except Exception:
            inter = None
        try:
            v = cmds.polyEvaluate(m, vertex=True)
        except Exception:
            v = -1
        rows.append({"m": m, "inter": inter, "verts": v})
    rows.sort(key=lambda r: -(r["verts"] or 0))
    OUT["top"] = rows[:6]
    big = [r for r in rows if (r["verts"] or 0) > 1000]
    OUT["big_count"] = len(big)
    if big:
        m = big[0]["m"]
        bb = cmds.xform(m, q=True, ws=True, bb=True)
        OUT["bbox"] = [round(x,1) for x in bb]
        OUT["height"] = round(bb[4]-bb[1], 1)
        OUT["width_x"] = round(bb[3]-bb[0], 1)
        OUT["depth_z"] = round(bb[5]-bb[2], 1)
        OUT["sg"] = len(cmds.listConnections(m, type="shadingEngine") or [])
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","m2.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
