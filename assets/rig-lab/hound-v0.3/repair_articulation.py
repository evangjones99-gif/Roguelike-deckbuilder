"""Repair joint-axis assumptions using bone rest-space transforms.
Preserves prior variants; remains a technical, non-production motion study.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Quaternion
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cairn-hound-lab-contact.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['CairnHound_Rig'];skin=bpy.data.objects['CairnHound_Lab_SkinnedMesh'];root=rig.pose.bones['root']
for tr in rig.animation_data.nla_tracks:tr.mute=True
actions=list(bpy.data.actions)
def hinge(name,angle):
    axis=rig.data.bones[name].matrix_local.to_3x3().inverted()@Vector((0,1,0))
    rig.pose.bones[name].rotation_euler=Quaternion(axis.normalized(),angle).to_euler('XYZ')
def minz():
    ev=skin.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();z=min((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear();return z
def interpolate(f,keys):
    for (a,v),(b,w) in zip(keys,keys[1:]):
        if a<=f<=b:return v+(w-v)*(f-a)/(b-a)
    return keys[-1][1]
clearance={}
for act in actions:
    rig.animation_data.action=act;start,end=map(int,act.frame_range)
    if 'Lunge_' in act.name:keys=[(1,0),(6,.10),(12,.36),(18,.16),(end,0)]
    elif 'Anticipation_' in act.name:keys=[(1,0),(8,.10),(end,.10)]
    elif 'Death_' in act.name:keys=[(1,0),(9,.02),(23,.17),(end,.17)]
    elif 'Hit_' in act.name:keys=[(1,0),(5,.09),(10,.025),(end,0)]
    else:keys=[(1,0),(end,0)]
    for frame in range(start,end+1):
        scene.frame_set(frame);hinge('jaw',interpolate(frame,keys));rig.pose.bones['jaw'].keyframe_insert('rotation_euler',frame=frame,group='jaw')
        if 'Death_' in act.name:
            t=max(0,min(1,(frame-9)/14))
            for side in ['L','R']:
                for name,angle in [('fore.upper',.55),('fore.lower',-.75),('hind.upper',-.45),('hind.lower',.65)]:
                    bn=name+'.'+side;hinge(bn,angle*t);rig.pose.bones[bn].keyframe_insert('rotation_euler',frame=frame,group=bn)
    samples=[]
    for frame in range(start,end+1):
        scene.frame_set(frame);z=minz();delta=rig.data.bones['root'].matrix_local.to_3x3().inverted()@Vector((0,0,.01-z));samples.append((frame,root.location.copy()+delta))
    for frame,loc in samples:root.location=loc;root.keyframe_insert('location',frame=frame,group='root')
    zz=[]
    for frame in range(start,end+1):scene.frame_set(frame);zz.append(minz())
    clearance[act.name]=min(zz);assert min(zz)>.009
rig.animation_data.action=None
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab-articulation.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=next(a for a in actions if 'Idle_' in a.name);scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab-articulation.blend'))
cam=scene.camera;cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);cam.rotation_euler=(Vector((-.15,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=24;scene.render.resolution_percentage=100
for fragment,frame,name in [('Lunge_',12,'lunge-articulation.png'),('Death_',41,'death-articulation.png')]:
    rig.animation_data.action=next(a for a in actions if fragment in a.name);scene.frame_set(frame);scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
(OUT/'ARTICULATION-REPORT.json').write_text(json.dumps({'method':'Jaw and folded-limb hinge axes transformed from anatomical rest-space sagittal axis into each bone local space','minimumZAllFrames':clearance,'limitations':['Whole-actor contact projection remains; no planted-foot IK.','Death pose and lunge are author-created approximations and need independent motion critique.','Original anatomical/art deficiencies remain.']},indent=2)+'\n')
print('JOINT AXIS REPAIR COMPLETE')
