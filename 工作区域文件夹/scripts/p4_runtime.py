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
