# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
P = print
# current scene has CH_Ma + CH_Huang + CH_Shiye imported without namespaces
tops = [o for o in (cmds.ls(transforms=True) or []) if cmds.listRelatives(o, parent=True) is None]
P("TOPS:")
for t in tops:
    P("  " + t)
jo = cmds.ls(type='joint') or []
P("NJOINT=%d" % len(jo))
import collections
pref = collections.Counter()
for j in jo:
    pref[j.split('|')[-1].split('_')[0]] += 1
P("JOINT_PREFIX=%s" % dict(list(pref.items())[:10]))
P("SAMPLE_JOINTS=" + ",".join(jo[:8]))
print("PROBE4_DONE")
'''

r = py(CODE, timeout=300)
print(r[-2500:])
