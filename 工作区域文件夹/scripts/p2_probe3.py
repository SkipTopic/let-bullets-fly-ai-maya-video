# -*- coding: utf-8 -*-
"""Drive blink weight via indexed weight[] and alias lookup on the blendShape node."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds

bs = (cmds.ls(type='blendShape') or [None])[0]
P = print
if bs:
    # try indexed weights
    n = cmds.getAttr(bs + '.weight', size=True) if cmds.objExists(bs + '.weight') else -1
    P("weight_array_size=%s" % n)
    if n and n > 0:
        vals = cmds.getAttr(bs + '.weight')  # list of dicts
        P("weights_sample=%s" % str(vals[:3]))
    # aliases on the blendShape node itself
    als = cmds.aliasAttr(bs, q=True) or []
    P("bs_alias_n=%d" % (len(als) if isinstance(als, list) else -1))
    if isinstance(als, list):
        pairs = list(zip(als[0::2], als[1::2]))
        P("bs_alias_pairs=%s" % str(pairs[:12]))
        blink_pair = [p for p in pairs if 'blink' in p[0].lower()]
        P("blink_pair=%s" % blink_pair)
        if blink_pair:
            attr = '%s.%s' % (bs, blink_pair[0][0])
            cmds.setAttr(attr, 1.0)
            P("SET1=%s" % cmds.getAttr(attr))
            cmds.setAttr(attr, 0.0)
            P("SET0=%s" % cmds.getAttr(attr))
print("PROBE3_DONE")
'''

r = py(CODE, timeout=300)
print(r[-2000:])
