"""Preserved technical animation variant: correct measured floor penetration.
This is whole-actor contact projection, not IK or physically accurate falling.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cairn-hound-lab-pbr.blend'))
rig=bpy.data.objects['CairnHound_Rig'];skin=bpy.data.objects['CairnHound_Lab_SkinnedMesh'];scene=bpy.context.scene
for tr in rig.animation_data.nla_tracks:tr.mute=True
root=rig.pose.bones['root'];basis=rig.data.bones['root'].matrix_local.to_3x3()
before={};after={};actions=list(bpy.data.actions)
def bounds():
    ev=skin.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();co=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
    return min(p.z for p in co),(.5*(min(p.y for p in co)+max(p.y for p in co)))
for action in actions:
    rig.animation_data.action=action;start,end=map(int,action.frame_range);samples=[];zs=[]
    # Read every original frame before modifying interpolation.
    for frame in range(start,end+1):
        scene.frame_set(frame);z,cy=bounds();zs.append(z)
        worlddelta=Vector((0,-cy if 'Death_' in action.name else 0,.01-z))
        correction=basis.inverted()@worlddelta
        samples.append((frame,root.location.copy()+correction))
    before[action.name]=min(zs)
    for frame,location in samples:
        root.location=location;root.keyframe_insert('location',frame=frame,group='root')
    measured=[]
    for frame in range(start,end+1):scene.frame_set(frame);measured.append(bounds()[0])
    after[action.name]=min(measured)
    assert after[action.name]>=.009
rig.animation_data.action=None
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab-contact.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=next(a for a in actions if 'Idle_' in a.name);scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab-contact.blend'))
cam=scene.camera;cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);cam.rotation_euler=(Vector((-.15,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_percentage=100;scene.cycles.samples=24
for fragment,frame,name in [('Anticipation_',13,'anticipation-contact.png'),('Lunge_',12,'lunge-contact.png'),('Death_',41,'death-contact.png')]:
    rig.animation_data.action=next(a for a in actions if fragment in a.name);scene.frame_set(frame);scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
(OUT/'CONTACT-REPORT.json').write_text(json.dumps({'method':'Sampled whole-actor floor projection and death lateral recentering; not IK','minimumZBefore':before,'minimumZAfter':after,'limitations':['Ground clearance corrected, but planted feet can still slide.','Projection can cancel crouch depth instead of bending limbs.','Root trajectory/death timing need artist motion review.','Asset still fails realistic-creature art bar.']},indent=2)+'\n')
print('MEASURED CONTACT VARIANT COMPLETE')
