

# ============================================================
# 最终材质分配（必须放在文件最后：同名函数后者生效）
# ============================================================

def color_char_materials(geo, palette):
    """按面片空间位置分色：头部靠前=脸、头部其余=头发、脚=鞋、其余=衣服。"""
    shapes = cmds.listRelatives(geo, shapes=True, ni=True) or []
    if not shapes:
        return []
    shape = shapes[0]
    sgs = list(dict.fromkeys(cmds.listConnections(shape, type="shadingEngine") or []))
    if not sgs:
        return []

    bb = cmds.exactWorldBoundingBox(shape)
    zmin, zmax = bb[2], bb[5]
    ymin, ymax = bb[1], bb[4]
    h = max(ymax - ymin, 1.0)

    info = []
    for sg in sgs:
        faces = [f for f in (cmds.sets(sg, q=True) or []) if ".f[" in f]
        ys, zs = [], []
        step = max(1, len(faces) // 50)
        for f in faces[::step][:50]:
            try:
                fb = cmds.xform(f, q=True, ws=True, bb=True)
                ys.append((fb[1] + fb[4]) / 2.0)
                zs.append((fb[2] + fb[5]) / 2.0)
            except Exception:
                pass
        info.append({"sg": sg, "n": len(faces),
                     "cy": (sum(ys) / len(ys)) if ys else 0.0,
                     "cz": (sum(zs) / len(zs)) if zs else 0.0})

    total = sum(i["n"] for i in info) or 1
    head_y = ymin + h * 0.74
    foot_y = ymin + h * 0.12

    head = [i for i in info if i["cy"] >= head_y and i["n"] < total * 0.5]
    face_sg = max(head, key=lambda i: i["cz"])["sg"] if head else max(info, key=lambda i: i["cy"])["sg"]
    head_sgs = {i["sg"] for i in head}

    done = []
    ci = 0
    for i in info:
        if i["sg"] == face_sg:
            col = palette["skin"]
        elif i["sg"] in head_sgs:
            col = palette["hair"]
        elif i["cy"] <= foot_y:
            col = palette["shoe"]
        else:
            col = palette["cloth"] if ci % 2 == 0 else palette["cloth2"]
            ci += 1
        m = new_material("M_%s_%d" % (shape.replace(":", "_"), len(done)), col)
        cmds.connectAttr(m + ".outColor", i["sg"] + ".surfaceShader", force=True)
        done.append((i["sg"], round(i["cy"], 1), col))
    return done
