"""Preserved topology-budget experiment; does not establish visual acceptance."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cairn-hound-lab-articulation.blend'))
scene=bpy.context.scene;skin=bpy.data.objects['CairnHound_Lab_SkinnedMesh'];rig=bpy.data.objects['CairnHound_Rig']
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=None
for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
skin.data.calc_loop_triangles();before=len(skin.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);bpy.context.view_layer.objects.active=skin
mod=skin.modifiers.new('Budget experiment 45 percent','DECIMATE');mod.ratio=.45;mod.use_collapse_triangulate=True
while skin.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
bpy.ops.object.modifier_apply(modifier=mod.name)
skin.data.calc_loop_triangles();after=len(skin.data.loop_triangles)
assert after<before*.5 and all(v.groups for v in skin.data.vertices)
rig.animation_data.action=None
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab-budget.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=bpy.data.actions['Idle_BreathAndWatch'];scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab-budget.blend'))
cam=scene.camera;cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);cam.rotation_euler=(Vector((-.15,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=24;scene.render.resolution_percentage=100
scene.render.filepath=str(OUT/'hero-budget.png');bpy.ops.render.render(write_still=True)
(OUT/'BUDGET-REPORT.json').write_text(json.dumps({'beforeTriangles':before,'afterTriangles':after,'ratio':after/before,'vertices':len(skin.data.vertices),'bones':len(rig.data.bones),'actions':[a.name for a in bpy.data.actions],'unweightedVertices':sum(not v.groups for v in skin.data.vertices),'method':'Blender collapse decimation in rest pose before armature modifier','limitations':['Automatic reduction is not authored retopology.','UV seams, deformation, fur/armor detail and silhouette require independent comparison.','No runtime promotion or automatic LOD switching.']},indent=2)+'\n')
print('MESH BUDGET VARIANT COMPLETE')
