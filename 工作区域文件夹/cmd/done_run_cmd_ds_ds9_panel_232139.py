"""诊断：查看 modelPanel4 的视口属性，找 2D 平移/缩放等影响画面的设置。"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
panel = "modelPanel4"
out = {"attrs": {}, "errors": []}

try:
    attrs = cmds.listAttr(panel) or []
    keep = [a for a in attrs if any(k in a.lower() for k in ("zoom", "pan", "camera", "focal", "fit", "overscan"))]
    out["candidate_attrs"] = keep
    for a in keep:
        try:
            v = cmds.getAttr(panel + "." + a)
            out["attrs"][a] = v if not isinstance(v, list) else v[:8]
        except Exception as exc:  # noqa: BLE001
            out["attrs"][a] = "ERR %r" % (exc,)
except Exception as exc:  # noqa: BLE001
    out["errors"].append(repr(exc))

# 相机侧
cam = "DS_S001_CAM1"
shape = cmds.listRelatives(cam, shapes=True)[0]
for a in ("focalLength", "horizontalFilmAperture", "verticalFilmAperture", "filmFit",
          "overscan", "panZoomEnabled", "centerOfInterest", "orthographic"):
    try:
        out["attrs"]["cam." + a] = cmds.getAttr(shape + "." + a)
    except Exception:
        pass

with open(os.path.join(ROOT, "logs", "ds9_panel.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
