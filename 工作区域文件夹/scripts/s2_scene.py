import maya.cmds as cmds
import json, os, sys, importlib, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)

OUT = {"errors": []}
try:
    chars = L.build_all()

    # 四个机位：每个角色正对（对面两人中间）
    res = {}
    for key, ch in chars.items():
        j = ch["j"]
        res[key] = {
            "hip": [round(v, 2) for v in cmds.xform(L.hip_joint(j), q=True, ws=True, t=True)],
            "head": [round(v, 2) for v in cmds.xform(j + "Head", q=True, ws=True, t=True)],
            "handL": [round(v, 2) for v in cmds.xform(j + "LeftHand", q=True, ws=True, t=True)],
            "handR": [round(v, 2) for v in cmds.xform(j + "RightHand", q=True, ws=True, t=True)],
            "footL": [round(v, 2) for v in cmds.xform(j + "LeftFoot", q=True, ws=True, t=True)],
            "grp": [round(v, 2) for v in cmds.getAttr(ch["grp"] + ".translate")[0]],
        }
    OUT["chars"] = res

    # 渲染四机位
    import math
    cams = {}
    for key, ch in chars.items():
        ang = math.radians(ch["theta"] + 180)
        eye = (math.cos(ang) * 205, 116, math.sin(ang) * 205)
        aim = cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
        cam = L.make_cam("CAM_test_" + key, eye, aim, 85)
        cmds.lookThru(cam)
        cams[key] = L.render_to(os.path.join(ROOT, "_接手检查", "s2_" + key + ".png"))
    OUT["cams"] = cams

    # 全景
    cam = L.make_cam("CAM_test_wide", (0, 150, 330), (0, 95, -30), 35)
    cmds.lookThru(cam)
    OUT["wide"] = L.render_to(os.path.join(ROOT, "_接手检查", "s2_wide.png"))

    cmds.file(os.path.join(ROOT, "scenes", "v3_base.mb"), f=True, type="mayaBinary", ea=True)
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s2_scene.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
