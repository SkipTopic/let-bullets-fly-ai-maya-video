# -*- coding: utf-8 -*-
"""P5: render all 71 shots with the proven WIDE camera, 854x480 PNG seq."""
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")

with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# build render script chunks: 6 shots per chunk
lines = []
lines.append("import maya.cmds as cmds")
lines.append("P = print")
lines.append('W = r"%s"' % W)
lines.append('mp = "modelPanel4"')
lines.append("cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)")
lines.append("cmds.modelEditor(mp, e=True, camera='CAM_WIDE')")
lines.append("import os")
lines.append("for tag, shot in SHOTS:")
lines.append("    f0, f1 = shot")
lines.append("    d = r'%s' % W + ('/frames/S%03d' % tag)")
lines.append("    os.makedirs(d, exist_ok=True)")
lines.append("    cmds.currentTime(f0)")
lines.append("    cmds.playblast(frame=[f0, f1], format='image', filename=d + '/S%03d' % tag,")
lines.append("                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,")
lines.append("                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression='png')")
lines.append("    P('shot %03d done' % tag)")
render_head = "\n".join(lines)

# emit shot list definition + split into chunks of 6
shot_defs = []
for r in rows:
    i = int(r["shot_id"][1:])
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    shot_defs.append("SHOTS.append((%d, %d, %d))" % (i, f0, f1))

chunks = []
per = 6
for k in range(0, len(shot_defs), per):
    grp = shot_defs[k:k + per]
    code = render_head + "\nSHOTS = []\n" + "\n".join(grp) + "\nprint('RCHUNK_DONE')"
    p = W / "scripts" / "_render" / ("rc_%02d.py" % (k // per))
    p.parent.mkdir(exist_ok=True)
    p.write_text(code, encoding="utf-8")
    chunks.append(p)
print("render chunks=%d" % len(chunks))

# setup wide camera first
setup = r'''
import maya.cmds as cmds
P = print
W = r"%s"
if cmds.objExists("CAM_WIDE"):
    cmds.delete("CAM_WIDE")
c = cmds.camera(name="CAM_WIDE", focalLength=40)
cmds.setAttr("CAM_WIDE.translate", 0, 205, 425)
cmds.setAttr("CAM_WIDE.rotate", -18, 0, 0)
mp = "modelPanel4"
cmds.modelEditor(mp, e=True, camera="CAM_WIDE", grid=False, hud=False, joints=False)
cmds.currentTime(1)
cmds.playblast(frame=[1], format="image", filename=W + "/qa/wide_check",
               sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
               fp=4, percent=100, widthHeight=[854, 480], quality=90, compression="png")
P("wide cam ready")
''' % W
r = py(setup, timeout=600)
print(r[-200:])

ok, fail = 0, []
for i, p in enumerate(chunks):
    code = 'import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n    print("RC_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("RC_FAIL")' % p
    r = py(code, timeout=1800)
    if "RC_OK" in r:
        ok += 1
        print("render chunk %d OK" % i)
    else:
        fail.append(i)
        print("render chunk %d FAIL:\n%s" % (i, r[-500:]))
print("render ok=%d fail=%d %s" % (ok, len(fail), fail[:5]))
