# -*- coding: utf-8 -*-
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")

with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

RUN = W / "scripts" / "_render"
RUN.mkdir(exist_ok=True)

shot_defs = []
for r in rows:
    i = int(r["shot_id"][1:])
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    shot_defs.append((i, f0, f1))

chunks = []
per = 6
for k in range(0, len(shot_defs), per):
    grp = shot_defs[k:k + per]
    code = (
        "import maya.cmds as cmds\nimport os\nP = print\n"
        "W = r\"%s\"\nmp = \"modelPanel4\"\n"
        "cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False)\n"
        "cmds.modelEditor(mp, e=True, camera=\"CAM_WIDE\")\n"
        "SHOTS = %s\n" % (W, repr(grp)) +
        "for tag, f0, f1 in SHOTS:\n"
        "    d = W + (\"/frames/S%03d\" % tag)\n"
        "    os.makedirs(d, exist_ok=True)\n"
        "    cmds.currentTime(f0)\n"
        "    cmds.playblast(frame=list(range(f0, f1 + 1)), format=\"image\", filename=d + \"/S%03d\" % tag,\n"
        "                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,\n"
        "                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression=\"png\")\n"
        "    P(\"shot %03d done\" % tag)\n"
    )
    p = RUN / ("rc_%02d.py" % (k // per))
    p.write_text(code, encoding="utf-8")
    chunks.append(p)
print("render chunks=%d" % len(chunks))

ok, fail = 0, []
for i, p in enumerate(chunks):
    code = 'import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n    print("RC_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("RC_FAIL")' % p
    r = py(code, timeout=3600)
    if "RC_OK" in r:
        ok += 1
        print("render chunk %d OK" % i, flush=True)
    else:
        fail.append(i)
        print("render chunk %d FAIL:\n%s" % (i, r[-400:]), flush=True)
print("render ok=%d fail=%d %s" % (ok, len(fail), fail[:5]))
