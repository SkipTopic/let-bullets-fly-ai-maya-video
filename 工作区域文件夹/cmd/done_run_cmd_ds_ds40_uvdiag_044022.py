"""UV 诊断：每块材质的 UV 范围与贴图采样颜色，用来判断谁是脸、谁是头发、谁是衣服。"""
import json
import os

import maya.api.OpenMaya as om
import maya.cmds as cmds
from PIL import Image

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = {"errors": [], "chars": {}}

CHARS = {
    "Huang": {
        "shape": "Huang_AragakiFBXASC032Shinjiro_meshShape",
        "tex": {"face": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_f1_tex00.png",
                "hair": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_h00_tex00.png",
                "body": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_26_SEES00.png",
                "body2": r"{R}\models_raw\aragaki_shinjiro\textures\pc110_03_body00.png"},
    },
    "Shiye": {
        "shape": "Shiye_JunpeiFBXASC032Iori_meshShape",
        "tex": {"face": r"{R}\models_raw\junpei_iori\textures\pc103_f1_tex00.png",
                "hair": r"{R}\models_raw\junpei_iori\textures\pc103_h00_tex00.png",
                "body": r"{R}\models_raw\junpei_iori\textures\pc103_26_SEES00.png",
                "body2": r"{R}\models_raw\junpei_iori\textures\pc103_03_body00.png"},
    },
}

imgs = {}
for name, cfg in CHARS.items():
    for k, p in cfg["tex"].items():
        path = p.format(R=ROOT)
        if os.path.exists(path):
            im = Image.open(path).convert("RGB")
            imgs[(name, k)] = (im, im.size)


def sample(name, key, u, v):
    if (name, key) not in imgs:
        return None
    im, (w, h) = imgs[(name, key)]
    x = int(max(0, min(w - 1, u * w)))
    y = int(max(0, min(h - 1, (1.0 - v) * h)))
    # 取 5x5 平均
    acc = [0, 0, 0]
    n = 0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            xx = max(0, min(w - 1, x + dx))
            yy = max(0, min(h - 1, y + dy))
            c = im.getpixel((xx, yy))
            acc[0] += c[0]
            acc[1] += c[1]
            acc[2] += c[2]
            n += 1
    return [round(c / n / 255.0, 3) for c in acc]


for name, cfg in CHARS.items():
    shape = cfg["shape"]
    sel = om.MSelectionList()
    sel.add(shape)
    dag = sel.getDagPath(0)
    fn = om.MFnMesh(dag)
    uv_sets = fn.getUVSetNames()
    sgs = cmds.listConnections(shape, type="shadingEngine") or []
    rows = []
    for sg in sgs:
        mats = cmds.listConnections(sg + ".surfaceShader") or []
        if not mats:
            continue
        mat = mats[0]
        comps = cmds.sets(sg, q=True) or []
        faces = []
        for t in comps:
            if "[" not in t:
                continue
            body = t.split("[")[-1].rstrip("]")
            parts = body.split(":")
            if len(parts) == 1:
                faces.append(int(parts[0]))
            else:
                a, b = int(parts[0]), int(parts[1])
                step = int(parts[2]) if len(parts) > 2 else 1
                faces.extend(range(a, b + 1, step))
        us, vs = [], []
        for f in faces[:800]:
            try:
                uarr, varr = fn.getPolygonUVs(f, uv_sets[0])
            except Exception:
                continue
            us.extend(uarr)
            vs.extend(varr)
        if not us:
            continue
        cu, cv = sum(us) / len(us), sum(vs) / len(vs)
        row = {
            "mat": mat, "faces": len(faces),
            "uv": [round(cu, 3), round(cv, 3)],
            "uv_range": [round(min(us), 3), round(max(us), 3), round(min(vs), 3), round(max(vs), 3)],
            "color": {k: sample(name, k, cu, cv) for k in cfg["tex"]},
        }
        i = cmds.xform(shape, q=True, ws=True, t=True)
        rows.append(row)
    OUT["chars"][name] = {"uv_sets": uv_sets, "rows": rows}

with open(os.path.join(ROOT, "logs", "ds40_uv.json"), "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, ensure_ascii=False, indent=1)

for name, d in OUT["chars"].items():
    print("==", name, "uvsets", d["uv_sets"])
    for r in d["rows"]:
        print("  %-22s f=%-5d uv=%s range=%s face=%s hair=%s body=%s" % (
            r["mat"][-22:], r["faces"], r["uv"], r["uv_range"],
            r["color"]["face"], r["color"]["hair"], r["color"]["body"]))
