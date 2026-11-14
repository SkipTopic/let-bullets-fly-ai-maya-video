import os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SEQ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "render", "all_v2")
font = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 46)
small = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 24)
n = 0
for f in range(2343, 2370):
    p = os.path.join(SEQ, "S046.%04d.png" % f)
    if not os.path.exists(p):
        continue
    im = Image.new("RGB", (960, 540), (8, 8, 9))
    d = ImageDraw.Draw(im)
    d.text((430, 232), "S046", fill=(214, 206, 190), font=font)
    d.text((330, 300), "暴力插叙 · 按方案以黑场替代", fill=(120, 116, 108), font=small)
    im.save(p)
    n += 1
print("replaced", n)
