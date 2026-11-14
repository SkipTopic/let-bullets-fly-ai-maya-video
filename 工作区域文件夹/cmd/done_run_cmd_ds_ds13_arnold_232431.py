"""用 Arnold 直接渲染一台相机，验证相机几何是否正确（与 playblast 对照）。"""
import glob
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
out = {"errors": []}

try:
    cmds.setAttr("defaultResolution.width", 960)
    cmds.setAttr("defaultResolution.height", 540)
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "ds_arnold_test", type="string")
    # 低采样，快出图
    try:
        cmds.setAttr("defaultArnoldRenderOptions.AASamples", 3)
        cmds.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", 1)
        cmds.setAttr("defaultArnoldRenderOptions.GISpecularSamples", 1)
        cmds.setAttr("defaultArnoldRenderOptions.GITransmissionSamples", 0)
        cmds.setAttr("defaultArnoldRenderOptions.GISssSamples", 0)
        cmds.setAttr("defaultArnoldRenderOptions.GIVolumeSamples", 0)
    except Exception as exc:  # noqa: BLE001
        out["errors"].append("arnold opts: %r" % (exc,))
    out["renderer"] = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    out["project"] = cmds.workspace(q=True, rootDirectory=True)
    cmds.currentTime(1)
    out["result"] = cmds.render("DS_S001_CAM1", x=960, y=540)
    out["ok"] = True
except Exception as exc:  # noqa: BLE001
    out["errors"].append(repr(exc))

out["found"] = glob.glob(os.path.join(ROOT, "**", "ds_arnold_test*"), recursive=True)[-5:]
with open(os.path.join(ROOT, "logs", "ds13_arnold.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
