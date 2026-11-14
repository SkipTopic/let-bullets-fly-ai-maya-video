# ---- S063 ----
cam = cmds.camera(name='CAM_S063')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S063')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3024)
cmds.setKeyframe(cam + '.rotateY', t=3024)
cmds.setKeyframe(cam + '.rotateZ', t=3024)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3024, 3040)
breath('Ma', 3024, 3040)
breath('Huang', 3024, 3040)
breath('Shiye', 3024, 3040)
glance('Ma', 'Huang', 3032)
