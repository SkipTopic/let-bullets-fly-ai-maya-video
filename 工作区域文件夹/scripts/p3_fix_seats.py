# -*- coding: utf-8 -*-
"""Fix seating (Ma far side facing camera), then wide-angle test frame."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"

# camera looks from +Z toward -Z. Ma should be FAR side facing camera (+Z).
cmds.setAttr('Ma_root.translate', 0, 0, -55)
cmds.setAttr('Ma_root.rotateY', 0)        # try 0 first: MMD FBX often faces +Z
cmds.setAttr('Huang_root.translate', 48, 0, 28)
cmds.setAttr('Huang_root.rotateY', -120)  # face table center (from lower-right)
cmds.setAttr('Shiye_root.translate', -48, 0, 28)
cmds.setAttr('Shiye_root.rotateY', 120)   # face table center (from lower-left)

# wide-angle overview camera for orientation check
wide = cmds.camera(name='CAM_check', focalLength=35)
cmds.setAttr(wide[0] + '.translate', 0, 170, 330)
cmds.setAttr(wide[0] + '.rotate', -14, 0, 0)

panels = cmds.getPanel(type='modelPanel') or []
if panels:
    cmds.modelEditor(panels[0], e=True, camera='CAM_check')
    cmds.modelEditor(panels[0], e=True, grid=False, hud=False)

cmds.currentTime(1)
cmds.playblast(frame=[1], format='image', filename=W + r"\qa\CAM_check",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression='png')
P("check frame done")
print("SEAT_FIX_DONE")
'''

r = py(CODE, timeout=600)
print(r[-1200:])
