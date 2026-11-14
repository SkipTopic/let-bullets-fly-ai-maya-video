import os, json
from PIL import Image, ImageDraw, ImageFont
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SRC = os.path.join(ROOT, "ds_stills", "v05_71")
OUT = os.path.join(ROOT, "ds_stills", "contact_v4")
os.makedirs(OUT, exist_ok=True)
shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
TW, TH, PAD = 320, 180, 22
cols, rows = 4, 3
per = cols*rows
for i in range(0, len(shots), per):
    grp = shots[i:i+per]
    sheet = Image.new("RGB", (cols*TW, rows*(TH+PAD)), (18,18,18))
    d = ImageDraw.Draw(sheet)
    for j, s in enumerate(grp):
        p = os.path.join(SRC, "DS_%s.0000.png" % s["id"])
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)
        x, y = (j % cols)*TW, (j//cols)*(TH+PAD)
        sheet.paste(im, (x, y+PAD))
        d.text((x+5, y+2), "%s %s %s" % (s["id"], s["type"], s.get("subject") or "-"), fill=(255,215,90), font=font)
        d.text((x+TW-90, y+2), "f%.0f %s" % (s["focal"], s["frame_range"]), fill=(120,220,255), font=font)
    name = "sheet_%02d_%s.png" % (i//per+1, grp[0]["id"])
    sheet.save(os.path.join(OUT, name))
    print(name)
