"""给 71 台相机加运镜：缓推/缓拉 + 轻微升降，逐镜不同。"""
import json
import os
import traceback

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "shots": {}}

# 需要特殊运镜的镜头：向上跟、晃动
SPECIAL = {
    "S069": ("up", 6.0),
    "S070": ("shake", 2.0),
    "S041": ("up", 4.0),
    "S045": ("up", 3.0),
    "S056": ("down", 3.0),
    "S066": ("up", 3.0),
    "S067": ("down", 3.0),
    "S068": ("up", 4.0),
}

try:
    shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                           encoding="utf-8"))["shots"]
    for i, s in enumerate(shots):
        sid = s["id"]
        cam = cmds.ls("DS_%s_CAM*" % sid)
        if not cam:
            continue
        cam = cam[0]
        f0, f1 = s["frame_range"]

        # 基础机位（相机刚建好的位置）
        base = cmds.xform(cam, q=True, ws=True, t=True)
        m = cmds.xform(cam, q=True, ws=True, m=True)
        fwd = (-m[8], -m[9], -m[10])
        # 与主体的距离用于换算推拉幅度
        proj = s.get("projection") or {}
        subj = s.get("subject")
        dist = 200.0
        if subj and proj.get(subj):
            dist = proj[subj]["dist"]
        if s["type"] == "title":
            dist = 150.0

        mode, mag = SPECIAL.get(sid, ("push" if i % 2 == 0 else "pull", 0.0))
        amp = mag if mag else dist * (0.030 if s["type"] == "single" else 0.040)
        if mode == "pull":
            amp = -amp

        # 起幅
        cmds.currentTime(f0)
        cmds.xform(cam, ws=True, t=base)
        cmds.setKeyframe(cam, at="translate", time=f0)

        # 落幅
        end = list(base)
        if mode == "up":
            end[1] += abs(amp)
        elif mode == "down":
            end[1] -= abs(amp)
        elif mode == "shake":
            end[0] += 1.2
            end[1] += 0.8
        else:
            end = [base[k] + fwd[k] * amp for k in range(3)]
        cmds.currentTime(f1)
        cmds.xform(cam, ws=True, t=end)
        cmds.setKeyframe(cam, at="translate", time=f1)

        OUT["shots"][sid] = {"mode": mode, "amp_cm": round(amp, 1),
                             "start": [round(v, 1) for v in base],
                             "end": [round(v, 1) for v in end]}
    cmds.currentTime(1)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds36_cammove.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "n": len(OUT["shots"]),
                  "sample": list(OUT["shots"].items())[:3], "err": OUT["errors"][:1]},
                 ensure_ascii=False)[:600])
