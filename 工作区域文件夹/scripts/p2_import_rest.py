# -*- coding: utf-8 -*-
"""P2: import remaining two characters, set triangle seating around table,
T-pose arm droop calibration, verify blink on all three."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import math

P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"

def import_fbx(path, ns):
    cmds.loadPlugin('fbxmaya', quiet=True)
    cmds.file(path, i=True, type="FBX", ignoreVersion=True,
              mergeNamespacesOnClash=False, namespace=ns,
              options="v=0;", pr=True, ra=True)

if not cmds.objExists('CH_Ma_root'):
    import_fbx(W + r"\models_fbx\CH_Ma.fbx", "CH_Ma")
import_fbx(W + r"\models_fbx\CH_Huang.fbx", "CH_Huang")
import_fbx(W + r"\models_fbx\CH_Shiye.fbx", "CH_Shiye")

# group each character under a root group for clean transform
def wrap(ns, rootname):
    top = []
    for o in cmds.ls(ns + ':*', transforms=True) or []:
        if ':' in o and len(o.split(':')) == 2:
            p = cmds.listRelatives(o, parent=True) or []
            if not p or not p[0].startswith(ns + ':'):
                top.append(o)
    g = cmds.group(em=True, name=rootname)
    for t in top:
        cmds.parent(t, g)
    return g

g_m = wrap('CH_Ma', 'CH_Ma_root')
g_h = wrap('CH_Huang', 'CH_Huang_root')
g_s = wrap('CH_Shiye', 'CH_Shiye_root')

# seating: round table center at origin, diameter 180 (cm). radius 90.
# Ma at 12 o'clock (facing -Z toward camera side... decide: camera looks from +Z)
# Ma: z=+55 (near camera), Huang at 4 o'clock, Shiye at 8 o'clock
cmds.setAttr(g_m + '.translate', 0, 0, 55)
cmds.setAttr(g_m + '.rotateY', 180)          # face -Z? MMD models face +Z by default in FBX(-Z forward). We'll verify by test render.
cmds.setAttr(g_h + '.translate', 47.6, 0, -27.5)
cmds.setAttr(g_h + '.rotateY', 60)
cmds.setAttr(g_s + '.translate', -47.6, 0, -27.5)
cmds.setAttr(g_s + '.rotateY', -60)

# T-pose arm droop: rotate arms down ~68deg, elbows bend 15
def droop(ns):
    j = cmds.ls(ns + ':LeftArm', ns + ':RightArm') or []
    for a in j:
        rz = cmds.getAttr(a + '.rotateZ')
        cmds.setAttr(a + '.rotateZ', rz + (68 if 'Left' in a else -68))
    e = cmds.ls(ns + ':LeftForeArm', ns + ':RightForeArm') or []
    for a in e:
        cmds.setAttr(a + '.rotateY', 15 if 'Left' in a else -15)
    return j

P("droop_ma=%s" % droop('CH_Ma'))
P("droop_huang=%s" % droop('CH_Huang'))
P("droop_shiye=%s" % droop('CH_Shiye'))

# verify blink on all three
for ns in ('CH_Ma', 'CH_Huang', 'CH_Shiye'):
    bs = [b for b in (cmds.ls(type='blendShape') or []) if b.startswith(ns + ':')]
    ok = False
    for b in bs:
        als = cmds.aliasAttr(b, q=True) or []
        if isinstance(als, list) and 'blink' in als:
            attr = '%s.%s' % (b, 'weight[9]')
            # find index by alias
            idx = None
            for k in range(0, len(als), 2):
                if als[k] == 'blink':
                    idx = als[k + 1]
            if idx:
                cmds.setAttr('%s.%s' % (b, idx), 1.0)
                v = cmds.getAttr('%s.%s' % (b, idx))
                cmds.setAttr('%s.%s' % (b, idx), 0.0)
                P("%s blink=%s idx=%s" % (ns, v, idx))
                ok = True
                break
    if not ok:
        P("%s blink=MISSING bs=%s" % (ns, bs))

# joint/mesh stats per char
for ns in ('CH_Ma', 'CH_Huang', 'CH_Shiye'):
    P("%s joints=%d meshes=%d" % (ns, len(cmds.ls(ns + ':*', type='joint') or []),
                                  len(cmds.ls(ns + ':*', type='mesh') or [])))

# save this state as the character base scene
cmds.file(rename=W + r"\scenes\p2_characters.mb")
cmds.file(save=True, force=True, type='mayaBinary')
P("SAVED p2_characters.mb")
print("P2_IMPORT_DONE")
'''

r = py(CODE, timeout=900)
print(r[-3000:])
