"""测试 Viewport 2.0 景深是否生效。"""
import json, os
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": []}
try:
    cam = cmds.ls("DS_S003_CAM*")[0]
    shape = cmds.listRelatives(cam, shapes=True)[0]
    data = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                                               encoding="utf-8"))["shots"]}
    s = data["S003"]
    focus = s["projection"]["Ma"]["dist"]
    cmds.setAttr(shape + ".depthOfField", True)
    cmds.setAttr(shape + ".focusDistance", focus)
    cmds.setAttr(shape + ".fStop", 1.6)
    OUT["focus"] = focus
    OUT["attrs"] = {a: cmds.getAttr(shape + "." + a) for a in ("depthOfField", "focusDistance", "fStop")}

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.lookThru(panel, cam)
    cmds.currentTime(150)
    cmds.refresh(force=True)
    os.makedirs(os.path.join(ROOT, "ds_stills", "doftest"), exist_ok=True)
    cmds.playblast(frame=150, format="image", filename=os.path.join(ROOT, "ds_stills", "doftest", "dof_on"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(960, 540), quality=90, compression="png")
    OUT["ok"] = True
except Exception as exc:
    import traceback
    OUT["errors"].append(traceback.format_exc())
print(json.dumps(OUT, ensure_ascii=False)[:400])
