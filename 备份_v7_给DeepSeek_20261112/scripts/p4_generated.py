# -*- coding: utf-8 -*-
"""P4 runtime library - injected into Maya before the generated shot code.

Naming: chars imported in order Ma, Huang, Shiye -> same-named joints get
suffix '', '1', '2'. Mesh/arm tops keep original names. All performance is
FK + blendShape weights (eyes only).
"""

import math
import random

import maya.cmds as cmds

print("RUNTIME loading...")

SUF = {"Ma": "", "Huang": "1", "Shiye": "2"}

# world layout of character roots (arm + mesh moved together)
SEAT = {
    "Ma":    (0, 0, -100, 180),
    "Huang": (44, 0, 26, 120),
    "Shiye": (-44, 0, 26, -120),
}

_TOPPAT = {
    "Ma": ("*MakotoFBXASC032Yuki_arm", "*MakotoFBXASC032Yuki_mesh"),
    "Huang": ("*AragakiFBXASC032Shinjiro_arm", "*AragakiFBXASC032Shinjiro_mesh"),
    "Shiye": ("*JunpeiFBXASC032Iori_arm", "*JunpeiFBXASC032Iori_mesh"),
}
_TOPCACHE = {}


def T(tag, kind):
    """resolve arm/mesh top node name (whatever prefix it carries)."""
    key = (tag, kind)
    if key in _TOPCACHE:
        return _TOPCACHE[key]
    pat = _TOPPAT[tag][0 if kind == "arm" else 1]
    lst = cmds.ls(pat) or []
    val = lst[0] if lst else None
    _TOPCACHE[key] = val
    return val

BS = {}  # tag -> (blendShapeNode, {alias: index})


_JCACHE = {}


def _jointmap(tag):
    if tag in _JCACHE:
        return _JCACHE[tag]
    arm = T(tag, "arm")
    mp = {}
    for jpath in (cmds.ls(arm, long=True, dag=True, type="joint") or []):
        nm = jpath.split("|")[-1]
        if nm not in mp:
            mp[nm] = jpath
    _JCACHE[tag] = mp
    return mp


def J(tag, name):
    return _jointmap(tag).get(name)


def _bs_of(tag):
    if tag in BS:
        return BS[tag]
    mesh = T(tag, "mesh")
    hist = cmds.listHistory(mesh, pdo=True) or []
    bs = None
    for n in hist:
        if cmds.nodeType(n) == "blendShape":
            bs = n
            break
    idx = {}
    if bs:
        als = cmds.aliasAttr(bs, q=True) or []
        if isinstance(als, list):
            for k in range(0, len(als), 2):
                idx[als[k]] = als[k + 1]
    BS[tag] = (bs, idx)
    return BS[tag]


def morph(tag, name, value, t):
    ent = _bs_of(tag)
    if not ent or not ent[0]:
        return
    bs, idx = ent
    if name in idx:
        a = "%s.%s" % (bs, idx[name])
        cmds.setAttr(a, value)
        cmds.setKeyframe(a, t=t)


# ---------- eyes ----------
def blink(tag, t, dur=5):
    h = dur / 2.0
    morph(tag, "blink", 0.0, max(1, t - h))
    morph(tag, "blink", 1.0, t)
    morph(tag, "blink", 0.0, t + h)


def hold_eyes(tag, openness, t):
    morph(tag, "blink", 0.0, t)
    if "half_eye" in _bs_of(tag)[1]:
        morph(tag, "half_eye", 1.0 - openness, t)


def blink_loop(tag, start, end, seed=None):
    rnd = random.Random(seed or (hash(tag) & 0xFFFF))
    t = start + rnd.uniform(0.6, 2.0)
    while t < end - 3:
        blink(tag, t)
        t += rnd.uniform(2.2, 4.2)


def blink_loop_all(start, end):
    for i, tag in enumerate(("Ma", "Huang", "Shiye")):
        blink_loop(tag, start, end, seed=hash(tag) & 0xFFFF + i)


# ---------- head ----------
def look_key(tag, target_tag, t0, t1, amp=1.0):
    """turn head toward another seated character between t0..t1."""
    x0, _, z0, fac = SEAT[tag]
    x1, _, z1, _ = SEAT[target_tag]
    # relative yaw in world, then adjust by facing
    yaw_world = math.degrees(math.atan2(x1 - x0, z1 - z0))
    rel = ((yaw_world - fac + 180) % 360) - 180
    rel = max(-60, min(60, rel)) * amp
    head = J(tag, "Head")
    neck = J(tag, "Neck")
    base_h = cmds.getAttr(head + ".rotateY") if head else 0
    base_n = cmds.getAttr(neck + ".rotateY") if neck else 0
    if neck:
        cmds.setKeyframe(neck + ".rotateY", t=t0, v=base_n)
        cmds.setAttr(neck + ".rotateY", base_n + rel * 0.4)
        cmds.setKeyframe(neck + ".rotateY", t=t1)
    if head:
        cmds.setKeyframe(head + ".rotateY", t=t0, v=base_h)
        cmds.setAttr(head + ".rotateY", base_h + rel * 0.6)
        cmds.setKeyframe(head + ".rotateY", t=t1)


def nod(tag, t, times=1, amp=10):
    head = J(tag, "Head")
    if not head:
        return
    base = cmds.getAttr(head + ".rotateX")
    cmds.setKeyframe(head + ".rotateX", t=t, v=base)
    tt = t
    for i in range(times):
        tt += 4
        cmds.setAttr(head + ".rotateX", base + amp)
        cmds.setKeyframe(head + ".rotateX", t=tt)
        tt += 4
        cmds.setAttr(head + ".rotateX", base - amp * 0.3)
        cmds.setKeyframe(head + ".rotateX", t=tt)
    cmds.setAttr(head + ".rotateX", base)
    cmds.setKeyframe(head + ".rotateX", t=tt + 3)


# ---------- arms ----------
def _arm(tag, side, lift=0, spread=0, elbow=0, t=None):
    ua = J(tag, side + "Arm")
    fa = J(tag, side + "ForeArm")
    s = 1 if side == "Left" else -1
    if ua:
        cmds.setAttr(ua + ".rotateZ", (lift) * s)
        if spread:
            cmds.setAttr(ua + ".rotateY", spread * s)
        if t is not None:
            cmds.setKeyframe(ua + ".rotateZ", t=t)
            cmds.setKeyframe(ua + ".rotateY", t=t)
    if fa:
        cmds.setAttr(fa + ".rotateY", elbow * s)
        if t is not None:
            cmds.setKeyframe(fa + ".rotateY", t=t)


def rest_pose(tag, t=1):
    _arm(tag, "Left", lift=-8, elbow=28, t=t)
    _arm(tag, "Right", lift=-8, elbow=28, t=t)


def gesture(tag, style, t, dur=16, amp=1.0):
    if style == "A":
        _arm(tag, "Right", lift=38 * amp, elbow=42, t=t)
        _arm(tag, "Right", lift=22 * amp, elbow=26, t=t + dur)
    elif style == "B":
        _arm(tag, "Left", lift=30 * amp, spread=18, elbow=32, t=t)
        _arm(tag, "Right", lift=30 * amp, spread=18, elbow=32, t=t)
        _arm(tag, "Left", lift=10 * amp, elbow=22, t=t + dur)
        _arm(tag, "Right", lift=10 * amp, elbow=22, t=t + dur)
    elif style == "C":
        _arm(tag, "Right", lift=52 * amp, spread=8, elbow=18, t=t)
        _arm(tag, "Right", lift=45 * amp, elbow=12, t=t + dur)
        _arm(tag, "Right", lift=-4, elbow=28, t=t + dur + 5)


def smooth_chest(tag, t, dur=14):
    _arm(tag, "Left", lift=48, elbow=48, t=t)
    _arm(tag, "Right", lift=48, elbow=48, t=t + 2)
    _arm(tag, "Left", lift=6, elbow=30, t=t + dur)
    _arm(tag, "Right", lift=6, elbow=30, t=t + dur + 2)


def raise_cup(tag, t, dur=16, side="Right"):
    _arm(tag, side, lift=44, elbow=58, t=t)
    _arm(tag, side, lift=40, elbow=72, t=t + dur // 2)
    _arm(tag, side, lift=2, elbow=30, t=t + dur)


def knock(tag, t):
    _arm(tag, "Right", lift=36, elbow=50, t=t)
    _arm(tag, "Right", lift=30, elbow=44, t=t + 3)
    _arm(tag, "Right", lift=36, elbow=50, t=t + 6)
    _arm(tag, "Right", lift=-2, elbow=28, t=t + 14)


# ---------- body ----------
def lean(tag, t, amp=6, dur=18):
    sp = J(tag, "Spine")
    if not sp:
        return
    base = cmds.getAttr(sp + ".rotateX")
    cmds.setKeyframe(sp + ".rotateX", t=t, v=base)
    cmds.setAttr(sp + ".rotateX", base + amp)
    cmds.setKeyframe(sp + ".rotateX", t=t + dur)
    cmds.setAttr(sp + ".rotateX", base)
    cmds.setKeyframe(sp + ".rotateX", t=t + dur + 4)


def breath(tag, start, end):
    sp = J(tag, "Spine")
    if not sp:
        return
    base = cmds.getAttr(sp + ".rotateX")
    step = max(4, int((end - start) / 20))
    for t in range(int(start), int(end) + 1, step):
        v = base + 1.1 * math.sin((t - start) / 11.0 * math.pi)
        cmds.setAttr(sp + ".rotateX", v)
        cmds.setKeyframe(sp + ".rotateX", t=t)


def glance(tag, target, t):
    look_key(tag, target, t, t + 12, amp=0.7)


def sit_all():
    """apply sit pose to all three + set root transforms."""
    for tag in ("Ma", "Huang", "Shiye"):
        x, y, z, ry = SEAT[tag]
        for top in (T(tag, "arm"), T(tag, "mesh")):
            if top and cmds.objExists(top):
                for ax in ("X", "Y", "Z"):
                    try:
                        cmds.setAttr(top + ".translate" + ax, lock=False)
                    except Exception:
                        pass
                try:
                    cmds.setAttr(top + ".translate", x, y, z)
                    cmds.setAttr(top + ".rotateY", ry)
                except Exception as e:
                    print("move fail %s: %s" % (top, e))
        for side in ("Left", "Right"):
            s = 1 if side == "Left" else -1
            hip = J(tag, side + "UpLeg")
            knee = J(tag, side + "Leg")
            foot = J(tag, side + "Foot")
            if hip:
                cmds.setAttr(hip + ".rotateX", -80)
                cmds.setKeyframe(hip + ".rotateX", t=1)
            if knee:
                cmds.setAttr(knee + ".rotateX", 80)
                cmds.setKeyframe(knee + ".rotateX", t=1)
            if foot:
                cmds.setAttr(foot + ".rotateX", 10)
                cmds.setKeyframe(foot + ".rotateX", t=1)
        rest_pose(tag, 1)


print("RUNTIME_READY")


# ---- S001 ----
cam = cmds.camera(name='CAM_S001')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S001')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1)
cmds.setKeyframe(cam + '.rotateY', t=1)
cmds.setKeyframe(cam + '.rotateZ', t=1)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1)
cmds.setKeyframe(cam + '.translateX', t=56)
cmds.setKeyframe(cam + '.translateY', t=1)
cmds.setKeyframe(cam + '.translateY', t=56)
cmds.setKeyframe(cam + '.translateZ', t=1)
cmds.setKeyframe(cam + '.translateZ', t=56)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=56)
cmds.setKeyframe(cam + '.rotateY', t=56)
cmds.setKeyframe(cam + '.rotateZ', t=56)
cmds.delete(lt)
blink_loop_all(1, 56)
breath('Ma', 1, 56)
breath('Huang', 1, 56)
breath('Shiye', 1, 56)
glance('Ma', 'Huang', 28)

# ---- S002 ----
cam = cmds.camera(name='CAM_S002')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S002')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=57)
cmds.setKeyframe(cam + '.rotateY', t=57)
cmds.setKeyframe(cam + '.rotateZ', t=57)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=57)
cmds.setKeyframe(cam + '.translateX', t=103)
cmds.setKeyframe(cam + '.translateY', t=57)
cmds.setKeyframe(cam + '.translateY', t=103)
cmds.setKeyframe(cam + '.translateZ', t=57)
cmds.setKeyframe(cam + '.translateZ', t=103)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=103)
cmds.setKeyframe(cam + '.rotateY', t=103)
cmds.setKeyframe(cam + '.rotateZ', t=103)
cmds.delete(lt)
blink_loop_all(57, 103)
breath('Ma', 57, 103)
breath('Huang', 57, 103)
breath('Shiye', 57, 103)
glance('Ma', 'Huang', 80)

# ---- S003 ----
cam = cmds.camera(name='CAM_S003')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S003')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=104)
cmds.setKeyframe(cam + '.rotateY', t=104)
cmds.setKeyframe(cam + '.rotateZ', t=104)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=104)
cmds.setKeyframe(cam + '.translateX', t=193)
cmds.setKeyframe(cam + '.translateY', t=104)
cmds.setKeyframe(cam + '.translateY', t=193)
cmds.setKeyframe(cam + '.translateZ', t=104)
cmds.setKeyframe(cam + '.translateZ', t=193)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=193)
cmds.setKeyframe(cam + '.rotateY', t=193)
cmds.setKeyframe(cam + '.rotateZ', t=193)
cmds.delete(lt)
blink_loop_all(104, 193)
breath('Ma', 104, 193)
breath('Huang', 104, 193)
breath('Shiye', 104, 193)
glance('Ma', 'Huang', 148)

# ---- S004 ----
cam = cmds.camera(name='CAM_S004')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S004')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=194)
cmds.setKeyframe(cam + '.rotateY', t=194)
cmds.setKeyframe(cam + '.rotateZ', t=194)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=194)
cmds.setKeyframe(cam + '.translateX', t=251)
cmds.setKeyframe(cam + '.translateY', t=194)
cmds.setKeyframe(cam + '.translateY', t=251)
cmds.setKeyframe(cam + '.translateZ', t=194)
cmds.setKeyframe(cam + '.translateZ', t=251)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=251)
cmds.setKeyframe(cam + '.rotateY', t=251)
cmds.setKeyframe(cam + '.rotateZ', t=251)
cmds.delete(lt)
blink_loop_all(194, 251)
breath('Ma', 194, 251)
breath('Huang', 194, 251)
breath('Shiye', 194, 251)
glance('Ma', 'Huang', 222)

# ---- S005 ----
cam = cmds.camera(name='CAM_S005')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S005')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=252)
cmds.setKeyframe(cam + '.rotateY', t=252)
cmds.setKeyframe(cam + '.rotateZ', t=252)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=252)
cmds.setKeyframe(cam + '.translateX', t=288)
cmds.setKeyframe(cam + '.translateY', t=252)
cmds.setKeyframe(cam + '.translateY', t=288)
cmds.setKeyframe(cam + '.translateZ', t=252)
cmds.setKeyframe(cam + '.translateZ', t=288)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=288)
cmds.setKeyframe(cam + '.rotateY', t=288)
cmds.setKeyframe(cam + '.rotateZ', t=288)
cmds.delete(lt)
blink_loop_all(252, 288)
breath('Ma', 252, 288)
breath('Huang', 252, 288)
breath('Shiye', 252, 288)
glance('Ma', 'Huang', 270)

# ---- S006 ----
cam = cmds.camera(name='CAM_S006')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S006')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=289)
cmds.setKeyframe(cam + '.rotateY', t=289)
cmds.setKeyframe(cam + '.rotateZ', t=289)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=289)
cmds.setKeyframe(cam + '.translateX', t=314)
cmds.setKeyframe(cam + '.translateY', t=289)
cmds.setKeyframe(cam + '.translateY', t=314)
cmds.setKeyframe(cam + '.translateZ', t=289)
cmds.setKeyframe(cam + '.translateZ', t=314)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=314)
cmds.setKeyframe(cam + '.rotateY', t=314)
cmds.setKeyframe(cam + '.rotateZ', t=314)
cmds.delete(lt)
blink_loop_all(289, 314)
breath('Ma', 289, 314)
breath('Huang', 289, 314)
breath('Shiye', 289, 314)
glance('Ma', 'Huang', 301)

# ---- S007 ----
cam = cmds.camera(name='CAM_S007')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S007')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=315)
cmds.setKeyframe(cam + '.rotateY', t=315)
cmds.setKeyframe(cam + '.rotateZ', t=315)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=315)
cmds.setKeyframe(cam + '.translateX', t=336)
cmds.setKeyframe(cam + '.translateY', t=315)
cmds.setKeyframe(cam + '.translateY', t=336)
cmds.setKeyframe(cam + '.translateZ', t=315)
cmds.setKeyframe(cam + '.translateZ', t=336)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=336)
cmds.setKeyframe(cam + '.rotateY', t=336)
cmds.setKeyframe(cam + '.rotateZ', t=336)
cmds.delete(lt)
blink_loop_all(315, 336)
breath('Ma', 315, 336)
breath('Huang', 315, 336)
breath('Shiye', 315, 336)
glance('Ma', 'Huang', 325)

# ---- S008 ----
cam = cmds.camera(name='CAM_S008')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S008')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=337)
cmds.setKeyframe(cam + '.rotateY', t=337)
cmds.setKeyframe(cam + '.rotateZ', t=337)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=337)
cmds.setKeyframe(cam + '.translateX', t=370)
cmds.setKeyframe(cam + '.translateY', t=337)
cmds.setKeyframe(cam + '.translateY', t=370)
cmds.setKeyframe(cam + '.translateZ', t=337)
cmds.setKeyframe(cam + '.translateZ', t=370)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=370)
cmds.setKeyframe(cam + '.rotateY', t=370)
cmds.setKeyframe(cam + '.rotateZ', t=370)
cmds.delete(lt)
blink_loop_all(337, 370)
breath('Ma', 337, 370)
breath('Huang', 337, 370)
breath('Shiye', 337, 370)
glance('Ma', 'Huang', 353)

# ---- S009 ----
cam = cmds.camera(name='CAM_S009')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S009')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=371)
cmds.setKeyframe(cam + '.rotateY', t=371)
cmds.setKeyframe(cam + '.rotateZ', t=371)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=371)
cmds.setKeyframe(cam + '.translateX', t=395)
cmds.setKeyframe(cam + '.translateY', t=371)
cmds.setKeyframe(cam + '.translateY', t=395)
cmds.setKeyframe(cam + '.translateZ', t=371)
cmds.setKeyframe(cam + '.translateZ', t=395)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=395)
cmds.setKeyframe(cam + '.rotateY', t=395)
cmds.setKeyframe(cam + '.rotateZ', t=395)
cmds.delete(lt)
blink_loop_all(371, 395)
breath('Ma', 371, 395)
breath('Huang', 371, 395)
breath('Shiye', 371, 395)
glance('Ma', 'Huang', 383)

# ---- S010 ----
cam = cmds.camera(name='CAM_S010')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S010')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=396)
cmds.setKeyframe(cam + '.rotateY', t=396)
cmds.setKeyframe(cam + '.rotateZ', t=396)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=396)
cmds.setKeyframe(cam + '.translateX', t=427)
cmds.setKeyframe(cam + '.translateY', t=396)
cmds.setKeyframe(cam + '.translateY', t=427)
cmds.setKeyframe(cam + '.translateZ', t=396)
cmds.setKeyframe(cam + '.translateZ', t=427)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=427)
cmds.setKeyframe(cam + '.rotateY', t=427)
cmds.setKeyframe(cam + '.rotateZ', t=427)
cmds.delete(lt)
blink_loop_all(396, 427)
breath('Ma', 396, 427)
breath('Huang', 396, 427)
breath('Shiye', 396, 427)
glance('Ma', 'Huang', 411)

# ---- S011 ----
cam = cmds.camera(name='CAM_S011')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S011')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=428)
cmds.setKeyframe(cam + '.rotateY', t=428)
cmds.setKeyframe(cam + '.rotateZ', t=428)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=428)
cmds.setKeyframe(cam + '.translateX', t=479)
cmds.setKeyframe(cam + '.translateY', t=428)
cmds.setKeyframe(cam + '.translateY', t=479)
cmds.setKeyframe(cam + '.translateZ', t=428)
cmds.setKeyframe(cam + '.translateZ', t=479)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=479)
cmds.setKeyframe(cam + '.rotateY', t=479)
cmds.setKeyframe(cam + '.rotateZ', t=479)
cmds.delete(lt)
blink_loop_all(428, 479)
breath('Ma', 428, 479)
breath('Huang', 428, 479)
breath('Shiye', 428, 479)
glance('Ma', 'Huang', 453)

# ---- S012 ----
cam = cmds.camera(name='CAM_S012')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S012')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=480)
cmds.setKeyframe(cam + '.rotateY', t=480)
cmds.setKeyframe(cam + '.rotateZ', t=480)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=480)
cmds.setKeyframe(cam + '.translateX', t=536)
cmds.setKeyframe(cam + '.translateY', t=480)
cmds.setKeyframe(cam + '.translateY', t=536)
cmds.setKeyframe(cam + '.translateZ', t=480)
cmds.setKeyframe(cam + '.translateZ', t=536)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=536)
cmds.setKeyframe(cam + '.rotateY', t=536)
cmds.setKeyframe(cam + '.rotateZ', t=536)
cmds.delete(lt)
blink_loop_all(480, 536)
breath('Ma', 480, 536)
breath('Huang', 480, 536)
breath('Shiye', 480, 536)
glance('Ma', 'Huang', 508)

# ---- S013 ----
cam = cmds.camera(name='CAM_S013')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S013')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=537)
cmds.setKeyframe(cam + '.rotateY', t=537)
cmds.setKeyframe(cam + '.rotateZ', t=537)
cmds.setAttr(cam + '.translate', 26, 111, 207)
cmds.setKeyframe(cam + '.translateX', t=537)
cmds.setKeyframe(cam + '.translateX', t=560)
cmds.setKeyframe(cam + '.translateY', t=537)
cmds.setKeyframe(cam + '.translateY', t=560)
cmds.setKeyframe(cam + '.translateZ', t=537)
cmds.setKeyframe(cam + '.translateZ', t=560)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=560)
cmds.setKeyframe(cam + '.rotateY', t=560)
cmds.setKeyframe(cam + '.rotateZ', t=560)
cmds.delete(lt)
blink_loop_all(537, 560)
breath('Ma', 537, 560)
breath('Huang', 537, 560)
breath('Shiye', 537, 560)
glance('Ma', 'Huang', 548)

# ---- S014 ----
cam = cmds.camera(name='CAM_S014')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S014')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=561)
cmds.setKeyframe(cam + '.rotateY', t=561)
cmds.setKeyframe(cam + '.rotateZ', t=561)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=561)
cmds.setKeyframe(cam + '.translateX', t=609)
cmds.setKeyframe(cam + '.translateY', t=561)
cmds.setKeyframe(cam + '.translateY', t=609)
cmds.setKeyframe(cam + '.translateZ', t=561)
cmds.setKeyframe(cam + '.translateZ', t=609)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=609)
cmds.setKeyframe(cam + '.rotateY', t=609)
cmds.setKeyframe(cam + '.rotateZ', t=609)
cmds.delete(lt)
blink_loop_all(561, 609)
breath('Ma', 561, 609)
breath('Huang', 561, 609)
breath('Shiye', 561, 609)
glance('Ma', 'Huang', 585)

# ---- S015 ----
cam = cmds.camera(name='CAM_S015')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S015')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=610)
cmds.setKeyframe(cam + '.rotateY', t=610)
cmds.setKeyframe(cam + '.rotateZ', t=610)
cmds.setAttr(cam + '.translate', 26, 111, 207)
cmds.setKeyframe(cam + '.translateX', t=610)
cmds.setKeyframe(cam + '.translateX', t=635)
cmds.setKeyframe(cam + '.translateY', t=610)
cmds.setKeyframe(cam + '.translateY', t=635)
cmds.setKeyframe(cam + '.translateZ', t=610)
cmds.setKeyframe(cam + '.translateZ', t=635)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=635)
cmds.setKeyframe(cam + '.rotateY', t=635)
cmds.setKeyframe(cam + '.rotateZ', t=635)
cmds.delete(lt)
blink_loop_all(610, 635)
breath('Ma', 610, 635)
breath('Huang', 610, 635)
breath('Shiye', 610, 635)
glance('Ma', 'Huang', 622)

# ---- S016 ----
cam = cmds.camera(name='CAM_S016')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S016')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=636)
cmds.setKeyframe(cam + '.rotateY', t=636)
cmds.setKeyframe(cam + '.rotateZ', t=636)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=636)
cmds.setKeyframe(cam + '.translateX', t=749)
cmds.setKeyframe(cam + '.translateY', t=636)
cmds.setKeyframe(cam + '.translateY', t=749)
cmds.setKeyframe(cam + '.translateZ', t=636)
cmds.setKeyframe(cam + '.translateZ', t=749)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=749)
cmds.setKeyframe(cam + '.rotateY', t=749)
cmds.setKeyframe(cam + '.rotateZ', t=749)
cmds.delete(lt)
blink_loop_all(636, 749)
breath('Ma', 636, 749)
breath('Huang', 636, 749)
breath('Shiye', 636, 749)
glance('Ma', 'Huang', 692)

# ---- S017 ----
cam = cmds.camera(name='CAM_S017')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S017')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=750)
cmds.setKeyframe(cam + '.rotateY', t=750)
cmds.setKeyframe(cam + '.rotateZ', t=750)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=750)
cmds.setKeyframe(cam + '.translateX', t=810)
cmds.setKeyframe(cam + '.translateY', t=750)
cmds.setKeyframe(cam + '.translateY', t=810)
cmds.setKeyframe(cam + '.translateZ', t=750)
cmds.setKeyframe(cam + '.translateZ', t=810)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=810)
cmds.setKeyframe(cam + '.rotateY', t=810)
cmds.setKeyframe(cam + '.rotateZ', t=810)
cmds.delete(lt)
blink_loop_all(750, 810)
breath('Ma', 750, 810)
breath('Huang', 750, 810)
breath('Shiye', 750, 810)
glance('Ma', 'Huang', 780)

# ---- S018 ----
cam = cmds.camera(name='CAM_S018')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S018')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=811)
cmds.setKeyframe(cam + '.rotateY', t=811)
cmds.setKeyframe(cam + '.rotateZ', t=811)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=811)
cmds.setKeyframe(cam + '.translateX', t=857)
cmds.setKeyframe(cam + '.translateY', t=811)
cmds.setKeyframe(cam + '.translateY', t=857)
cmds.setKeyframe(cam + '.translateZ', t=811)
cmds.setKeyframe(cam + '.translateZ', t=857)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=857)
cmds.setKeyframe(cam + '.rotateY', t=857)
cmds.setKeyframe(cam + '.rotateZ', t=857)
cmds.delete(lt)
blink_loop_all(811, 857)
breath('Ma', 811, 857)
breath('Huang', 811, 857)
breath('Shiye', 811, 857)
glance('Ma', 'Huang', 834)

# ---- S019 ----
cam = cmds.camera(name='CAM_S019')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S019')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=858)
cmds.setKeyframe(cam + '.rotateY', t=858)
cmds.setKeyframe(cam + '.rotateZ', t=858)
cmds.setAttr(cam + '.translate', 26, 111, 207)
cmds.setKeyframe(cam + '.translateX', t=858)
cmds.setKeyframe(cam + '.translateX', t=941)
cmds.setKeyframe(cam + '.translateY', t=858)
cmds.setKeyframe(cam + '.translateY', t=941)
cmds.setKeyframe(cam + '.translateZ', t=858)
cmds.setKeyframe(cam + '.translateZ', t=941)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=941)
cmds.setKeyframe(cam + '.rotateY', t=941)
cmds.setKeyframe(cam + '.rotateZ', t=941)
cmds.delete(lt)
blink_loop_all(858, 941)
breath('Ma', 858, 941)
breath('Huang', 858, 941)
breath('Shiye', 858, 941)
glance('Ma', 'Huang', 899)

# ---- S020 ----
cam = cmds.camera(name='CAM_S020')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S020')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=942)
cmds.setKeyframe(cam + '.rotateY', t=942)
cmds.setKeyframe(cam + '.rotateZ', t=942)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=942)
cmds.setKeyframe(cam + '.translateX', t=999)
cmds.setKeyframe(cam + '.translateY', t=942)
cmds.setKeyframe(cam + '.translateY', t=999)
cmds.setKeyframe(cam + '.translateZ', t=942)
cmds.setKeyframe(cam + '.translateZ', t=999)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=999)
cmds.setKeyframe(cam + '.rotateY', t=999)
cmds.setKeyframe(cam + '.rotateZ', t=999)
cmds.delete(lt)
blink_loop_all(942, 999)
breath('Ma', 942, 999)
breath('Huang', 942, 999)
breath('Shiye', 942, 999)
glance('Ma', 'Huang', 970)

# ---- S021 ----
cam = cmds.camera(name='CAM_S021')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S021')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1000)
cmds.setKeyframe(cam + '.rotateY', t=1000)
cmds.setKeyframe(cam + '.rotateZ', t=1000)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1000)
cmds.setKeyframe(cam + '.translateX', t=1101)
cmds.setKeyframe(cam + '.translateY', t=1000)
cmds.setKeyframe(cam + '.translateY', t=1101)
cmds.setKeyframe(cam + '.translateZ', t=1000)
cmds.setKeyframe(cam + '.translateZ', t=1101)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1101)
cmds.setKeyframe(cam + '.rotateY', t=1101)
cmds.setKeyframe(cam + '.rotateZ', t=1101)
cmds.delete(lt)
blink_loop_all(1000, 1101)
breath('Ma', 1000, 1101)
breath('Huang', 1000, 1101)
breath('Shiye', 1000, 1101)
glance('Ma', 'Huang', 1050)

# ---- S022 ----
cam = cmds.camera(name='CAM_S022')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', -22, 106, 219)
lt = cmds.spaceLocator(name='aimT_S022')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1102)
cmds.setKeyframe(cam + '.rotateY', t=1102)
cmds.setKeyframe(cam + '.rotateZ', t=1102)
cmds.setAttr(cam + '.translate', 4, 106, 219)
cmds.setKeyframe(cam + '.translateX', t=1102)
cmds.setKeyframe(cam + '.translateX', t=1138)
cmds.setKeyframe(cam + '.translateY', t=1102)
cmds.setKeyframe(cam + '.translateY', t=1138)
cmds.setKeyframe(cam + '.translateZ', t=1102)
cmds.setKeyframe(cam + '.translateZ', t=1138)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Shiye', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1138)
cmds.setKeyframe(cam + '.rotateY', t=1138)
cmds.setKeyframe(cam + '.rotateZ', t=1138)
cmds.delete(lt)
blink_loop_all(1102, 1138)
breath('Ma', 1102, 1138)
breath('Huang', 1102, 1138)
breath('Shiye', 1102, 1138)
glance('Ma', 'Huang', 1120)

# ---- S023 ----
cam = cmds.camera(name='CAM_S023')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S023')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1139)
cmds.setKeyframe(cam + '.rotateY', t=1139)
cmds.setKeyframe(cam + '.rotateZ', t=1139)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1139)
cmds.setKeyframe(cam + '.translateX', t=1178)
cmds.setKeyframe(cam + '.translateY', t=1139)
cmds.setKeyframe(cam + '.translateY', t=1178)
cmds.setKeyframe(cam + '.translateZ', t=1139)
cmds.setKeyframe(cam + '.translateZ', t=1178)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1178)
cmds.setKeyframe(cam + '.rotateY', t=1178)
cmds.setKeyframe(cam + '.rotateZ', t=1178)
cmds.delete(lt)
blink_loop_all(1139, 1178)
breath('Ma', 1139, 1178)
breath('Huang', 1139, 1178)
breath('Shiye', 1139, 1178)
glance('Ma', 'Huang', 1158)

# ---- S024 ----
cam = cmds.camera(name='CAM_S024')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S024')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1179)
cmds.setKeyframe(cam + '.rotateY', t=1179)
cmds.setKeyframe(cam + '.rotateZ', t=1179)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1179)
cmds.setKeyframe(cam + '.translateX', t=1228)
cmds.setKeyframe(cam + '.translateY', t=1179)
cmds.setKeyframe(cam + '.translateY', t=1228)
cmds.setKeyframe(cam + '.translateZ', t=1179)
cmds.setKeyframe(cam + '.translateZ', t=1228)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1228)
cmds.setKeyframe(cam + '.rotateY', t=1228)
cmds.setKeyframe(cam + '.rotateZ', t=1228)
cmds.delete(lt)
blink_loop_all(1179, 1228)
breath('Ma', 1179, 1228)
breath('Huang', 1179, 1228)
breath('Shiye', 1179, 1228)
glance('Ma', 'Huang', 1203)

# ---- S025 ----
cam = cmds.camera(name='CAM_S025')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S025')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1229)
cmds.setKeyframe(cam + '.rotateY', t=1229)
cmds.setKeyframe(cam + '.rotateZ', t=1229)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1229)
cmds.setKeyframe(cam + '.translateX', t=1277)
cmds.setKeyframe(cam + '.translateY', t=1229)
cmds.setKeyframe(cam + '.translateY', t=1277)
cmds.setKeyframe(cam + '.translateZ', t=1229)
cmds.setKeyframe(cam + '.translateZ', t=1277)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1277)
cmds.setKeyframe(cam + '.rotateY', t=1277)
cmds.setKeyframe(cam + '.rotateZ', t=1277)
cmds.delete(lt)
blink_loop_all(1229, 1277)
breath('Ma', 1229, 1277)
breath('Huang', 1229, 1277)
breath('Shiye', 1229, 1277)
glance('Ma', 'Huang', 1253)

# ---- S026 ----
cam = cmds.camera(name='CAM_S026')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S026')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1278)
cmds.setKeyframe(cam + '.rotateY', t=1278)
cmds.setKeyframe(cam + '.rotateZ', t=1278)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1278)
cmds.setKeyframe(cam + '.translateX', t=1315)
cmds.setKeyframe(cam + '.translateY', t=1278)
cmds.setKeyframe(cam + '.translateY', t=1315)
cmds.setKeyframe(cam + '.translateZ', t=1278)
cmds.setKeyframe(cam + '.translateZ', t=1315)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1315)
cmds.setKeyframe(cam + '.rotateY', t=1315)
cmds.setKeyframe(cam + '.rotateZ', t=1315)
cmds.delete(lt)
blink_loop_all(1278, 1315)
breath('Ma', 1278, 1315)
breath('Huang', 1278, 1315)
breath('Shiye', 1278, 1315)
glance('Ma', 'Huang', 1296)

# ---- S027 ----
cam = cmds.camera(name='CAM_S027')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S027')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1316)
cmds.setKeyframe(cam + '.rotateY', t=1316)
cmds.setKeyframe(cam + '.rotateZ', t=1316)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1316)
cmds.setKeyframe(cam + '.translateX', t=1374)
cmds.setKeyframe(cam + '.translateY', t=1316)
cmds.setKeyframe(cam + '.translateY', t=1374)
cmds.setKeyframe(cam + '.translateZ', t=1316)
cmds.setKeyframe(cam + '.translateZ', t=1374)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1374)
cmds.setKeyframe(cam + '.rotateY', t=1374)
cmds.setKeyframe(cam + '.rotateZ', t=1374)
cmds.delete(lt)
blink_loop_all(1316, 1374)
breath('Ma', 1316, 1374)
breath('Huang', 1316, 1374)
breath('Shiye', 1316, 1374)
glance('Ma', 'Huang', 1345)

# ---- S028 ----
cam = cmds.camera(name='CAM_S028')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S028')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1375)
cmds.setKeyframe(cam + '.rotateY', t=1375)
cmds.setKeyframe(cam + '.rotateZ', t=1375)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1375)
cmds.setKeyframe(cam + '.translateX', t=1424)
cmds.setKeyframe(cam + '.translateY', t=1375)
cmds.setKeyframe(cam + '.translateY', t=1424)
cmds.setKeyframe(cam + '.translateZ', t=1375)
cmds.setKeyframe(cam + '.translateZ', t=1424)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1424)
cmds.setKeyframe(cam + '.rotateY', t=1424)
cmds.setKeyframe(cam + '.rotateZ', t=1424)
cmds.delete(lt)
blink_loop_all(1375, 1424)
breath('Ma', 1375, 1424)
breath('Huang', 1375, 1424)
breath('Shiye', 1375, 1424)
glance('Ma', 'Huang', 1399)

# ---- S029 ----
cam = cmds.camera(name='CAM_S029')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S029')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1425)
cmds.setKeyframe(cam + '.rotateY', t=1425)
cmds.setKeyframe(cam + '.rotateZ', t=1425)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1425)
cmds.setKeyframe(cam + '.translateX', t=1471)
cmds.setKeyframe(cam + '.translateY', t=1425)
cmds.setKeyframe(cam + '.translateY', t=1471)
cmds.setKeyframe(cam + '.translateZ', t=1425)
cmds.setKeyframe(cam + '.translateZ', t=1471)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1471)
cmds.setKeyframe(cam + '.rotateY', t=1471)
cmds.setKeyframe(cam + '.rotateZ', t=1471)
cmds.delete(lt)
blink_loop_all(1425, 1471)
breath('Ma', 1425, 1471)
breath('Huang', 1425, 1471)
breath('Shiye', 1425, 1471)
glance('Ma', 'Huang', 1448)

# ---- S030 ----
cam = cmds.camera(name='CAM_S030')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 22, 108, 219)
lt = cmds.spaceLocator(name='aimT_S030')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Huang', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1472)
cmds.setKeyframe(cam + '.rotateY', t=1472)
cmds.setKeyframe(cam + '.rotateZ', t=1472)
cmds.setAttr(cam + '.translate', 48, 108, 219)
cmds.setKeyframe(cam + '.translateX', t=1472)
cmds.setKeyframe(cam + '.translateX', t=1508)
cmds.setKeyframe(cam + '.translateY', t=1472)
cmds.setKeyframe(cam + '.translateY', t=1508)
cmds.setKeyframe(cam + '.translateZ', t=1472)
cmds.setKeyframe(cam + '.translateZ', t=1508)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Huang', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1508)
cmds.setKeyframe(cam + '.rotateY', t=1508)
cmds.setKeyframe(cam + '.rotateZ', t=1508)
cmds.delete(lt)
blink_loop_all(1472, 1508)
breath('Ma', 1472, 1508)
breath('Huang', 1472, 1508)
breath('Shiye', 1472, 1508)
glance('Ma', 'Huang', 1490)

# ---- S031 ----
cam = cmds.camera(name='CAM_S031')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S031')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1509)
cmds.setKeyframe(cam + '.rotateY', t=1509)
cmds.setKeyframe(cam + '.rotateZ', t=1509)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1509)
cmds.setKeyframe(cam + '.translateX', t=1617)
cmds.setKeyframe(cam + '.translateY', t=1509)
cmds.setKeyframe(cam + '.translateY', t=1617)
cmds.setKeyframe(cam + '.translateZ', t=1509)
cmds.setKeyframe(cam + '.translateZ', t=1617)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1617)
cmds.setKeyframe(cam + '.rotateY', t=1617)
cmds.setKeyframe(cam + '.rotateZ', t=1617)
cmds.delete(lt)
blink_loop_all(1509, 1617)
breath('Ma', 1509, 1617)
breath('Huang', 1509, 1617)
breath('Shiye', 1509, 1617)
glance('Ma', 'Huang', 1563)

# ---- S032 ----
cam = cmds.camera(name='CAM_S032')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S032')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1618)
cmds.setKeyframe(cam + '.rotateY', t=1618)
cmds.setKeyframe(cam + '.rotateZ', t=1618)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1618)
cmds.setKeyframe(cam + '.translateX', t=1683)
cmds.setKeyframe(cam + '.translateY', t=1618)
cmds.setKeyframe(cam + '.translateY', t=1683)
cmds.setKeyframe(cam + '.translateZ', t=1618)
cmds.setKeyframe(cam + '.translateZ', t=1683)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1683)
cmds.setKeyframe(cam + '.rotateY', t=1683)
cmds.setKeyframe(cam + '.rotateZ', t=1683)
cmds.delete(lt)
blink_loop_all(1618, 1683)
breath('Ma', 1618, 1683)
breath('Huang', 1618, 1683)
breath('Shiye', 1618, 1683)
glance('Ma', 'Huang', 1650)

# ---- S033 ----
cam = cmds.camera(name='CAM_S033')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S033')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1684)
cmds.setKeyframe(cam + '.rotateY', t=1684)
cmds.setKeyframe(cam + '.rotateZ', t=1684)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1684)
cmds.setKeyframe(cam + '.translateX', t=1753)
cmds.setKeyframe(cam + '.translateY', t=1684)
cmds.setKeyframe(cam + '.translateY', t=1753)
cmds.setKeyframe(cam + '.translateZ', t=1684)
cmds.setKeyframe(cam + '.translateZ', t=1753)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1753)
cmds.setKeyframe(cam + '.rotateY', t=1753)
cmds.setKeyframe(cam + '.rotateZ', t=1753)
cmds.delete(lt)
blink_loop_all(1684, 1753)
breath('Ma', 1684, 1753)
breath('Huang', 1684, 1753)
breath('Shiye', 1684, 1753)
glance('Ma', 'Huang', 1718)

# ---- S034 ----
cam = cmds.camera(name='CAM_S034')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S034')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1754)
cmds.setKeyframe(cam + '.rotateY', t=1754)
cmds.setKeyframe(cam + '.rotateZ', t=1754)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1754)
cmds.setKeyframe(cam + '.translateX', t=1815)
cmds.setKeyframe(cam + '.translateY', t=1754)
cmds.setKeyframe(cam + '.translateY', t=1815)
cmds.setKeyframe(cam + '.translateZ', t=1754)
cmds.setKeyframe(cam + '.translateZ', t=1815)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1815)
cmds.setKeyframe(cam + '.rotateY', t=1815)
cmds.setKeyframe(cam + '.rotateZ', t=1815)
cmds.delete(lt)
blink_loop_all(1754, 1815)
breath('Ma', 1754, 1815)
breath('Huang', 1754, 1815)
breath('Shiye', 1754, 1815)
glance('Ma', 'Huang', 1784)

# ---- S035 ----
cam = cmds.camera(name='CAM_S035')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S035')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1816)
cmds.setKeyframe(cam + '.rotateY', t=1816)
cmds.setKeyframe(cam + '.rotateZ', t=1816)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1816)
cmds.setKeyframe(cam + '.translateX', t=1875)
cmds.setKeyframe(cam + '.translateY', t=1816)
cmds.setKeyframe(cam + '.translateY', t=1875)
cmds.setKeyframe(cam + '.translateZ', t=1816)
cmds.setKeyframe(cam + '.translateZ', t=1875)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1875)
cmds.setKeyframe(cam + '.rotateY', t=1875)
cmds.setKeyframe(cam + '.rotateZ', t=1875)
cmds.delete(lt)
blink_loop_all(1816, 1875)
breath('Ma', 1816, 1875)
breath('Huang', 1816, 1875)
breath('Shiye', 1816, 1875)
glance('Ma', 'Huang', 1845)

# ---- S036 ----
cam = cmds.camera(name='CAM_S036')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S036')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1876)
cmds.setKeyframe(cam + '.rotateY', t=1876)
cmds.setKeyframe(cam + '.rotateZ', t=1876)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1876)
cmds.setKeyframe(cam + '.translateX', t=1963)
cmds.setKeyframe(cam + '.translateY', t=1876)
cmds.setKeyframe(cam + '.translateY', t=1963)
cmds.setKeyframe(cam + '.translateZ', t=1876)
cmds.setKeyframe(cam + '.translateZ', t=1963)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=1963)
cmds.setKeyframe(cam + '.rotateY', t=1963)
cmds.setKeyframe(cam + '.rotateZ', t=1963)
cmds.delete(lt)
blink_loop_all(1876, 1963)
breath('Ma', 1876, 1963)
breath('Huang', 1876, 1963)
breath('Shiye', 1876, 1963)
glance('Ma', 'Huang', 1919)

# ---- S037 ----
cam = cmds.camera(name='CAM_S037')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S037')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=1964)
cmds.setKeyframe(cam + '.rotateY', t=1964)
cmds.setKeyframe(cam + '.rotateZ', t=1964)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=1964)
cmds.setKeyframe(cam + '.translateX', t=2091)
cmds.setKeyframe(cam + '.translateY', t=1964)
cmds.setKeyframe(cam + '.translateY', t=2091)
cmds.setKeyframe(cam + '.translateZ', t=1964)
cmds.setKeyframe(cam + '.translateZ', t=2091)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2091)
cmds.setKeyframe(cam + '.rotateY', t=2091)
cmds.setKeyframe(cam + '.rotateZ', t=2091)
cmds.delete(lt)
blink_loop_all(1964, 2091)
breath('Ma', 1964, 2091)
breath('Huang', 1964, 2091)
breath('Shiye', 1964, 2091)
glance('Ma', 'Huang', 2027)

# ---- S038 ----
cam = cmds.camera(name='CAM_S038')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S038')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2092)
cmds.setKeyframe(cam + '.rotateY', t=2092)
cmds.setKeyframe(cam + '.rotateZ', t=2092)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=2092)
cmds.setKeyframe(cam + '.translateX', t=2156)
cmds.setKeyframe(cam + '.translateY', t=2092)
cmds.setKeyframe(cam + '.translateY', t=2156)
cmds.setKeyframe(cam + '.translateZ', t=2092)
cmds.setKeyframe(cam + '.translateZ', t=2156)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2156)
cmds.setKeyframe(cam + '.rotateY', t=2156)
cmds.setKeyframe(cam + '.rotateZ', t=2156)
cmds.delete(lt)
blink_loop_all(2092, 2156)
breath('Ma', 2092, 2156)
breath('Huang', 2092, 2156)
breath('Shiye', 2092, 2156)
glance('Ma', 'Huang', 2124)

# ---- S039 ----
cam = cmds.camera(name='CAM_S039')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S039')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2157)
cmds.setKeyframe(cam + '.rotateY', t=2157)
cmds.setKeyframe(cam + '.rotateZ', t=2157)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=2157)
cmds.setKeyframe(cam + '.translateX', t=2204)
cmds.setKeyframe(cam + '.translateY', t=2157)
cmds.setKeyframe(cam + '.translateY', t=2204)
cmds.setKeyframe(cam + '.translateZ', t=2157)
cmds.setKeyframe(cam + '.translateZ', t=2204)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2204)
cmds.setKeyframe(cam + '.rotateY', t=2204)
cmds.setKeyframe(cam + '.rotateZ', t=2204)
cmds.delete(lt)
blink_loop_all(2157, 2204)
breath('Ma', 2157, 2204)
breath('Huang', 2157, 2204)
breath('Shiye', 2157, 2204)
glance('Ma', 'Huang', 2180)

# ---- S040 ----
cam = cmds.camera(name='CAM_S040')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S040')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2205)
cmds.setKeyframe(cam + '.rotateY', t=2205)
cmds.setKeyframe(cam + '.rotateZ', t=2205)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=2205)
cmds.setKeyframe(cam + '.translateX', t=2238)
cmds.setKeyframe(cam + '.translateY', t=2205)
cmds.setKeyframe(cam + '.translateY', t=2238)
cmds.setKeyframe(cam + '.translateZ', t=2205)
cmds.setKeyframe(cam + '.translateZ', t=2238)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2238)
cmds.setKeyframe(cam + '.rotateY', t=2238)
cmds.setKeyframe(cam + '.rotateZ', t=2238)
cmds.delete(lt)
blink_loop_all(2205, 2238)
breath('Ma', 2205, 2238)
breath('Huang', 2205, 2238)
breath('Shiye', 2205, 2238)
glance('Ma', 'Huang', 2221)

# ---- S041 ----
cam = cmds.camera(name='CAM_S041')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S041')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2239)
cmds.setKeyframe(cam + '.rotateY', t=2239)
cmds.setKeyframe(cam + '.rotateZ', t=2239)
cmds.setAttr(cam + '.translate', 0, 117, 156)
cmds.setKeyframe(cam + '.translateX', t=2239)
cmds.setKeyframe(cam + '.translateX', t=2263)
cmds.setKeyframe(cam + '.translateY', t=2239)
cmds.setKeyframe(cam + '.translateY', t=2263)
cmds.setKeyframe(cam + '.translateZ', t=2239)
cmds.setKeyframe(cam + '.translateZ', t=2263)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2263)
cmds.setKeyframe(cam + '.rotateY', t=2263)
cmds.setKeyframe(cam + '.rotateZ', t=2263)
cmds.delete(lt)
blink_loop_all(2239, 2263)
breath('Ma', 2239, 2263)
breath('Huang', 2239, 2263)
breath('Shiye', 2239, 2263)
glance('Ma', 'Huang', 2251)

# ---- S042 ----
cam = cmds.camera(name='CAM_S042')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S042')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2264)
cmds.setKeyframe(cam + '.rotateY', t=2264)
cmds.setKeyframe(cam + '.rotateZ', t=2264)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=2264)
cmds.setKeyframe(cam + '.translateX', t=2272)
cmds.setKeyframe(cam + '.translateY', t=2264)
cmds.setKeyframe(cam + '.translateY', t=2272)
cmds.setKeyframe(cam + '.translateZ', t=2264)
cmds.setKeyframe(cam + '.translateZ', t=2272)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2272)
cmds.setKeyframe(cam + '.rotateY', t=2272)
cmds.setKeyframe(cam + '.rotateZ', t=2272)
cmds.delete(lt)
blink_loop_all(2264, 2272)
breath('Ma', 2264, 2272)
breath('Huang', 2264, 2272)
breath('Shiye', 2264, 2272)
glance('Ma', 'Huang', 2268)

# ---- S043 ----
cam = cmds.camera(name='CAM_S043')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S043')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2273)
cmds.setKeyframe(cam + '.rotateY', t=2273)
cmds.setKeyframe(cam + '.rotateZ', t=2273)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2273, 2291)
breath('Ma', 2273, 2291)
breath('Huang', 2273, 2291)
breath('Shiye', 2273, 2291)
glance('Ma', 'Huang', 2282)

# ---- S044 ----
cam = cmds.camera(name='CAM_S044')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S044')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2292)
cmds.setKeyframe(cam + '.rotateY', t=2292)
cmds.setKeyframe(cam + '.rotateZ', t=2292)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2292, 2312)
breath('Ma', 2292, 2312)
breath('Huang', 2292, 2312)
breath('Shiye', 2292, 2312)
glance('Ma', 'Huang', 2302)

# ---- S045 ----
cam = cmds.camera(name='CAM_S045')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S045')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2313)
cmds.setKeyframe(cam + '.rotateY', t=2313)
cmds.setKeyframe(cam + '.rotateZ', t=2313)
cmds.setAttr(cam + '.translate', 0, 117, 156)
cmds.setKeyframe(cam + '.translateX', t=2313)
cmds.setKeyframe(cam + '.translateX', t=2342)
cmds.setKeyframe(cam + '.translateY', t=2313)
cmds.setKeyframe(cam + '.translateY', t=2342)
cmds.setKeyframe(cam + '.translateZ', t=2313)
cmds.setKeyframe(cam + '.translateZ', t=2342)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2342)
cmds.setKeyframe(cam + '.rotateY', t=2342)
cmds.setKeyframe(cam + '.rotateZ', t=2342)
cmds.delete(lt)
blink_loop_all(2313, 2342)
breath('Ma', 2313, 2342)
breath('Huang', 2313, 2342)
breath('Shiye', 2313, 2342)
glance('Ma', 'Huang', 2327)

# ---- S046 ----
cam = cmds.camera(name='CAM_S046')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S046')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2343)
cmds.setKeyframe(cam + '.rotateY', t=2343)
cmds.setKeyframe(cam + '.rotateZ', t=2343)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2343, 2369)
breath('Ma', 2343, 2369)
breath('Huang', 2343, 2369)
breath('Shiye', 2343, 2369)
glance('Ma', 'Huang', 2356)

# ---- S047 ----
cam = cmds.camera(name='CAM_S047')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S047')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2370)
cmds.setKeyframe(cam + '.rotateY', t=2370)
cmds.setKeyframe(cam + '.rotateZ', t=2370)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2370, 2405)
breath('Ma', 2370, 2405)
breath('Huang', 2370, 2405)
breath('Shiye', 2370, 2405)
glance('Ma', 'Huang', 2387)

# ---- S048 ----
cam = cmds.camera(name='CAM_S048')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S048')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2406)
cmds.setKeyframe(cam + '.rotateY', t=2406)
cmds.setKeyframe(cam + '.rotateZ', t=2406)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2406, 2453)
breath('Ma', 2406, 2453)
breath('Huang', 2406, 2453)
breath('Shiye', 2406, 2453)
glance('Ma', 'Huang', 2429)

# ---- S049 ----
cam = cmds.camera(name='CAM_S049')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S049')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2454)
cmds.setKeyframe(cam + '.rotateY', t=2454)
cmds.setKeyframe(cam + '.rotateZ', t=2454)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2454, 2489)
breath('Ma', 2454, 2489)
breath('Huang', 2454, 2489)
breath('Shiye', 2454, 2489)
glance('Ma', 'Huang', 2471)

# ---- S050 ----
cam = cmds.camera(name='CAM_S050')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S050')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2490)
cmds.setKeyframe(cam + '.rotateY', t=2490)
cmds.setKeyframe(cam + '.rotateZ', t=2490)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2490, 2526)
breath('Ma', 2490, 2526)
breath('Huang', 2490, 2526)
breath('Shiye', 2490, 2526)
glance('Ma', 'Huang', 2508)

# ---- S051 ----
cam = cmds.camera(name='CAM_S051')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S051')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2527)
cmds.setKeyframe(cam + '.rotateY', t=2527)
cmds.setKeyframe(cam + '.rotateZ', t=2527)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2527, 2549)
breath('Ma', 2527, 2549)
breath('Huang', 2527, 2549)
breath('Shiye', 2527, 2549)
glance('Ma', 'Huang', 2538)

# ---- S052 ----
cam = cmds.camera(name='CAM_S052')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S052')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2550)
cmds.setKeyframe(cam + '.rotateY', t=2550)
cmds.setKeyframe(cam + '.rotateZ', t=2550)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2550, 2571)
breath('Ma', 2550, 2571)
breath('Huang', 2550, 2571)
breath('Shiye', 2550, 2571)
glance('Ma', 'Huang', 2560)

# ---- S053 ----
cam = cmds.camera(name='CAM_S053')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S053')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2572)
cmds.setKeyframe(cam + '.rotateY', t=2572)
cmds.setKeyframe(cam + '.rotateZ', t=2572)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2572, 2642)
breath('Ma', 2572, 2642)
breath('Huang', 2572, 2642)
breath('Shiye', 2572, 2642)
glance('Ma', 'Huang', 2607)

# ---- S054 ----
cam = cmds.camera(name='CAM_S054')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S054')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2643)
cmds.setKeyframe(cam + '.rotateY', t=2643)
cmds.setKeyframe(cam + '.rotateZ', t=2643)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2643, 2657)
breath('Ma', 2643, 2657)
breath('Huang', 2643, 2657)
breath('Shiye', 2643, 2657)
glance('Ma', 'Huang', 2650)

# ---- S055 ----
cam = cmds.camera(name='CAM_S055')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 50)
cmds.setAttr(cam + '.translate', 0, 111, 207)
lt = cmds.spaceLocator(name='aimT_S055')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2658)
cmds.setKeyframe(cam + '.rotateY', t=2658)
cmds.setKeyframe(cam + '.rotateZ', t=2658)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2658, 2687)
breath('Ma', 2658, 2687)
breath('Huang', 2658, 2687)
breath('Shiye', 2658, 2687)
glance('Ma', 'Huang', 2672)

# ---- S056 ----
cam = cmds.camera(name='CAM_S056')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S056')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2688)
cmds.setKeyframe(cam + '.rotateY', t=2688)
cmds.setKeyframe(cam + '.rotateZ', t=2688)
cmds.setAttr(cam + '.translate', 0, 91, 156)
cmds.setKeyframe(cam + '.translateX', t=2688)
cmds.setKeyframe(cam + '.translateX', t=2736)
cmds.setKeyframe(cam + '.translateY', t=2688)
cmds.setKeyframe(cam + '.translateY', t=2736)
cmds.setKeyframe(cam + '.translateZ', t=2688)
cmds.setKeyframe(cam + '.translateZ', t=2736)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=2736)
cmds.setKeyframe(cam + '.rotateY', t=2736)
cmds.setKeyframe(cam + '.rotateZ', t=2736)
cmds.delete(lt)
blink_loop_all(2688, 2736)
breath('Ma', 2688, 2736)
breath('Huang', 2688, 2736)
breath('Shiye', 2688, 2736)
glance('Ma', 'Huang', 2712)

# ---- S057 ----
cam = cmds.camera(name='CAM_S057')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S057')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2737)
cmds.setKeyframe(cam + '.rotateY', t=2737)
cmds.setKeyframe(cam + '.rotateZ', t=2737)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2737, 2796)
breath('Ma', 2737, 2796)
breath('Huang', 2737, 2796)
breath('Shiye', 2737, 2796)
glance('Ma', 'Huang', 2766)

# ---- S058 ----
cam = cmds.camera(name='CAM_S058')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S058')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2797)
cmds.setKeyframe(cam + '.rotateY', t=2797)
cmds.setKeyframe(cam + '.rotateZ', t=2797)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2797, 2841)
breath('Ma', 2797, 2841)
breath('Huang', 2797, 2841)
breath('Shiye', 2797, 2841)
glance('Ma', 'Huang', 2819)

# ---- S059 ----
cam = cmds.camera(name='CAM_S059')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S059')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2842)
cmds.setKeyframe(cam + '.rotateY', t=2842)
cmds.setKeyframe(cam + '.rotateZ', t=2842)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2842, 2877)
breath('Ma', 2842, 2877)
breath('Huang', 2842, 2877)
breath('Shiye', 2842, 2877)
glance('Ma', 'Huang', 2859)

# ---- S060 ----
cam = cmds.camera(name='CAM_S060')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S060')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2878)
cmds.setKeyframe(cam + '.rotateY', t=2878)
cmds.setKeyframe(cam + '.rotateZ', t=2878)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2878, 2945)
breath('Ma', 2878, 2945)
breath('Huang', 2878, 2945)
breath('Shiye', 2878, 2945)
glance('Ma', 'Huang', 2911)

# ---- S061 ----
cam = cmds.camera(name='CAM_S061')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S061')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2946)
cmds.setKeyframe(cam + '.rotateY', t=2946)
cmds.setKeyframe(cam + '.rotateZ', t=2946)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2946, 2971)
breath('Ma', 2946, 2971)
breath('Huang', 2946, 2971)
breath('Shiye', 2946, 2971)
glance('Ma', 'Huang', 2958)

# ---- S062 ----
cam = cmds.camera(name='CAM_S062')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S062')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=2972)
cmds.setKeyframe(cam + '.rotateY', t=2972)
cmds.setKeyframe(cam + '.rotateZ', t=2972)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(2972, 3023)
breath('Ma', 2972, 3023)
breath('Huang', 2972, 3023)
breath('Shiye', 2972, 3023)
glance('Ma', 'Huang', 2997)

# ---- S063 ----
cam = cmds.camera(name='CAM_S063')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S063')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3024)
cmds.setKeyframe(cam + '.rotateY', t=3024)
cmds.setKeyframe(cam + '.rotateZ', t=3024)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3024, 3040)
breath('Ma', 3024, 3040)
breath('Huang', 3024, 3040)
breath('Shiye', 3024, 3040)
glance('Ma', 'Huang', 3032)

# ---- S064 ----
cam = cmds.camera(name='CAM_S064')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S064')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3041)
cmds.setKeyframe(cam + '.rotateY', t=3041)
cmds.setKeyframe(cam + '.rotateZ', t=3041)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3041, 3064)
breath('Ma', 3041, 3064)
breath('Huang', 3041, 3064)
breath('Shiye', 3041, 3064)
glance('Ma', 'Huang', 3052)

# ---- S065 ----
cam = cmds.camera(name='CAM_S065')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S065')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3065)
cmds.setKeyframe(cam + '.rotateY', t=3065)
cmds.setKeyframe(cam + '.rotateZ', t=3065)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3065, 3087)
breath('Ma', 3065, 3087)
breath('Huang', 3065, 3087)
breath('Shiye', 3065, 3087)
glance('Ma', 'Huang', 3076)

# ---- S066 ----
cam = cmds.camera(name='CAM_S066')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S066')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3088)
cmds.setKeyframe(cam + '.rotateY', t=3088)
cmds.setKeyframe(cam + '.rotateZ', t=3088)
cmds.setAttr(cam + '.translate', 0, 117, 156)
cmds.setKeyframe(cam + '.translateX', t=3088)
cmds.setKeyframe(cam + '.translateX', t=3125)
cmds.setKeyframe(cam + '.translateY', t=3088)
cmds.setKeyframe(cam + '.translateY', t=3125)
cmds.setKeyframe(cam + '.translateZ', t=3088)
cmds.setKeyframe(cam + '.translateZ', t=3125)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=3125)
cmds.setKeyframe(cam + '.rotateY', t=3125)
cmds.setKeyframe(cam + '.rotateZ', t=3125)
cmds.delete(lt)
blink_loop_all(3088, 3125)
breath('Ma', 3088, 3125)
breath('Huang', 3088, 3125)
breath('Shiye', 3088, 3125)
glance('Ma', 'Huang', 3106)

# ---- S067 ----
cam = cmds.camera(name='CAM_S067')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S067')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3126)
cmds.setKeyframe(cam + '.rotateY', t=3126)
cmds.setKeyframe(cam + '.rotateZ', t=3126)
cmds.setAttr(cam + '.translate', 0, 91, 156)
cmds.setKeyframe(cam + '.translateX', t=3126)
cmds.setKeyframe(cam + '.translateX', t=3202)
cmds.setKeyframe(cam + '.translateY', t=3126)
cmds.setKeyframe(cam + '.translateY', t=3202)
cmds.setKeyframe(cam + '.translateZ', t=3126)
cmds.setKeyframe(cam + '.translateZ', t=3202)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=3202)
cmds.setKeyframe(cam + '.rotateY', t=3202)
cmds.setKeyframe(cam + '.rotateZ', t=3202)
cmds.delete(lt)
blink_loop_all(3126, 3202)
breath('Ma', 3126, 3202)
breath('Huang', 3126, 3202)
breath('Shiye', 3126, 3202)
glance('Ma', 'Huang', 3164)

# ---- S068 ----
cam = cmds.camera(name='CAM_S068')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S068')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3203)
cmds.setKeyframe(cam + '.rotateY', t=3203)
cmds.setKeyframe(cam + '.rotateZ', t=3203)
cmds.setAttr(cam + '.translate', 0, 117, 156)
cmds.setKeyframe(cam + '.translateX', t=3203)
cmds.setKeyframe(cam + '.translateX', t=3327)
cmds.setKeyframe(cam + '.translateY', t=3203)
cmds.setKeyframe(cam + '.translateY', t=3327)
cmds.setKeyframe(cam + '.translateZ', t=3203)
cmds.setKeyframe(cam + '.translateZ', t=3327)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=3327)
cmds.setKeyframe(cam + '.rotateY', t=3327)
cmds.setKeyframe(cam + '.rotateZ', t=3327)
cmds.delete(lt)
blink_loop_all(3203, 3327)
breath('Ma', 3203, 3327)
breath('Huang', 3203, 3327)
breath('Shiye', 3203, 3327)
glance('Ma', 'Huang', 3265)

# ---- S069 ----
cam = cmds.camera(name='CAM_S069')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S069')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3328)
cmds.setKeyframe(cam + '.rotateY', t=3328)
cmds.setKeyframe(cam + '.rotateZ', t=3328)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3328, 3443)
breath('Ma', 3328, 3443)
breath('Huang', 3328, 3443)
breath('Shiye', 3328, 3443)
glance('Ma', 'Huang', 3385)

# ---- S070 ----
cam = cmds.camera(name='CAM_S070')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S070')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3444)
cmds.setKeyframe(cam + '.rotateY', t=3444)
cmds.setKeyframe(cam + '.rotateZ', t=3444)
cmds.delete(ac)
cmds.delete(lt)
blink_loop_all(3444, 3467)
breath('Ma', 3444, 3467)
breath('Huang', 3444, 3467)
breath('Shiye', 3444, 3467)
glance('Ma', 'Huang', 3455)

# ---- S071 ----
cam = cmds.camera(name='CAM_S071')[0]
sh = cmds.listRelatives(cam, s=True)[0]
cmds.setAttr(sh + '.focalLength', 65)
cmds.setAttr(cam + '.translate', 0, 103, 156)
lt = cmds.spaceLocator(name='aimT_S071')[0]
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.setKeyframe(cam + '.rotateX', t=3468)
cmds.setKeyframe(cam + '.rotateY', t=3468)
cmds.setKeyframe(cam + '.rotateZ', t=3468)
cmds.setAttr(cam + '.translate', 26, 103, 156)
cmds.setKeyframe(cam + '.translateX', t=3468)
cmds.setKeyframe(cam + '.translateX', t=3512)
cmds.setKeyframe(cam + '.translateY', t=3468)
cmds.setKeyframe(cam + '.translateY', t=3512)
cmds.setKeyframe(cam + '.translateZ', t=3468)
cmds.setKeyframe(cam + '.translateZ', t=3512)
cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('Ma', 'Head'), q=True, ws=True, t=True)[:3]])
ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))
cmds.delete(ac)
cmds.setKeyframe(cam + '.rotateX', t=3512)
cmds.setKeyframe(cam + '.rotateY', t=3512)
cmds.setKeyframe(cam + '.rotateZ', t=3512)
cmds.delete(lt)
blink_loop_all(3468, 3512)
breath('Ma', 3468, 3512)
breath('Huang', 3468, 3512)
breath('Shiye', 3468, 3512)
glance('Ma', 'Huang', 3490)

print('P4_ALL_SHOTS_BUILT')
