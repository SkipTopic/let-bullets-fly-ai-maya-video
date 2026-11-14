import maya.cmds as cmds
import os
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
cmds.modelEditor(mp, e=True, camera="CAM_WIDE")
SHOTS = [(43, 2273, 2291), (44, 2292, 2312), (45, 2313, 2342), (46, 2343, 2369), (47, 2370, 2405), (48, 2406, 2453)]
for tag, f0, f1 in SHOTS:
    d = W + ("/frames/S%03d" % tag)
    os.makedirs(d, exist_ok=True)
    cmds.currentTime(f0)
    cmds.playblast(frame=list(range(f0, f1 + 1)), format="image", filename=d + "/S%03d" % tag,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression="png")
    P("shot %03d done" % tag)
