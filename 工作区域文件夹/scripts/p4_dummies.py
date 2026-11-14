# -*- coding: utf-8 -*-
"""Buddy-fallback: hide PMX, build 3 dummy figures (capsule+ball) seated at chairs,
with head-turn animation keys. Verify with renders."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import math
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

# 1) hide all PMX parts
hidden = 0
for pat in ("*MakotoFBXASC032Yuki*", "*AragakiFBXASC032Shinjiro*", "*JunpeiFBXASC032Iori*"):
    for t in (cmds.ls(pat) or []):
        try:
            cmds.setAttr(t + ".visibility", False)
            hidden += 1
        except Exception:
            pass
P("pmx hidden=%d" % hidden)

# 2) materials
def lam(name, rgb):
    if cmds.objExists(name + "SG"):
        return name
    m = cmds.shadingNode("lambert", asShader=True, name=name)
    cmds.setAttr(name + ".color", *rgb, type="double3")
    sg = cmds.sets(name=name + "SG", renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr(name + ".outColor", sg + ".surfaceShader")
    return name

m_cloth1 = lam("DUM_cloth1", (0.78, 0.74, 0.62))   # Ma light robe
m_cloth2 = lam("DUM_cloth2", (0.16, 0.17, 0.20))   # Huang dark suit
m_cloth3 = lam("DUM_cloth3", (0.55, 0.50, 0.40))   # Shiye beige
m_skin = lam("DUM_skin", (0.82, 0.62, 0.48))

# 3) build dummies
SEATS = {"Ma": ((0, -100), 180, m_cloth1), "Huang": ((44, 26), 120, m_cloth2), "Shiye": ((-44, 26), -120, m_cloth3)}
for tag, ((x, z), ry, mat) in SEATS.items():
    if cmds.objExists("DUM_" + tag):
        cmds.delete("DUM_" + tag)
    g = cmds.group(em=True, name="DUM_" + tag)[0]
    # torso capsule: r=16 h=58, center y=44+29=73
    torso = cmds.polyCylinder(r=16, h=58, sx=16, name="DUM_%s_torso" % tag)[0]
    cmds.setAttr(torso + ".translate", x, 73, z)
    cmds.sets(torso, e=True, forceElement=mat + "SG")
    # head ball r=11 at y=44+58+11=113
    head = cmds.polySphere(r=11, name="DUM_%s_head" % tag)[0]
    cmds.setAttr(head + ".translate", x, 113, z)
    cmds.sets(head, e=True, forceElement=m_skin + "SG")
    # arms: cylinders angled down-forward from shoulders y=95
    for side, s in (("L", 1), ("R", -1)):
        armc = cmds.polyCylinder(r=5, h=42, sx=8, name="DUM_%s_arm%s" % (tag, side))[0]
        cmds.setAttr(armc + ".translate", x + s * 20, 78, z + 6)
        cmds.setAttr(armc + ".rotateX", -55)
        cmds.sets(armc, e=True, forceElement=mat + "SG")
    # legs hint under table
    for side, s in (("L", 1), ("R", -1)):
        leg = cmds.polyCylinder(r=6, h=40, sx=8, name="DUM_%s_leg%s" % (tag, side))[0]
        cmds.setAttr(leg + ".translate", x + s * 8, 22, z + 18)
        cmds.sets(leg, e=True, forceElement=mat + "SG")

    # animation: head turn beats + torso sway (simple, reliable)
    hd = head
    for t0 in range(2, 3510, 90):
        t1 = t0 + 30
        cmds.setAttr(hd + ".rotateY", -8)
        cmds.setKeyframe(hd + ".rotateY", t=t0)
        cmds.setAttr(hd + ".rotateY", 8)
        cmds.setKeyframe(hd + ".rotateY", t=t1)
    for t0 in range(1, 3510, 55):
        cmds.setAttr(torso + ".rotateX", 1.2)
        cmds.setKeyframe(torso + ".rotateX", t=t0)
        cmds.setAttr(torso + ".rotateX", -0.8)
        cmds.setKeyframe(torso + ".rotateX", t=t0 + 27)

P("dummies built")

# 4) verify render S001
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
cmds.modelEditor(mp, e=True, camera="CAM_S1")
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/dummy_S001",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.modelEditor(mp, e=True, camera="CAM_S30")
cmds.currentTime(1268)
cmds.playblast(frame=[1268], format="image", filename=W + "/qa/dummy_S030",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("DUMMY_DONE")
'''

r = py(CODE, timeout=1200)
print(r[-1000:])
