# ---- S054 ----
cam = cmds.camera(name='CAM_S054')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S054')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2643)
cmds.setKeyframe(cam + '.rotateY', t=2643)
cmds.setKeyframe(cam + '.rotateZ', t=2643)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2643, 2657)
breath('Ma', 2643, 2657)
breath('Huang', 2643, 2657)
breath('Shiye', 2643, 2657)
glance('Ma', 'Huang', 2650)
