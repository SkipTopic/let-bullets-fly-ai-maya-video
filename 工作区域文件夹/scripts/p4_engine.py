# -*- coding: utf-8 -*-
"""P4 engine: read shotlist.csv, generate per-shot python blocks for Maya."""
import csv
import re
import sys
from pathlib import Path

W = Path(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹")

SEAT = {
    "Ma":    (0, -46, -100, 180),
    "Huang": (44, -46, 26, 120),
    "Shiye": (-44, -46, 26, -120),
}
CHAR_RE = {"Ma": "马县长|马某人|县长", "Huang": "黄四郎|黄四爷|黄老爷", "Shiye": "师爷"}
SPEAK_RE = re.compile(r"[（(](马县长|黄四郎|师爷|三人)[)）]")
HEADY = {"Ma": 95, "Huang": 100, "Shiye": 98}  # observed head joint world y


def speaker_of(dialogue):
    m = SPEAK_RE.search(dialogue or "")
    if not m:
        return None
    t = m.group(1)
    if t == "三人":
        return "Ma"
    for k, pat in CHAR_RE.items():
        if re.search(pat, t):
            return k
    return None


def looks_target(action):
    if not action:
        return None
    if re.search("看向.{0,8}师爷|望着师爷|师爷后", action):
        return "Shiye"
    if re.search("看向.{0,8}黄四郎|望着黄|对着黄四郎|比向黄四郎", action):
        return "Huang"
    if re.search("看向.{0,8}马县长|看着马县长|对马县长|比向马县长", action):
        return "Ma"
    return None


def cam_plan(shot):
    size = shot["shot_size"]
    move = shot["camera_move"] or ""
    dial = shot["dialogue"] or ""
    act = shot["action"] or ""
    spk = speaker_of(dial) or looks_target(act) or "Ma"
    hx, hy, hz, _ = SEAT[spk]
    head_y = HEADY[spk]
    if "特写" in size:
        focal, dist, camh = 75, 210, head_y + 8
    elif "中景" in size:
        focal, dist, camh = 50, 330, head_y + 16
    else:
        focal, dist, camh = 65, 265, head_y + 8
    dx, dz = -hx * 0.5, -hz * 0.5 + dist * 0.78
    px, pz = hx + dx, hz + dz
    drift = 0
    if re.search("向右移动|向右移", move):
        drift = 26
    elif re.search("向左", move):
        drift = -26
    up = 0
    if re.search("向上移动|向上动|跟着向上", move):
        up = 14
    elif re.search("向下移动|向下动", move):
        up = -12
    return {"focal": focal, "pos": (px, camh, pz), "aim": (hx, head_y, hz),
            "drift": drift, "up": up, "spk": spk}


def perf_plan(shot, f0, f1):
    act = shot["action"] or ""
    dial = shot["dialogue"] or ""
    spk = speaker_of(dial)
    lines = []
    tags = ["Ma", "Huang", "Shiye"]
    dur = f1 - f0
    lines.append("blink_loop_all(%d, %d)" % (f0, f1))
    for t in tags:
        lines.append("breath('%s', %d, %d)" % (t, f0, f1))
    if not spk:
        lines.append("glance('Ma', 'Huang', %d)" % (f0 + dur // 2))
        return lines
    others = [t for t in tags if t != spk]
    t = f0 + 6
    gi = 0
    while t < f1 - 8:
        style = "ABCB"[gi % 4]
        lines.append("gesture('%s', '%s', %d, %d)" % (spk, style, t, min(16, f1 - t - 4)))
        t += 20
        gi += 1
    lt = looks_target(act)
    if lt:
        lines.append("look_key('%s', '%s', %d, %d)" % (spk, lt, f0 + 4, f1 - 6))
    elif len(others) > 1 and dur > 30:
        lines.append("look_key('%s', '%s', %d, %d)" % (spk, others[0], f0 + 8, f0 + dur // 2))
        lines.append("look_key('%s', '%s', %d, %d)" % (spk, others[1], f0 + dur // 2, f1 - 6))
    if "顺" in act and "衣" in act:
        lines.append("smooth_chest('%s', %d, %d)" % (spk, f0 + 4, 16))
    if "点头" in act:
        lines.append("nod('%s', %d, %d, 10)" % (spk, f0 + 6, 2))
    if "指" in act:
        lines.append("gesture('%s', 'C', %d, %d)" % (spk, f0 + 8, 14))
    if "拿" in act and "杯" in act:
        lines.append("raise_cup('%s', %d, %d)" % (spk, f0 + 6, max(8, dur - 12)))
    if "敲" in act:
        lines.append("knock('%s', %d)" % (spk, f0 + 10))
    if "瞪" in act or "盯" in act or "定住" in act:
        for o in others:
            lines.append("hold_eyes('%s', 0.15, %d)" % (o, f0 + 4))
    if "站起" in act:
        lines.append("lean('%s', %d, -6, %d)" % (spk, f0 + 4, 12))
    if "眨" in act and spk:
        lines.append("blink('%s', %d)" % (spk, f0 + dur // 2))
    return lines


def gen_shot_code(shot):
    i = int(shot["shot_id"][1:])
    f0, f1 = int(shot["start_frame"]), int(shot["end_frame"])
    cam = cam_plan(shot)
    L = []
    L.append("# ---- S%03d ----" % i)
    L.append("cam = cmds.camera(name='CAM_S%03d')[0]" % i)
    L.append("sh = cmds.listRelatives(cam, s=True)[0]")
    L.append("cmds.setAttr(sh + '.focalLength', %d)" % cam["focal"])
    L.append("cmds.setAttr(cam + '.translate', %d, %d, %d)" % cam["pos"])
    L.append("lt = cmds.spaceLocator(name='aimT_S%03d')[0]" % i)
    L.append("cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('%s', 'Head'), q=True, ws=True, t=True)[:3]])" % cam["spk"])
    L.append("ac = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))")
    L.append("cmds.setKeyframe(cam + '.rotateX', t=%d)" % f0)
    L.append("cmds.setKeyframe(cam + '.rotateY', t=%d)" % f0)
    L.append("cmds.setKeyframe(cam + '.rotateZ', t=%d)" % f0)
    if cam["drift"] or cam["up"]:
        L.append("cmds.setAttr(cam + '.translate', %d, %d, %d)" % (
            cam["pos"][0] + cam["drift"], cam["pos"][1] + cam["up"], cam["pos"][2]))
        for ax in ("X", "Y", "Z"):
            L.append("cmds.setKeyframe(cam + '.translate%s', t=%d)" % (ax, f0))
            L.append("cmds.setKeyframe(cam + '.translate%s', t=%d)" % (ax, f1))
        L.append("cmds.setAttr(lt + '.translate', *[round(v, 2) for v in cmds.xform(J('%s', 'Head'), q=True, ws=True, t=True)[:3]])" % cam["spk"])
        L.append("ac2 = cmds.aimConstraint(lt, cam, aimVector=(0,0,-1), upVector=(0,1,0), worldUpVector=(0,1,0))")
    L.append("cmds.delete(ac)")
    if cam["drift"] or cam["up"]:
        for ax in ("X", "Y", "Z"):
            L.append("cmds.setKeyframe(cam + '.rotate%s', t=%d)" % (ax, f1))
    L.append("cmds.delete(lt)")
    L += perf_plan(shot, f0, f1)
    return "\n".join(L)


def main():
    with open(W / "shotlist.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    blocks = []
    for r in rows:
        if r["status"] == "black":
            continue
        blocks.append(gen_shot_code(r))
    header = open(Path(__file__).parent / "p4_runtime.py", encoding="utf-8").read()
    out = W / "scripts" / "p4_generated.py"
    out.write_text(header + "\n\n" + "\n\n".join(blocks) + "\n\nprint('P4_ALL_SHOTS_BUILT')\n", encoding="utf-8")
    print("generated %d blocks -> %s" % (len(blocks), out))


if __name__ == "__main__":
    main()
