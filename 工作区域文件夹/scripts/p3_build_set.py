# -*- coding: utf-8 -*-
"""P3: build the banquet set in Maya (units cm) + lighting + CAM_TEMPLATE.

Set pieces: round table, 3 chairs, 2 candelabra (emissive+point lights),
wall panels, lattice window, flowers, floor, table props. Flat Lambert colors.
"""
CODE = r'''
import maya.cmds as cmds
import math

P = print
W = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"

# start from character scene
cmds.file(W + r"\scenes\p2_characters.mb", o=True, force=True)

# clean any prior set build (idempotent re-run)
for pat in ('SET_*', 'prop_*', 'L_*', 'PL_*', 'CAM_TEMPLATE*'):
    for o in cmds.ls(pat) or []:
        try:
            cmds.delete(o)
        except Exception:
            pass

def lam(name, rgb):
    if cmds.objExists(name + 'SG'):
        return name
    m = cmds.shadingNode('lambert', asShader=True, name=name)
    cmds.setAttr(name + '.color', *rgb, type='double3')
    sg = cmds.sets(name=name + 'SG', renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr(name + '.outColor', sg + '.surfaceShader')
    return name

def assign(objs, shader):
    cmds.sets(objs, e=True, forceElement=shader + 'SG')

def poly(name, ptype, **kw):
    n = cmds.polyCreateFacet if False else None
    obj = cmds.polyPrimitive if False else None
    if ptype == 'cyl':
        r = kw.get('r', 10); h = kw.get('h', 10)
        o = cmds.polyCylinder(r=r, h=h, sx=24, name=name)[0]
    elif ptype == 'cube':
        o = cmds.polyCube(w=kw.get('w',10), h=kw.get('h',10), d=kw.get('d',10), name=name)[0]
    elif ptype == 'sph':
        o = cmds.polySphere(r=kw.get('r',10), name=name)[0]
    elif ptype == 'cone':
        o = cmds.polyCone(r=kw.get('r',10), h=kw.get('h',10), name=name)[0]
    elif ptype == 'torus':
        o = cmds.polyTorus(r=kw.get('r',10), sr=kw.get('sr',1), name=name)[0]
    elif ptype == 'plane':
        o = cmds.polyPlane(w=kw.get('w',10), h=kw.get('h',10), name=name)[0]
    return o

# ---- materials ----
m_floor = lam('M_floor', (0.10, 0.06, 0.045))
m_wall  = lam('M_wall', (0.16, 0.05, 0.045))
m_panel = lam('M_panel', (0.24, 0.08, 0.06))
m_table = lam('M_table', (0.22, 0.10, 0.07))
m_wood  = lam('M_wood', (0.18, 0.09, 0.06))
m_cloth = lam('M_cloth', (0.55, 0.50, 0.42))
m_candle= lam('M_candle', (0.90, 0.80, 0.55))
m_fire  = cmds.shadingNode('lambert', asShader=True, name='M_fire')
cmds.setAttr('M_fire.incandescence', 1.0, 0.55, 0.18, type='double3')
cmds.setAttr('M_fire.color', 1.0, 0.6, 0.2, type='double3')
if not cmds.objExists('M_fireSG'):
    _sg = cmds.sets(name='M_fireSG', renderable=True, noSurfaceShader=True, empty=True)
    cmds.connectAttr('M_fire.outColor', 'M_fireSG.surfaceShader')
m_glass = lam('M_glass', (0.45, 0.55, 0.40))
m_gold  = lam('M_gold', (0.55, 0.38, 0.15))
m_paper = lam('M_paper', (0.85, 0.75, 0.50))
cmds.setAttr('M_paper.incandescence', 0.25, 0.18, 0.08, type='double3')
m_flower= lam('M_flower', (0.55, 0.10, 0.10))
m_green = lam('M_green', (0.12, 0.22, 0.08))
m_bowl  = lam('M_bowl', (0.75, 0.72, 0.65))

objs = []

# ---- floor ----
f = poly('SET_floor', 'plane', w=900, h=900)
cmds.setAttr(f + '.translateY', 0)
assign([f], m_floor); objs.append(f)

# ---- walls: back (-Z), left (-X), right (+X) ----
for wname, pos, rot, w, h in (
    ('SET_wallB', (0, 150, -260), (0, 0, 0), 620, 300),
    ('SET_wallL', (-260, 150, 0), (0, 90, 0), 620, 300),
    ('SET_wallR', (260, 150, 0), (0, 90, 0), 620, 300),
):
    wll = poly(wname, 'cube', w=w, h=h, d=6)
    cmds.setAttr(wll + '.translate', *pos)
    cmds.setAttr(wll + '.rotate', *rot)
    assign([wll], m_wall); objs.append(wll)

# ---- wall panels (lower 120cm, dark red wood) ----
for pname, pos, rot, w in (
    ('SET_panelB', (0, 60, -255), (0, 0, 0), 620),
    ('SET_panelL', (-255, 60, 0), (0, 90, 0), 620),
    ('SET_panelR', (255, 60, 0), (0, 90, 0), 620),
):
    pn = poly(pname, 'cube', w=w, h=120, d=3)
    cmds.setAttr(pn + '.translate', *pos)
    cmds.setAttr(pn + '.rotate', *rot)
    assign([pn], m_panel); objs.append(pn)

# ---- lattice window on back wall ----
win = cmds.group(em=True, name='SET_window')
fw = poly('SET_winFrame', 'cube', w=200, h=150, d=4)
cmds.setAttr(fw + '.translate', -40, 175, -252)
cmds.setAttr(fw + '.visibility', False)
paper = poly('SET_winPaper', 'plane', w=190, h=140)
cmds.setAttr(paper + '.translate', -40, 175, -251.5)
assign([paper], m_paper); objs.append(paper)
# lattice bars
for i in range(7):
    b = poly('SET_winBarV%d' % i, 'cube', w=3, h=140, d=2)
    cmds.setAttr(b + '.translate', -130 + i * 30, 175, -250)
    assign([b], m_wood); objs.append(b)
for j in range(5):
    b = poly('SET_winBarH%d' % j, 'cube', w=190, h=3, d=2)
    cmds.setAttr(b + '.translate', -40, 110 + j * 32, -250)
    assign([b], m_wood); objs.append(b)

# ---- round table ----
top = poly('SET_tableTop', 'cyl', r=90, h=6)
cmds.setAttr(top + '.translateY', 72)
assign([top], m_table); objs.append(top)
leg = poly('SET_tableLeg', 'cyl', r=14, h=70)
cmds.setAttr(leg + '.translateY', 35)
assign([leg], m_wood); objs.append(leg)
base = poly('SET_tableBase', 'cyl', r=35, h=5)
cmds.setAttr(base + '.translateY', 2.5)
assign([base], m_wood); objs.append(base)

# ---- 3 chairs (high back), at seats facing table center ----
chair_pos = [('chairMa', 0, -92, 0), ('chairHuang', 92, 46, -150), ('chairShiye', -92, 46, 150)]
for cname, cx, cz, cry in chair_pos:
    cg = cmds.group(em=True, name='SET_' + cname)
    seat = poly(cname + '_seat', 'cube', w=48, h=5, d=46)
    cmds.setAttr(seat + '.translate', cx, 44, cz)
    assign([seat], m_wood); objs.append(seat)
    back = poly(cname + '_back', 'cube', w=48, h=110, d=5)
    bz = cz + (23 if cz < 0 else -23)
    cmds.setAttr(back + '.translate', cx, 100, bz)
    cmds.setAttr(back + '.rotateY', 0)
    assign([back], m_wood); objs.append(back)
    for lx, lz in ((-20, -20), (20, -20), (-20, 20), (20, 20)):
        lg = poly(cname + '_leg%d%d' % (lx, lz), 'cube', w=5, h=44, d=5)
        cmds.setAttr(lg + '.translate', cx + lx, 22, cz + lz)
        assign([lg], m_wood); objs.append(lg)
    cmds.setAttr(cg + '.rotateY', cry)

# ---- candelabra x2 (behind table, left & right) ----
for ci, (cx, cz) in enumerate(((-55, -60), (55, -60))):
    cg = cmds.group(em=True, name='SET_candelabra%d' % ci)
    stem = poly('cand%d_stem' % ci, 'cyl', r=2.5, h=30)
    cmds.setAttr(stem + '.translate', cx, 90, cz)
    assign([stem], m_gold); objs.append(stem)
    holder = poly('cand%d_hold' % ci, 'cyl', r=8, h=2)
    cmds.setAttr(holder + '.translate', cx, 76, cz)
    assign([holder], m_gold); objs.append(holder)
    for k, dx in enumerate((-12, 0, 12)):
        cd = poly('cand%d_c%d' % (ci, k), 'cyl', r=1.5, h=14)
        cmds.setAttr(cd + '.translate', cx + dx, 98, cz)
        assign([cd], m_candle); objs.append(cd)
        flame = poly('cand%d_f%d' % (ci, k), 'cone', r=1.8, h=5)
        cmds.setAttr(flame + '.translate', cx + dx, 107, cz)
        assign([flame], 'M_fire'); objs.append(flame)
    # point light (warm, weak)
    pl = cmds.pointLight(name='PL_candle%d' % ci, rgb=(1.0, 0.55, 0.25), intensity=6, decayRate=2)
    pltr = cmds.listRelatives(pl, parent=True)[0]
    cmds.setAttr(pltr + '.translate', cx, 105, cz)

# ---- flowers (back-left and back-right corners) ----
for fi, (fx, fz) in enumerate(((-150, -180), (150, -180))):
    pot = poly('flower%d_pot' % fi, 'cyl', r=16, h=25)
    cmds.setAttr(pot + '.translate', fx, 12.5, fz)
    assign([pot], m_wood); objs.append(pot)
    for k in range(6):
        bl = poly('flower%d_b%d' % (fi, k), 'sph', r=7)
        cmds.setAttr(bl + '.translate', fx - 15 + k * 6, 45 + (k % 3) * 8, fz - 8 + (k % 2) * 16)
        assign([bl], m_flower if k % 2 else m_green); objs.append(bl)

# ---- table props: bowls, bottle, 3 cups ----
for bi, (bx, bz) in enumerate(((-35, 10), (30, 18), (5, -25), (-10, 35))):
    bw = poly('prop_bowl%d' % bi, 'cyl', r=7, h=5)
    cmds.setAttr(bw + '.translate', bx, 77.5, bz)
    assign([bw], m_bowl); objs.append(bw)
bottle = poly('prop_bottle', 'cyl', r=4.5, h=26)
cmds.setAttr(bottle + '.translate', 0, 88, -20)
assign([bottle], m_glass); objs.append(bottle)
neck = poly('prop_bottleNeck', 'cyl', r=1.8, h=8)
cmds.setAttr(neck + '.translate', 0, 104, -20)
assign([neck], m_glass); objs.append(neck)
for ci, (cx, cz) in enumerate(((20, -5), (-25, -8), (8, 22))):
    cup = poly('prop_cup%d' % ci, 'cyl', r=3, h=7)
    cmds.setAttr(cup + '.translate', cx, 78.5, cz)
    assign([cup], m_glass); objs.append(cup)

# ---- lights: key warm from upper right + dim ambient ----
if not cmds.objExists('L_key'):
    key = cmds.directionalLight(name='L_key', rgb=(1.0, 0.88, 0.72), intensity=1.6)
    keytr = cmds.listRelatives(key, parent=True) or [key]
    keytr = keytr[0] if isinstance(keytr, list) else keytr
    cmds.setAttr(keytr + '.translate', 180, 320, 260)
    cmds.setAttr(keytr + '.rotate', -42, -28, 0)
keytr = cmds.ls('L_key', transforms=True) or ['L_key']
keytr = keytr[0]
cmds.setAttr(keytr + '.translate', 180, 320, 260)
cmds.setAttr(keytr + '.rotate', -42, -28, 0)
if not cmds.objExists('L_amb'):
    cmds.ambientLight(name='L_amb', intensity=0.18, rgb=(0.5, 0.4, 0.35))

# ---- camera template: 85mm half-body, y=105, looking at Ma ----
caml = cmds.ls('CAM_TEMPLATE', transforms=True)
cam = caml[0] if caml else cmds.camera(name='CAM_TEMPLATE', focalLength=85, filmFit='horizontal')[0]
cmds.setAttr(cam + '.translate', 20, 108, 130)
cmds.setAttr(cam + '.rotate', -4, 12, 0)
shps = cmds.listRelatives(cam, s=True) or []
for shp in shps:
    try:
        cmds.setAttr(shp + '.focalLength', 85)
        cmds.setAttr(shp + '.displayGateMask', 1)
        cmds.setAttr(shp + '.displayResolution', 1)
    except Exception:
        pass
# default render res 854x480 + 24fps
cmds.setAttr('defaultResolution.width', 854)
cmds.setAttr('defaultResolution.height', 480)
cmds.currentUnit(time='film')

# set finish
P("SET objects: %d" % len(objs))
cmds.file(rename=W + r"\scenes\p3_set.mb")
cmds.file(save=True, force=True, type='mayaBinary')
P("SAVED p3_set.mb")
P("P3_BUILD_DONE")
'''
import sys
sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
from mel_client import py
r = py(CODE, timeout=900)
print(r[-2000:])
