import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    OUT["refs"] = cmds.file(q=True, reference=True) or []
    OUT["top"] = cmds.ls(assemblies=True)
    for g in ("CHARS", "CAMERAS", "SET", "LIGHTS", "SCENE"):
        OUT[g] = len(cmds.listRelatives(g, children=True) or []) if cmds.objExists(g) else None
    OUT["char_groups"] = [x for x in (cmds.listRelatives("CHARS", children=True) or [])]
    OUT["cam_sample"] = [x for x in (cmds.listRelatives("CAMERAS", children=True) or [])][:3]
    for nm in ("CHR_Ma", "CHR_Huang", "CHR_Shiye"):
        OUT[nm] = {
            "translate": [round(v, 2) for v in cmds.getAttr(nm + ".translate")[0]],
            "rotateY": round(cmds.getAttr(nm + ".rotateY"), 1),
        }
    OUT["hand_Ma"] = [round(v, 1) for v in cmds.xform("Ma_LeftHand", q=True, ws=True, t=True)]
    OUT["scene_file"] = cmds.file(q=True, sn=True)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r8.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
