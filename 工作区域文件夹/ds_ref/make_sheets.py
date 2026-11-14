import os, csv
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SRC = os.path.join(ROOT, "ds_ref", "S001_S007")
OUT = os.path.join(ROOT, "ds_ref", "sheets")
os.makedirs(OUT, exist_ok=True)
FONT = r"C:\Windows\Fonts\msyh.ttc"
font = ImageFont.truetype(FONT, 20)

rows = list(csv.DictReader(open(os.path.join(ROOT, "shotlist.csv"), encoding="utf-8-sig")))
shots = [r for r in rows if r["shot_id"] in ("S001","S002","S003","S004","S005","S006","S007")]

def frame_path(maya_frame):
    n = int(maya_frame)
    return os.path.join(SRC, "f_%04d.png" % n)

for r in shots:
    s, e = int(r["start_frame"]), int(r["end_frame"])
    picks = [s, s+ (e-s)//4, s+(e-s)//2, s+3*(e-s)//4, e]
    picks = sorted(set(picks))
    th_w, th_h = 480, 270
    cols = 3
    rows_n = (len(picks)+cols-1)//cols
    head = 34
    sheet = Image.new("RGB", (cols*th_w, rows_n*(th_h+head)), (24,24,24))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(picks):
        p = frame_path(f)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((th_w, th_h), Image.LANCZOS)
        x = (i%cols)*th_w; y = (i//cols)*(th_h+head)
        sheet.paste(im, (x, y+head))
        d.text((x+8, y+6), "F%d" % f, fill=(255,220,90), font=font)
    out = os.path.join(OUT, "%s_%d-%d.png" % (r["shot_id"], s, e))
    sheet.save(out)
    print(out, len(picks))
