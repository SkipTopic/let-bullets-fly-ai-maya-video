import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(ROOT, "logs", "e2.json")
OUT = {"steps": [], "errors": []}
def dump():
    json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
def h(mesh):
    bb = cmds.xform(mesh, q=True, ws=True, bb=True)
    return {"h": round(bb[4]-bb[1],0), "y": [round(bb[1],0), round(bb[4],0)]}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    mesh = "Huang_AragakiFBXASC032Shinjiro_mesh"; j = "Huang_"
    OUT["rest"] = h(mesh)
    cmds.setAttr(j + "LeftArm.rotate", -30.8, 33.1, -20.2)
    cmds.setAttr(j + "LeftForeArm.rotate", -66.1, -6.2, 66.3)
    cmds.refresh(force=True)
    OUT["pose_no_dm"] = h(mesh); dump()

    # 关键测试：pinBorderVertices=1，迭代降到 3
    n = cmds.deltaMush(mesh, smoothingIterations=3, smoothingStep=0.4,
                       pinBorderVertices=1, envelope=1.0)
    OUT["dm"] = n
    cmds.refresh(force=True)
    OUT["pose_pin1"] = h(mesh); OUT["steps"].append("pin1"); dump()

    # 对照：把 pin 关掉
    try:
        cmds.setAttr(n[0] + ".pinBorderVertices", 0)
        cmds.refresh(force=True)
        OUT["pose_pin0"] = h(mesh)
    except Exception as e:
        OUT["pin_err"] = repr(e)
    dump()
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
dump()
