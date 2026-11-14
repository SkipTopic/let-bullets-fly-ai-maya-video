import maya.cmds as cmds
import json, os, sys, math, traceback

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
import lib_scene as _L
L = importlib.reload(_L)

OUT = {"errors": []}
TABLE = 75.75


def chain_to(sj, ee):
    out = [ee]
    cur = ee
    while cur and cur != sj:
        p = cmds.listRelatives(cur, parent=True)
        cur = p[0] if p else None
        if cur:
            out.append(cur)
    return out


def put_hand(j, side, target, pole):
    sj, ee = j + side + "Arm", j + side + "Hand"
    h = cmds.ikHandle(sj=sj, ee=ee, sol="ikRPsolver")[0]
    pv = cmds.spaceLocator(name="PV_tmp")[0]
    cmds.setAttr(pv + ".translate", *pole)
    cmds.poleVectorConstraint(pv, h)
    cmds.move(target[0], target[1], target[2], h, absolute=True)
    vals = {b: list(cmds.getAttr(b + ".rotate")[0]) for b in chain_to(sj, ee)}
    cmds.delete(h)
    cmds.delete(pv)
    for b, v in vals.items():
        cmds.setAttr(b + ".rotate", *v)


try:
    chars = L.build_all()

    # ---- 姿势：抬头 + 手放桌面 ----
    for key, ch in chars.items():
        j = ch["j"]
        cmds.setAttr(j + "Spine.rotateX", 8)
        cmds.setAttr(j + "Spine1.rotateX", 4)
        cmds.setAttr(j + "Neck.rotateX", -19)
        cmds.setAttr(j + "Head.rotateX", -16)
    cmds.refresh(force=True)

    for key, ch in chars.items():
        j = ch["j"]
        gx, gy, gz = cmds.getAttr(ch["grp"] + ".translate")[0]
        ang = math.radians(ch["theta"])
        fwd = (-math.cos(ang), -math.sin(ang))
        right = (-fwd[1], fwd[0])
        for side, s in (("Left", 1), ("Right", -1)):
            tgt = (gx + fwd[0] * 27 + right[0] * 16 * s, TABLE + 3.0,
                   gz + fwd[1] * 27 + right[1] * 16 * s)
            pole = (gx + fwd[0] * 4 + right[0] * 82 * s, TABLE + 26,
                    gz + fwd[1] * 4 + right[1] * 82 * s)
            put_hand(j, side, tgt, pole)

    # ---- 相机：建好后把朝向烘焙进 rotate，删掉约束和 locator ----
    shots = json.load(open(os.path.join(ROOT, "shots.json"), encoding="utf-8"))
    head_pos = {k: cmds.xform(ch["j"] + "Head", q=True, ws=True, t=True)
                for k, ch in chars.items()}
    cams = []
    cam_names = {}
    for s in shots:
        h = head_pos[s["subject"]]
        dist = 132.0 if "近" in s["size"] else 198.0
        k = dist / max(s["dist"], 1.0)
        cam = cmds.camera(name="%s_CAM" % s["id"], focalLength=s["focal"])[0]
        cam_names[s["id"]] = cam
        cmds.setAttr(cam + ".translate", s["eye0"][0] * k, h[1] + 4.0, s["eye0"][2] * k)
        loc = cmds.spaceLocator(name="TMP_AIM")[0]
        cmds.setAttr(loc + ".translate", h[0], h[1] - 2.0, h[2])
        cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                           worldUpType="vector", worldUpVector=(0, 1, 0))
        cmds.delete(cmds.listRelatives(cam, type="aimConstraint", children=False) or [])
        # 取世界矩阵 → 烘焙
        m = cmds.xform(cam, q=True, ws=True, m=True)
        for c in (cmds.listRelatives(cam, type="aimConstraint", children=False) or []):
            cmds.delete(c)
        for c in (cmds.listConnections(cam, type="aimConstraint") or []):
            try:
                cmds.delete(c)
            except Exception:
                pass
        cmds.xform(cam, ws=True, m=m)
        cmds.delete(loc)
        cams.append(cam)

    # ---- 组结构 ----
    root = cmds.group(em=True, name="SCENE")
    grp_chars = cmds.group(em=True, name="CHARS", parent=root)
    grp_cams = cmds.group(em=True, name="CAMERAS", parent=root)
    grp_set = cmds.group(em=True, name="SET", parent=root)
    grp_lights = cmds.group(em=True, name="LIGHTS", parent=root)

    for key, nm in (("Ma", "CHR_Ma"), ("Huang", "CHR_Huang"), ("Shiye", "CHR_Shiye")):
        g = chars[key]["grp"]
        cmds.rename(g, nm)
        cmds.parent(nm, grp_chars)

    exact = [x for x in (cmds.ls(type="transform") or []) if x == "SET"]
    if exact:
        for c in cmds.listRelatives(exact[0], children=True, type="transform") or []:
            cmds.parent(c, grp_set)
        cmds.delete(exact[0])

    exact = [x for x in (cmds.ls(type="transform") or []) if x == "LIGHTS"]
    if exact:
        for c in cmds.listRelatives(exact[0], children=True, type="transform") or []:
            cmds.parent(c, grp_lights)
        cmds.delete(exact[0])

    for c in cams:
        cmds.parent(c, grp_cams)

    # ---- 导出位置表 ----
    data = {"chars": {}, "cams": {}, "set": {}}
    for key, nm in (("Ma", "CHR_Ma"), ("Huang", "CHR_Huang"), ("Shiye", "CHR_Shiye")):
        data["chars"][key] = {
            "group": nm,
            "translate": [round(v, 2) for v in cmds.getAttr(nm + ".translate")[0]],
            "rotateY": round(cmds.getAttr(nm + ".rotateY"), 2),
            "head_ws": [round(v, 1) for v in cmds.xform(key + "_Head", q=True, ws=True, t=True)],
        }
    for s in shots:
        nm = cam_names[s["id"]]
        data["cams"][s["id"]] = {
            "name": nm,
            "translate": [round(v, 2) for v in cmds.getAttr(nm + ".translate")[0]],
            "rotate": [round(v, 2) for v in cmds.getAttr(nm + ".rotate")[0]],
            "focal": round(cmds.getAttr(nm + ".focalLength"), 1),
            "subject": s["subject"],
            "size": s["size"],
            "frames": [s["start"], s["end"]],
        }
    data["table"] = {"top_y": TABLE, "radius": 88, "seat_radius": 102,
                     "seat_top_y": 46.5, "floor_y": 0}
    OUT["data"] = data

    # 工程工作区指向项目目录，避免绝对路径漂移
    cmds.workspace(os.path.join(ROOT, "mayaProject"), openWorkspace=True)
    cmds.file(os.path.join(ROOT, "scenes", "手工摆位_v1.mb"), f=True, type="mayaBinary", ea=True)
    OUT["saved"] = "scenes/手工摆位_v1.mb"
    OUT["ok"] = True
except Exception:
    OUT["errors"].append(traceback.format_exc())

json.dump(OUT, open(os.path.join(ROOT, "logs", "s20.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
