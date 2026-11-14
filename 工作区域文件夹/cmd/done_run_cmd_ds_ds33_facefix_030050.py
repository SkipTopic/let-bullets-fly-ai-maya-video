"""修正 MMD 人物头部材质：最大头部件用脸贴图，其余头部小件改肤色/发色纯色。"""
import json, os, traceback
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
HEAD_Y = {"Huang": 123.2, "Shiye": 123.5}
SKIN = (0.86, 0.71, 0.60)
HAIR = (0.20, 0.17, 0.16)
OUT = {"errors": [], "fix": {}}

try:
    log = json.load(open(os.path.join(ROOT, "logs", "ds32_materials.json"), encoding="utf-8"))["assign"]
    for name in ("Huang", "Shiye"):
        items = [i for i in log.get(name, []) if i.get("center")]
        head = [i for i in items if abs(i["center"][1] - HEAD_Y[name]) < 16.0]
        if not head:
            continue
        head.sort(key=lambda x: -x["faces"])
        main = head[0]
        for it in head:
            mat = it["mat"]
            for c in (cmds.listConnections(mat + ".color", plugs=True) or []):
                cmds.disconnectAttr(c, mat + ".color")
            if it is main:
                it["kind"] = "face_main"
                continue
            if it["center"][1] > HEAD_Y[name] + 6.0:
                cmds.setAttr(mat + ".color", HAIR[0], HAIR[1], HAIR[2])
                it["kind"] = "hair_flat"
            else:
                cmds.setAttr(mat + ".color", SKIN[0], SKIN[1], SKIN[2])
                it["kind"] = "skin_flat"
        OUT["fix"][name] = {"main": main["mat"], "main_faces": main["faces"],
                            "head_parts": len(head)}
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds33_facefix.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:600])
