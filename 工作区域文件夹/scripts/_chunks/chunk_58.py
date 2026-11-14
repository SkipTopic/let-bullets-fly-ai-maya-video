# ---- S058 ----
cam = cmds.camera(name='CAM_S058')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S058')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2797)
cmds.setKeyframe(cam + '.rotateY', t=2797)
cmds.setKeyframe(cam + '.rotateZ', t=2797)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2797, 2841)
breath('Ma', 2797, 2841)
breath('Huang', 2797, 2841)
breath('Shiye', 2797, 2841)
glance('Ma', 'Huang', 2819)
