import maya.cmds as cmds
import os
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
SHOTS = [(67, 3126, 3202), (68, 3203, 3327), (69, 3328, 3443), (70, 3444, 3467), (71, 3468, 3512)]
for tag, f0, f1 in SHOTS:
    cam = "CAM_S%d" % tag
    if not cmds.objExists(cam):
        raise RuntimeError("missing camera " + cam)
    cmds.modelEditor(mp, e=True, camera=cam)
    d = W + ("/frames/S%03d" % tag)
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    cmds.currentTime(f0)
    cmds.playblast(frame=list(range(f0, f1 + 1)), format="image", filename=d + "/S%03d" % tag,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression="png")
    P("shot %03d done via " + cam)
