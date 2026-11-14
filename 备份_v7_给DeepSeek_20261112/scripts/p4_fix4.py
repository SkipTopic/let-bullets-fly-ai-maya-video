# -*- coding: utf-8 -*-
"""Fix4: pose arms/legs via long-path joints, rebuild 71 cams (3 sizes + real drift)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import math, re, csv
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

CHARS = {
    "Ma": ("*MakotoFBXASC032Yuki_arm", (0, -100), 180),
    "Huang": ("*AragakiFBXASC032Shinjiro_arm", (44, 26), 120),
    "Shiye": ("*JunpeiFBXASC032Iori_arm", (-44, 26), -120),
}
JMAP = {}
for tag, (pa, pos, ry) in CHARS.items():
    arm = (cmds.ls(pa) or [None])[0]
    mp = {}
    for jp in (cmds.ls(arm, long=True, dag=True, type="joint") or []):
        nm = jp.split("|")[-1]
        if nm not in mp:
            mp[nm] = jp
    JMAP[tag] = mp

def J(tag, name):
    return JMAP[tag].get(name)

def setrot(j, rx=None, ry=None, rz=None):
    if not j:
        return
    for ax, lock in (("rotateX", rx), ("rotateY", ry), ("rotateZ", rz)):
        if lock is None:
            continue
        try:
            cmds.setAttr(j + "." + ax, lock=False)
        except Exception:
            pass
        try:
            cmds.setAttr(j + "." + ax, lock)
        except Exception as e:
            P("rot fail %s.%s: %s" % (j.split("|")[-1], ax, e))

# ---- pose: arms down from T, elbows bent, sit legs
for tag in CHARS:
    setrot(J(tag, "LeftArm"), rz=62)
    setrot(J(tag, "RightArm"), rz=-62)
    setrot(J(tag, "LeftForeArm"), ry=25)
    setrot(J(tag, "RightForeArm"), ry=-25)
    setrot(J(tag, "LeftUpLeg"), rx=-80)
    setrot(J(tag, "RightUpLeg"), rx=-80)
    setrot(J(tag, "LeftLeg"), rx=80)
    setrot(J(tag, "RightLeg"), rx=80)
    setrot(J(tag, "LeftFoot"), rx=10)
    setrot(J(tag, "RightFoot"), rx=10)
P("pose done")

# ---- rebuild 71 cameras
n = 0
for c in (cmds.ls("CAM_S*") or []):
    try:
        cmds.delete(c); n += 1
    except Exception:
        pass
P("old cams cleaned=%d" % n)

SEAT = {"Ma": (0, -100), "Huang": (44, 26), "Shiye": (-44, 26)}
HEADY = 118.0
CHESTY = 96.0

with open(W + "/shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

def spk_of(dial, act):
    m = re.search(r"[（(](马县长|黄四郎|师爷|三人)[)）]", dial or "")
    if m:
        return {"马县长": "Ma", "黄四郎": "Huang", "师爷": "Shiye", "三人": "Ma"}.get(m.group(1), "Ma")
    a = act or ""
    if "师爷" in a:
        return "Shiye"
    if "黄四郎" in a or "黄老爷" in a:
        return "Huang"
    return "Ma"

made = 0
for r in rows:
    i = int(r["shot_id"][1:])
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    spk = spk_of(r["dialogue"], r["action"])
    sx, sz = SEAT[spk]
    size = r["shot_size"]
    move = r["camera_move"] or ""
    if "特写" in size:
        focal, dist, ty = 85, 150, HEADY
    elif "中景" in size:
        focal, dist, ty = 50, 245, CHESTY
    else:
        focal, dist, ty = 65, 190, HEADY - 6
    # camera across table from speaker
    px = sx - (sx / max(1, abs(sx))) * dist * 0.62 if sx != 0 else 14
    pz = sz - (sz / max(1, abs(sz))) * dist * 0.62 if sz != 0 else dist * 0.9
    if sx == 0:
        px = 16
        pz = sz + dist * 0.92
    cam = cmds.camera(name="CAM_S%03d" % i)[0]
    shp = cmds.listRelatives(cam, s=True)[0]
    cmds.setAttr(shp + ".focalLength", focal)
    cmds.setAttr(cam + ".translate", px, ty + 12, pz)
    tx, tyy, tz = sx * 0.7, ty - 4, sz * 0.7
    yaw = math.degrees(math.atan2(px - tx, pz - tz))
    pitch = math.degrees(math.atan2(tyy - (ty + 12), math.sqrt((tx - px) ** 2 + (tz - pz) ** 2)))
    cmds.setAttr(cam + ".rotateY", yaw)
    cmds.setAttr(cam + ".rotateX", pitch)
    cmds.setAttr(cam + ".rotateZ", 0)
    for ax in ("X", "Y", "Z"):
        cmds.setKeyframe(cam + ".rotate" + ax, t=f0)
    # real drift: different start/end translateX when move says so
    drift = 0
    if re.search("向右移动|向右移", move):
        drift = 24
    elif re.search("向左", move):
        drift = -24
    if drift:
        x0, x1 = px - drift / 2.0, px + drift / 2.0
        cmds.setAttr(cam + ".translateX", x0)
        cmds.setKeyframe(cam + ".translateX", t=f0)
        cmds.setAttr(cam + ".translateX", x1)
        cmds.setKeyframe(cam + ".translateX", t=f1)
        yaw1 = math.degrees(math.atan2(x1 - tx, pz - tz))
        cmds.setAttr(cam + ".rotateY", yaw1)
        cmds.setKeyframe(cam + ".rotateY", t=f1)
    made += 1
P("cams made=%d" % made)

cmds.playbackOptions(min=1, max=3512)

# ---- verify render 2 shots
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
for nm, f in (("S001", 1), ("S030", 1268)):
    cmds.modelEditor(mp, e=True, camera="CAM_S%d" % int(nm[1:]))
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/fix4_" + nm,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("FIX4_DONE")
'''

r = py(CODE, timeout=1200)
print(r[-1200:])
