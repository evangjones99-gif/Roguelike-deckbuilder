"""Bake the procedural model shaders with Blender; no raster input editing.
Preserves the original study and creates a portable-material variant.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cairn-hound-lab.blend'))
skin=bpy.data.objects['CairnHound_Lab_SkinnedMesh'];rig=bpy.data.objects['CairnHound_Rig'];scene=bpy.context.scene
rig.animation_data.action=None
for tr in rig.animation_data.nla_tracks:tr.mute=True
for p in rig.pose.bones:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(1,1,1)
scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);bpy.context.view_layer.objects.active=skin
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
images={}
for kind,resolution in [('basecolor',2048),('normal',2048)]:
    im=bpy.data.images.new('CairnHound_'+kind,width=resolution,height=resolution,alpha=False)
    if kind=='normal':im.colorspace_settings.name='Non-Color'
    images[kind]=im
    for mat in skin.data.materials:
        nodes=mat.node_tree.nodes
        node=nodes.new('ShaderNodeTexImage');node.name='Bake_'+kind;node.image=im
        for n in nodes:n.select=False
        node.select=True;nodes.active=node
    bpy.ops.object.bake(type='DIFFUSE' if kind=='basecolor' else 'NORMAL',pass_filter={'COLOR'} if kind=='basecolor' else set(),margin=4)
    im.filepath_raw=str(OUT/('cairn-hound-'+kind+'.png'));im.file_format='PNG';im.save()
for mat in skin.data.materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    for socket in ['Base Color','Normal']:
        for link in list(p.inputs[socket].links):links.remove(link)
    links.new(nodes['Bake_basecolor'].outputs['Color'],p.inputs['Base Color'])
    normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1
    links.new(nodes['Bake_normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],p.inputs['Normal'])
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab-pbr.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=bpy.data.actions['Idle_BreathAndWatch'];scene.frame_set(1)
scene.render.resolution_percentage=100;scene.cycles.samples=32
cam=scene.camera;cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);cam.rotation_euler=(Vector((-.15,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab-pbr.blend'))
scene.render.filepath=str(OUT/'hero-baked-pbr.png');bpy.ops.render.render(write_still=True)
(OUT/'PBR-REPORT.json').write_text(json.dumps({'status':'portable-material technical variant; art bar unfulfilled','generatedBy':'Blender diffuse-color and tangent-normal bake from original geometry/shader nodes','inputRasterEdited':False,'maps':[{'kind':k,'dimensions':[im.size[0],im.size[1]],'colorspace':im.colorspace_settings.name} for k,im in images.items()],'uvLayers':len(skin.data.uv_layers),'limitations':['Automatic UV unwrap has many islands and needs seam/texel-density review.','No metallic/roughness maps; per-material factors only.','No runtime integration, LODs or production anatomical sculpt.']},indent=2)+'\n')
print('PORTABLE PBR EXPORT COMPLETE')
