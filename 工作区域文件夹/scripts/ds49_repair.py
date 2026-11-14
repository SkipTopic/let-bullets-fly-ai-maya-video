"""黑帧修补：把黑帧替换成相邻正常帧（S046 黑场卡保留）。"""
import glob, json, os, sys
from PIL import Image
import numpy as np

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SEQ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "render", "all_v4")


def lum(p):
    im = np.asarray(Image.open(p).convert("L").resize((96, 54)), dtype=np.float32)
    return float(im.mean())


shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
fixed_total = 0
report = []
for s in shots:
    sid = s["id"]
    if sid == "S046":
        continue
    f0, f1 = s["frame_range"]
    paths = [(f, os.path.join(SEQ, "%s.%04d.png" % (sid, f))) for f in range(f0, f1 + 1)]
    paths = [(f, p) for f, p in paths if os.path.exists(p)]
    if not paths:
        continue
    lums = {f: lum(p) for f, p in paths}
    bad = [f for f in lums if lums[f] < 12.0]
    if not bad:
        continue
    good = [f for f in lums if lums[f] >= 12.0]
    if not good:
        report.append([sid, "ALL_BLACK", len(bad)])
        continue
    for f in bad:
        # 取最近的好帧
        near = min(good, key=lambda g: abs(g - f))
        src = os.path.join(SEQ, "%s.%04d.png" % (sid, near))
        dst = os.path.join(SEQ, "%s.%04d.png" % (sid, f))
        Image.open(src).save(dst)
        fixed_total += 1
    report.append([sid, len(bad), len(good)])

print("fixed", fixed_total)
print("shots", report[:40])
with open(os.path.join(ROOT, "logs", "ds49_repair.json"), "w", encoding="utf-8") as fh:
    json.dump({"fixed": fixed_total, "report": report}, fh, ensure_ascii=False, indent=1)
