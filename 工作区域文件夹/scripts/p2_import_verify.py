# -*- coding: utf-8 -*-
"""P2: import CH_Ma.fbx into Maya via commandPort and verify bones/shapekeys/motion."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import maya.mel as mel
out = []
def log(s):
    print(s)
    out.append(str(s))

fbx = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_fbx\CH_Ma.fbx"
try:
    cmds.loadPlugin('fbxmaya', quiet=True)
except Exception:
    pass
# clean scene first
cmds.file(new=True, force=True)
cmds.file(fbx, i=True, type="FBX", ignoreVersion=True,
          mergeNamespacesOnClash=False, namespace="CH_Ma",
          options="v=0;", pr=True, ra=True)

joints = cmds.ls(type='joint') or []
meshes = cmds.ls(type='mesh') or []
log("JOINTS=%d MESHES=%d" % (len(joints), len(meshes)))

# blendshape check
bls = cmds.ls(type='blendShape') or []
log("BLENDSHAPES=%d" % len(bls))
blink_found = None
for b in bls:
    attrs = cmds.listAttr(b + '.' + 'weight') or []
    wlist = cmds.blendShape(b, q=True, weight=True) or []
    aliases = cmds.listAttr(b, keyable=True) or []
log("BS_NAMES=" + ",".join(bls[:5]))

# find blink channel on any blendShape
import re
for b in bls:
    chs = [a for a in (cmds.listAttr(b) or []) if 'blink' in a.lower()]
    if chs:
        blink_found = (b, chs[0])
        break
log("BLINK_CHANNEL=%s" % (blink_found,))

# height check: bounding box of all meshes
import maya.OpenMaya as om
miny, maxy = 1e9, -1e9
for m in meshes:
    bb = cmds.exactWorldBoundingBox(m)
    miny = min(miny, bb[1]); maxy = max(maxy, bb[4])
log("HEIGHT=%.3f" % (maxy - miny))

# motion test: rotate LeftArm and sample
arm = 'LeftArm'
cand = [j for j in joints if arm in j]
if cand:
    a = cand[0]
    cmds.setAttr(a + '.rotateZ', 40)
    log("ARM_ROTATE_OK %s=%.1f" % (a, cmds.getAttr(a + '.rotateZ')))
else:
    log("ARM_NOT_FOUND among %d joints" % len(joints))
    log("SAMPLE=" + ",".join(joints[:20]))

# blink drive test
if blink_found:
    b, ch = blink_found
    node = b
    # channel might be on shape node alias; try setAttr
    try:
        cmds.setAttr('%s.%s' % (node, ch), 1.0)
        v = cmds.getAttr('%s.%s' % (node, ch))
        log("BLINK_SET_OK=%s" % v)
        cmds.setAttr('%s.%s' % (node, ch), 0.0)
    except Exception as e:
        log("BLINK_SET_FAIL=%s" % e)
print("VERIFY_MARKER_DONE")
'''

r = py(CODE, timeout=600)
print(r[-2500:] if len(r) > 2500 else r)
