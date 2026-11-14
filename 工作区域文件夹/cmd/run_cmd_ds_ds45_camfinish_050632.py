"""给 71 台相机加：景深 + 手持微晃（逐帧烘焙推拉+抖动）。"""
import json, math, os, traceback
import maya.cmds as cmds

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "cams": {}}
FSTOP = {"single": 2.0, "close": 2.0, "medium": 2.8, "ots": 1.6, "title": 2.8}


def shake(f, seed):
    a1 = math.sin(f * 0.171 + seed) * 0.22
    a2 = math.sin(f * 0.061 + seed * 1.7) * 0.30
    a3 = math.cos(f * 0.113 + seed * 2.3) * 0.18
    return (a1 + a2 * 0.4, a3, a2 * 0.5)


try:
    shots = json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                           encoding="utf-8"))["shots"]
    moves = json.load(open(os.path.join(ROOT, "logs", "ds36_cammove.json"), encoding="utf-8"))["shots"]

    for idx, s in enumerate(shots):
        sid = s["id"]
        cams = cmds.ls("DS_%s_CAM*" % sid)
        if not cams:
            continue
        cam = cams[0]
        shape = cmds.listRelatives(cam, shapes=True)[0]
        proj = s.get("projection") or {}
        subj = s.get("subject")
        focus = 200.0
        if subj and proj.get(subj):
            focus = proj[subj]["dist"]

        cmds.setAttr(shape + ".depthOfField", True)
        cmds.setAttr(shape + ".focusDistance", focus)
        cmds.setAttr(shape + ".fStop", FSTOP.get(s["type"], 2.4))
        cmds.setAttr(shape + ".focusRegionScale", 1.0)

        f0, f1 = s["frame_range"]
        mv = moves.get(sid) or {}
        start = mv.get("start") or list(cmds.xform(cam, q=True, ws=True, t=True))
        end = mv.get("end") or start

        # 清掉原来的两帧推拉关键帧，改成逐帧烘焙
        for f in range(f0, f1 + 1):
            try:
                cmds.cutKey(cam, at="translate", time=(f, f))
            except Exception:
                pass

        seed = idx * 1.37
        for f in range(f0, f1 + 1, 2):
            t = (f - f0) / max(1, (f1 - f0))
            base = [start[k] + (end[k] - start[k]) * t for k in range(3)]
            sx, sy, sz = shake(f, seed)
            cmds.currentTime(f)
            cmds.xform(cam, ws=True, t=(base[0] + sx, base[1] + sy, base[2] + sz))
            cmds.setKeyframe(cam, at="translate", time=f)

        # 末帧补一个点，保证走完
        t = 1.0
        base = [start[k] + (end[k] - start[k]) * t for k in range(3)]
        sx, sy, sz = shake(f1, seed)
        cmds.currentTime(f1)
        cmds.xform(cam, ws=True, t=(base[0] + sx, base[1] + sy, base[2] + sz))
        cmds.setKeyframe(cam, at="translate", time=f1)

        OUT["cams"][sid] = {"focus": round(focus, 1), "fstop": FSTOP.get(s["type"], 2.4)}

    cmds.currentTime(1)
    cmds.file(save=True, force=True, type="mayaBinary")
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds45_camfinish.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "n": len(OUT["cams"]), "err": OUT["errors"][:1]}, ensure_ascii=False)[:400])
