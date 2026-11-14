# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
cmds.currentTime(1)
try:
    cmds.ogs(render=True, frame=1, camera="CAM_S1",
             filename=W + "/qa/ogs_S001.png", width=854, height=480)
    P("ogs ok")
except Exception as e:
    P("ogs fail: %s" % e)
P("OGS_DONE")
'''
r = py(CODE, timeout=600)
print(r[-300:])
