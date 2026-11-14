import maya.cmds as cmds
import maya.mel as mel
import json, os, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"attempts": {}}
try:
    cmds.file(os.path.join(ROOT, "scenes", "摆姿重建_v4.mb"), o=True, f=True)
    panels = cmds.getPanel(type="modelPanel") or []
    visible = [p for p in panels if cmds.control(p, q=True, visible=True)]
    panel = visible[0]
    cam = "front"
    OUT["panel"] = panel
    OUT["panels"] = {p: {"visible": cmds.control(p, q=True, visible=True), "camera": cmds.modelEditor(p, q=True, camera=True)} for p in panels}
    OUT["doc"] = cmds.lookThru.__doc__
    OUT["camera_shapes"] = cmds.ls(type="camera", long=True) or []
    attempts = (
        ("panel_cam", "cmds.lookThru(panel, cam)"),
        ("cam_panel", "cmds.lookThru(cam, panel)"),
        ("keyword", "cmds.lookThru(panel, camera=cam)"),
        ("mel", "mel.eval('lookThru %s %s' % (panel, cam))"),
    )
    for name, code in attempts:
        try:
            eval(code)
            cmds.refresh(force=True)
            OUT["attempts"][name] = {"ok": True, "active": cmds.modelEditor(panel, q=True, camera=True)}
        except Exception:
            OUT["attempts"][name] = {"ok": False, "error": traceback.format_exc()}
    OUT["ok"] = True
except Exception:
    OUT["fatal"] = traceback.format_exc()
with open(os.path.join(ROOT, "logs", "q4b_view_probe.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
