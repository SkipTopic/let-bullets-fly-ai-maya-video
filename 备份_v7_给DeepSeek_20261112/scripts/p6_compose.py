# -*- coding: utf-8 -*-
"""P6: subtitle PNGs (PIL) + per-shot mp4 + concat to final MP4 (854x480/24fps/no audio)."""
import csv
import subprocess
from pathlib import Path

FFMPEG = r"C:\Users\admin\bin\ffmpeg.exe"
W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")
OUT = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\输出文件夹")
OUT.mkdir(exist_ok=True)
FRAMES = W / "frames"
SUBS = W / "subs"
SUBS.mkdir(exist_ok=True)

from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\msyh.ttc"
font = ImageFont.truetype(FONT, 28)


def make_sub(text, path):
    img = Image.new("RGBA", (854, 480), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # wrap text
    lines = []
    cur = ""
    for chch in text:
        cur += chch
        if len(cur) >= 22:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    y = 480 - 30 - 34 * len(lines)
    for ln in lines:
        w = d.textlength(ln, font=font)
        x = (854 - w) / 2
        d.text((x + 1, y + 1), ln, font=font, fill=(0, 0, 0, 255))
        d.text((x - 1, y - 1), ln, font=font, fill=(0, 0, 0, 255))
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255))
        y += 34
    img.save(path)


with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 1) subtitle pngs
nsub = 0
for r in rows:
    dial = (r["dialogue"] or "").strip()
    if not dial:
        continue
    p = SUBS / ("sub_%s.png" % r["shot_id"])
    if not p.exists():
        make_sub(dial, p)
    nsub += 1
print("subs=%d" % nsub)

# 2) per-shot mp4 (with subtitle overlay when present)
concat_lines = []
for r in rows:
    sid = r["shot_id"]
    fdir = FRAMES / sid
    pngs = sorted(fdir.glob("*.png")) if fdir.exists() else []
    if not pngs:
        print("NO FRAMES", sid)
        continue
    subp = SUBS / ("sub_%s.png" % sid)
    outmp4 = W / "shots_mp4" / ("%s.mp4" % sid)
    outmp4.parent.mkdir(exist_ok=True)
    nf = len(pngs)
    if subp.exists():
        vf = "overlay=0:0:enable='between(t,0,%.3f)'" % (nf / 24.0)
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-framerate", "24",
               "-i", str(fdir / ("%s.%%04d.png" % sid)),
               "-i", str(subp),
               "-filter_complex", "[0:v][1:v]" + vf,
               "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
               "-r", "24", "-an", str(outmp4)]
    else:
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-framerate", "24",
               "-i", str(fdir / ("%s.%%04d.png" % sid)),
               "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
               "-r", "24", "-an", str(outmp4)]
    subprocess.run(cmd, check=True)
    concat_lines.append("file '%s'" % outmp4)

(W / "shots_mp4" / "concat.txt").write_text("\n".join(concat_lines), encoding="utf-8")

# 3) final concat
final = OUT / "成片_鸿门宴复刻_480P.mp4"
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(W / "shots_mp4" / "concat.txt"),
                "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an",
                str(final)], check=True)
print("FINAL:", final)

# 4) probe
pr = subprocess.run([r"C:\Users\admin\bin\ffprobe.exe", "-v", "error",
                     "-select_streams", "v:0", "-show_entries",
                     "stream=width,height,nb_frames,duration",
                     "-of", "csv=p=0", str(final)], capture_output=True, text=True)
print("PROBE:", pr.stdout.strip())
