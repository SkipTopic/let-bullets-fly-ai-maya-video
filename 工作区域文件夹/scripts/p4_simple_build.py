# -*- coding: utf-8 -*-
"""Fallback P4: fixed cameras + root animation + blink. Builds 71 shots."""
import sys
import math
import re
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
RUN = W / "scripts" / "_simp"
RUN.mkdir(exist_ok=True)

SEATS = {"Ma": (0, -46, -100), "Huang": (44, -46, 26), "Shiye": (-44, -46, 26)}

with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

runtime = r'''
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
'''
(RUN / "runtime.py").write_text(runtime, encoding="utf-8")


def shot_code(r):
    i = int(r["shot_id"][1:])
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    dial = r["dialogue"] or ""
    act = r["action"] or ""
    move = r["camera_move"] or ""
    size = r["shot_size"]
    m = re.search(r"[（(](马县长|黄四郎|师爷|三人)[)）]", dial)
    spk = None
    if m:
        t = m.group(1)
        spk = {"马县长": "Ma", "黄四郎": "Huang", "师爷": "Shiye", "三人": "Ma"}.get(t)
    if not spk:
        if re.search("师爷", act):
            spk = "Shiye"
        elif re.search("黄四郎|黄老爷", act):
            spk = "Huang"
        else:
            spk = "Ma"
    sx, sy, sz = SEATS[spk]
    L = []
    L.append("# ---- S%03d ----" % i)
    L.append("cam = cmds.camera(name='CAM_S%03d')[0]" % i)
    L.append("shp = cmds.listRelatives(cam, s=True)[0]")
    focal = 50 if "中景" in size else 65
    L.append("cmds.setAttr(shp + '.focalLength', %d)" % focal)
    px = sx * 0.5
    pz = sz * 0.35 + 185
    L.append("cmds.setAttr(cam + '.translate', %.0f, 132, %.0f)" % (px, pz))
    drift = 0
    if re.search("向右移动|向右移", move):
        drift = 30
    elif re.search("向左", move):
        drift = -30
    tx, ty, tz = sx * 0.55, 96, sz * 0.55 - 5
    yaw0 = math.degrees(math.atan2(px - tx, pz - tz))
    pitch0 = math.degrees(math.atan2(ty - 132, math.sqrt((tx - px) ** 2 + (tz - pz) ** 2)))
    L.append("cmds.setAttr(cam + '.rotateY', %.2f)" % yaw0)
    L.append("cmds.setAttr(cam + '.rotateX', %.2f)" % pitch0)
    L.append("cmds.setAttr(cam + '.rotateZ', 0)")
    for ax in ("X", "Y", "Z"):
        L.append("cmds.setKeyframe(cam + '.rotate%s', t=%d)" % (ax, f0))
    if drift:
        L.append("cmds.setAttr(cam + '.translateX', %.0f)" % (px + drift))
        L.append("cmds.setKeyframe(cam + '.translateX', t=%d)" % f0)
        L.append("cmds.setKeyframe(cam + '.translateX', t=%d)" % f1)
        tx2 = sx * 0.5 - 14
        yaw1 = math.degrees(math.atan2((px + drift) - tx2, pz - tz))
        pitch1 = math.degrees(math.atan2(ty - 132, math.sqrt((tx2 - (px + drift)) ** 2 + (tz - pz) ** 2)))
        L.append("cmds.setAttr(cam + '.rotateY', %.2f)" % yaw1)
        L.append("cmds.setAttr(cam + '.rotateX', %.2f)" % pitch1)
        for ax in ("X", "Y", "Z"):
            L.append("cmds.setKeyframe(cam + '.rotate%s', t=%d)" % (ax, f1))
    L.append("blink_loop_all(%d, %d)" % (f0, f1))
    for tag in ("Ma", "Huang", "Shiye"):
        L.append("sway('%s', %d, %d, %.1f)" % (tag, f0, f1, 1.4 if tag == spk else 0.9))
    if "身体向前" in act or ("前" in act and "倾" in act):
        L.append("lean_root('%s', %d, %d, -4)" % (spk, f0 + 6, 14))
    return "\n".join(L)


chunks = []
for idx in range(0, len(rows), 6):
    grp = rows[idx:idx + 6]
    chunks.append("\n\n".join(shot_code(r) for r in grp))
for i, ch in enumerate(chunks):
    (RUN / ("simp_%02d.py" % i)).write_text(ch, encoding="utf-8")
print("chunks=%d" % len(chunks))

code_all = (
    "import maya.cmds as cmds\nimport io\nP = print\n"
    "W = r\"%s\"\nn = 0\n"
    "for pat in (\"CAM_S*\", \"aimT_S*\"):\n"
    "    for c in cmds.ls(pat) or []:\n"
    "        try:\n            cmds.delete(c); n += 1\n        except Exception:\n            pass\n"
    "P(\"cleaned=\" + str(n))\n"
    "exec(io.open(r\"%s\", encoding=\"utf-8\").read())\n"
    % (W, RUN / "runtime.py")
)
r = py(code_all, timeout=600)
print("CLEAN+RT:", r[-200:])

ok, fail = 0, []
for i in range(len(chunks)):
    p = RUN / ("simp_%02d.py" % i)
    code = ('import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n'
            '    print("CHUNK_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("CHUNK_FAIL")' % p)
    r = py(code, timeout=900)
    if "CHUNK_OK" in r:
        ok += 1
    else:
        fail.append(i)
        print("simp %d FAIL:\n%s" % (i, r[-600:]))
print("simple ok=%d fail=%d %s" % (ok, len(fail), fail[:6]))

r = py(
    "import maya.cmds as cmds\nimport io\nP = print\n"
    "W = r\"%s\"\nmp = \"modelPanel4\"\n"
    "cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)\n"
    "frames = {\"S001\": (1, 1), \"S030\": (1268, 30), \"S060\": (2489, 60)}\n"
    "for name, (f, n) in frames.items():\n"
    "    cam = \"CAM_S%d\" % n\n"
    "    if not cmds.objExists(cam):\n        P(\"MISSING \" + cam)\n        continue\n"
    "    cmds.modelEditor(mp, e=True, camera=cam)\n    cmds.currentTime(f)\n"
    "    cmds.playblast(frame=[f], format=\"image\", filename=W + \"/qa/simple_\" + name,\n"
    "                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,\n"
    "                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression=\"png\")\n"
    "    P(\"rendered \" + name)\n"
    "cmds.file(rename=W + \"/scenes/p4_simple.mb\")\n"
    "cmds.file(save=True, force=True, type=\"mayaBinary\")\n"
    "print(\"SIMPLE_DONE\")\n" % W, timeout=900)
print(r[-400:])
