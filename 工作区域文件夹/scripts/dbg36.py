import os, glob
import maya.cmds as cmds
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
cam = cmds.ls("DS_S036_CAM*")[0]
shape = cmds.listRelatives(cam, shapes=True)[0]
old = cmds.getAttr(shape + ".focalLength")
cmds.setAttr(shape + ".focalLength", 32.0)
panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
cmds.lookThru(panel, cam)
cmds.currentTime(1916)
cmds.refresh(force=True)
cmds.playblast(frame=1916, format="image", filename=os.path.join(ROOT, "render", "dbg36"),
               sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
               offScreen=True, percent=100, widthHeight=(960, 540), quality=80, compression="png")
cmds.setAttr(shape + ".focalLength", old)
print("ok")
