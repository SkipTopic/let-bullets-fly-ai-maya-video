import os, glob, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SEQ = os.path.join(ROOT, "render", "all")
OUT = os.path.join(ROOT, "render", "qa_sheet.png")
files = sorted(glob.glob(os.path.join(SEQ, "*.png")))
if not files:
    raise SystemExit("no frames")
picks = [files[int(i*(len(files)-1)/11)] for i in range(12)]
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
TW, TH, PAD = 400, 225, 24
sheet = Image.new("RGB", (TW*4, (TH+PAD)*3), (16,16,16))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(picks):
    im = Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)
    x, y = (i%4)*TW, (i//4)*(TH+PAD)
    sheet.paste(im, (x, y+PAD))
    d.text((x+5, y+3), os.path.basename(p), fill=(255,215,90), font=font)
sheet.save(OUT)
print("ok", OUT, len(files))
