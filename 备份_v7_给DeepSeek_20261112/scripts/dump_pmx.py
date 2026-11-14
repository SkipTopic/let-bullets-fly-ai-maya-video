# -*- coding: utf-8 -*-
"""Dump bone/morph inventory of candidate PMX models via Blender + mmd_tools."""
import bpy
import sys
import json

ARGS = sys.argv[sys.argv.index('--') + 1:]
OUT = ARGS[0]
PMXS = ARGS[1:]

report = {}
try:
    bpy.ops.preferences.addon_enable(module='bl_ext.blender_org.mmd_tools')
except Exception as e:
    report['addon_error'] = str(e)

for pmx in PMXS:
    key = pmx.split('/')[-1].replace('.pmx', '')
    ent = {}
    try:
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.preferences.addon_enable(module='bl_ext.blender_org.mmd_tools')
        bpy.ops.mmd_tools.import_model(filepath=pmx, scale=0.08,
                                       types={'MESH', 'ARMATURE', 'MORPHS'},
                                       clean_model=False, log_level='ERROR')
        arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        ent['armatures'] = [a.name for a in arms]
        ent['n_meshes'] = len(meshes)
        if arms:
            bones = [b.name for b in arms[0].data.bones]
            ent['n_bones'] = len(bones)
            # finger bones per hand (MMD: 親指/人指/中指/薬指/小指)
            lfin = sum(1 for b in bones if any(k in b for k in ('親指', '人指', '中指', '薬指', '小指')) and b.endswith('.L'))
            rfin = sum(1 for b in bones if any(k in b for k in ('親指', '人指', '中指', '薬指', '小指')) and b.endswith('.R'))
            ent['finger_bones_L'] = lfin
            ent['finger_bones_R'] = rfin
            ent['sample_bones'] = bones[:12]
            ent['has_arm_L'] = any(b.startswith('腕.L') for b in bones)
        sk = set()
        for m in meshes:
            if m.data.shape_keys:
                for kb in m.data.shape_keys.key_blocks:
                    sk.add(kb.name)
        ent['shape_keys'] = sorted(sk)
        ent['has_blink_jp'] = any(k in sk for k in ('まばたき', 'ウィンク', '目閉じ'))
        ent['n_verts'] = sum(len(m.data.vertices) for m in meshes)
        ent['ok'] = True
    except Exception:
        import traceback
        ent['ok'] = False
        ent['error'] = traceback.format_exc()
    report[key] = ent

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print('DUMP_DONE')
