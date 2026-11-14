import bpy, json, os

SRC = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_raw"
OUT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\logs\bones_raw.json"
report = {}

targets = {
    "CH_Ma": os.path.join(SRC, "makoto_yuki", "Makoto Yuki.pmx"),
    "CH_Huang": os.path.join(SRC, "aragaki_shinjiro", "Aragaki Shinjiro.pmx"),
    "CH_Shiye": os.path.join(SRC, "junpei_iori", "Junpei Iori.pmx"),
}

for key, pmx in targets.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(pmx):
        report[key] = {"error": "not found", "path": pmx}
        continue
    for mod in ("bl_ext.blender_org.mmd_tools", "mmd_tools"):
        try:
            bpy.ops.preferences.addon_enable(module=mod)
            break
        except Exception:
            pass
    bpy.ops.mmd_tools.import_model(filepath=pmx, scale=0.08, types={'ARMATURE', 'MESH'})
    arm = None
    for ob in bpy.context.scene.objects:
        if ob.type == 'ARMATURE':
            arm = ob
            break
    bones = []
    if arm:
        for b in arm.data.bones:
            bones.append({
                "name": b.name,
                "parent": b.parent.name if b.parent else None,
                "head": [round(v, 4) for v in b.head_local],
                "tail": [round(v, 4) for v in b.tail_local],
            })
        report[key] = {
            "armature": arm.name,
            "obj_scale": [round(v, 4) for v in arm.scale],
            "obj_rot": [round(v, 3) for v in arm.rotation_euler],
            "bones": bones,
            "bone_count": len(bones),
        }
    else:
        report[key] = {"error": "no armature"}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print("WROTE", OUT)
