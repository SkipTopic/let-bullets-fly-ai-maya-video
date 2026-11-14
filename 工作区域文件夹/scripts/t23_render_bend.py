import bpy, os, json, math
from mathutils import Vector

BASE = r"C:\Users\admin\Desktop\MayaProject\让子弹飞分镜测试\工作区域文件夹"
OUT = os.path.join(BASE, "_审片")
LOG = os.path.join(BASE, "logs", "bend_render.json")

TESTS = [
    ("OLD_Ma", os.path.join(BASE, "models_fbx2", "CH_Ma.fbx")),
    ("NEW_Male", os.path.join(BASE, "models_new", "NH_MaleM_140", "Model", "NH_MaleM_140.fbx")),
]

rep = {}

for tag, path in TESTS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not os.path.exists(path):
        rep[tag] = {"error": "missing"}
        continue
    bpy.ops.import_scene.fbx(filepath=path)

    arm = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)
    mesh = next((o for o in bpy.context.scene.objects if o.type == 'MESH'), None)
    if not arm or not mesh:
        rep[tag] = {"error": "missing arm/mesh"}
        continue

    names = [b.name for b in arm.data.bones]

    def find(keys):
        for k in keys:
            for n in names:
                if k.lower() == n.lower():
                    return n
        for k in keys:
            for n in names:
                if k.lower() in n.lower():
                    return n
        return None

    upper = find(["Bip001LUpperArm", "LUpperArm", "UpperArm_L", "upperarm_l", "LeftArm", "腕.L"])
    fore = find(["Bip001LForearm", "LForearm", "LowerArm_L", "lowerarm_l", "LeftForeArm", "ひじ.L"])
    rep[tag] = {"upper": upper, "fore": fore}
    if not upper or not fore:
        rep[tag]["error"] = "arm bones not found"
        continue

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    arm.pose.bones[upper].rotation_mode = 'XYZ'
    arm.pose.bones[fore].rotation_mode = 'XYZ'
    arm.pose.bones[upper].rotation_euler = (0, 0, math.radians(-65))
    arm.pose.bones[fore].rotation_euler = (math.radians(-90), 0, 0)
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()

    # 世界包围盒 -> 相机定位
    dg = bpy.context.evaluated_depsgraph_get()
    me = mesh.evaluated_get(dg).to_mesh()
    cos = [mesh.matrix_world @ v.co for v in me.vertices]
    mesh.evaluated_get(dg).to_mesh_clear()
    xs = [c.x for c in cos]; ys = [c.y for c in cos]; zs = [c.z for c in cos]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    cz = (min(zs) + max(zs)) / 2

    cam_d = bpy.data.cameras.new("C")
    cam_d.lens = 70
    cam = bpy.data.objects.new("C", cam_d)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (cx + 0.55, cy - 0.85, cz + 0.28)
    tgt = Vector((cx + 0.12, cy, cz + 0.18))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam

    sun = bpy.data.lights.new("S", type='SUN')
    sun.energy = 4.0
    so = bpy.data.objects.new("S", sun)
    bpy.context.scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(20), 0)

    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 24
    sc.render.resolution_x = 520
    sc.render.resolution_y = 420
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.06, 1)
    sc.render.filepath = os.path.join(OUT, "BN_%s.png" % tag)
    bpy.ops.render.render(write_still=True)

    bb = [round(v, 2) for v in (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))]
    rep[tag].update({"bbox": bb, "height": round(max(zs) - min(zs), 2), "png": sc.render.filepath})

json.dump(rep, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
