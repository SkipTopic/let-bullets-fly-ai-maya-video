# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
# 1) delete DUM leftovers
n = 0
for c in (cmds.ls("DUM_*") or []):
    try:
        cmds.delete(c); n += 1
    except Exception:
        pass
P("dum deleted=%d" % n)
# 2) raise three characters: +32 cm each so heads clear table/backrest
for pat in ("*MakotoFBXASC032Yuki_mesh", "*AragakiFBXASC032Shinjiro_mesh", "*JunpeiFBXASC032Iori_mesh",
            "*MakotoFBXASC032Yuki_arm", "*AragakiFBXASC032Shinjiro_arm", "*JunpeiFBXASC032Iori_arm"):
    l = cmds.ls(pat) or []
    if not l:
        continue
    t = l[0]
    try:
        cmds.setAttr(t + ".translateY", lock=False)
    except Exception:
        pass
    try:
        cmds.setAttr(t + ".translateY", cmds.getAttr(t + ".translateY") + 32)
    except Exception as e:
        P("raise fail %s: %s" % (t, e))
m = (cmds.ls("*MakotoFBXASC032Yuki_mesh") or [None])[0]
if m:
    bb = cmds.exactWorldBoundingBox(m)
    P("Ma bb now top=%.0f" % bb[4])
# 3) verify render
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
cmds.modelEditor(mp, e=True, camera="CAM_S1")
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/sprint_S001",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("SPRINT_SETUP_DONE")
'''
r = py(CODE, timeout=600)
print(r[-500:])
