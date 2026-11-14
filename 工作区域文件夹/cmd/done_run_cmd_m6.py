import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(new=True, f=True)
    fbx = os.path.join(ROOT, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")
    cmds.file(fbx, i=True, ignoreVersion=True)
    meshes = [m for m in (cmds.ls(type="mesh") or []) if not cmds.getAttr(m+".intermediateObject")]
    base = next((m for m in meshes if cmds.listConnections(m, type="skinCluster")), None)
    for bs in (cmds.ls(type="blendShape") or []):
        try: cmds.delete(bs)
        except Exception: pass
    kill = []
    for m in meshes:
        if m == base: continue
        p = cmds.listRelatives(m, parent=True)
        if p: kill.append(p[0])
    for k in dict.fromkeys(kill):
        try: cmds.delete(k)
        except Exception: pass

    tr = cmds.listRelatives(base, parent=True)[0]
    bb = cmds.xform(tr, q=True, ws=True, bb=True)
    OUT["height"] = round(bb[4]-bb[1], 1)
    OUT["bbox"] = [round(v,1) for v in bb]

    def pos(n):
        r = cmds.ls(n, type="joint")
        return [round(v,1) for v in cmds.xform(r[0], q=True, ws=True, t=True)] if r else None
    for n in ("Bip001Pelvis","Bip001Spine2","Bip001Head","Bip001LUpperArm",
              "Bip001LForearm","Bip001LHand","Bip001LThigh","Bip001LCalf","Bip001LFoot"):
        OUT[n] = pos(n)
    OUT["root"] = cmds.listRelatives(cmds.ls(type="joint")[0], parent=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","m4.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
