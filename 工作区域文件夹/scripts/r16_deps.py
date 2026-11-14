import maya.cmds as cmds, json, os, traceback
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v2.mb"), o=True, force=True)
    OUT["maya_version"] = cmds.about(version=True)
    OUT["references"] = cmds.file(q=True, reference=True) or []
    OUT["file_nodes"] = cmds.ls(type="file") or []
    OUT["unknown_nodes"] = cmds.ls(type="unknown") or []
    OUT["image_planes"] = []
    for cam in (cmds.ls(type="camera") or []):
        try:
            if cmds.getAttr(cam + ".imagePlane"):
                pass
        except Exception:
            pass
    OUT["all_node_types"] = sorted(set(cmds.nodeType(n) for n in (cmds.ls() or [])))
    OUT["external_files"] = cmds.filePathEditor(q=True, listFiles=True, listDirectories=True) or []
    OUT["size_mb"] = round(os.path.getsize(os.path.join(ROOT, "scenes", "手工摆位_v2.mb")) / 1048576, 1)
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())
json.dump(OUT, open(os.path.join(ROOT,"logs","r16.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
