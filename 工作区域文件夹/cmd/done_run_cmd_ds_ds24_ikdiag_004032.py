"""诊断 2 骨 IK 精度 + 试前臂单独弯举（小幅度）。"""
import json
import math
import os
import sys

import maya.cmds as cmds

sys.path.insert(0, r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\scripts")
import ds_animlib as A  # noqa: E402

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "log": []}

try:
    snap = A.snapshot([j for n in ("Ma", "Huang", "Shiye") for j in
                       (A.ARM[n]["L"] + A.ARM[n]["R"] + A.ARM[n]["head"])])
    A.restore(snap)
    cmds.currentTime(1)

    for j in ("Bip001RUpperArm", "Bip001RForearm", "Bip001RHand", "Bip001LUpperArm"):
        lim = cmds.joint(j, q=True, limitX=True, minX=True, maxX=True)
        OUT["log"].append([j, "limits", lim])

    S = A.pos("Bip001RUpperArm")
    E = A.pos("Bip001RForearm")
    W = A.pos("Bip001RHand")
    L1, L2 = math.dist(S, E), math.dist(E, W)
    OUT["log"].append(["rest", "S", [round(v, 1) for v in S], "E", [round(v, 1) for v in E],
                       "W", [round(v, 1) for v in W], "L1", round(L1, 1), "L2", round(L2, 1)])

    target = (W[0], W[1] + 14.0, W[2] + 6.0)
    A.two_bone_ik("Ma", "R", target, pole_dir=None)
    W2 = A.pos("Bip001RHand")
    OUT["log"].append(["ik", "target", [round(v, 1) for v in target],
                       "reached", [round(v, 1) for v in W2],
                       "err_cm", round(math.dist(target, W2), 2)])

    # 只弯前臂：把前臂绕世界 X 轴转 25 度
    A.restore(snap)
    E0 = A.pos("Bip001RForearm")
    A.rotate_about("Bip001RForearm", E0, A.rot_axis_angle((1.0, 0.0, 0.0), 22.0))
    W3 = A.pos("Bip001RHand")
    OUT["log"].append(["forearm_only", "W", [round(v, 1) for v in W3],
                       "delta_cm", round(math.dist(W, W3), 1)])

    panel = [p for p in cmds.getPanel(type="modelPanel") if cmds.control(p, q=True, visible=True)][0]
    cmds.lookThru(panel, cmds.ls("DS_S001_CAM*")[0])
    os.makedirs(os.path.join(ROOT, "ds_stills", "anim_test"), exist_ok=True)
    cmds.currentTime(1)
    cmds.refresh(force=True)
    cmds.playblast(frame=1, format="image",
                   filename=os.path.join(ROOT, "ds_stills", "anim_test", "forearm_only"),
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(960, 540), quality=90, compression="png")
    OUT["ok"] = True
except Exception:  # noqa: BLE001
    import traceback
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds24_ikdiag.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False, indent=1)[:1500])
