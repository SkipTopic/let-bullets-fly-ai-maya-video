import maya.cmds as cmds
import json, os, sys, importlib, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
sp = os.path.join(ROOT, "scripts")
if sp not in sys.path:
    sys.path.insert(0, sp)
import lib_scene as _L
L = importlib.reload(_L)
OUT = {"errors": []}

# 实测最优的手臂静置姿势（Ma 上解的，三角色通用）
POSE = {
    "LeftArm": (-65, 0, -25), "LeftForeArm": 70,
    "RightArm": (40, 0, -40), "RightForeArm": -110,
}


def apply_rest_pose(j):
    for side in ("Left", "Right"):
        pass
    cmds.setAttr(j + "LeftArm.rotate", *POSE["LeftArm"])
    cmds.setAttr(j + "LeftForeArm.rotateX", POSE["LeftForeArm"])
    cmds.setAttr(j + "RightArm.rotate", *POSE["RightArm"])
    cmds.setAttr(j + "RightForeArm.rotateX", POSE["RightForeArm"])
    cmds.setAttr(j + "Spine.rotateX", 3)
    cmds.setAttr(j + "Spine1.rotateX", 1)
    cmds.setAttr(j + "Neck.rotateX", -12)
    cmds.setAttr(j + "Head.rotateX", -9)


try:
    chars = L.build_all()
    # 桌面抬到手下方
    cmds.setAttr("SET_table_top.translateY", 80.0)
    for key, ch in chars.items():
        apply_rest_pose(ch["j"])
    cmds.refresh(force=True)

    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))

    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    OUT["head_pos"] = {k: [round(v, 1) for v in p] for k, p in head_pos.items()}

    grp_cam = cmds.group(em=True, name="GRP_CAMERAS")
    built = []
    cmap = {}
    for s in shots:
        aim_at = head_pos[s["subject"]]
        aim_at = (aim_at[0], aim_at[1] - 6.0, aim_at[2])
        cam = cmds.camera(name="CAMX" + s["id"][1:] + "X", focalLength=s["focal"])[0]
        cmap[s["id"]] = cam
        cmds.setAttr(cam + ".translate", *s["eye0"])
        loc = cmds.spaceLocator(name="AIMX" + s["id"][1:] + "X")[0]
        cmds.setAttr(loc + ".translate", *aim_at)
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.parent(cam, grp_cam)
        cmds.parent(loc, grp_cam)

        # 运镜关键帧
        if s["eye0"] != s["eye1"]:
            cmds.setKeyframe(cam, attribute="translateX", time=s["start"], value=s["eye0"][0])
            cmds.setKeyframe(cam, attribute="translateZ", time=s["start"], value=s["eye0"][2])
            cmds.setKeyframe(cam, attribute="translateX", time=s["end"], value=s["eye1"][0])
            cmds.setKeyframe(cam, attribute="translateZ", time=s["end"], value=s["eye1"][2])
        built.append({"id": s["id"], "cam": cam, "start": s["start"], "end": s["end"],
                      "subject": s["subject"]})

    OUT["cameras"] = len(built)
    json.dump(cmap, open(os.path.join(ROOT, "logs", "cam_map.json"), "w", encoding="utf-8"), indent=1)
    cmds.file(os.path.join(ROOT, "scenes", "v6_cams.mb"), f=True, type="mayaBinary", ea=True)

    # 渲染 3 个样张
    tests = ["S001", "S020", "S045"]
    shots_by_id = {s["id"]: s for s in shots}
    for tid in tests:
        s = shots_by_id[tid]
        cmds.lookThru("CAM_" + tid)
        cmds.currentTime(s["start"] + 1)
        OUT[tid] = L.render_to(os.path.join(ROOT, "_接手检查", "s8_" + tid + ".png"))
    OUT["ok"] = True
except Exception as e:
    OUT["errors"].append(repr(e))
    OUT["trace"] = traceback.format_exc()

with open(os.path.join(ROOT, "logs", "s8_cams.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
