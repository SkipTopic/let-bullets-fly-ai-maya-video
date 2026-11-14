# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

SEAT = {"Ma": (0, -46, -100, 180), "Huang": (44, -46, 26, 120), "Shiye": (-44, -46, 26, -120)}
TOPS = {"Ma": ("*MakotoFBXASC032Yuki_arm", "*MakotoFBXASC032Yuki_mesh"),
        "Huang": ("*AragakiFBXASC032Shinjiro_arm", "*AragakiFBXASC032Shinjiro_mesh"),
        "Shiye": ("*JunpeiFBXASC032Iori_arm", "*JunpeiFBXASC032Iori_mesh")}
for tag, (pa, pm) in TOPS.items():
    x, y, z, ry = SEAT[tag]
    for pat in (pa, pm):
        lst = cmds.ls(pat) or []
        if not lst:
            P("MISS " + pat)
            continue
        t = lst[0]
        for attr in ("translateX", "translateY", "translateZ", "rotateY"):
            try:
                cmds.setAttr(t + "." + attr, lock=False)
            except Exception:
                pass
        try:
            cmds.setAttr(t + ".translate", x, y, z)
            cmds.setAttr(t + ".rotateY", ry)
        except Exception as e:
            P("fail %s: %s" % (t, e))
P("mesh+arm placed")

mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
frames = {"S001": (1, 1), "S030": (1268, 30), "S060": (2489, 60)}
for name, (f, n) in frames.items():
    cam = "CAM_S%d" % n
    if not cmds.objExists(cam):
        P("MISSING " + cam)
        continue
    cmds.modelEditor(mp, e=True, camera=cam)
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/verify_" + name,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
    P("rendered " + name + " with " + cam)
cmds.file(save=True, force=True, type="mayaBinary")
print("FIXVERIFY_DONE")
'''

r = py(CODE, timeout=900)
print(r[-900:])
