# -*- coding: utf-8 -*-
"""P1: cut all 71 shots - extract one frame each, crop the top table strip,
combine strips into groups of 6 for efficient reading.

Cut points from _cuts.txt: cut[i] is the START time of shot i+2 (0-based cuts),
shot 1 starts at 0.0. Verified: 12.054s = shot 5 start = 0:12.
"""
import subprocess
from pathlib import Path

FFMPEG = r"C:\Users\admin\bin\ffmpeg.exe"
VIDEO = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\原视频素材.mp4"
WORK = Path(VIDEO).parent / "\u5de5\u4f5c\u533a\u57df\u6587\u4ef6\u5939"
SHOTS = WORK / "shots"
SHOTS.mkdir(exist_ok=True)

FPS = 23.976
cuts = [float(x) for x in (WORK / "_摸底参考" / "_cuts.txt").read_text().split()]
total_dur = 146.56
n = len(cuts)
assert n == 71, f"expect 71 cuts, got {n}"

# shot i (1-based): start = cuts[i-2] for i>=2 else 0; end = cuts[i-1] for i<=70 else total
bounds = []
for i in range(1, n + 1):
    start = 0.0 if i == 1 else cuts[i - 2]
    end = cuts[i - 1] if i <= n - 1 else total_dur
    bounds.append((i, start, end))

def frame(t):
    return max(1, round(t * FPS))

rows = []
for i, (si, s, e) in enumerate(bounds):
    fs = frame(s)
    if i < len(bounds) - 1:
        fe = frame(bounds[i + 1][1]) - 1  # end = next shot's start - 1
    else:
        fe = 3512
    rows.append((i + 1, fs, fe, fe - fs + 1))
# ensure first shot starts at 1
rows[0] = (1, 1, rows[0][2], rows[0][2] - 1 + 1)

# sanity
print("total frames:", sum(r[3] for r in rows), "(target 3512)")
print("shots:", len(rows))
for r in rows[:5] + rows[-3:]:
    print("S%03d  f%d-f%d  %df  %.2fs-%.2fs" % (r[0], r[1], r[2], r[3],
          (r[1] - 1) / FPS, (r[2]) / FPS))

# extract frames: sample at start + min(0.35, 0.4*dur)
for (i, fs, fe, dur) in rows:
    s = (fs - 1) / FPS
    t = s + min(0.35, 0.4 * (fe - fs + 1) / FPS)
    out = SHOTS / f"S{i:03d}_frame.jpg"
    if out.exists():
        continue
    subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
         "-i", VIDEO, "-frames:v", "1", "-q:v", "2", str(out)],
        check=True)

# crop table strips (top band y=90..360 of 1920x1080) and stack in groups of 6
from PIL import Image
strips = []
for (i, fs, fe, dur) in rows:
    p = SHOTS / f"S{i:03d}_frame.jpg"
    im = Image.open(p)
    if im.size != (1920, 1080):
        im = im.resize((1920, 1080))
    strips.append((i, im.crop((0, 90, 1920, 365))))

GROUP = 6
for g in range(0, len(strips), GROUP):
    chunk = strips[g:g + GROUP]
    canvas = Image.new("RGB", (1920, 275 * len(chunk)), "white")
    for k, (i, st) in enumerate(chunk):
        canvas.paste(st, (0, 275 * k))
    canvas.save(SHOTS / f"table_group_{g // GROUP + 1:02d}.jpg", quality=88)

# write draft csv (no content yet)
import csv
with open(WORK / "shotlist.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["shot_id", "start_frame", "end_frame", "dur_frames", "dur_sec",
                "shot_size", "action", "camera_move", "dialogue", "source", "status"])
    for (i, fs, fe, dur) in rows:
        w.writerow([f"S{i:03d}", fs, fe, dur, round(dur / FPS, 2),
                    "", "", "", "", "", ""])

print("frames extracted:", len(list(SHOTS.glob("S*_frame.jpg"))))
print("table groups:", len(list(SHOTS.glob("table_group_*.jpg"))))
print("shotlist.csv written")
