"""把台词烧进已经渲染好的帧（PIL 直接改图，避免 ffmpeg 字体问题）。"""
import csv, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
FRAMES = os.path.join(ROOT, "frames")
OUTDIR = os.path.join(ROOT, "frames_sub")
FONT = r"C:\Windows\Fonts\msyh.ttc"

shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
os.makedirs(OUTDIR, exist_ok=True)

font = ImageFont.truetype(FONT, 25)
W, H = 854, 480


def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        t = cur + ch
        if draw.textlength(t, font=font) > maxw and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def shot_at(f):
    for s in shots:
        if s["start"] <= f <= s["end"]:
            return s
    return None


total = 0
written = 0
for f in sorted(os.listdir(FRAMES)):
    if not f.endswith(".png"):
        continue
    total += 1
    idx = int(f[:-4])
    src = os.path.join(FRAMES, f)
    dst = os.path.join(OUTDIR, f)
    s = shot_at(idx)
    text = (s or {}).get("dialogue", "").strip()
    if not text:
        if not os.path.exists(dst):
            os.link(src, dst) if False else Image.open(src).save(dst)
        continue
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    lines = wrap(d, text, font, W - 120)
    lh = 32
    y = H - 24 - lh * len(lines)
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=font)
        x = (W - tw) / 2
        d.text((x, y + i * lh), line, font=font, fill=(255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0))
    im.save(dst)
    written += 1

print("frames", total, "with_subs", written)
