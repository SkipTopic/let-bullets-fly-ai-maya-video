import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOG = os.path.join(ROOT, "logs", "m1.json")
OUT = {"errors": []}
try:
    cmds.file(new=True, f=True)
    fbx = os.path.join(ROOT, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")
    OUT["exists"] = os.path.exists(fbx)
    nodes = cmds.file(fbx, i=True, ignoreVersion=True, mergeNamespacesOnClash=False,
                      namespace="NEWM", options="fbx", pr=True)
    OUT["imported"] = len(nodes or [])
    arms = [x for x in (cmds.ls(type="joint") or [])]
    OUT["joints"] = len(arms)
    OUT["sample"] = arms[:10]
    # 找骨骼
    def j(name):
        m = [x for x in arms if x.endswith(name) or x == name]
        return m[0] if m else None
    OUT["bones"] = {k: j(k) for k in ("Bip001Pelvis", "Bip001Spine", "Bip001Spine1",
                                      "Bip001Spine2", "Bip001Neck", "Bip001Head",
                                      "Bip001LClavicle", "Bip001LUpperArm",
                                      "Bip001LForearm", "Bip001LHand",
                                      "Bip001LThigh", "Bip001LCalf", "Bip001LFoot")}
    meshes = [m for m in (cmds.ls(type="mesh") or []) if not cmds.getAttr(m+".intermediateObject")]
    OUT["mesh_count"] = len(meshes)
    if meshes:
        bb = cmds.xform(meshes[0], q=True, ws=True, bb=True)
        OUT["bbox"] = [round(v,1) for v in bb]
        OUT["height"] = round(bb[4]-bb[1], 1)
        OUT["width"] = round(bb[3]-bb[0], 1)
        OUT["mats"] = len(cmds.listConnections(meshes[0], type="shadingEngine") or [])
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(LOG,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
