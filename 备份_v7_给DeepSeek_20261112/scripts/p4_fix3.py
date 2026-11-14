# -*- coding: utf-8 -*-
"""Fix per WorkBuddy review: upright+fit characters, lights on, verify with renders."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"
cmds.file(W + "/scenes/p4_simple.mb", o=True, force=True)

CHARS = {
    "Ma": ("*MakotoFBXASC032Yuki_arm", "*MakotoFBXASC032Yuki_mesh", (0, -100), 180),
    "Huang": ("*AragakiFBXASC032Shinjiro_arm", "*AragakiFBXASC032Shinjiro_mesh", (44, 26), 120),
    "Shiye": ("*JunpeiFBXASC032Iori_arm", "*JunpeiFBXASC032Iori_mesh", (-44, 26), -120),
}

def bbox_top_h(node):
    bb = cmds.exactWorldBoundingBox(node)
    return bb[4], bb[4] - bb[1], bb

report = []
for tag, (pa, pm, (x, z), ry) in CHARS.items():
    arm = (cmds.ls(pa) or [None])[0]
    mesh = (cmds.ls(pm) or [None])[0]
    if not arm or not mesh:
        P("MISS " + tag)
        continue
    # --- A. upright the mesh: rotateX -90 -> 0, keep scale=100
    try:
        cmds.setAttr(mesh + ".rotateX", lock=False)
    except Exception:
        pass
    rx = cmds.getAttr(mesh + ".rotateX")
    if abs(rx + 90) < 1:
        cmds.setAttr(mesh + ".rotateX", 0)
    # --- B. scale to height 175 via bbox loop (mesh only; skin follows mesh transform)
    for ax in ("scaleX", "scaleY", "scaleZ", "rotateX", "rotateY", "rotateZ",
               "translateX", "translateY", "translateZ"):
        try:
            cmds.setAttr(mesh + "." + ax, lock=False)
        except Exception:
            pass
    for _ in range(4):
        top, h, bb = bbox_top_h(mesh)
        if h < 1:
            break
        s = cmds.getAttr(mesh + ".scaleY")
        cmds.setAttr(mesh + ".scaleY", s * 175.0 / h)
    # --- C. place: feet on floor -> shift so bbox bottom = 0, head ~ 160
    top, h, bb = bbox_top_h(mesh)
    dy = -bb[1]
    ty = cmds.getAttr(mesh + ".translateY")
    try:
        cmds.setAttr(mesh + ".translateY", lock=False)
    except Exception:
        pass
    cmds.setAttr(mesh + ".translateY", ty + dy)
    # seat them: hips to chair 44 => shift down 40 (torso above table 75)
    cmds.setAttr(mesh + ".translateY", cmds.getAttr(mesh + ".translateY") - 40)
    # --- D. rotate to face table center & move to seat pos
    cmds.setAttr(mesh + ".rotateY", ry)
    tx = cmds.getAttr(mesh + ".translateX")
    tz = cmds.getAttr(mesh + ".translateZ")
    cmds.setAttr(mesh + ".translateX", x)
    cmds.setAttr(mesh + ".translateZ", z)
    # --- E. arm follows: same rotateY/translate as mesh (joints drive skin)
    try:
        for attr in ("translateX", "translateY", "translateZ", "rotateY"):
            try:
                cmds.setAttr(arm + "." + attr, lock=False)
            except Exception:
                pass
        cmds.setAttr(arm + ".rotateY", ry)
        cmds.setAttr(arm + ".translate", x, cmds.getAttr(arm + ".translateY"), z)
    except Exception as e:
        P("arm move fail %s: %s" % (tag, e))
    top, h, bb = bbox_top_h(mesh)
    report.append((tag, round(top, 1), round(h, 1)))

P("FIT REPORT (top, height): %s" % report)

# --- F. lights on: shadows + all lights + darken walls
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, shadows=True, displayLights="all",
                 grid=False, hud=False, joints=False)
for m in cmds.ls("SET_wall*", "SET_panel*") or []:
    shape = m if cmds.nodeType(m) == "mesh" else (cmds.listRelatives(m, s=True) or [None])[0]
    if not shape:
        continue
    sg = cmds.listConnections(shape + ".instObjGroups[0]", d=False) or []
    for s in sg:
        mats = cmds.listConnections(s + ".surfaceShader") or []
        for mat in mats:
            try:
                cmds.setAttr(mat + ".color", 0.10, 0.045, 0.035, type="double3")
            except Exception:
                pass
P("lights+dark walls done")

# --- G. playback range
cmds.playbackOptions(min=1, max=3512)

# --- H. verify render: wide + one near cam
cmds.modelEditor(mp, e=True, camera="CAM_S1")
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/fix3_S001",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.modelEditor(mp, e=True, camera="CAM_WIDE" if cmds.objExists("CAM_WIDE") else "persp")
cmds.playblast(frame=[1], format="image", filename=W + "/qa/fix3_wide",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("FIX3_DONE")
'''

r = py(CODE, timeout=900)
print(r[-1500:])
