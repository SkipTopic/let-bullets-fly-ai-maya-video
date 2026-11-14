# ---- S052 ----
cam = cmds.camera(name='CAM_S052')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S052')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2550)
cmds.setKeyframe(cam + '.rotateY', t=2550)
cmds.setKeyframe(cam + '.rotateZ', t=2550)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2550, 2571)
breath('Ma', 2550, 2571)
breath('Huang', 2550, 2571)
breath('Shiye', 2550, 2571)
glance('Ma', 'Huang', 2560)
