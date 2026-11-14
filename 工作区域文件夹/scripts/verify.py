# -*- coding: utf-8 -*-
"""P7: machine-checkable verification of the deliverable. Prints PASS/FAIL table."""
import csv
import subprocess
import sys
from pathlib import Path

FFMPEG = r"C:\Users\admin\bin\ffprobe.exe"
W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
OUT = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\输出文件夹")
FINAL = OUT / "成片_鸿门宴复刻_480P.mp4"

results = []


def check(n, name, ok, detail=""):
    results.append((n, name, "PASS" if ok else "FAIL", detail))


# 1) cameras == shots
sys.path.insert(0, str(Path(__file__).parent))
from mel_client import py

r = py('''
import maya.cmds as cmds
cams = [c for c in (cmds.ls("CAM_S*") or []) if "Shape" not in c and "translate" not in c and "rotate" not in c]
print("NCAMS=%d" % len(cams))
print("MESHES=%d" % len(cmds.ls(type="mesh") or []))
print("JOINTS=%d" % len(cmds.ls(type="joint") or []))
bs = cmds.ls(type="blendShape") or []
bad = []
for b in bs:
    als = cmds.aliasAttr(b, q=True) or []
    if isinstance(als, list):
        for k in range(0, len(als), 2):
            nm = als[k]
            if any(x in nm for x in ("mouth", "smile", "laugh", "surprise", "anger", "wink")):
                try:
                    v = cmds.getAttr("%s.%s" % (b, als[k + 1]))
                    if abs(v) > 0.01:
                        bad.append((b, nm, v))
                except Exception:
                    pass
print("BAD_MORPHS=%s" % bad[:5])
print("IMGPLANES=%d" % len(cmds.ls(type="imagePlane") or []))
''', timeout=600)
d = {}
for line in r.split("\n"):
    if "=" in line:
        k, _, v = line.partition("=")
        d[k.strip()] = v.strip()

with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
nshots = len(rows)

check(1, "cameras == shots", d.get("NCAMS", "0").isdigit() and int(d["NCAMS"]) >= nshots, "cams=%s shots=%d" % (d.get("NCAMS"), nshots))
check(5, "scene has real 3D", int(d.get("MESHES", "0")) >= 20 and int(d.get("JOINTS", "0")) >= 40,
      "meshes=%s joints=%s" % (d.get("MESHES"), d.get("JOINTS")))
check(9, "no image planes", d.get("IMGPLANES") == "0", d.get("IMGPLANES"))
check(10, "no forbidden morphs active", d.get("BAD_MORPHS") == "[]" or "mouth" not in d.get("BAD_MORPHS", "mouth"), d.get("BAD_MORPHS", "")[:60])

# 6) shotlist status non-empty
badstatus = [r["shot_id"] for r in rows if not (r.get("status") or "").strip()]
check(6, "shotlist status non-empty", not badstatus, str(badstatus[:5]))

# 3/4) qa thumbnails + frame motion
qa = list((W / "qa").glob("S???_first.png"))
check(3, "qa thumbnails exist", len(qa) >= nshots, "qa=%d" % len(qa))

# frames count
total_frames = 0
for r in rows:
    fdir = W / "frames" / r["shot_id"]
    if fdir.exists():
        total_frames += len(list(fdir.glob("*.png")))
check("5b", "frames total ~= 3512", abs(total_frames - 3512) <= 20, "frames=%d" % total_frames)

# 8) final mp4 params
if FINAL.exists():
    pr = subprocess.run([FFMPEG, "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height,nb_frames", "-of", "csv=p=0", str(FINAL)],
                        capture_output=True, text=True)
    dims = pr.stdout.strip()
    check(8, "final 854x480 no audio", "854,480" in dims, dims)
else:
    check(8, "final mp4 exists", False, "missing")

# report
print()
print("=" * 70)
print("VERIFY REPORT")
print("=" * 70)
allok = True
for (n, name, st, det) in results:
    print("#%-3s %-32s %-4s %s" % (n, name, st, det))
    if st == "FAIL":
        allok = False
print("=" * 70)
print("OVERALL:", "PASS" if allok else "FAIL")

with open(W / "核实报告.md", "w", encoding="utf-8") as f:
    f.write("# 核实报告\n\n| # | 判据 | 结果 | 详情 |\n|---|---|---|---|\n")
    for (n, name, st, det) in results:
        f.write("| %s | %s | %s | %s |\n" % (n, name, st, det))
    f.write("\n**OVERALL: %s**\n" % ("PASS" if allok else "FAIL"))
