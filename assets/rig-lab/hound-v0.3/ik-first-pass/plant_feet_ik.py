"""Preserved planted-foot experiment using Blender IK, baked for glTF.
Four nondeforming control bones keep targets/action switching within one rig.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'cairn-hound-lab-articulation.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['CairnHound_Rig'];skin=bpy.data.objects['CairnHound_Lab_SkinnedMesh']
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=None
for p in rig.pose.bones:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(1,1,1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for kind in ['fore','hind']:
    for side in ['L','R']:
        source=rig.data.edit_bones[f'{kind}.paw.{side}'];c=rig.data.edit_bones.new(f'ik.{kind}.{side}');c.head=source.head;c.tail=source.tail;c.parent=rig.data.edit_bones['root'];c.use_deform=False
bpy.ops.object.mode_set(mode='POSE')
controls={};constraints={}
for kind in ['fore','hind']:
    for side in ['L','R']:
        name=f'ik.{kind}.{side}';controls[name]=rig.pose.bones[name]
        lower=rig.pose.bones[f'{kind}.lower.{side}'];ik=lower.constraints.new('IK');ik.name='Planted wrist/hock';ik.target=rig;ik.subtarget=name;ik.chain_count=2;ik.use_stretch=False
        # Restrict solver to the rest-space sagittal hinge axis.
        for part in ['upper','lower']:
            pb=rig.pose.bones[f'{kind}.{part}.{side}'];axis=rig.data.bones[pb.name].matrix_local.to_3x3().inverted()@Vector((0,1,0));free=max(range(3),key=lambda i:abs(axis[i]))
            pb.lock_ik_x=free!=0;pb.lock_ik_y=free!=1;pb.lock_ik_z=free!=2;pb.ik_stretch=0
        paw=rig.pose.bones[f'{kind}.paw.{side}'];rot=paw.constraints.new('COPY_ROTATION');rot.name='Maintain pad orientation';rot.target=rig;rot.subtarget=name;rot.target_space='WORLD';rot.owner_space='WORLD'
        constraints[name]=(ik,rot)
bpy.ops.object.mode_set(mode='OBJECT')
def interp(f,keys):
    for (a,v),(b,w) in zip(keys,keys[1:]):
        if a<=f<=b:return v+(w-v)*(f-a)/(b-a)
    return keys[-1][1]
root=rig.pose.bones['root'];actions=list(bpy.data.actions);rootbasis=rig.data.bones['root'].matrix_local.to_3x3();errors={};foot_ranges={}
for act in actions:
    rig.animation_data.action=act;start,end=map(int,act.frame_range);death='Death_' in act.name
    for frame in range(start,end+1):
        scene.frame_set(frame)
        if not death:
            if 'Anticipation_' in act.name:x=interp(frame,[(1,0),(8,-.10),(end,-.10)]);z=interp(frame,[(1,0),(8,-.12),(end,-.12)])
            elif 'Lunge_' in act.name:x=interp(frame,[(1,0),(6,-.10),(12,.30),(18,.08),(end,0)]);z=interp(frame,[(1,0),(6,-.12),(12,.035),(18,-.04),(end,0)])
            elif 'Hit_' in act.name:x=interp(frame,[(1,0),(5,-.14),(10,-.04),(end,0)]);z=interp(frame,[(1,0),(5,-.06),(end,0)])
            else:x=0;z=0
            root.location=(x,z,0);root.keyframe_insert('location',frame=frame,group='root')
        worldroot=rootbasis@root.location
        for name,target in controls.items():
            offset=Vector((0,0,0))
            if 'Lunge_' in act.name and '.fore.' in name:
                offset.x=interp(frame,[(1,0),(6,0),(12,.35),(18,.12),(end,0)])
                offset.z=interp(frame,[(1,0),(6,0),(12,.15),(18,.07),(end,0)])
            basis=rig.data.bones[name].matrix_local.to_3x3();target.location=basis.inverted()@(offset-worldroot);target.keyframe_insert('location',frame=frame,group=name)
            for c in constraints[name]:c.influence=0 if death else 1;c.keyframe_insert('influence',frame=frame)
    measures=[];feet={n:[] for n in controls}
    for frame in range(start,end+1):
        scene.frame_set(frame)
        if not death:
            for name in controls:
                kind,side=name.split('.')[1:];a=rig.pose.bones[f'{kind}.lower.{side}'].tail;b=rig.pose.bones[name].head;measures.append((a-b).length)
                feet[name].append(tuple(rig.pose.bones[f'{kind}.digits.{side}'].head))
    errors[act.name]=max(measures,default=0)
    foot_ranges[act.name]={n:[max(c[i] for c in positions)-min(c[i] for c in positions) for i in range(3)] for n,positions in feet.items() if positions}
rig.animation_data.action=None
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.object.select_all(action='DESELECT');skin.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab-ik.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True,export_force_sampling=True)
for tr in rig.animation_data.nla_tracks:tr.mute=True
rig.animation_data.action=next(a for a in actions if 'Idle_' in a.name);scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab-ik.blend'))
cam=scene.camera;cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);cam.rotation_euler=(Vector((-.15,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler();scene.cycles.samples=24;scene.render.resolution_percentage=100
for frag,frame,name in [('Anticipation_',13,'anticipation-ik.png'),('Lunge_',12,'lunge-ik.png')]:
    rig.animation_data.action=next(a for a in actions if frag in a.name);scene.frame_set(frame);scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
(OUT/'IK-REPORT.json').write_text(json.dumps({'bones':len(rig.data.bones),'deformingBones':sum(b.use_deform for b in rig.data.bones),'method':'Two-segment IK wrist/hock targets and world-space pad orientation; four nondeforming target controls keyed in each rig action; exported sampled transforms','maximumTargetDistanceByAction':errors,'digitHeadXYZRangesByAction':foot_ranges,'limitations':['Solver/pivot/deformation quality require independent motion review.','Death uses the preserved non-IK folded variant.','Creature sculpt/material silhouette still below production realism.','No runtime integration or acceptance.']},indent=2)+'\n')
print('PLANTED FOOT IK EXPERIMENT COMPLETE')
