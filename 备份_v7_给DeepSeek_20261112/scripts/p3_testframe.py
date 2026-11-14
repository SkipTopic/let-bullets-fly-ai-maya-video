# -*- coding: utf-8 -*-
"""P3 gate: render one CAM_TEMPLATE test frame via playblast 854x480."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
cmds.file(W + r"\scenes\p3_set.mb", o=True, force=True)

panels = cmds.getPanel(type='modelPanel') or []
if panels:
    cmds.modelEditor(panels[0], e=True, camera='CAM_TEMPLATE')
    cmds.modelEditor(panels[0], e=True, displayAppearance='smoothShaded')
    cmds.modelEditor(panels[0], e=True, dl='default')
    cmds.modelEditor(panels[0], e=True, wos=False)
    cmds.modelEditor(panels[0], e=True, grid=False)
    cmds.modelEditor(panels[0], e=True, hud=False)

cmds.currentTime(1)
qb = cmds.playblast(
    frame=[1], format='image',
    filename=W + r"\qa\CAM_test",
    sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
    fp=4, percent=100, widthHeight=[854, 480],
    quality=100, compression='png')
P("playblast done: %s" % qb)
print("P3_TEST_DONE")
'''

r = py(CODE, timeout=600)
print(r[-1500:])
