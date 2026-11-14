"""Gate 0：从 v7 另存 DS 工作基线，切 23.976fps，记录头手基准。

只读 v7，不改动它。输出：
  scenes/DS_相机动作_v01.mb
  logs/ds2_gate0.json
  ds_camera_action/baseline_pose.json
"""
import json
import os

import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
LOGS = os.path.join(ROOT, "logs")
OUTDIR = os.path.join(ROOT, "ds_camera_action")
os.makedirs(OUTDIR, exist_ok=True)

SRC = os.path.join(ROOT, "scenes", "摆姿重建_v7.mb").replace("\\", "/")
DST = os.path.join(ROOT, "scenes", "DS_相机动作_v01.mb").replace("\\", "/")

report = {"errors": [], "steps": []}


def log(msg):
    report["steps"].append(msg)
    print(msg)


def err(msg):
    report["errors"].append(msg)
    print("ERR: " + msg)


# --- 1. 确认当前场景就是 v7 ---
cur = (cmds.file(q=True, sn=True) or "").replace("\\", "/")
report["scene_before"] = cur
if cur.lower() != SRC.lower():
    err("当前场景不是 v7：%r" % cur)
else:
    log("已确认当前场景为 v7")

# --- 2. 记录基线（先记录再改帧率） ---
CHARS = {
    "Ma": {
        "group": "CHR_Ma",
        "head": "Bip001Head",
        "neck": "Bip001Neck",
        "spine": "Bip001Spine2",
        "handL": "Bip001LHand",
        "handR": "Bip001RHand",
        "elbowL": "Bip001LForearm",
        "elbowR": "Bip001RForearm",
        "shoulderL": "Bip001LClavicle",
        "shoulderR": "Bip001RClavicle",
    },
    "Huang": {
        "group": "CHR_Huang",
        "head": "Huang_Head",
        "neck": "Huang_Neck",
        "spine": "Huang_Spine1",
        "handL": "Huang_LeftHand",
        "handR": "Huang_RightHand",
        "elbowL": "Huang_LeftForeArm",
        "elbowR": "Huang_RightForeArm",
        "shoulderL": "Huang_LeftShoulder",
        "shoulderR": "Huang_RightShoulder",
    },
    "Shiye": {
        "group": "CHR_Shiye",
        "head": "Shiye_Head",
        "neck": "Shiye_Neck",
        "spine": "Shiye_Spine1",
        "handL": "Shiye_LeftHand",
        "handR": "Shiye_RightHand",
        "elbowL": "Shiye_LeftForeArm",
        "elbowR": "Shiye_RightForeArm",
        "shoulderL": "Shiye_LeftShoulder",
        "shoulderR": "Shiye_RightShoulder",
    },
}

baseline = {"scene": cur, "time_unit": cmds.currentUnit(q=True, time=True), "chars": {}}

for name, spec in CHARS.items():
    entry = {"group": spec["group"], "joints": {}, "missing": []}
    grp = spec["group"]
    if cmds.objExists(grp):
        entry["group_world_translate"] = list(cmds.xform(grp, q=True, ws=True, t=True))
        entry["group_rotate_y"] = cmds.getAttr(grp + ".rotateY")
    else:
        entry["missing"].append(grp)
    for role, jnt in spec.items():
        if role == "group":
            continue
        if not cmds.objExists(jnt):
            entry["missing"].append(jnt)
            continue
        entry["joints"][role] = {
            "node": jnt,
            "world_translate": [round(v, 4) for v in cmds.xform(jnt, q=True, ws=True, t=True)],
            "local_rotate": [round(v, 4) for v in cmds.xform(jnt, q=True, ro=True)],
            "rotate_order": cmds.getAttr(jnt + ".rotateOrder"),
        }
    baseline["chars"][name] = entry

# 场景自身结构
baseline["set_children"] = sorted(cmds.listRelatives("GRP_SET", children=True) or [])
baseline["pose_review_cams"] = (
    sorted(cmds.listRelatives("POSE_REVIEW_CAMERAS", children=True, type="transform") or [])
    if cmds.objExists("POSE_REVIEW_CAMERAS")
    else []
)
baseline["cameras_all"] = sorted(cmds.listCameras() or [])

with open(os.path.join(OUTDIR, "baseline_pose.json"), "w", encoding="utf-8") as fh:
    json.dump(baseline, fh, ensure_ascii=False, indent=1)
log("基线已写入 ds_camera_action/baseline_pose.json")

# --- 3. 另存为 DS 基线 ---
if os.path.exists(DST):
    bak = DST.replace(".mb", "_prev_%s.mb" % __import__("time").strftime("%H%M%S"))
    os.rename(DST, bak)
    log("已存在旧 DS 文件，先改名备份：%s" % os.path.basename(bak))

cmds.file(rename=DST)
cmds.file(save=True, type="mayaBinary")
log("已另存：DS_相机动作_v01.mb")

# --- 4. 切 23.976fps ---
fps_try = ["23.976fps", "23.976 fps"]
ok_fps = None
for cand in fps_try:
    try:
        cmds.currentUnit(time=cand)
        ok_fps = cand
        break
    except Exception as exc:  # noqa: BLE001
        log("帧率候选 %r 失败：%s" % (cand, exc))
if ok_fps is None:
    err("无法切换到 23.976fps")

report["time_unit_after"] = cmds.currentUnit(q=True, time=True)
report["fps_setting"] = ok_fps
report["time_unit_numeric_hint"] = cmds.currentUnit(q=True, time=True)

cmds.playbackOptions(min=1, max=3512, animationStartTime=1, animationEndTime=3512)
report["playback_after"] = [
    cmds.playbackOptions(q=True, min=True),
    cmds.playbackOptions(q=True, max=True),
]

# --- 5. 保存并回读确认 ---
cmds.file(save=True, type="mayaBinary")
report["scene_after"] = (cmds.file(q=True, sn=True) or "").replace("\\", "/")
report["animation_curves"] = len(cmds.ls(type="animCurve") or [])
report["references"] = cmds.file(q=True, reference=True) or []

with open(os.path.join(LOGS, "ds2_gate0.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1))
