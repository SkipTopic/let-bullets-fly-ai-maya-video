import bpy, json, sys, os
from mathutils import Vector

OUT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\logs\fbx_inspect.json"
files = [
    r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_fbx\CH_Ma.fbx",
    r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_fbx\CH_Huang.fbx",
    r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_fbx\CH_Shiye.fbx",
]

report = {}
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=f)
    name = os.path.basename(f)
    info = {"objects": [], "armatures": [], "meshes": []}

    for ob in bpy.context.scene.objects:
        info["objects"].append({
            "name": ob.name, "type": ob.type,
            "loc": [round(v, 3) for v in ob.location],
            "rot": [round(v, 3) for v in ob.rotation_euler],
            "scale": [round(v, 4) for v in ob.scale],
            "parent": ob.parent.name if ob.parent else None,
        })
        if ob.type == 'ARMATURE':
            mw = ob.matrix_world
            info["armatures"].append({
                "name": ob.name,
                "bone_count": len(ob.data.bones),
                "matrix_world_scale": [round(v, 4) for v in mw.to_scale()],
                "matrix_world_rot_deg": [round(v, 2) for v in [a * 57.2958 for a in mw.to_euler()]],
                "head_bone_z": None,
                "bones_sample": [b.name for b in ob.data.bones][:25],
            })
        if ob.type == 'MESH':
            mw = ob.matrix_world
            bb = [mw @ Vector(c) for c in ob.bound_box]
            xs = [v.x for v in bb]; ys = [v.y for v in bb]; zs = [v.z for v in bb]
            info["meshes"].append({
                "name": ob.name,
                "verts": len(ob.data.vertices),
                "polys": len(ob.data.polygons),
                "scale": [round(v, 4) for v in ob.scale],
                "matrix_world_scale": [round(v, 4) for v in mw.to_scale()],
                "world_bbox_min": [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2)],
                "world_bbox_max": [round(max(xs), 2), round(max(ys), 2), round(max(zs), 2)],
                "shape_keys": [k.name for k in ob.data.shape_keys.key_blocks] if ob.data.shape_keys else [],
                "vgroups": len(ob.vertex_groups),
                "modifiers": [m.type for m in ob.modifiers],
                "materials": [m.name for m in ob.data.materials if m],
            })
    report[name] = info

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print("WROTE", OUT)
