# -*- coding: utf-8 -*-
"""P2 fix: rebuild characters with per-node prefix, hide morph targets,
save per-char scenes + combined scene with seating & droop & blink check."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import math

P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
CHARS = [
    ("Ma",    W + r"\models_fbx\CH_Ma.fbx"),
    ("Huang", W + r"\models_fbx\CH_Huang.fbx"),
    ("Shiye", W + r"\models_fbx\CH_Shiye.fbx"),
]

cmds.loadPlugin('fbxmaya', quiet=True)

def rename_all_dag(prefix):
    n = 0
    dag = cmds.ls(dag=True, long=True) or []
    for path in reversed(dag):
        short = path.split('|')[-1]
        if short.startswith(prefix + '_'):
            continue
        new = prefix + '_' + short.replace('FBXASC032', '_')
        try:
            cmds.rename(path, new)
            n += 1
        except Exception:
            pass
    # non-DAG nodes (deformers)
    for typ in ('blendShape', 'skinCluster', 'transformGeometry'):
        for nd in cmds.ls(type=typ) or []:
            if not nd.startswith(prefix + '_'):
                try:
                    cmds.rename(nd, prefix + '_' + nd.replace('FBXASC032', '_'))
                    n += 1
                except Exception:
                    pass
    return n

for tag, fbx in CHARS:
    cmds.file(new=True, force=True)
    cmds.file(fbx, i=True, type="FBX", ignoreVersion=True,
              options="v=0;", pr=True, ra=True)
    n = rename_all_dag(tag)
    # identify morph-target top-level meshes: shapes named like blink/trouble/wink...
    MORPH_HINTS = ('blink', 'wink', 'trouble', 'gentle', 'half_eye', 'keen', 'laugh',
                   'smile', 'surprise', 'serious', 'anger', 'pupil', 'mouth_',
                   'eye_up', 'eye_down', 'mmd_sdef', 'Basis')
    tops = [o for o in (cmds.ls(assemblies=True) or [])]
    keep, morphs = [], []
    pref = tag + '_'
    for t in tops:
        base = t[len(pref):] if t.startswith(pref) else t
        if any(base == h or base.startswith(h) for h in ('blink', 'wink', 'trouble', 'gentle', 'half_eye', 'keen', 'laugh', 'smile', 'smile2', 'surprise', 'serious', 'anger', 'pupil', 'mouth_', 'eye_up', 'eye_down', 'mmd_sdef')):
            morphs.append(t)
        else:
            keep.append(t)
    # hide morph targets
    for m in morphs:
        try:
            cmds.setAttr(m + '.visibility', False)
        except Exception:
            pass
    # group everything
    g = cmds.group(em=True, name='%s_root' % tag)
    for t in keep + morphs:
        try:
            cmds.parent(t, g)
        except Exception:
            pass
    out = W + r"\scenes\p2_ch_%s.mb" % tag
    cmds.file(rename=out)
    cmds.file(save=True, force=True, type='mayaBinary')
    nj = len(cmds.ls(type='joint') or [])
    P("%s renamed=%d joints=%d tops_keep=%s morphs=%d" % (tag, n, nj, len(keep), len(morphs)))

# combined scene
cmds.file(new=True, force=True)
for tag, _f in CHARS:
    cmds.file(W + r"\scenes\p2_ch_%s.mb" % tag, i=True)

# seating positions (cm units; table center origin, diameter 180)
place = {
    'Ma_root':    (0, 0, 62, 180),
    'Huang_root': (52, 0, -30, 120),
    'Shiye_root': (-52, 0, -30, -120),
}
for g, (x, y, z, ry) in place.items():
    if cmds.objExists(g):
        cmds.setAttr(g + '.translate', x, y, z)
        cmds.setAttr(g + '.rotateY', ry)

# T-pose arm droop
def joints_with(tag, name):
    return [j for j in (cmds.ls(type='joint') or []) if j.startswith(tag + '_') and j.endswith(name)]

for tag in ('Ma', 'Huang', 'Shiye'):
    for side, sign in (('Left', 1), ('Right', -1)):
        arms = joints_with(tag, side + 'Arm')
        for a in arms:
            try:
                cmds.setAttr(a + '.rotateZ', 68 * sign)
            except Exception as e:
                P("droop_fail %s: %s" % (a, e))
        elbs = joints_with(tag, side + 'ForeArm')
        for e in elbs:
            try:
                cmds.setAttr(e + '.rotateY', 15 * sign)
            except Exception:
                pass

# stats & blink verify
for tag in ('Ma', 'Huang', 'Shiye'):
    jo = [j for j in cmds.ls(type='joint') or [] if j.startswith(tag + '_')]
    me = [m for m in cmds.ls(type='mesh') or [] if m.startswith(tag + '_')]
    P("%s joints=%d meshes=%d" % (tag, len(jo), len(me)))
    bs = [b for b in (cmds.ls(type='blendShape') or []) if b.startswith(tag + '_')]
    for b in bs:
        als = cmds.aliasAttr(b, q=True) or []
        if isinstance(als, list) and 'blink' in als:
            i = als.index('blink')
            idx = als[i + 1]
            cmds.setAttr('%s.%s' % (b, idx), 1.0)
            v = cmds.getAttr('%s.%s' % (b, idx))
            cmds.setAttr('%s.%s' % (b, idx), 0.0)
            P("%s blink idx=%s set=%s OK" % (tag, idx, v))
            break

cmds.file(rename=W + r"\scenes\p2_characters.mb")
cmds.file(save=True, force=True, type='mayaBinary')
P("SAVED p2_characters.mb")
print("P2_FIX_DONE")
'''

r = py(CODE, timeout=1800)
print(r[-3500:])
