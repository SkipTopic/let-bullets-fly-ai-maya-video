import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
import lib_scene as _L
L = importlib.reload(_L)          # Maya 进程内模块会缓存，必须重载

OUT = {"errors": []}
try:
    cmds.file(new=True, force=True)
    L.setup_viewport()

    CHARS = {
        "Ma":    {"fbx": "CH_Ma.fbx",    "pal": {"hair": (0.09, 0.10, 0.13), "skin": (0.62, 0.45, 0.36),
                                                 "cloth": (0.16, 0.18, 0.22), "cloth2": (0.10, 0.11, 0.14),
                                                 "shoe": (0.05, 0.05, 0.06)}, "theta": 214},
        "Huang": {"fbx": "CH_Huang.fbx", "pal": {"hair": (0.12, 0.09, 0.07), "skin": (0.66, 0.48, 0.38),
                                                 "cloth": (0.22, 0.10, 0.09), "cloth2": (0.13, 0.06, 0.05),
                                                 "shoe": (0.05, 0.05, 0.06)}, "theta": 326},
        "Shiye": {"fbx": "CH_Shiye.fbx", "pal": {"hair": (0.10, 0.09, 0.09), "skin": (0.64, 0.46, 0.37),
                                                 "cloth": (0.19, 0.17, 0.14), "cloth2": (0.12, 0.11, 0.09),
                                                 "shoe": (0.05, 0.05, 0.06)}, "theta": 270},
    }

    chars = {}
    for key, cfg in CHARS.items():
        info = L.import_char(key, os.path.join(ROOT, "models_fbx2", cfg["fbx"]))
        L.color_char_materials(info["geo"], cfg["pal"])
        chars[key] = {"root": key + "_Root", "geo": info["geo"], "j": key + "_",
                      "grp": info["grp"], "arm": info["arm"], "theta": cfg["theta"]}
        OUT[key] = {"geo": info["geo"], "joints": info["joints"], "grp": info["grp"]}

    # 布景与灯
    L.build_set()
    L.build_lights()

    # 坐姿
    for key, ch in chars.items():
        L.place_seated(ch, ch["theta"])
    for key, ch in chars.items():
        dy = L.fit_to_seat(ch, 46.0)
        OUT[key]["root_dy"] = round(dy, 2)
        OUT[key]["hip"] = [round(v, 2) for v in cmds.xform(L.hip_joint(ch["j"]), q=True, ws=True, t=True)]
        OUT[key]["head"] = [round(v, 2) for v in cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)]
        OUT[key]["foot"] = [round(v, 2) for v in cmds.xform(ch["j"] + "LeftFoot", q=True, ws=True, t=True)]
        OUT[key]["handL"] = [round(v, 2) for v in cmds.xform(ch["j"] + "LeftHand", q=True, ws=True, t=True)]

    # 三视图
    cams = {
        "wide":  ((0, 118, 300), (0, 96, -40), 42),
        "med":   ((0, 108, 190), (0, 100, -60), 65),
        "close": ((-30, 112, 130), (-40, 112, -70), 85),
        "side":  ((190, 105, 60), (0, 98, -40), 55),
    }
    shots = {}
    for name, (eye, aim, focal) in cams.items():
        cam = L.make_cam("CAM_" + name, eye, aim, focal)
        cmds.lookThru(cam)
        p = L.render_to(os.path.join(ROOT, "_接手检查", "p1_" + name + ".png"))
        shots[name] = p
    OUT["shots"] = shots
    OUT["ok"] = True

    cmds.file(os.path.join(ROOT, "scenes", "v2_base.mb"), f=True, type="mayaBinary", ea=True)
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "p1_pose.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
