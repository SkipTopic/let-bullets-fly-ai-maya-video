# -*- coding: utf-8 -*-
"""71 cams on the proven wide angle (verified to show all dummies+table) + drift variants."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

CODE = r'''
import maya.cmds as cmds
import math, re, csv
P = print
W = r"C:/Users/admin/Desktop/MayaProject/让子弹飞分镜测试/工作区域文件夹"

n = 0
for c in (cmds.ls("CAM_S*") or []):
    try:
        cmds.delete(c); n += 1
    except Exception:
        pass
P("cleaned=%d" % n)

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

# proven wide rig: pos (0,205,425) rot (-18,0,0) focal 40 shows whole scene
# variants: shift x by speaker direction, small focal range, drift for moves
made = 0
for r in rows:
    i = int(r["shot_id"][1:])
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    spk = spk_of(r["dialogue"], r["action"])
    sx, sz = SEAT_POS[spk]
    size = r["shot_size"]
    move = r["camera_move"] or ""
    focal = 40
    # shift camera toward speaker side a bit, keep same height/angle
    px = sx * 0.28
    pz = 425 - abs(sx) * 0.35
    py = 205
    cam = cmds.camera(name="CAM_S%03d" % i)[0]
    shp = cmds.listRelatives(cam, s=True)[0]
    cmds.setAttr(shp + ".focalLength", focal)
    cmds.setAttr(cam + ".translate", px, py, pz)
    tx, tyy, tz = sx * 0.55, 92, sz * 0.55
    yaw = math.degrees(math.atan2(px - tx, pz - tz))
    pitch = math.degrees(math.atan2(tyy - py, math.sqrt((tx - px) ** 2 + (tz - pz) ** 2)))
    cmds.setAttr(cam + ".rotateY", yaw)
    cmds.setAttr(cam + ".rotateX", pitch)
    cmds.setAttr(cam + ".rotateZ", 0)
    for ax in ("X", "Y", "Z"):
        cmds.setKeyframe(cam + ".rotate" + ax, t=f0)
        cmds.setKeyframe(cam + ".translate" + ax, t=f0)
    drift = 0
    if re.search("向右移动|向右移", move):
        drift = 40
    elif re.search("向左", move):
        drift = -40
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

mp = "modelPanel4"
cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights="all")
for nm, f in (("S001", 1), ("S030", 1268)):
    cmds.modelEditor(mp, e=True, camera="CAM_S%d" % int(nm[1:]))
    cmds.currentTime(f)
    cmds.playblast(frame=[f], format="image", filename=W + "/qa/cam3_" + nm,
                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                   fp=4, percent=100, widthHeight=[854, 480], quality=100, compression="png")
cmds.file(save=True, force=True, type="mayaBinary")
P("CAMS3_DONE")
'''

# SEAT_POS needed inside
CODE = "SEAT_POS = {'Ma': (0, -100), 'Huang': (44, 26), 'Shiye': (-44, 26)}\n" + CODE

r = py(CODE, timeout=1200)
print(r[-500:])
