

# ============================================================
# 材质分配（几何驱动，覆盖关键词版）
# ============================================================

def color_char_materials(geo, palette):
    """按"每个材质槽的几何位置/面积"分配颜色，避免整人身肤色。"""
    shapes = cmds.listRelatives(geo, shapes=True, ni=True) or []
    if not shapes:
        return []
    shape = shapes[0]
    sgs = list(dict.fromkeys(cmds.listConnections(shape, type="shadingEngine") or []))
    if not sgs:
        return []

    info = []
    for sg in sgs:
        faces = cmds.sets(sg, q=True) or []
        faces = [f for f in faces if ".f[" in f]
        ys = []
        for f in faces[:400]:
            try:
                ys.append(cmds.polyEvaluate(f, boundingBoxY=True)[1])
            except Exception:
                pass
        if not ys:
            info.append((sg, len(faces), 0.0, 0.0, 0.0))
            continue
        info.append((sg, len(faces), sum(ys) / len(ys), min(ys), max(ys)))

    top = max(i[4] for i in info) if info else 0
    total_faces = sum(i[1] for i in info) or 1
    head_line = top * 0.86

    # 头区：max_y 超过 head_line 且面积占比小
    head_slots = [i for i in info if i[4] >= head_line and i[1] < total_faces * 0.22]
    face_sg = None
    if head_slots:
        face_sg = max(head_slots, key=lambda i: i[1])[0]

    done = []
    cloth_i = 0
    for sg, n, ay, mn, mx in info:
        if sg == face_sg:
            col = palette["skin"]
        elif mx >= head_line:
            col = palette["hair"]
        elif mn < top * 0.06:
            col = palette["shoe"]
        else:
            col = palette["cloth"] if cloth_i % 2 == 0 else palette["cloth2"]
            cloth_i += 1
        m = new_material("M_%s_%d" % (shape.replace(":", "_"), len(done)), col)
        cmds.connectAttr(m + ".outColor", sg + ".surfaceShader", force=True)
        done.append((sg, n, col))
    return done
