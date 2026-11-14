import maya.cmds as cmds, json, os, math, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(ROOT, "logs", "e1.json")
OUT = {"steps": [], "errors": []}
TABLE = 75.75
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def h(mesh):
    bb = cmds.xform(mesh, q=True, ws=True, bb=True)
    return {"y": [round(bb[1],0), round(bb[4],0)], "h": round(bb[4]-bb[1],0),
            "x": [round(bb[0],0), round(bb[3],0)]}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    mesh = "Huang_AragakiFBXASC032Shinjiro_mesh"
    j = "Huang_"
    OUT["before_pose"] = h(mesh); dump()

    # 只弯手臂，不加 deltaMush
    cmds.setAttr(j + "LeftArm.rotate", -30.8, 33.1, -20.2)
    cmds.setAttr(j + "LeftForeArm.rotate", -66.1, -6.2, 66.3)
    cmds.refresh(force=True)
    OUT["pose_only"] = h(mesh); OUT["steps"].append("pose_only"); dump()

    # 再加 deltaMush
    try:
        dm = cmds.deltaMush(mesh, smoothingIterations=8, smoothingStep=0.5,
                            pinBorderVertices=0, envelope=1.0)
        OUT["dm"] = dm
        cmds.refresh(force=True)
        OUT["pose_plus_mush"] = h(mesh)
        OUT["steps"].append("pose_plus_mush")
    except Exception as e:
        OUT["dm_err"] = repr(e)
    dump()
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
