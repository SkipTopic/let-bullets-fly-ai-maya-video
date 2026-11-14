"""从 shotlist.csv 生成 71 个镜头的机位与表演规格（host 侧，不依赖 Maya）。"""
import csv, json, math, os, re

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
SEAT_ANGLE = {"Ma": 270, "Huang": 30, "Shiye": 150}
SEAT_R = 118.0

NAMES = [("马县长", "Ma"), ("黄四郎", "Huang"), ("师爷", "Shiye")]


def who(txt):
    hits = []
    for name, key in NAMES:
        if name in txt:
            hits.append((txt.index(name), key))
    hits.sort()
    return [k for _, k in hits]


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "shotlist.csv"), encoding="utf-8-sig")))
    shots = []
    for i, r in enumerate(rows):
        act = r["action"]
        order = who(act) or ["Ma", "Huang", "Shiye"]
        subject = order[0]
        others = [n for n, k in NAMES if k != subject]

        size = r["shot_size"]
        if "近" in size:
            dist, focal, height = 186.0, 85.0, 116.0
        elif "中" in size:
            dist, focal, height = 250.0, 55.0, 120.0
        else:
            dist, focal, height = 300.0, 40.0, 125.0

        ca = math.radians(SEAT_ANGLE[subject] + 180)
        ex, ez = math.cos(ca) * dist, math.sin(ca) * dist

        # 运镜：横向移动 → 沿弧线给起止两个机位
        mv = r.get("camera_move", "") or ""
        span = 0.0
        if "右" in mv:
            span = 20.0
        elif "左" in mv:
            span = -20.0
        if "跟" in mv or "推" in mv:
            span = span or 12.0

        a0 = math.radians(SEAT_ANGLE[subject] + 180 - span / 2.0)
        a1 = math.radians(SEAT_ANGLE[subject] + 180 + span / 2.0)

        shots.append({
            "id": r["shot_id"],
            "start": int(r["start_frame"]),
            "end": int(r["end_frame"]),
            "dur": int(r["dur_frames"]),
            "size": size,
            "subject": subject,
            "speaker": order[0],
            "listener": order[1] if len(order) > 1 else None,
            "dist": dist, "focal": focal, "height": height,
            "eye0": [round(math.cos(a0) * dist, 2), height, round(math.sin(a0) * dist, 2)],
            "eye1": [round(math.cos(a1) * dist, 2), height, round(math.sin(a1) * dist, 2)],
            "action": act,
            "move": mv,
            "dialogue": r.get("dialogue", ""),
        })

    out = os.path.join(ROOT, "shots.json")
    json.dump(shots, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", out, len(shots))
    from collections import Counter
    print(Counter(s["subject"] for s in shots))
    print("total frames", sum(s["dur"] for s in shots))


if __name__ == "__main__":
    main()
