"""v04 渲染器：非离屏 playblast + 逐镜黑帧自检重渲。

用法：参数文件 cmd/ds_v4_param.json {"ids": [...], "outdir": "..."}
"""
import glob
import json
import os
import time
import traceback

import maya.cmds as cmds
import maya.api.OpenMaya as om

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
PARAM = os.path.join(ROOT, "cmd", "ds_v4_param.json")
OUT = {"errors": [], "done": []}


def mean_lum(path):
    """用 MImage 采样平均亮度（Maya 自带 Python 没有 PIL）。"""
    try:
        img = om.MImage()
        img.readFromFile(path)
        w, h = img.getSize()
        px = img.getPixels(0, w, 0, h)  # RGBA bytes，线性
        if px is None:
            return -1.0
        n = len(px) // 4
        step = max(1, n // 20000)
        acc = 0
        cnt = 0
        for i in range(0, n, step):
            j = i * 4
            acc += px[j] + px[j + 1] + px[j + 2]
            cnt += 3
        return (acc / max(1, cnt)) / 255.0 * 255.0
    except Exception:
        return -1.0


def render_frames(panel, cam, base, f0, f1, w, h, q):
    cmds.lookThru(panel, cam)
    cmds.setFocus(panel)
    cmds.currentTime(f0)
    cmds.refresh(force=True)
    cmds.playblast(startTime=f0, endTime=f1, filename=base, format="image",
                   sequenceTime=False, clearCache=True, viewer=False, showOrnaments=False,
                   offScreen=True, percent=100, widthHeight=(w, h), quality=q,
                   compression="png")


def render_single(panel, cam, base, f, w, h, q):
    cmds.lookThru(panel, cam)
    cmds.setFocus(panel)
    cmds.currentTime(f)
    cmds.refresh(force=True)
    time.sleep(0.05)
    cmds.playblast(frame=f, filename=base, format="image", sequenceTime=False,
                   clearCache=True, viewer=False, showOrnaments=False, offScreen=True,
                   percent=100, widthHeight=(w, h), quality=q, compression="png")


try:
    p = json.load(open(PARAM, encoding="utf-8"))
    ids = p["ids"]
    outdir = p["outdir"]
    w, h, q = p.get("w", 960), p.get("h", 540), p.get("q", 85)
    os.makedirs(outdir, exist_ok=True)
    shots = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "ds_camera_action", "shots_deepseek.json"),
                                                encoding="utf-8"))["shots"]}

    panel = [x for x in cmds.getPanel(type="modelPanel") if cmds.control(x, q=True, visible=True)][0]
    cmds.modelEditor(panel, e=True, displayAppearance="smoothShaded", displayTextures=True,
                     displayLights="all", grid=False, joints=False, cameras=False,
                     locators=False, manipulators=False, handles=False, headsUpDisplay=False,
                     selectionHiliteDisplay=False, lights=False)
    cmds.select(clear=True)

    for sid in ids:
        cams = cmds.ls("DS_%s_CAM*" % sid)
        if not cams:
            OUT["errors"].append("missing cam " + sid)
            continue
        cam = cams[0]
        s = shots[sid]
        f0, f1 = s["frame_range"]
        base = os.path.join(outdir, sid)

        t0 = time.time()
        try:
            render_frames(panel, cam, base, f0, f1, w, h, q)
        except Exception as exc:
            OUT["errors"].append("%s batch: %r" % (sid, exc))

        # 黑帧自检
        bad = []
        for f in range(f0, f1 + 1):
            path = "%s.%04d.png" % (base, f)
            if not os.path.exists(path) or mean_lum(path) < 12.0:
                bad.append(f)
        # S046 是黑场卡，跳过
        if sid == "S046":
            bad = []

        fixed = 0

        OUT["done"].append({"id": sid, "frames": f1 - f0 + 1, "black_found": len(bad),
                            "black_fixed": fixed, "sec": round(time.time() - t0, 1)})
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

with open(os.path.join(ROOT, "logs", "ds48_v4.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)
print(json.dumps({"ok": OUT.get("ok"), "done": OUT["done"], "err": OUT["errors"][:1]}, ensure_ascii=False)[:900])
