# -*- coding: utf-8 -*-
"""P2 v2: clean re-import of all three characters.
No rename, no reparent, no droop. One scene file per character.
Then combined scene: import all three, auto-detect suffixes, verify skinning
by vertex-height, apply sit pose, render checks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
cmds.loadPlugin('fbxmaya', quiet=True)

def vtop(m):
    import maya.OpenMaya as om
    sl = om.MSelectionList()
    try:
        sl.add(m)
    except Exception:
        return None
    dag = om.MDagPath()
    sl.getDagPath(0, dag)
    it = om.MItMeshVertex(dag)
    ymax = -1e9
    while not it.isDone():
        p = it.position(om.MSpace.kWorld)
        if p[1] > ymax:
            ymax = p[1]
        it.next()
    return ymax

stats = {}
for tag, fb in (("Ma", "CH_Ma.fbx"), ("Huang", "CH_Huang.fbx"), ("Shiye", "CH_Shiye.fbx")):
    cmds.file(new=True, force=True)
    cmds.file(W + "/models_fbx/" + fb, i=True, type="FBX", ignoreVersion=True,
              options="v=0;", pr=True, ra=True)
    meshes = cmds.ls(type="mesh") or []
    nj = len(cmds.ls(type="joint") or [])
    # main mesh = the one with most verts
    main, mv = None, -1
    for m in meshes:
        try:
            v = cmds.polyEvaluate(m, v=True)
            if v > mv:
                mv, main = v, m
        except Exception:
            pass
    ytop = vtop(main) if main else None
    stats[tag] = {"joints": nj, "nmesh": len(meshes), "main": main, "verts": mv, "ytop": ytop}
    P("%s joints=%d main=%s verts=%s ytop=%s" % (tag, nj, main, mv, ytop))
    cmds.file(rename=W + "/scenes/p2v2_%s.mb" % tag)
    cmds.file(save=True, force=True, type="mayaBinary")

# combined
cmds.file(new=True, force=True)
suffix = {}
for tag in ("Ma", "Huang", "Shiye"):
    before = set(cmds.ls(transforms=True, long=True) or [])
    cmds.file(W + "/scenes/p2v2_%s.mb" % tag, i=True)
    after = set(cmds.ls(transforms=True, long=True) or [])
    newt = [t for t in (after - before)]
    # find the armature/joints of this import: joints whose top-parent is in newt
    ns_j = []
    for t in newt:
        short = t.split("|")[-1]
        ns_j.append(short)
    suffix[tag] = ns_j
    P("%s imported tops=%d e.g. %s" % (tag, len(newt), ns_j[:4]))

# place roots: find top transform that has joint descendants
def top_of_joints(tag):
    js = cmds.ls(type="joint") or []
    # group joints by top ancestor
    return js

# simple approach: move every top-level transform group that contains joints
tops = cmds.ls(assemblies=True) or []
P("assemblies=%s" % tops)

print("P2V2_DONE")
'''

r = py(CODE, timeout=1200)
print(r[-3000:])
