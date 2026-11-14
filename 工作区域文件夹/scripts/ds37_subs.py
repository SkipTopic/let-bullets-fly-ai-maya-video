"""按 shotlist 的对白生成 SRT 字幕。"""
import csv, json, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
FPS = 24000.0 / 1001.0


def tc(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return ("%02d:%02d:%05.2f" % (h, m, s)).replace(".", ",")


rows = list(csv.DictReader(open(os.path.join(ROOT, "shotlist.csv"), encoding="utf-8-sig")))
lines = []
idx = 1
for r in rows:
    txt = (r.get("dialogue") or "").strip()
    if not txt:
        continue
    f0, f1 = int(r["start_frame"]), int(r["end_frame"])
    # 留一点头尾余量，避免字幕压帧
    start = (f0 - 1) / FPS + 0.04
    end = f1 / FPS - 0.04
    if end <= start:
        end = start + 0.5
    lines.append("%d\n%s --> %s\n%s\n" % (idx, tc(start).replace(".", ","), tc(end).replace(".", ","), txt))
    idx += 1

p = os.path.join(ROOT, "render", "subs_zh.srt")
with open(p, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("cues", idx - 1, p)
