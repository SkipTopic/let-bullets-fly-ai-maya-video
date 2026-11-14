"""把台词烧到成片帧上（PIL 直接改图）。"""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SRC = os.path.join(ROOT, "frames_all")
DST = os.path.join(ROOT, "frames_sub")
FONT = r"C:\Windows\Fonts\msyh.ttc"
W, H = 854, 480

shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
os.makedirs(DST, exist_ok=True)
font = ImageFont.truetype(FONT, 24)


def wrap(draw, text, maxw):
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


n = 0
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".png"):
        continue
    idx = int(fn[:-4])
    s = shot_at(idx)
    text = (s or {}).get("dialogue", "").strip()
    im = Image.open(os.path.join(SRC, fn)).convert("RGB")
    if text:
        d = ImageDraw.Draw(im)
        lines = wrap(d, text, W - 120)
        lh = 31
        y0 = H - 26 - lh * len(lines)
        for i, line in enumerate(lines):
            tw = d.textlength(line, font=font)
            x = (W - tw) / 2
            d.text((x, y0 + i * lh), line, font=font, fill=(255, 255, 255),
                   stroke_width=2, stroke_fill=(12, 12, 12))
    im.save(os.path.join(DST, fn))
    n += 1

print("burned", n)
