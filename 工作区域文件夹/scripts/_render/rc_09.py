import maya.cmds as cmds
import os
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)
cmds.modelEditor(mp, e=True, camera="CAM_WIDE")
SHOTS = [(55, 2658, 2687), (56, 2688, 2736), (57, 2737, 2796), (58, 2797, 2841), (59, 2842, 2877), (60, 2878, 2945)]
for tag, f0, f1 in SHOTS:
    d = W + ("/frames/S%03d" % tag)
    os.makedirs(d, exist_ok=True)
    cmds.currentTime(f0)
    cmds.playblast(frame=list(range(f0, f1 + 1)), format="image", filename=d + "/S%03d" % tag,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression="png")
    P("shot %03d done" % tag)
