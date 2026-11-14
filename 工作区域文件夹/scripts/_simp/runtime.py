
import maya.cmds as cmds
import math, random

SEATS = {"Ma": (0, -46, -100), "Huang": (44, -46, 26), "Shiye": (-44, -46, 26)}
TOPP = {"Ma": "*MakotoFBXASC032Yuki_arm",
        "Huang": "*AragakiFBXASC032Shinjiro_arm",
        "Shiye": "*JunpeiFBXASC032Iori_arm"}
_BS = {}


def _top(tag):
    l = cmds.ls(TOPP[tag]) or []
    return l[0] if l else None


def _bs(tag):
    if tag in _BS:
        return _BS[tag]
    m = (cmds.ls(TOPP[tag].replace("_arm", "_mesh")) or [None])[0]
    bs = None
    for n in (cmds.listHistory(m, pdo=True) or []):
        if cmds.nodeType(n) == "blendShape":
            bs = n
            break
    idx = {}
    if bs:
        als = cmds.aliasAttr(bs, q=True) or []
        if isinstance(als, list):
            for k in range(0, len(als), 2):
                idx[als[k]] = als[k + 1]
    _BS[tag] = (bs, idx)
    return _BS[tag]


def blink(tag, t, dur=5):
    ent = _bs(tag)
    if not ent or not ent[0]:
        return
    bs, idx = ent
    if "blink" not in idx:
        return
    a = "%s.%s" % (bs, idx["blink"])
    h = dur / 2.0
    for tt, v in ((max(1, t - h), 0.0), (t, 1.0), (t + h, 0.0)):
        cmds.setAttr(a, v)
        cmds.setKeyframe(a, t=tt)


def blink_loop_all(f0, f1):
    for tag in ("Ma", "Huang", "Shiye"):
        rnd = random.Random(hash(tag) & 0xFFFF)
        t = f0 + rnd.uniform(0.6, 2.2)
        while t < f1 - 3:
            blink(tag, t)
            t += rnd.uniform(2.2, 4.2)


def sway(tag, f0, f1, amp=1.2):
    t0 = _top(tag)
    if not t0:
        return
    try:
        cmds.setAttr(t0 + ".rotateX", lock=False)
    except Exception:
        pass
    try:
        base = cmds.getAttr(t0 + ".rotateX")
    except Exception:
        base = 0
    step = max(4, int((f1 - f0) / 18))
    for t in range(int(f0), int(f1) + 1, step):
        v = base + amp * math.sin((t - f0) / 10.0 * math.pi)
        try:
            cmds.setAttr(t0 + ".rotateX", v)
            cmds.setKeyframe(t0 + ".rotateX", t=t)
        except Exception:
            pass


def lean_root(tag, t, dur, amp):
    t0 = _top(tag)
    if not t0:
        return
    try:
        cmds.setAttr(t0 + ".rotateX", lock=False)
    except Exception:
        pass
    try:
        base = cmds.getAttr(t0 + ".rotateX")
    except Exception:
        base = 0
    try:
        cmds.setAttr(t0 + ".rotateX", base + amp)
        cmds.setKeyframe(t0 + ".rotateX", t=t)
        cmds.setAttr(t0 + ".rotateX", base)
        cmds.setKeyframe(t0 + ".rotateX", t=t + dur)
    except Exception:
        pass


print("SIMPLE_RUNTIME_READY")
