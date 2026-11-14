import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), o=True, force=True)
    OUT["refs"] = cmds.file(q=True, reference=True) or []
    OUT["top"] = [x for x in (cmds.ls(assemblies=True) or []) if not x in ("persp","top","front","side")]
    OUT["chars"] = cmds.listRelatives("CHARS", children=True) or []
    OUT["cams"] = len(cmds.listRelatives("CAMERAS", children=True) or [])
    OUT["char_child"] = {c: (cmds.listRelatives(c, children=True) or []) for c in OUT["chars"]}

    # 移动测试：把 CHR_Ma 往 +X 移 50，看网格和骨骼是否同时动
    m = "Ma_MakotoFBXASC032Yuki_mesh"
    before_m = cmds.xform(m, q=True, ws=True, t=True)
    before_h = cmds.xform("Ma_Head", q=True, ws=True, t=True)
    cmds.setAttr("CHR_Ma.translateX", cmds.getAttr("CHR_Ma.translateX") + 50)
    cmds.refresh(force=True)
    after_m = cmds.xform(m, q=True, ws=True, t=True)
    after_h = cmds.xform("Ma_Head", q=True, ws=True, t=True)
    OUT["move"] = {
        "mesh_dx": round(after_m[0] - before_m[0], 2),
        "head_dx": round(after_h[0] - before_h[0], 2),
    }
    cmds.setAttr("CHR_Ma.translateX", cmds.getAttr("CHR_Ma.translateX") - 50)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r9.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
