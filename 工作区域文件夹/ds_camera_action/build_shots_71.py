"""生成 71 镜设计表：内容来自原片逐镜取样，机位沿用 ds_camdesign 的求解器。"""
import hashlib
import json
import os

import ds_camdesign as D

HERE = os.path.dirname(os.path.abspath(__file__))

# (镜号, 主体, 类型, 前景, 备注)
# 类型: single=单人近景  medium=中景  ots=带前景  close=极特  title=替代镜头
SHOTS = [
    ("S001", "Ma", "single", None, "马县长比拇指指自己"),
    ("S002", "Huang", "single", None, "黄四郎拿杯嬉笑小喝"),
    ("S003", "Ma", "ots", "Shiye", "师爷右前景；先看师爷再看黄"),
    ("S004", "Huang", "ots", "Ma", "马县长左前景；右手比向马后收回"),
    ("S005", "Ma", "single", None, "边说边看师爷再看黄"),
    ("S006", "Huang", "single", None, "黄看着马问"),
    ("S007", "Ma", "single", None, "右手边指黄四郎"),
    ("S008", "Huang", "single", None, "竖拇指大笑"),
    ("S009", "Ma", "single", None, "收回右手笑"),
    ("S010", "Shiye", "single", None, "笑看黄，转向前方思考"),
    ("S011", "Huang", "single", None, "右手向右指着家里"),
    ("S012", "Ma", "single", None, "严肃后笑起来再看师爷"),
    ("S013", "Shiye", "medium", None, "看马跟着笑"),
    ("S014", "Ma", "ots", "Shiye", "右前景；笑着看师爷"),
    ("S015", "Huang", "medium", None, "肘靠桌看马（左前景师爷）"),
    ("S016", "Ma", "ots", "Shiye", "左前景；庄重说话转看师爷"),
    ("S017", "Ma", "single", None, "看着黄，右手比划"),
    ("S018", "Shiye", "single", None, "师爷看黄比 2；黄手入画"),
    ("S019", "Huang", "medium", None, "黄比拇指指向自己后侧"),
    ("S020", "Shiye", "ots", "Huang", "黄右前景；师爷看桌说话"),
    ("S021", "Huang", "ots", "Ma", "马右前景；黄打手势"),
    ("S022", "Shiye", "single", None, "师爷边思考边说"),
    ("S023", "Ma", "ots", "Shiye", "左前景；马微点头思考"),
    ("S024", "Shiye", "single", None, "师爷曲头笑看黄"),
    ("S025", "Ma", "single", None, "马笑看师爷"),
    ("S026", "Shiye", "single", None, "师爷拿杯前"),
    ("S027", "Ma", "single", None, "马拿杯敬酒"),
    ("S028", "Huang", "single", None, "黄喝一口放下"),
    ("S029", "Ma", "ots", "Shiye", "左前景；马双手顺衣"),
    ("S030", "Huang", "single", None, "黄皱眉看马"),
    ("S031", "Ma", "single", None, "马身体前倾说"),
    ("S032", "Huang", "single", None, "黄笑着右手划过后靠桌"),
    ("S033", "Shiye", "ots", "Huang", "黄左前景；师爷嚼着看黄"),
    ("S034", "Huang", "single", None, "黄指着说"),
    ("S035", "Ma", "ots", "Shiye", "右前景；马看黄"),
    ("S036", "Huang", "ots", "Shiye", "右前景；黄碰桌指桌"),
    ("S037", "Ma", "ots", "Shiye", "左前景；马转看师爷"),
    ("S038", "Huang", "ots", "Shiye", "左前景；黄看师爷后看马"),
    ("S039", "Ma", "ots", "Huang", "左前景；马定住盯黄"),
    ("S040", "Shiye", "medium", None, "师爷愣住看马"),
    ("S041", "Huang", "single", None, "黄微眯眼盯马"),
    ("S042", "Huang", "close", None, "9 帧极特写（原片为狗腿子）"),
    ("S043", None, "title", None, "幻想段：暗色桌面道具剪影"),
    ("S044", "Shiye", "single", None, "师爷听声"),
    ("S045", "Shiye", "single", None, "师爷受惊（原片为插入段）"),
    ("S046", None, "title", None, "暴力插叙：黑场+镜号"),
    ("S047", "Ma", "single", None, "马盯着看"),
    ("S048", "Huang", "single", None, "黄看自己的手"),
    ("S049", "Shiye", "medium", None, "师爷害怕看黄"),
    ("S050", "Ma", "single", None, "马盯黄眨眼"),
    ("S051", "Ma", "single", None, "马看黄（原片为幻想段）"),
    ("S052", "Huang", "single", None, "黄甩头（原片为幻想段）"),
    ("S053", "Huang", "single", None, "黄吧唧嘴拿筷子"),
    ("S054", None, "title", None, "幻想段收尾：窗格光影"),
    ("S055", "Shiye", "single", None, "师爷看窗帘"),
    ("S056", "Ma", "single", None, "马强调语气"),
    ("S057", "Huang", "single", None, "黄拿酒杯说"),
    ("S058", "Ma", "single", None, "马看黄再看桌"),
    ("S059", "Shiye", "single", None, "师爷思考眨眼"),
    ("S060", "Ma", "single", None, "马看桌后看黄"),
    ("S061", "Huang", "single", None, "黄斜着微仰头说"),
    ("S062", "Ma", "single", None, "马看桌后看黄"),
    ("S063", "Huang", "single", None, "黄点头说"),
    ("S064", "Ma", "single", None, "马看黄"),
    ("S065", "Shiye", "single", None, "师爷看黄等讲话"),
    ("S066", "Huang", "single", None, "黄看师爷后转看马"),
    ("S067", "Ma", "single", None, "马憋笑"),
    ("S068", "Shiye", "single", None, "师爷大笑前伸脖子"),
    ("S069", "Ma", "ots", "Shiye", "右前景；师爷起身倒酒"),
    ("S070", "Shiye", "single", None, "师爷倒完酒坐回"),
    ("S071", "Ma", "single", None, "师爷放回酒看马"),
]

TITLES = {
    "S043": {"eye": (-30.0, 62.0, 118.0), "aim": (10.0, 74.0, -35.0), "focal": 70.0,
             "note": "低机位贴桌面，看瓶子与桌面剪影"},
    "S046": {"eye": (0.0, 120.0, 120.0), "aim": (0.0, 70.0, 0.0), "focal": 50.0,
             "note": "黑场+镜号，机位仅占位"},
    "S054": {"eye": (10.0, 120.0, 150.0), "aim": (-20.0, 90.0, -60.0), "focal": 55.0,
             "note": "窗格光影暗转，机位仅占位"},
}

# 每个主体的机位变化区间（避免所有镜头同一机位）
VARY = {
    "single": {"head_frac": (0.30, 0.36), "focal": (50.0, 68.0), "radius": (185.0, 235.0)},
    "medium": {"head_frac": (0.17, 0.23), "focal": (38.0, 50.0), "radius": (230.0, 300.0)},
    "close": {"head_frac": (0.46, 0.54), "focal": (80.0, 95.0), "radius": (150.0, 185.0)},
    "ots": {"head_frac": (0.28, 0.32), "focal": (66.0, 76.0), "radius": (245.0, 292.0)},
}
BASE_H = {"Ma": 110.0, "Huang": 119.0, "Shiye": 119.0}


def rnd(seed, lo, hi):
    h = int(hashlib.md5(seed.encode("utf-8")).hexdigest()[:8], 16)
    return lo + (hi - lo) * ((h % 10000) / 10000.0)


def build_spec(sid, subj, kind, fg, note, idx):
    if kind == "title":
        t = TITLES[sid]
        return {"id": sid, "subject": None, "type": "title", "eye": list(t["eye"]),
                "aim": list(t["aim"]), "focal": t["focal"], "note": note, "title_note": t["note"]}

    v = VARY[kind]
    hf = rnd(sid + "hf", *v["head_frac"])
    focal = rnd(sid + "f", *v["focal"])
    radius = rnd(sid + "r", *v["radius"])
    height = BASE_H[subj] + rnd(sid + "h", -6.0, 6.0)
    fx = 0.5 + rnd(sid + "x", -0.06, 0.06)
    az = rnd(sid + "a", 8.0, 26.0)
    side = 1.0 if (hash(sid) % 2) else -1.0

    spec = {"id": sid, "subject": subj, "type": kind, "fx": fx, "fy": 0.45,
            "head_frac": hf, "height": height, "focal": focal, "azimuth": az,
            "radius_range": (max(120.0, radius - 35.0), radius + 40.0), "note": note}

    if kind == "ots":
        # 过肩镜几何很紧，用固定目标，避免随机化把约束顶死
        right_side = fg in ("Shiye", "Huang")
        spec["foreground"] = {"name": fg, "fx": 1.02 if right_side else -0.02,
                              "dist": rnd(sid + "fd", 88.0, 128.0)}
        spec["head_frac"] = rnd(sid + "oh", 0.27, 0.32)
        spec["focal"] = rnd(sid + "of", 62.0, 84.0)
        spec["radius_range"] = (240.0, 300.0)
        spec["fx"] = rnd(sid + "ox", 0.40, 0.50) if right_side else rnd(sid + "ox", 0.50, 0.60)
        spec["height"] = BASE_H[subj] + rnd(sid + "ohh", -4.0, 8.0)
    return spec


def solve_shot(spec):
    if spec["type"] == "title":
        return {"id": spec["id"], "eye": spec["eye"], "aim": spec["aim"], "focal": spec["focal"],
                "cost": 0.0, "type": "title", "note": spec["note"], "title_note": spec["title_note"]}
    cam, cost = D.solve(spec)
    m = D.metrics(cam)
    return {"id": spec["id"], "eye": [round(v, 2) for v in cam["eye"]],
            "aim": [round(v, 2) for v in cam["aim"]], "focal": round(cam["focal"], 2),
            "cost": round(cost, 3), "type": spec["type"], "subject": spec["subject"],
            "note": spec["note"], "projection": {k: m[k] for k in ("Ma", "Huang", "Shiye")},
            "clearance": m["head_clearance_cm"]}


if __name__ == "__main__":
    out = []
    for i, (sid, subj, kind, fg, note) in enumerate(SHOTS):
        spec = build_spec(sid, subj, kind, fg, note, i)
        rec = solve_shot(spec)
        rec["frame_range"] = None
        out.append(rec)
        print(sid, rec["type"], rec.get("focal"), rec.get("eye"), "cost", rec.get("cost"))

    # 补充帧范围与台词
    import csv
    rows = {r["shot_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "..", "shotlist.csv"), encoding="utf-8-sig"))}
    for rec in out:
        r = rows[rec["id"]]
        rec["frame_range"] = [int(r["start_frame"]), int(r["end_frame"])]
        rec["shot_size_text"] = r["shot_size"]
        rec["dialogue"] = r["dialogue"]
        rec["film_action"] = r["action"]

    path = os.path.join(HERE, "shots_deepseek.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "source": "film-sampled + solver", "shots": out}, fh,
                  ensure_ascii=False, indent=1)
    print("written", path, len(out))
