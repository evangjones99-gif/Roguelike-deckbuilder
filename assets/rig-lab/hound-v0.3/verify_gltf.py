"""Independent import check of the exported artifact, not a production acceptance test."""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
asset=OUT/(args[0] if args else 'cairn-hound-lab.glb')
prefix=args[1] if len(args)>1 else 'gltf-roundtrip'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(asset))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
print('IMPORTED OBJECTS',[(o.name,o.type) for o in bpy.context.scene.objects])
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o not in meshes:o.hide_render=True
assert len(meshes)==1 and len(rigs)==1
rig=rigs[0];mesh=meshes[0]
assert len(rig.data.bones) in (28,32)
acts=list(bpy.data.actions);assert len(acts)==5
assert all(v.groups for v in mesh.data.vertices)
for track in rig.animation_data.nla_tracks:track.mute=True
poses={}
for a in acts:
    rig.animation_data.action=a;minimum=[]
    for frame in range(int(a.frame_range[0]),int(a.frame_range[1])+1):
        bpy.context.scene.frame_set(frame)
        ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        coords=[ev.matrix_world@v.co for v in me.vertices];minimum.append(min(p.z for p in coords));ev.to_mesh_clear()
    poses[a.name]={'endFrame':int(a.frame_range[1]),'minimumZ':minimum[-1],'minimumZAllFrames':min(minimum)}
idle=next(a for a in acts if 'Idle_' in a.name);rig.animation_data.action=idle
scene=bpy.context.scene;scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=False
scene.render.resolution_x=880;scene.render.resolution_y=624;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Verification world');scene.world.color=(.035,.035,.035)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));floor=bpy.context.object
mat=bpy.data.materials.new('Verification slate');mat.diffuse_color=(.025,.032,.036,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.025,.032,.036,1);floor.data.materials.append(mat)
def aim(o):o.rotation_euler=(Vector((-.15,0,1.12))-o.location).to_track_quat('-Z','Y').to_euler()
for name,pos,power,col,size in [('Key',(1.5,-3.5,5),620,(.65,.78,1),4),('Fill',(1,4,3),300,(.75,.82,.87),3),('Rim',(-3,1.8,3.2),850,(1,.48,.22),3)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=col;d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;aim(o)
d=bpy.data.cameras.new('Imported GLB camera');d.type='ORTHO';d.ortho_scale=5.2;cam=bpy.data.objects.new('Imported GLB camera',d);scene.collection.objects.link(cam);cam.location=(-.15+6*math.cos(-.85),6*math.sin(-.85),3.3);aim(cam);scene.camera=cam
scene.render.filepath=str(OUT/(prefix+'.png'));bpy.ops.render.render(write_still=True)
report={'asset':asset.name,'importSucceeded':True,'bones':len(rig.data.bones),'actions':[a.name for a in acts],'skinnedVertices':len(mesh.data.vertices),'unweightedVertices':sum(not v.groups for v in mesh.data.vertices),'endPoseBounds':poses,'limitations':'Import and structure checks only; no engine integration or independent quality acceptance.'}
(OUT/(prefix+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
