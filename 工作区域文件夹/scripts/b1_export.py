"""PMX -> 干净 FBX：坐标系、缩放、骨名、IK 全部在这里处理掉，Maya 只负责摆姿势。"""
import bpy, os, json

SRC = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_raw"
DST = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_fbx2"
os.makedirs(DST, exist_ok=True)

TARGETS = {
    "CH_Ma": os.path.join(SRC, "makoto_yuki", "Makoto Yuki.pmx"),
    "CH_Huang": os.path.join(SRC, "aragaki_shinjiro", "Aragaki Shinjiro.pmx"),
    "CH_Shiye": os.path.join(SRC, "junpei_iori", "Junpei Iori.pmx"),
}

MAP = {
    "全ての親": "Root", "センター": "Center", "グルーブ": "Groove",
    "下半身": "LowerBody", "上半身": "Spine", "上半身2": "Spine1",
    "首": "Neck", "頭": "Head", "両目": "Eyes", "左目": "LeftEye", "右目": "RightEye",
}
SIDE = {"L": "Left", "R": "Right"}
LIMB = {
    "肩": "Shoulder", "腕": "Arm", "腕捩": "ArmTwist", "ひじ": "ForeArm",
    "手捩": "HandTwist", "手首": "Hand",
    "足": "UpLeg", "ひざ": "Leg", "足首": "Foot", "つま先": "ToeBase",
    "足D": "UpLegD", "ひざD": "LegD", "足首D": "FootD",
    "人指": "Index", "中指": "Middle", "小指": "Pinky", "薬指": "Ring", "親指": "Thumb",
}
NUM = {"０": "0", "１": "1", "２": "2", "３": "3", "４": "4"}


def to_ascii(name):
    if name in MAP:
        return MAP[name]
    base, side = name, None
    if name.endswith(".L"):
        base, side = name[:-2], "L"
    elif name.endswith(".R"):
        base, side = name[:-2], "R"
    base = base.replace(".", "_")
    # 长键优先，避免 "腕" 抢先匹配 "腕捩"
    for jp in sorted(LIMB.keys(), key=len, reverse=True):
        if base.startswith(jp):
            en = LIMB[jp]
            rest = base[len(jp):]
            for k, v in NUM.items():
                rest = rest.replace(k, v)
            rest = "".join(ch for ch in rest if ch.isascii() and ch.isalnum())
            core = en + rest
            return (SIDE[side] + core) if side else core
    # 兜底：保留可读 ASCII
    out = []
    for ch in base:
        if ch.isascii() and (ch.isalnum() or ch == "_"):
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out).strip("_") or "Bone"
    return (SIDE[side] + "_" + s) if side else s


report = {}
for key, pmx in TARGETS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for mod in ("bl_ext.blender_org.mmd_tools", "mmd_tools"):
        try:
            bpy.ops.preferences.addon_enable(module=mod)
            break
        except Exception:
            pass
    if not os.path.exists(pmx):
        report[key] = {"error": "missing", "path": pmx}
        continue

    bpy.ops.mmd_tools.import_model(filepath=pmx, scale=0.08, types={'ARMATURE', 'MESH'})
    arm = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not arm:
        report[key] = {"error": "no armature"}
        continue

    # 1) 清掉所有约束（MMD IK 走约束，Maya 里不需要）
    for pb in arm.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)

    # 2) 删除 IK 骨
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    ik_bones = [b for b in arm.data.bones if "ＩＫ" in b.name or b.name.endswith("IK")]
    for b in ik_bones:
        try:
            arm.data.edit_bones.remove(arm.data.edit_bones[b.name])
        except Exception:
            pass

    # 3) 重命名（保证唯一）
    used = {}
    rename = {}
    for b in arm.data.edit_bones:
        new = to_ascii(b.name)
        if new in used:
            used[new] += 1
            new = "%s_%d" % (new, used[new])
        else:
            used[new] = 0
        rename[b.name] = new
    for b in arm.data.edit_bones:
        b.name = rename[b.name]
    bpy.ops.object.mode_set(mode='OBJECT')

    # 4) 应用对象级变换，确保导出不带脏矩阵
    for ob in [arm] + meshes:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # 5) 导出：global_scale=100 → Maya 里 1.75m 变 175cm
    out = os.path.join(DST, key + ".fbx")
    for ob in bpy.context.scene.objects:
        ob.select_set(ob.type in {'ARMATURE', 'MESH'})
    bpy.ops.export_scene.fbx(
        filepath=out,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Z', axis_up='Y',
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=False,
        add_leaf_bones=False,
        bake_anim=False,
        mesh_smooth_type='OFF',
        primary_bone_axis='Y', secondary_bone_axis='X',
    )

    b = [{"name": x.name, "parent": x.parent.name if x.parent else None}
         for x in arm.data.bones]
    report[key] = {
        "fbx": out,
        "size_mb": round(os.path.getsize(out) / 1048576, 2),
        "bone_count": len(b),
        "renames": rename,
        "bones": b,
        "mesh_count": len(meshes),
    }

with open(r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\logs\b1_export.json",
          "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print("DONE")
