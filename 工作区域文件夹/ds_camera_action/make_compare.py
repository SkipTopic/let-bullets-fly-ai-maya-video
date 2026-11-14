import os
from PIL import Image, ImageDraw, ImageFont
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
REF = os.path.join(ROOT, "ds_ref", "all_frames")
STILL = os.path.join(ROOT, "ds_stills", "v05_71")
OUT = os.path.join(ROOT, "ds_stills", "compare")
os.makedirs(OUT, exist_ok=True)
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 20)
pairs = [("S001", 42), ("S002", 80), ("S003", 170), ("S004", 222)]
TW, TH, PAD = 640, 360, 30
sheet = Image.new("RGB", (TW*2, (TH+PAD)*len(pairs)), (16,16,16))
d = ImageDraw.Draw(sheet)
for i, (sid, f) in enumerate(pairs):
    ref = Image.open(os.path.join(REF, "f_%04d.jpg" % f)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    ren = Image.open(os.path.join(STILL, "DS_%s.0000.png" % sid)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    y = i*(TH+PAD)
    sheet.paste(ref, (0, y+PAD)); sheet.paste(ren, (TW, y+PAD))
    d.text((6, y+3), "%s 原片 F%d" % (sid, f), fill=(255,210,90), font=font)
    d.text((TW+6, y+3), "%s DS 机位静帧" % sid, fill=(120,220,255), font=font)
sheet.save(os.path.join(OUT, "compare_S001_S004.png"))
print("ok")
