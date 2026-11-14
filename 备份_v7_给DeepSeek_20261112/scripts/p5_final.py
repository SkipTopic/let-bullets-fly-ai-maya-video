# -*- coding: utf-8 -*-
"""Final render: per-shot camera switch (explicit, no silent fallback), 3512 frames."""
import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")

with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

RUN = W / "scripts" / "_rfinal"
RUN.mkdir(exist_ok=True)

shot_defs = []
for r in rows:
    i = int(r["shot_id"][1:])
    shot_defs.append((i, int(r["start_frame"]), int(r["end_frame"])))

chunks = []
per = 6
for k in range(0, len(shot_defs), per):
    grp = shot_defs[k:k + per]
    code = (
        "import maya.cmds as cmds\nimport os\nP = print\n"
        "W = r\"%s\"\nmp = \"modelPanel4\"\n"
        "cmds.modelEditor(mp, e=True, grid=False, hud=False, joints=False, shadows=True, displayLights=\"all\")\n"
        "SHOTS = %s\n" % (W, repr(grp)) +
        "for tag, f0, f1 in SHOTS:\n"
        "    cam = \"CAM_S%d\" % tag\n"
        "    if not cmds.objExists(cam):\n"
        "        raise RuntimeError(\"missing camera \" + cam)\n"
        "    cmds.modelEditor(mp, e=True, camera=cam)\n"
        "    d = W + (\"/frames/S%03d\" % tag)\n"
        "    os.makedirs(d, exist_ok=True)\n"
        "    for f in os.listdir(d):\n"
        "        os.remove(os.path.join(d, f))\n"
        "    cmds.currentTime(f0)\n"
        "    cmds.playblast(frame=list(range(f0, f1 + 1)), format=\"image\", filename=d + \"/S%03d\" % tag,\n"
        "                   sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,\n"
        "                   fp=4, percent=100, widthHeight=[854, 480], quality=95, compression=\"png\")\n"
        "    P(\"shot %03d done via \" + cam)\n"
    )
    p = RUN / ("rf_%02d.py" % (k // per))
    p.write_text(code, encoding="utf-8")
    chunks.append(p)
print("chunks=%d" % len(chunks))

ok, fail = 0, []
for i, p in enumerate(chunks):
    code = 'import io,traceback\ntry:\n    exec(io.open(r"%s", encoding="utf-8").read())\n    print("RF_OK")\nexcept Exception:\n    print(traceback.format_exc())\n    print("RF_FAIL")' % p
    r = py(code, timeout=3600)
    if "RF_OK" in r:
        ok += 1
        print("rf chunk %d OK" % i, flush=True)
    else:
        fail.append(i)
        print("rf chunk %d FAIL:\n%s" % (i, r[-400:]), flush=True)
print("FINAL RENDER ok=%d fail=%d %s" % (ok, len(fail), fail[:5]))
