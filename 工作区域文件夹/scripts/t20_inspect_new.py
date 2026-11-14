import bpy, json, os
from mathutils import Vector

BASE = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\models_new"
OUT = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹\logs\newmodels.json"

FILES = {
    "NH_MaleM": os.path.join(BASE, "NH_MaleM_140", "Model", "NH_MaleM_140.fbx"),
    "Himeko": os.path.join(BASE, "Art_NPC_Full_W5_Lady_HimekoYouth",
                           "Art_NPC_Full_W5_Lady_HimekoYouth.fbx"),
    "JXR_ASZ": os.path.join(BASE, "JXR", "ASZ.fbx"),
}

rep = {}
for key, path in FILES.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(path):
        rep[key] = {"error": "missing"}
        continue
    try:
        bpy.ops.import_scene.fbx(filepath=path)
    except Exception as e:
        rep[key] = {"error": repr(e)}
        continue

    d = {"file": os.path.basename(path),
         "size_mb": round(os.path.getsize(path) / 1048576, 1),
         "armatures": [], "meshes": [], "images": []}

    for ob in bpy.context.scene.objects:
        if ob.type == 'ARMATURE':
            bones = [b.name for b in ob.data.bones]
            d["armatures"].append({
                "name": ob.name, "bones": len(bones),
                "ws_scale": [round(v, 4) for v in ob.matrix_world.to_scale()],
                "sample": bones[:28],
                "has_ue_names": any("upperarm" in b.lower() or "lowerarm" in b.lower()
                                    for b in bones),
                "has_mmd_names": any(b in ("腕.L", "ひじ.L") for b in bones),
            })
        elif ob.type == 'MESH':
            mw = ob.matrix_world
            bb = [mw @ Vector(c) for c in ob.bound_box]
            zs = [v.z for v in bb]
            ys = [v.y for v in bb]
            d["meshes"].append({
                "name": ob.name, "verts": len(ob.data.vertices),
                "polys": len(ob.data.polygons),
                "mods": [m.type for m in ob.modifiers],
                "vgroups": len(ob.vertex_groups),
                "height": round(max(zs) - min(zs), 2),
                "height_y": round(max(ys) - min(ys), 2),
                "shape_keys": [k.name for k in ob.data.shape_keys.key_blocks][:8] if ob.data.shape_keys else [],
            })
    d["images"] = [i.filepath.split("\\")[-1].split("/")[-1] for i in bpy.data.images][:8]
    rep[key] = d

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
