"""按镜头表给三人打表演关键帧：头看向对话对象 + 手部手势。

每镜只在该镜帧范围内打点，镜头之间靠剪切切换。
"""
import json
import math
import os
import sys
import traceback

import maya.cmds as cmds

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
import ds_animlib as A  # noqa: E402

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "shots": {}, "stats": {}}

JOINTS = [j for n in ("Ma", "Huang", "Shiye") for j in (A.ARM[n]["L"] + A.ARM[n]["R"] + A.ARM[n]["head"])]

# 镜号: (主体, 看向谁, 第二个看点(可空), 手势)
PERF = {
    "S001": ("Ma", "Huang", None, "thumb"),
    "S002": ("Huang", "Ma", None, "cup"),
    "S003": ("Ma", "Shiye", "Huang", "open"),
    "S004": ("Huang", "Ma", None, "point"),
    "S005": ("Ma", "Shiye", "Huang", "open"),
    "S006": ("Huang", "Ma", None, "lift"),
    "S007": ("Ma", "Huang", None, "point"),
    "S008": ("Huang", "Ma", None, "thumb"),
    "S009": ("Ma", "Huang", None, "lift"),
    "S010": ("Shiye", "Huang", None, "open"),
    "S011": ("Huang", "Ma", None, "point"),
    "S012": ("Ma", "Huang", None, "open"),
    "S013": ("Shiye", "Ma", None, "open"),
    "S014": ("Ma", "Shiye", None, "lift"),
    "S015": ("Huang", "Ma", None, "table"),
    "S016": ("Ma", "Shiye", None, "open"),
    "S017": ("Ma", "Huang", None, "point"),
    "S018": ("Shiye", "Huang", None, "lift"),
    "S019": ("Huang", "Ma", None, "lift"),
    "S020": ("Shiye", "Huang", None, "point"),
    "S021": ("Huang", "Ma", None, "open"),
    "S022": ("Shiye", "Ma", None, "lift"),
    "S023": ("Ma", "Shiye", None, "lift"),
    "S024": ("Shiye", "Huang", None, "open"),
    "S025": ("Ma", "Shiye", None, "open"),
    "S026": ("Shiye", "Huang", None, "cup"),
    "S027": ("Ma", "Huang", None, "cup"),
    "S028": ("Huang", "Ma", None, "cup"),
    "S029": ("Ma", "Shiye", None, "table"),
    "S030": ("Huang", "Ma", None, "lift"),
    "S031": ("Ma", "Huang", None, "open"),
    "S032": ("Huang", "Ma", None, "open"),
    "S033": ("Shiye", "Huang", None, "lift"),
    "S034": ("Huang", "Ma", None, "point"),
    "S035": ("Ma", "Shiye", None, "open"),
    "S036": ("Huang", "Shiye", None, "lift"),
    "S037": ("Ma", "Shiye", None, "open"),
    "S038": ("Huang", "Shiye", "Ma", "point"),
    "S039": ("Ma", "Huang", None, "lift"),
    "S040": ("Shiye", "Ma", None, "lift"),
    "S041": ("Huang", "Ma", None, "lift"),
    "S042": ("Huang", "Ma", None, "lift"),
    "S044": ("Shiye", "Ma", None, "lift"),
    "S045": ("Shiye", "Ma", None, "lift"),
    "S047": ("Ma", "Huang", None, "lift"),
    "S048": ("Huang", "Ma", None, "lift"),
    "S049": ("Shiye", "Huang", None, "open"),
    "S050": ("Ma", "Huang", None, "lift"),
    "S051": ("Ma", "Huang", None, "lift"),
    "S052": ("Huang", "Ma", None, "lift"),
    "S053": ("Huang", "Ma", None, "lift"),
    "S055": ("Shiye", "Huang", None, "lift"),
    "S056": ("Ma", "Huang", None, "open"),
    "S057": ("Huang", "Ma", None, "cup"),
    "S058": ("Ma", "Huang", None, "point"),
    "S059": ("Shiye", "Ma", None, "lift"),
    "S060": ("Ma", "Huang", None, "lift"),
    "S061": ("Huang", "Ma", None, "lift"),
    "S062": ("Ma", "Huang", None, "lift"),
    "S063": ("Huang", "Ma", None, "lift"),
    "S064": ("Ma", "Huang", None, "lift"),
    "S065": ("Shiye", "Huang", None, "lift"),
    "S066": ("Huang", "Ma", None, "lift"),
    "S067": ("Ma", "Huang", None, "lift"),
    "S068": ("Shiye", "Huang", None, "open"),
    "S069": ("Ma", "Shiye", None, "cup"),
    "S070": ("Shiye", "Ma", None, "lift"),
    "S071": ("Ma", "Shiye", None, "lift"),
}


def hand_target(name, g, side="R"):
    """按手势算出世界空间的手部目标点。"""
    up_j, fore_j, hand_j = A.ARM[name][side]
    h = A.pos(hand_j)
    hp = A.HEAD[name]
    f = A.fwd(name)
    l = A.left(name)
    if g == "lift":
        return (h[0] + f[0] * 3.0, h[1] + 9.0, h[2] + f[2] * 3.0)
    if g == "open":
        return (h[0] + l[0] * 3.0, h[1] + 6.0, h[2] + f[2] * 5.0)
    if g == "thumb":
        return (h[0] - l[0] * 2.0, min(hp[1] - 12.0, h[1] + 17.0), h[2] + f[2] * 8.0)
    if g == "point":
        return (h[0] + f[0] * 22.0, h[1] + 8.0, h[2] + f[2] * 22.0)
    if g == "cup":
        return (hp[0] - l[0] * 3.0, hp[1] - 8.0, hp[2] + f[2] * 13.0)
    if g == "table":
        return (h[0] + f[0] * 6.0, 79.0, h[2] + f[2] * 6.0)
    return h


def apply_look(name, target_name):
    if target_name:
        A.aim_head(name, A.HEAD[target_name])


def bake_shot(sid, spec, snaps):
    subj, look1, look2, g = spec
    s, e = shot_frames[sid]
    d = max(2, e - s)

    # 每个镜头先复位所有受控骨
    A.restore(snaps)

    # 关键帧时间点
    t0 = s
    t1 = s + int(d * 0.32)
    t2 = s + int(d * 0.62)
    t3 = s + int(d * 0.92)

    # 起始：看向第一目标，手在位
    cmds.currentTime(t0)
    A.restore(snaps)
    apply_look(subj, look1)
    A.key_joints(JOINTS, t0)

    # 峰值：手势 + 第二目标（若有多段视线）
    cmds.currentTime(t1)
    A.restore(snaps)
    A.two_bone_ik(subj, "R", hand_target(subj, g))
    if g in ("open", "table"):
        A.two_bone_ik(subj, "L", hand_target(subj, g, "L"))
    apply_look(subj, look2 or look1)
    A.key_joints(JOINTS, t1)

    # 保持
    cmds.currentTime(t2)
    A.restore(snaps)
    A.two_bone_ik(subj, "R", hand_target(subj, g))
    if g in ("open", "table"):
        A.two_bone_ik(subj, "L", hand_target(subj, g, "L"))
    apply_look(subj, look2 or look1)
    A.key_joints(JOINTS, t2)

    # 回收：手回位，看向第一目标
    cmds.currentTime(t3)
    A.restore(snaps)
    apply_look(subj, look1)
    A.key_joints(JOINTS, t3)

    return (t0, t1, t2, t3)


try:
    data = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"), encoding="utf-8"))["shots"]
    shot_frames = {s["id"]: tuple(s["frame_range"]) for s in data}
    titles = {s["id"] for s in data if s["type"] == "title"}

    for c in cmds.ls(type="animCurve") or []:
        cmds.delete(c)

    snaps = A.snapshot(JOINTS)
    A.restore(snaps)

    done = 0
    for s in data:
        sid = s["id"]
        if sid in titles or sid not in PERF:
            continue
        A.restore(snaps)
        keys = bake_shot(sid, PERF[sid], snaps)
        OUT["shots"][sid] = keys
        done += 1

    A.restore(snaps)
    cmds.currentTime(1)
    OUT["stats"]["shots_animated"] = done
    OUT["stats"]["anim_curves"] = len(cmds.ls(type="animCurve") or [])
    OUT["stats"]["key_count"] = sum(
        int(cmds.keyframe(c, q=True, keyframeCount=True) or 0) for c in (cmds.ls(type="animCurve") or []))
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds26_anim.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "stats": OUT["stats"], "err": OUT["errors"][:1]}, ensure_ascii=False))
