# ---- S067 ----
cam = cmds.camera(name='CAM_S067')[0]
shp = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(shp + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 132, 194)
cmds.setAttr(cam + '.rotateY', 0.68)
cmds.setAttr(cam + '.rotateX', -11.02)
cmds.setAttr(cam + '.rotateZ', 0)
cmds.setKeyframe(cam + '.rotateX', t=3126)
cmds.setKeyframe(cam + '.rotateY', t=3126)
cmds.setKeyframe(cam + '.rotateZ', t=3126)
blink_loop_all(3126, 3202)
sway('Ma', 3126, 3202, 0.9)
sway('Huang', 3126, 3202, 0.9)
sway('Shiye', 3126, 3202, 1.4)

# ---- S068 ----
cam = cmds.camera(name='CAM_S068')[0]
shp = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(shp + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 22, 132, 194)
cmds.setAttr(cam + '.rotateY', -0.68)
cmds.setAttr(cam + '.rotateX', -11.02)
cmds.setAttr(cam + '.rotateZ', 0)
cmds.setKeyframe(cam + '.rotateX', t=3203)
cmds.setKeyframe(cam + '.rotateY', t=3203)
cmds.setKeyframe(cam + '.rotateZ', t=3203)
blink_loop_all(3203, 3327)
sway('Ma', 3203, 3327, 0.9)
sway('Huang', 3203, 3327, 1.4)
sway('Shiye', 3203, 3327, 0.9)

# ---- S069 ----
cam = cmds.camera(name='CAM_S069')[0]
shp = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(shp + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 132, 194)
cmds.setAttr(cam + '.rotateY', 0.68)
cmds.setAttr(cam + '.rotateX', -11.02)
cmds.setAttr(cam + '.rotateZ', 0)
cmds.setKeyframe(cam + '.rotateX', t=3328)
cmds.setKeyframe(cam + '.rotateY', t=3328)
cmds.setKeyframe(cam + '.rotateZ', t=3328)
blink_loop_all(3328, 3443)
sway('Ma', 3328, 3443, 0.9)
sway('Huang', 3328, 3443, 0.9)
sway('Shiye', 3328, 3443, 1.4)

# ---- S070 ----
cam = cmds.camera(name='CAM_S070')[0]
shp = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(shp + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 132, 194)
cmds.setAttr(cam + '.rotateY', 0.68)
cmds.setAttr(cam + '.rotateX', -11.02)
cmds.setAttr(cam + '.rotateZ', 0)
cmds.setKeyframe(cam + '.rotateX', t=3444)
cmds.setKeyframe(cam + '.rotateY', t=3444)
cmds.setKeyframe(cam + '.rotateZ', t=3444)
blink_loop_all(3444, 3467)
sway('Ma', 3444, 3467, 0.9)
sway('Huang', 3444, 3467, 0.9)
sway('Shiye', 3444, 3467, 1.4)

# ---- S071 ----
cam = cmds.camera(name='CAM_S071')[0]
shp = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(shp + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 132, 194)
cmds.setAttr(cam + '.rotateY', 0.68)
cmds.setAttr(cam + '.rotateX', -11.02)
cmds.setAttr(cam + '.rotateZ', 0)
cmds.setKeyframe(cam + '.rotateX', t=3468)
cmds.setKeyframe(cam + '.rotateY', t=3468)
cmds.setKeyframe(cam + '.rotateZ', t=3468)
cmds.setAttr(cam + '.translateX', 8)
cmds.setKeyframe(cam + '.translateX', t=3468)
cmds.setKeyframe(cam + '.translateX', t=3512)
cmds.setAttr(cam + '.rotateY', 13.39)
cmds.setAttr(cam + '.rotateX', -10.73)
cmds.setKeyframe(cam + '.rotateX', t=3512)
cmds.setKeyframe(cam + '.rotateY', t=3512)
cmds.setKeyframe(cam + '.rotateZ', t=3512)
blink_loop_all(3468, 3512)
sway('Ma', 3468, 3512, 0.9)
sway('Huang', 3468, 3512, 0.9)
sway('Shiye', 3468, 3512, 1.4)