import os, csv, math
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SRC = os.path.join(ROOT, "ds_ref", "all_frames")
OUT = os.path.join(ROOT, "ds_ref", "sheets_all")
os.makedirs(OUT, exist_ok=True)
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)
fonts = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 16)

rows = list(csv.DictReader(open(os.path.join(ROOT, "shotlist.csv"), encoding="utf-8-sig")))
per_sheet = 4
TW, TH = 400, 225
PAD = 26

def frame(f):
    return os.path.join(SRC, "f_%04d.jpg" % int(f))

sheets = []
for i in range(0, len(rows), per_sheet):
    group = rows[i:i+per_sheet]
    W = TW*3
    H = (TH+PAD)*len(group)
    sheet = Image.new("RGB", (W, H), (20,20,20))
    d = ImageDraw.Draw(sheet)
    for gi, r in enumerate(group):
        s, e = int(r["start_frame"]), int(r["end_frame"])
        picks = [s+1, (s+e)//2, e-1]
        base_y = gi*(TH+PAD)
        for ci, f in enumerate(picks):
            p = frame(f)
            if not os.path.exists(p):
                continue
            im = Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)
            x = ci*TW
            sheet.paste(im, (x, base_y+PAD))
            d.text((x+6, base_y+4), "%s  F%d" % (r["shot_id"], f), fill=(255,210,80), font=fonts)
        d.text((W-150, base_y+4), r["shot_size"], fill=(120,220,255), font=fonts)
    name = "%02d_%s-%s.png" % (i//per_sheet+1, group[0]["shot_id"], group[-1]["shot_id"])
    sheet.save(os.path.join(OUT, name))
    sheets.append(name)
print(len(sheets), "sheets")
for s in sheets: print(s)
