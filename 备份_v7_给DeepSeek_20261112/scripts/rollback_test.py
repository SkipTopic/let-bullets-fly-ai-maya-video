# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
# undo the +32 raise on all six tops
for pat in ("*MakotoFBXASC032Yuki_mesh", "*AragakiFBXASC032Shinjiro_mesh", "*JunpeiFBXASC032Iori_mesh",
            "*MakotoFBXASC032Yuki_arm", "*AragakiFBXASC032Shinjiro_arm", "*JunpeiFBXASC032Iori_arm"):
    l = cmds.ls(pat) or []
    if l:
        t = l[0]
        try:
            cmds.setAttr(t + ".translateY", cmds.getAttr(t + ".translateY") - 32)
        except Exception:
            pass
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
cmds.modelEditor(mp, e=True, camera="CAM_S1")
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/rollback_S001",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("ROLLBACK_DONE")
'''
r = py(CODE, timeout=600)
print(r[-200:])
