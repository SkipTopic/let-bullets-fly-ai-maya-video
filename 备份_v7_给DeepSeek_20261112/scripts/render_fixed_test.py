# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
cmds.file(W + "/scenes/p4_fixed.mb", o=True, force=True)
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
cmds.modelEditor(mp, e=True, camera="CAM_S1")
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/fixed_test",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
P("TEST_DONE")
'''
r = py(CODE, timeout=600)
print(r[-300:])
