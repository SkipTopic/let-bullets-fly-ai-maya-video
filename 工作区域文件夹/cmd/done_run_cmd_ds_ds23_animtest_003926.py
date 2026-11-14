"""动画试做：S001 马县长抬头看黄 + 右手比拇指，出三帧检查。"""
import json
import os
import sys

import maya.cmds as cmds

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
import ds_animlib as A  # noqa: E402

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "steps": []}

ALL = []
for n in ("Ma", "Huang", "Shiye"):
    ALL += [A.ARM[n]["L"][0], A.ARM[n]["L"][1], A.ARM[n]["L"][2],
            A.ARM[n]["R"][0], A.ARM[n]["R"][1], A.ARM[n]["R"][2],
            A.ARM[n]["head"][0], A.ARM[n]["head"][1]]

try:
    snap = A.snapshot(ALL)
    A.restore(snap)

    f0, f1, f2 = 1, 26, 50
    # 起手：静止
    cmds.currentTime(f0)
    A.restore(snap)
    A.key_joints(ALL, f0)

    # 峰值：看黄 + 右手抬到胸前
    cmds.currentTime(f1)
    A.restore(snap)
    hp = A.HEAD["Ma"]
    # 看向黄四郎头部
    A.aim_head("Ma", A.HEAD["Huang"])
    f = A.fwd("Ma")
    l = A.left("Ma")
    chest = (hp[0] + f[0] * 14.0, 96.0, hp[2] + f[2] * 14.0)
    hand_before = A.pos("Bip001RHand")
    A.two_bone_ik("Ma", "R", chest, pole_dir=(l[0] * -1.0, 0.4, l[2] * -1.0))
    hand_after = A.pos("Bip001RHand")
    OUT["steps"].append("hand moved %.1f cm" % ((hand_after[0] - hand_before[0]) ** 2 + (hand_after[1] - hand_before[1]) ** 2 + (hand_after[2] - hand_before[2]) ** 2) ** 0.5)
    A.key_joints(ALL, f1)

    # 回落
    cmds.currentTime(f2)
    A.restore(snap)
    A.aim_head("Ma", A.HEAD["Huang"])
    A.key_joints(ALL, f2)

    # 出图
    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cam = cmds.ls("DS_S001_CAM*")[0]
    cmds.lookThru(panel, cam)
    os.makedirs(os.path.join(ROOT, "ds_stills", "anim_test"), exist_ok=True)
    for fr in (f0, f1, f2):
        cmds.currentTime(fr)
        cmds.refresh(force=True)
        base = os.path.join(ROOT, "ds_stills", "anim_test", "S001_%03d" % fr)
        cmds.playblast(frame=fr, format="image", filename=base, sequenceTime=False,
                       clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                       percent=100, widthHeight=(960, 540), quality=90, compression="png")
    OUT["hand_target"] = [round(v, 1) for v in chest]
    OUT["hand_reached"] = [round(v, 1) for v in hand_after]
    OUT["ok"] = True
except Exception as exc:  # noqa: BLE001
    import traceback
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds23_animtest.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False)[:800])
