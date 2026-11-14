# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

code = (
    "import maya.cmds as cmds\nP = print\n"
    "mp = \"modelPanel4\"\n"
    "cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)\n"
    "frames = {\"S001\": (1, 1), \"S030\": (1268, 30), \"S060\": (2489, 60)}\n"
    "for name, (f, n) in frames.items():\n"
    "    cam = \"CAM_S\" + str(n)\n"
    "    if not cmds.objExists(cam):\n        P(\"MISSING \" + cam)\n        continue\n"
    "    cmds.modelEditor(mp, e=True, camera=cam)\n    cmds.currentTime(f)\n"
    "    cmds.playblast(frame=[f], format=\"image\", filename=r\"@W\" + \"/qa/simple_\" + name,\n"
    "                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,\n"
    "                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression=\"png\")\n"
    "    P(\"rendered \" + name)\n"
    "cmds.file(rename=r\"@W\" + \"/scenes/p4_simple.mb\")\n"
    "cmds.file(save=True, force=True, type=\"mayaBinary\")\n"
    "P(\"SAVED p4_simple.mb\")\n"
).replace("@W", W)

r = py(code, timeout=900)
print(r[-500:])
