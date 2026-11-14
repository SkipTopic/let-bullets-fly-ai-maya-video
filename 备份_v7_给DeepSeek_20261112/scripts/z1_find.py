import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REV = os.path.join(ROOT, "_审片")
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v3_mush.mb"), o=True, force=True)
    meshes = [m for m in (cmds.ls(type="mesh") or []) if not cmds.getAttr(m + ".intermediateObject")]
    rows = []
    for m in meshes:
        try:
            bb = cmds.xform(m, q=True, ws=True, bb=True)
        except Exception:
            continue
        # 只看与桌面高度（70~78）相交、且横向范围在桌子以内的
        if bb[1] < 78 and bb[4] > 70 and bb[0] > -100 and bb[3] < 100 and bb[2] > -100 and bb[5] < 100:
            tr = (cmds.listRelatives(m, parent=True) or [m])[0]
            rows.append({"node": tr, "mesh": m,
                         "y": [round(bb[1], 2), round(bb[4], 2)],
                         "x": [round(bb[0], 1), round(bb[3], 1)],
                         "z": [round(bb[2], 1), round(bb[5], 1)]})
    OUT["near_table"] = rows
    OUT["count"] = len(rows)
    # 检查同名重复
    names = [r["node"] for r in rows]
    OUT["dupes"] = sorted({n for n in names if names.count(n) > 1})
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","z1.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
