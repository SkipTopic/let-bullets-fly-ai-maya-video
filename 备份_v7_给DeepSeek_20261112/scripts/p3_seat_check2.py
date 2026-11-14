# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
cmds.file(W + r"\scenes\p3_set.mb", o=True, force=True)

cmds.setAttr('Ma_root.translate', 0, 0, -55)
cmds.setAttr('Ma_root.rotateY', 0)
cmds.setAttr('Huang_root.translate', 48, 0, 28)
cmds.setAttr('Huang_root.rotateY', -120)
cmds.setAttr('Shiye_root.translate', -48, 0, 28)
cmds.setAttr('Shiye_root.rotateY', 120)

for c in (cmds.ls('CAM_check*') or []):
    cmds.delete(c)
wide = cmds.camera(name='CAM_check', focalLength=35)
wide_t = wide[0] if isinstance(wide, (list, tuple)) else wide
cmds.setAttr(wide_t + '.translate', 0, 170, 330)
cmds.setAttr(wide_t + '.rotate', -14, 0, 0)
P("wide_t=" + wide_t)

for t in (cmds.ls(transforms=True) or []):
    try:
        bb = cmds.exactWorldBoundingBox(t)
        dx, dy, dz = bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]
        if max(dx, dy, dz) > 250:
            P("BIG %s dx=%.0f dy=%.0f dz=%.0f ctr=(%.0f,%.0f,%.0f)" % (
                t, dx, dy, dz, (bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2))
    except Exception:
        pass

panels = cmds.getPanel(type='modelPanel') or []
P("panels=%s" % panels)
if panels:
    cmds.modelEditor(panels[0], e=True, camera=wide_t, grid=False, hud=False)
cmds.currentTime(1)
cmds.playblast(frame=[1], format='image', filename=W + r"\qa\CAM_check",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression='png')
cmds.file(rename=W + r"\scenes\p3_set.mb")
cmds.file(save=True, force=True, type='mayaBinary')
P("SAVED")
print("SEAT2_DONE")
'''

r = py(CODE, timeout=600)
print(r[-2500:])
