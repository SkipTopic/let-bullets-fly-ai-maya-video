"""场景构建库：材质 / 布景 / 坐姿 / 相机 / 渲染。"""
import maya.cmds as cmds
import math, os

ROOT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"

# 三人 120° 分开坐（整圈，不是半圈）
SEAT_ANGLE = {"Ma": 270, "Huang": 30, "Shiye": 150}

# ============ 基础工具 ============

def _tr(node):
    """灯光命令返回的可能是 shape，统一取 transform。"""
    if cmds.nodeType(node) in ("directionalLight", "pointLight", "ambientLight", "spotLight"):
        p = cmds.listRelatives(node, parent=True)
        return p[0] if p else node
    return node


def panel():
    ps = cmds.getPanel(type="modelPanel") or []
    return ps[0] if ps else None


def setup_viewport():
    p = panel()
    if p:
        flags = dict(displayAppearance="smoothShaded", displayTextures=False,
                     displayLights="default", grid=False, joints=False,
                     manipulators=False, headsUpDisplay=False,
                     dynamicConstraints=False, selectionHiliteDisplay=False,
                     wireframeOnShaded=False, backfaceCulling=False,
                     twoSidedLighting=True, displayFilmGate=False,
                     displayResolution=False)
        for k, v in flags.items():
            try:
                cmds.modelEditor(p, e=True, **{k: v})
            except Exception:
                pass
    try:
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.ssaoRadius", 8)
        cmds.setAttr("hardwareRenderingGlobals.ssaoAmount", 1.2)
        cmds.setAttr("hardwareRenderingGlobals.floatingPointRTEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
        cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
    except Exception:
        pass
    return p


def new_material(name, rgb, spec=0.1, amb=0.15):
    """surfaceShader = 完全不受光，直接输出颜色（平涂/无光照）。"""
    if cmds.objExists(name):
        cmds.delete(name)
    m = cmds.shadingNode("lambert", asShader=True, name=name)
    cmds.setAttr(m + ".color", rgb[0], rgb[1], rgb[2], type="double3")
    cmds.setAttr(m + ".ambientColor", rgb[0] * 0.35, rgb[1] * 0.35, rgb[2] * 0.35,
                 type="double3")
    cmds.setAttr(m + ".diffuse", 0.9)
    return m


def assign(obj, mat):
    sg = cmds.listConnections(mat, type="shadingEngine")
    if not sg:
        sg = [cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat + "SG")]
        cmds.connectAttr(mat + ".outColor", sg[0] + ".surfaceShader", force=True)
    cmds.sets(obj, e=True, forceElement=sg[0])


def color_char_materials(geo, palette):
    """按面片实际空间位置分色：头顶=头发、头部前方=脸、脚部=鞋、其余=衣服。"""
    shapes = cmds.listRelatives(geo, shapes=True, ni=True) or []
    if not shapes:
        return []
    shape = shapes[0]
    sgs = list(dict.fromkeys(cmds.listConnections(shape, type="shadingEngine") or []))
    if not sgs:
        return []

    bbox = cmds.exactWorldBoundingBox(shape)
    zmin, zmax = bbox[2], bbox[5]
    ymin, ymax = bbox[1], bbox[4]
    h = max(ymax - ymin, 1.0)

    info = []
    for sg in sgs:
        faces = [f for f in (cmds.sets(sg, q=True) or []) if ".f[" in f]
        if not faces:
            info.append({"sg": sg, "n": 0, "cy": 0, "cz": 0})
            continue
        sample = faces[::max(1, len(faces) // 60)][:60]
        ys, zs = [], []
        for f in sample:
            try:
                bb = cmds.xform(f, q=True, ws=True, bb=True)
                ys.append((bb[1] + bb[4]) / 2.0)
                zs.append((bb[2] + bb[5]) / 2.0)
            except Exception:
                pass
        info.append({"sg": sg, "n": len(faces),
                     "cy": (sum(ys) / len(ys)) if ys else 0,
                     "cz": (sum(zs) / len(zs)) if zs else 0})

    total = sum(i["n"] for i in info) or 1
    head_y = ymin + h * 0.76
    foot_y = ymin + h * 0.12
    zmid = (zmin + zmax) / 2.0

    # 头部区域里，最靠前(z大)的槽 = 脸；其余头部槽 = 头发
    head = [i for i in info if i["cy"] >= head_y and i["n"] < total * 0.45]
    if head:
        face_sg = max(head, key=lambda i: i["cz"])["sg"]
    else:
        face_sg = max(info, key=lambda i: i["cy"])["sg"]
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


def import_char(key, path):
    """导入 FBX 并给所有新节点加 key_ 前缀（FBX 导入会忽略 namespace 参数）。"""
    before_j = set(cmds.ls(type="joint", long=True) or [])
    before_m = set(cmds.ls(type="mesh", long=True) or [])
    before_t = set(cmds.ls(type="transform", long=True) or [])

    cmds.file(path, i=True, ignoreVersion=True, ra=True, mergeNamespacesOnClash=False)

    new_j = [n for n in (cmds.ls(type="joint", long=True) or []) if n not in before_j]
    new_m = [n for n in (cmds.ls(type="mesh", long=True) or []) if n not in before_m]
    new_t = [n for n in (cmds.ls(type="transform", long=True) or []) if n not in before_t]

    # 先改 transform/joint（层级内改名不影响其他节点短名唯一性）
    for n in new_j + new_t:
        sn = n.split("|")[-1]
        if sn.startswith(key + "_"):
            continue
        try:
            cmds.rename(sn, key + "_" + sn)
        except Exception:
            pass

    # 重新定位 mesh
    meshes = []
    for n in (cmds.ls(type="mesh", long=True) or []):
        sn = n.split("|")[-1]
        if sn.startswith(key + "_") and not cmds.getAttr(n + ".intermediateObject"):
            meshes.append(sn)
    main = [m for m in meshes if cmds.listConnections(m, type="skinCluster")] or meshes
    if not main:
        raise RuntimeError("导入后找不到网格: " + key)
    tr = cmds.listRelatives(main[0], parent=True)

    # 骨架父级（带 ×100 缩放和 -90 旋转的那个 transform）
    root_j = key + "_Root"
    arm = cmds.listRelatives(root_j, parent=True)
    arm = arm[0] if arm else None
    grp = cmds.group(em=True, name="GRP_" + key)
    if arm:
        cmds.parent(arm, grp)          # Maya 默认保持世界变换
    return {"geo": tr[0] if tr else main[0], "mesh": main[0],
            "joints": len(new_j), "arm": arm, "grp": grp}


def place_seated(char, theta_deg, seat_radius=102):
    """把角色放到圆桌某方位并摆坐姿。theta_deg: 0=+X，270=远侧（-Z）"""
    a = math.radians(theta_deg)
    cx, cz = math.cos(a) * seat_radius, math.sin(a) * seat_radius
    grp = char["grp"]
    cmds.setAttr(grp + ".translate", cx, 0, cz)
    yaw = math.degrees(math.atan2(-math.cos(a), -math.sin(a)))
    cmds.setAttr(grp + ".rotateY", yaw)

    j = char["j"]
    for side in ("Left", "Right"):
        cmds.setAttr(j + side + "UpLeg.rotateX", -92)
        cmds.setAttr(j + side + "Leg.rotateX", 92)
        cmds.setAttr(j + side + "Foot.rotateX", -6)
    # 抬头：躯干直、颈略前伸、头抬起（模型 rest 本身偏低，必须补偿）
    cmds.setAttr(j + "Spine.rotateX", 2)
    cmds.setAttr(j + "Spine1.rotateX", 1)
    cmds.setAttr(j + "Neck.rotateX", -14)
    cmds.setAttr(j + "Head.rotateX", -12)
    # 手臂：左 -75 / 右 +75，前臂 ±90（实测手能落在桌面上）
    cmds.setAttr(j + "LeftArm.rotateX", -75)
    cmds.setAttr(j + "LeftArm.rotateZ", 0)
    cmds.setAttr(j + "LeftForeArm.rotateX", 90)
    cmds.setAttr(j + "RightArm.rotateX", 75)
    cmds.setAttr(j + "RightArm.rotateZ", 0)
    cmds.setAttr(j + "RightForeArm.rotateX", -90)
    return grp


def hip_joint(j):
    """髋参考：优先用 LeftUpLeg 的父级（真正的骨盆），再退回常见名。"""
    up = j + "LeftUpLeg"
    if cmds.objExists(up):
        p = cmds.listRelatives(up, parent=True)
        if p:
            return p[0]
    for cand in ("Hips", "LowerBody", "Bone"):
        if cmds.objExists(j + cand):
            return j + cand
    return j + "Root"


def fit_to_seat(char, hip_height=46.0):
    """按髋关节世界高度补偿外层组的 Y，使臀部刚好坐在座面上"""
    j = char["j"]
    hj = hip_joint(j)
    grp = char["grp"]
    cmds.refresh(force=True)
    hip = cmds.xform(hj, q=True, ws=True, t=True)
    dy = hip_height - hip[1]
    cur = cmds.getAttr(grp + ".translate")[0]
    cmds.setAttr(grp + ".translate", cur[0], cur[1] + dy, cur[2])
    cmds.refresh(force=True)
    return round(dy, 2)


# ============ 相机 ============

def make_cam(name, eye, aim, focal=85):
    cam = cmds.camera(name=name, focalLength=focal)[0]
    cmds.setAttr(cam + ".translate", *eye)
    loc = cmds.spaceLocator(name=name + "_aim")[0]
    cmds.setAttr(loc + ".translate", *aim)
    cmds.aimConstraint(loc, cam, aimVector=(0, 0, -1), upVector=(0, 1, 0),
                       worldUpType="vector", worldUpVector=(0, 1, 0))
    cmds.delete(loc)
    return cam


def render_to(path, w=854, h=480, frame=1):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    base = os.path.splitext(path)[0]
    for f in os.listdir(d):
        if f.startswith(os.path.basename(base)) and f.endswith(".png"):
            os.remove(os.path.join(d, f))
    cmds.playblast(frame=frame, format="image", filename=base, sequenceTime=0,
                   clearCache=1, viewer=0, showOrnaments=0, fp=4, percent=100,
                   widthHeight=[w, h], quality=100, compression="png")
    files = sorted([f for f in os.listdir(d) if f.startswith(os.path.basename(base))
                    and f.endswith(".png")])
    return os.path.join(d, files[0]) if files else None


# ============ 整体装配 ============

CHARS = {
    "Ma": {"fbx": "CH_Ma.fbx",
           "pal": {"hair": (0.34, 0.38, 0.48), "skin": (0.98, 0.84, 0.72),
                   "cloth": (0.62, 0.68, 0.78), "cloth2": (0.50, 0.56, 0.66),
                   "shoe": (0.30, 0.30, 0.34)}},
    "Huang": {"fbx": "CH_Huang.fbx",
              "pal": {"hair": (0.40, 0.30, 0.24), "skin": (0.99, 0.86, 0.74),
                      "cloth": (0.82, 0.40, 0.36), "cloth2": (0.68, 0.30, 0.27),
                      "shoe": (0.30, 0.30, 0.34)}},
    "Shiye": {"fbx": "CH_Shiye.fbx",
              "pal": {"hair": (0.38, 0.36, 0.36), "skin": (0.98, 0.83, 0.71),
                      "cloth": (0.76, 0.70, 0.58), "cloth2": (0.62, 0.56, 0.46),
                      "shoe": (0.30, 0.30, 0.34)}},
}


def build_all(render_check=None):
    cmds.file(new=True, force=True)
    setup_viewport()

    chars = {}
    for key, cfg in CHARS.items():
        info = import_char(key, os.path.join(ROOT, "models_fbx2", cfg["fbx"]))
        color_char_materials(info["geo"], cfg["pal"])
        chars[key] = {"root": key + "_Root", "geo": info["geo"], "grp": info["grp"],
                      "arm": info["arm"], "j": key + "_", "theta": SEAT_ANGLE[key],
                      "joints": info["joints"]}

    build_set()
    build_lights()

    for key, ch in chars.items():
        place_seated(ch, ch["theta"])
    for key, ch in chars.items():
        ch["dy"] = fit_to_seat(ch, 46.0)

    return chars


# ============================================================
# 室外庭院版布景与日光（覆盖上面的室内版）
# ============================================================

def build_set():
    """室外庭院：圆桌 + 椅子 + 背景房子 + 天空穹顶。没有棚子、没有蜡烛。"""
    grp = cmds.group(em=True, name="SET")
    mats = {
        "wood": new_material("SET_wood", (0.40, 0.22, 0.13)),
        "wood_dark": new_material("SET_wood_dark", (0.24, 0.14, 0.09)),
        "cloth": new_material("SET_cloth", (0.55, 0.16, 0.13)),
        "earth": new_material("SET_earth", (0.46, 0.38, 0.28)),
        "stone": new_material("SET_stone", (0.62, 0.58, 0.52)),
        "plaster": new_material("SET_plaster", (0.80, 0.74, 0.64)),
        "tile": new_material("SET_tile", (0.30, 0.30, 0.33)),
        "sky": new_material("SET_sky", (0.60, 0.75, 0.92)),
        "porcelain": new_material("SET_porcelain", (0.55, 0.54, 0.52)),
        "foliage": new_material("SET_foliage", (0.24, 0.36, 0.18)),
    }

    fl = cmds.polyPlane(w=1400, h=1400, sx=1, sy=1, name="SET_floor")[0]
    assign(fl, mats["earth"])
    cmds.parent(fl, grp)

    # 天空穹顶：反转法线，从内部看
    sky = cmds.polySphere(r=900, sx=24, sy=12, name="SET_sky")[0]
    cmds.setAttr(sky + ".scaleX", -1)
    sky_mat = cmds.shadingNode("surfaceShader", asShader=True, name="SET_sky_unlit")
    cmds.setAttr(sky_mat + ".outColor", 0.62, 0.76, 0.90, type="double3")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="SET_sky_unlitSG")
    cmds.connectAttr(sky_mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(sky, e=True, forceElement=sg)
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
        cx, cz = math.cos(a) * 102, math.sin(a) * 102
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
    for i, (x, z, r) in enumerate(((-300, -300, 70), (280, -320, 80))):
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

    # 假接触阴影（硬件渲染无阴影贴图，用暗盘顶替）
    sh_mat = new_material("SET_shadow", (0.12, 0.095, 0.075))
    sh = cmds.polyCylinder(r=150, h=0.4, sx=48, name="SET_contact_shadow")[0]
    cmds.move(0, 0.4, 0, sh)
    assign(sh, sh_mat)
    cmds.parent(sh, grp)

    return grp, mats


def build_lights():
    """自然日光：斜上方太阳 + 天空环境 + 地面反弹。"""
    grp = cmds.group(em=True, name="LIGHTS")
    sun = _tr(cmds.directionalLight(name="LGT_sun", intensity=2.10))
    cmds.setAttr(sun + ".color", 1.0, 0.955, 0.875, type="double3")
    cmds.setAttr(sun + ".rotate", 52, 34, 0)
    # 深度贴图阴影在本机硬件渲染下会把整个场景压成黑的，必须关掉
    try:
        cmds.setAttr(sun + ".useDepthMapShadows", 0)
        cmds.setAttr(sun + ".useRayTraceShadows", 0)
    except Exception:
        pass

    sky = _tr(cmds.ambientLight(name="LGT_sky", intensity=0.52))
    cmds.setAttr(sky + ".color", 0.70, 0.80, 0.96, type="double3")

    bounce = _tr(cmds.directionalLight(name="LGT_bounce", intensity=0.75))
    cmds.setAttr(bounce + ".color", 0.88, 0.76, 0.60, type="double3")
    cmds.setAttr(bounce + ".rotate", -58, 165, 0)

    for l in (sun, sky, bounce):
        cmds.parent(l, grp)
    return grp


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
        face_sg = min(head_slots, key=lambda i: i[1])[0]

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


def build_lights():
    """照抄 MayaTest：不建任何自定义灯，靠视口默认两盏灯。"""
    grp = cmds.group(em=True, name="LIGHTS")
    amb = _tr(cmds.ambientLight(name="LGT_amb", intensity=0.25))
    cmds.setAttr(amb + ".color", 0.75, 0.78, 0.85, type="double3")
    cmds.parent(amb, grp)
    return grp


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
