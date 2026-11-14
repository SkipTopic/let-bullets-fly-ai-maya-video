import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(new=True, f=True)
    fbx = os.path.join(ROOT, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")
    cmds.file(fbx, i=True, ignoreVersion=True)
    meshes = [m for m in (cmds.ls(type="mesh") or []) if not cmds.getAttr(m+".intermediateObject")]
    OUT["imported_meshes"] = len(meshes)
    # 真正的身体网格 = 被 skinCluster 驱动的那个
    base = None
    for m in meshes:
        if cmds.listConnections(m, type="skinCluster"):
            base = m
            break
    OUT["base"] = base
    if base:
        OUT["base_verts"] = cmds.polyEvaluate(base, vertex=True)
        tr = cmds.listRelatives(base, parent=True)[0]
        OUT["base_transform"] = tr
        # 删掉其余所有网格（都是表情 morph）
        kill = []
        for m in meshes:
            if m == base:
                continue
            p = cmds.listRelatives(m, parent=True)
            if p:
                kill.append(p[0])
        kill = list(dict.fromkeys(kill))
        OUT["to_delete"] = len(kill)
        # 先删 blendShape 节点，再删网格
        for bs in (cmds.ls(type="blendShape") or []):
            try: cmds.delete(bs)
            except Exception: pass
        for k in kill:
            try: cmds.delete(k)
            except Exception: pass
        OUT["remaining_meshes"] = len([x for x in (cmds.ls(type="mesh") or [])
                                       if not cmds.getAttr(x+".intermediateObject")])
        bb = cmds.xform(tr, q=True, ws=True, bb=True)
        OUT["bbox"] = [round(v,1) for v in bb]
        OUT["height"] = round(bb[4]-bb[1], 1)
        OUT["sg"] = len(cmds.listConnections(base, type="shadingEngine") or [])
        OUT["joints"] = len(cmds.ls(type="joint") or [])
        cmds.file(os.path.join(ROOT,"scenes","NEWM_test.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","m3.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
