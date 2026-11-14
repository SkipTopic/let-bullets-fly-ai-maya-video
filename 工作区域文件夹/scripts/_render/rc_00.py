import maya.cmds as cmds
import os
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
cmds.modelEditor(mp, e=True, camera="CAM_WIDE")
SHOTS = [(1, 1, 56), (2, 57, 103), (3, 104, 193), (4, 194, 251), (5, 252, 288), (6, 289, 314)]
for tag, f0, f1 in SHOTS:
    d = W + ("/frames/S%03d" % tag)
    os.makedirs(d, exist_ok=True)
    cmds.currentTime(f0)
    cmds.playblast(frame=list(range(f0, f1 + 1)), format="image", filename=d + "/S%03d" % tag,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression="png")
    P("shot %03d done" % tag)
