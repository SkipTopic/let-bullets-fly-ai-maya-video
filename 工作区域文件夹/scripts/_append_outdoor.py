

# ============================================================
# 室外庭院版布景与日光（覆盖上面的室内版）
# ============================================================

def build_set():
    """室外庭院：圆桌 + 椅子 + 背景房子 + 天空穹顶。没有棚子、没有蜡烛。"""
    grp = cmds.group(em=True, name="SET")
    mats = {
        "wood": new_material("SET_wood", (0.205, 0.108, 0.062)),
        "wood_dark": new_material("SET_wood_dark", (0.105, 0.055, 0.036)),
        "cloth": new_material("SET_cloth", (0.34, 0.08, 0.06)),
        "earth": new_material("SET_earth", (0.305, 0.248, 0.186)),
        "stone": new_material("SET_stone", (0.43, 0.40, 0.36)),
        "plaster": new_material("SET_plaster", (0.60, 0.545, 0.47)),
        "tile": new_material("SET_tile", (0.175, 0.175, 0.185)),
        "sky": new_material("SET_sky", (0.55, 0.70, 0.86)),
        "porcelain": new_material("SET_porcelain", (0.55, 0.54, 0.52)),
        "foliage": new_material("SET_foliage", (0.115, 0.185, 0.085)),
    }

    fl = cmds.polyPlane(w=2400, h=2400, sx=1, sy=1, name="SET_floor")[0]
    assign(fl, mats["earth"])
    cmds.parent(fl, grp)

    # 天空穹顶：反转法线，从内部看
    sky = cmds.polySphere(r=1700, sx=32, sy=16, name="SET_sky")[0]
    cmds.setAttr(sky + ".scaleX", -1)
    assign(sky, mats["sky"])
    cmds.parent(sky, grp)

    # 圆桌
    top = cmds.polyCylinder(r=88, h=4.5, sx=48, name="SET_table_top")[0]
    cmds.move(0, 73.5, 0, top)
    assign(top, mats["wood"])
    cmds.parent(top, grp)
    for i in range(3):
        a = math.radians(90 + i * 120)
        leg = cmds.polyCylinder(r=5, h=73, sx=12, name="SET_leg_%d" % i)[0]
        cmds.move(math.cos(a) * 64, 36, math.sin(a) * 64, leg)
        assign(leg, mats["wood_dark"])
        cmds.parent(leg, grp)

    # 椅子
    for i, (who, ang) in enumerate(SEAT_ANGLE.items()):
        a = math.radians(ang)
        cx, cz = math.cos(a) * 118, math.sin(a) * 118
        yaw = math.degrees(math.atan2(-math.cos(a), -math.sin(a)))
        seat = cmds.polyCube(w=46, h=5, d=44, name="SET_seat_%d" % i)[0]
        cmds.move(cx, 44, cz, seat)
        cmds.rotate(0, yaw, 0, seat)
        assign(seat, mats["cloth"])
        cmds.parent(seat, grp)
        back = cmds.polyCube(w=46, h=54, d=5, name="SET_back_%d" % i)[0]
        cmds.move(cx + math.cos(a) * 20, 72, cz + math.sin(a) * 20, back)
        cmds.rotate(0, yaw, 0, back)
        assign(back, mats["wood_dark"])
        cmds.parent(back, grp)

    # 背景房子
    hz = -430
    house = cmds.polyCube(w=560, h=300, d=260, name="SET_house_body")[0]
    cmds.move(0, 150, hz, house)
    assign(house, mats["plaster"])
    cmds.parent(house, grp)
    eave = cmds.polyCube(w=640, h=26, d=330, name="SET_house_eave")[0]
    cmds.move(0, 306, hz, eave)
    assign(eave, mats["tile"])
    cmds.parent(eave, grp)
    roof = cmds.polyCube(w=600, h=90, d=300, name="SET_roof")[0]
    cmds.move(0, 362, hz, roof)
    assign(roof, mats["tile"])
    cmds.parent(roof, grp)
    for i in range(6):
        col = cmds.polyCylinder(r=11, h=300, sx=12, name="SET_col_%d" % i)[0]
        cmds.move(-220 + i * 88, 150, hz + 150, col)
        assign(col, mats["wood_dark"])
        cmds.parent(col, grp)
    step = cmds.polyCube(w=560, h=16, d=120, name="SET_step")[0]
    cmds.move(0, 8, hz + 195, step)
    assign(step, mats["stone"])
    cmds.parent(step, grp)

    # 两侧矮墙
    for tag, x in (("L", -420), ("R", 420)):
        w_ = cmds.polyCube(w=18, h=95, d=520, name="SET_lowwall_" + tag)[0]
        cmds.move(x, 47, -120, w_)
        assign(w_, mats["stone"])
        cmds.parent(w_, grp)

    # 树丛
    for i, (x, z, r) in enumerate(((-330, -300, 70), (300, -320, 82),
                                   (-180, -540, 95), (210, -560, 88))):
        t = cmds.polySphere(r=r, sx=14, sy=10, name="SET_tree_%d" % i)[0]
        cmds.move(x, r * 0.85, z, t)
        cmds.scale(1, 1.15, 1, t)
        assign(t, mats["foliage"])
        cmds.parent(t, grp)

    # 桌面道具（少而偏）
    b = cmds.polyCylinder(r=7, h=3.2, sx=24, name="SET_bowl_0")[0]
    cmds.move(-34, 76.6, 8, b)
    assign(b, mats["porcelain"])
    cmds.parent(b, grp)

    cup = cmds.polyCylinder(r=2.6, h=7, sx=14, name="SET_cup_0")[0]
    cmds.move(-12, 79.4, 22, cup)
    assign(cup, mats["porcelain"])
    cmds.parent(cup, grp)

    bottle = cmds.polyCylinder(r=2.4, h=12, sx=18, name="SET_bottle")[0]
    cmds.move(26, 81, -6, bottle)
    assign(bottle, mats["porcelain"])
    cmds.parent(bottle, grp)

    return grp, mats


def build_lights():
    """自然日光：斜上方太阳 + 天空环境 + 地面反弹。"""
    grp = cmds.group(em=True, name="LIGHTS")
    sun = _tr(cmds.directionalLight(name="LGT_sun", intensity=2.30))
    cmds.setAttr(sun + ".color", 1.0, 0.955, 0.875, type="double3")
    cmds.setAttr(sun + ".rotate", -54, 36, -8)
    try:
        cmds.setAttr(sun + ".useDepthMapShadows", 1)
        cmds.setAttr(sun + ".dmapResolution", 2048)
        cmds.setAttr(sun + ".dmapFilterSize", 4)
    except Exception:
        pass

    sky = _tr(cmds.ambientLight(name="LGT_sky", intensity=0.60))
    cmds.setAttr(sky + ".color", 0.64, 0.76, 0.94, type="double3")

    bounce = _tr(cmds.directionalLight(name="LGT_bounce", intensity=0.45))
    cmds.setAttr(bounce + ".color", 0.88, 0.76, 0.60, type="double3")
    cmds.setAttr(bounce + ".rotate", 66, -142, 0)

    for l in (sun, sky, bounce):
        cmds.parent(l, grp)
    return grp
