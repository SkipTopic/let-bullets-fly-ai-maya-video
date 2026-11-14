import os, subprocess
from PIL import Image
import numpy as np
SRC = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\ds_ref\S001_S007"
prev=None; out=[]
for i in range(1,342):
    p=os.path.join(SRC,"f_%04d.png"%i)
    im=np.asarray(Image.open(p).convert("L").resize((160,90)),dtype=np.float32)
    if prev is not None:
        d=float(np.mean(np.abs(im-prev)))
        out.append((i,d))
    prev=im
out.sort(key=lambda x:-x[1])
print("top diffs (maya_frame, mean abs diff):")
for f,d in out[:15]: print(f, round(d,2))
