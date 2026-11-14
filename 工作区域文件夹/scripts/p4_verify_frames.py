# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
cmds.file(W + "/scenes/p4_final.mb", o=True, force=True)
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
frames = {"S001": 1, "S030": 1268, "S060": 2489}
for name, f in frames.items():
    cam = "CAM_" + name
    if not cmds.objExists(cam):
        P("MISSING " + cam)
        continue
    cmds.modelEditor(mp, e=True, camera=cam)
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/verify_" + name,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
    P("rendered " + name)
print("VERIFY_DONE")
'''

r = py(CODE, timeout=900)
print(r[-800:])
