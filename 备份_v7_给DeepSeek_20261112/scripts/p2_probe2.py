# -*- coding: utf-8 -*-
"""Probe blendShape channel names and mesh breakdown of imported CH_Ma."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
out = []
def P(s):
    print(s)

bls = cmds.ls(type='blendShape') or []
for b in bls:
    P("BS=" + b)
    # the deformer's target weights: listAttr on the node shows weight channels
    allattrs = cmds.listAttr(b, m=True) or []
    wattrs = [a for a in allattrs if a.startswith('weight')]
    P("  weight_attrs=%d" % len(wattrs))
    P("  first20=" + ",".join(wattrs[:20]))
    # aliases on shape node often carry nice names
    shapes = cmds.listConnections(b, s=True, d=False, type='shape') or []
    P("  shapes=" + ",".join(shapes[:3]))
    for sh in shapes[:1]:
        als = cmds.aliasAttr(sh, q=True) or []
        P("  alias_n=%d first30=%s" % (len(als), ",".join(als[:30]) if isinstance(als, list) else str(als)[:200]))

# mesh breakdown
meshes = cmds.ls(type='mesh') or []
P("NMESH=%d" % len(meshes))
tot = 0
for m in meshes[:35]:
    v = cmds.polyEvaluate(m, v=True)
    tot += v
    P("  %s v=%d" % (m, v))
P("VTOT=%d" % tot)
print("PROBE2_DONE")
'''

r = py(CODE, timeout=300)
print(r[-3000:])
