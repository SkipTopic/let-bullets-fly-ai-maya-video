"""保存后回读验证：重新打开场景，核对相机、帧率、灯组、动画曲线数量。"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SCENE = os.path.join(ROOT, "scenes", "DS_相机动作_v01.mb").replace("\\", "/")
OUT = {"errors": []}

try:
    cmds.file(SCENE, o=True, f=True)
    cams = [c for c in (cmds.listCameras() or []) if c.startswith("DS_")]
    OUT["scene"] = cmds.file(q=True, sn=True)
    OUT["ds_camera_count"] = len(cams)
    OUT["review_camera_count"] = len(cmds.listRelatives("POSE_REVIEW_CAMERAS", children=True) or [])
    OUT["time_unit"] = cmds.currentUnit(q=True, time=True)
    OUT["playback"] = [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
    OUT["anim_curves"] = len(cmds.ls(type="animCurve") or [])
    OUT["ds_lights"] = len(cmds.ls("DS_*_LGT", type="pointLight") or [])
    OUT["group_exists"] = cmds.objExists("DS_PRODUCTION_CAMERAS")
    OUT["references"] = cmds.file(q=True, reference=True) or []
    OUT["missing_samples"] = [s for s in ("DS_S001_CAM", "DS_S071_CAM")
                              if not cmds.ls(s + "*")]
    OUT["ok"] = OUT["ds_camera_count"] == 71 and not OUT["missing_samples"]
except Exception as exc:  # noqa: BLE001
    OUT["errors"].append(repr(exc))

with open(os.path.join(ROOT, "logs", "ds19_reopen.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False, indent=1))
