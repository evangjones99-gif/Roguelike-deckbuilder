"""Original procedural creature/rig study. Run with Blender 4.3+ --background --python.
Geometry/shaders only; does not edit raster inputs or replace runtime assets.
"""
import bpy, math, json, hashlib, shutil, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/rig-lab/hound-v0.3'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for db in list(bpy.data.actions): bpy.data.actions.remove(db)
parts = []

def material(name, color, roughness, metallic=0, noise=8, bump=.11):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness; p.inputs['Metallic'].default_value=metallic
    tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=noise; tex.inputs['Detail'].default_value=3
    bn=n.new('ShaderNodeBump'); bn.inputs['Strength'].default_value=bump; bn.inputs['Distance'].default_value=.05
    m.node_tree.links.new(tex.outputs['Fac'],bn.inputs['Height']); m.node_tree.links.new(bn.outputs['Normal'],p.inputs['Normal'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[1].position=.78
    ramp.color_ramp.elements[0].color=(*(c*.50 for c in color),1)
    ramp.color_ramp.elements[1].color=(*(c*1.25 for c in color),1)
    m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    return m

hide=material('Scarred charcoal hide',(.038,.047,.049),.86,noise=11,bump=.20)
muscle=material('Dry exposed sinew',(.11,.055,.042),.82,noise=18,bump=.13)
bone=material('Aged mineralized bone',(.30,.25,.18),.82,noise=9,bump=.23)
darkbone=material('Sooted horn',(.09,.085,.073),.68,noise=14,bump=.10)
scar=material('Healed scar tissue',(.24,.10,.077),.92,noise=12,bump=.08)
iron=material('Worn binding iron',(.12,.145,.15),.56,.67,noise=12,bump=.12)
eye=material('Low ember eye',(.37,.10,.027),.3)
p=eye.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(.55,.12,.025,1); p.inputs['Emission Strength'].default_value=.8

def mesh(name, verts, faces, mat, weights):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(mat)
    for poly in me.polygons: poly.use_smooth=True
    groups={}
    for idx,w in enumerate(weights):
        for bn,value in w.items():
            if bn not in groups: groups[bn]=ob.vertex_groups.new(name=bn)
            groups[bn].add([idx],value,'REPLACE')
    parts.append(ob); return ob

def loft(name, rings, mat, sides=12):
    # rings: (center, transverse radius, vertical radius, bone weights).
    vs=[]; ws=[]; fs=[]
    for i,(pos,ry,rz,w) in enumerate(rings):
        c=Vector(pos); prev=Vector(rings[max(0,i-1)][0]); nex=Vector(rings[min(len(rings)-1,i+1)][0])
        axis=(nex-prev).normalized(); lateral=Vector((0,1,0))
        if abs(axis.dot(lateral))>.95: lateral=Vector((1,0,0))
        lateral=(lateral-axis*lateral.dot(axis)).normalized(); vertical=axis.cross(lateral).normalized()
        for j in range(sides):
            a=j*2*math.pi/sides
            # restrained irregularity; no random global state.
            ripple=1+.025*math.sin(j*3.1+i*1.7)
            v=c+lateral*(math.cos(a)*ry*ripple)+vertical*(math.sin(a)*rz*ripple)
            vs.append(v); ws.append(w)
        if i:
            for j in range(sides):
                a=(i-1)*sides+j; b=(i-1)*sides+(j+1)%sides; cc=i*sides+(j+1)%sides; d=i*sides+j
                fs.append((a,b,cc,d))
    fs.append(tuple(reversed(range(sides)))); fs.append(tuple(range((len(rings)-1)*sides,len(rings)*sides)))
    return mesh(name,vs,fs,mat,ws)

def tube(name, points, radii, mat, bn, sides=8):
    return loft(name,[(p,r,r,{bn:1}) for p,r in zip(points,radii)],mat,sides)

def ellipsoid(name,center,scale,mat,bn):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=center)
    ob=bpy.context.object; ob.name=name; ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    g=ob.vertex_groups.new(name=bn); g.add(list(range(len(ob.data.vertices))),1,'REPLACE');parts.append(ob);return ob

bones={}
def addbone(n,h,t,parent=None):bones[n]=(h,t,parent)
addbone('root',(0,0,0),(0,0,.4))
addbone('pelvis',(-1.0,0,1.35),(-.55,0,1.4),'root')
addbone('spine',(-.55,0,1.4),(.02,0,1.52),'pelvis')
addbone('chest',(.02,0,1.52),(.52,0,1.6),'spine')
addbone('neck',(.52,0,1.6),(.91,0,1.93),'chest')
addbone('head',(.91,0,1.93),(1.53,0,1.87),'neck')
addbone('jaw',(1.02,0,1.76),(1.7,0,1.68),'head')
addbone('tail.01',(-1.35,0,1.45),(-1.8,0,1.33),'pelvis')
addbone('tail.02',(-1.8,0,1.33),(-2.12,0,1.05),'tail.01')
addbone('tail.03',(-2.12,0,1.05),(-2.35,0,.82),'tail.02')
for side,y in [('L',.32),('R',-.32)]:
    front=[(.48,y,1.55),(.22,y,.91),(.52,y,.30),(.68,y,.11)]
    rear=[(-1.03,y,1.35),(-.60,y,.84),(-1.12,y,.43),(-.98,y,.12)]
    for label,pts in [('fore',front),('hind',rear)]:
        parent='chest' if label=='fore' else 'pelvis'
        for i,part in enumerate(['upper','lower','paw']):
            bn=f'{label}.{part}.{side}';addbone(bn,pts[i],pts[i+1],parent);parent=bn
        addbone(f'{label}.digits.{side}',pts[-1],(pts[-1][0]+.25,y,.08),parent)
    addbone(f'ear.{side}',(.89,y*.55,2.04),(.68,y*.72,2.43),'head')

# Continuous torso and neck forms, distributed weights across the spine.
loft('Thorax and tucked abdomen',[
    ((-1.45,0,1.38),.10,.16,{'pelvis':1}),((-1.25,0,1.36),.29,.30,{'pelvis':1}),
    ((-1.02,0,1.35),.37,.38,{'pelvis':.8,'spine':.2}),((-.72,0,1.35),.30,.25,{'pelvis':.3,'spine':.7}),
    ((-.35,0,1.42),.29,.33,{'spine':.8,'chest':.2}),((.04,0,1.43),.40,.49,{'spine':.3,'chest':.7}),
    ((.38,0,1.48),.45,.52,{'chest':1}),((.65,0,1.60),.29,.30,{'chest':.7,'neck':.3}),
    ((.78,0,1.8),.24,.26,{'chest':.2,'neck':.8}),((.96,0,1.96),.19,.21,{'neck':.5,'head':.5})],hide,20)
loft('Elongated skull and muzzle',[
    ((.85,0,1.97),.15,.17,{'head':1}),((1.04,0,1.99),.27,.26,{'head':1}),
    ((1.22,0,1.94),.24,.21,{'head':1}),((1.41,0,1.84),.17,.12,{'head':1}),
    ((1.69,0,1.78),.145,.09,{'head':1}),((1.83,0,1.76),.12,.07,{'head':1})],hide,16)
loft('Hinged lower jaw', [((1.02,0,1.78),.19,.07,{'jaw':1}),((1.28,0,1.65),.17,.055,{'jaw':1}),((1.68,0,1.61),.12,.04,{'jaw':1}),((1.8,0,1.65),.08,.025,{'jaw':1})],muscle,12)
ellipsoid('Nose',(1.82,0,1.78),(.08,.125,.045),darkbone,'head')
for side,y in [('L',.32),('R',-.32)]:
    sy=1 if y>0 else -1
    fore=[((.47,y,1.48),.18,.23,{'chest':.2,f'fore.upper.{side}':.8}),((.36,y,1.17),.14,.16,{f'fore.upper.{side}':1}),((.22,y,.91),.105,.11,{f'fore.upper.{side}':.5,f'fore.lower.{side}':.5}),((.39,y,.59),.075,.085,{f'fore.lower.{side}':1}),((.52,y,.30),.06,.065,{f'fore.lower.{side}':.5,f'fore.paw.{side}':.5}),((.68,y,.14),.12,.075,{f'fore.paw.{side}':1})]
    hind=[((-1.03,y,1.36),.25,.26,{'pelvis':.2,f'hind.upper.{side}':.8}),((-.78,y,1.13),.20,.22,{f'hind.upper.{side}':1}),((-.60,y,.84),.105,.11,{f'hind.upper.{side}':.5,f'hind.lower.{side}':.5}),((-.90,y,.62),.08,.09,{f'hind.lower.{side}':1}),((-1.12,y,.43),.08,.09,{f'hind.lower.{side}':.5,f'hind.paw.{side}':.5}),((-.98,y,.15),.11,.075,{f'hind.paw.{side}':1})]
    loft('Forelimb '+side,fore,hide,12);loft('Hindlimb '+side,hind,hide,12)
    for kind,x in [('fore',.68),('hind',-.98)]:
        ellipsoid(f'{kind} ankle-pad junction {side}',(x+.025,y,.16),(.14,.105,.15),hide,f'{kind}.paw.{side}')
        for d in range(4):
            yy=y+(d-1.5)*.065; length=.17 if d in (1,2) else .13
            ellipsoid(f'{kind} digit {side} {d}',(x+.09,yy,.10),(.12,.04,.06),hide,f'{kind}.digits.{side}')
            tube(f'{kind} claw {side} {d}',[(x+.14,yy,.12),(x+.14+length,yy,.10),(x+.18+length,yy,.055)],[.023,.018,.001],darkbone,f'{kind}.digits.{side}')
    # Triangular, torn ears and small orbital eyes: no mascot eyes.
    verts=[(.95,sy*.13,2.04),(.70,sy*.26,2.08),(.68,sy*.20,2.42),(.82,sy*.20,2.19),(.83,sy*.24,2.03)]
    mesh('Torn ear '+side,verts,[(0,1,2),(0,2,3),(0,3,4),(1,4,3,2)],hide,[{f'ear.{side}':1}]*5)
    ellipsoid('Deep orbital socket '+side,(1.23,sy*.217,1.995),(.08,.027,.053),darkbone,'head')
    ellipsoid('Ember slit '+side,(1.245,sy*.24,2.00),(.038,.013,.017),eye,'head')
    tube('Supraorbital ridge '+side,[(1.08,sy*.20,2.10),(1.25,sy*.23,2.09),(1.36,sy*.185,2.04)],[.04,.05,.012],bone,'head')
    for i in range(7):
        x=1.31+i*.067;yy=sy*(.145-i*.009)
        tube('Upper tooth '+side+str(i),[(x,yy,1.77),(x+.023,yy,1.68 if i!=1 else 1.59)],[.021,.001],bone,'head')
    # Visible ribs follow chest mass rather than decorating empty space.
    for i in range(5):
        x=.35-i*.18;bn='chest' if i<3 else 'spine';r=.44-i*.022
        pts=[(x-.12,sy*.05,1.92-i*.025),(x,sy*r*.68,1.78),(x+.03,sy*r,1.48),(x+.04,sy*r*.78,1.17),(x+.02,sy*r*.35,1.04+i*.035)]
        tube('Mineralized rib '+side+str(i),pts,[.042,.042,.037,.029,.018],bone,bn)
    tube('Flank healed slash '+side,[(-.85,sy*.285,1.57),(-.68,sy*.315,1.48),(-.51,sy*.32,1.39)],[.012,.018,.008],scar,'spine')
    tube('Shoulder binding strap '+side,[(.3,sy*.16,1.99),(.43,sy*.47,1.57),(.31,sy*.27,1.01)],[.042,.037,.03],iron,'chest')

# Spine armor: plates/ridges with restrained asymmetric chips.
for i in range(9):
    x=-1.15+i*.19;z=1.74+.20*math.exp(-((x-.25)/.6)**2)
    bn='pelvis' if x<-.75 else 'spine' if x<-.15 else 'chest'
    rise=.10+.09*(.5+.5*math.sin(i*2.7));lean=.09+.05*math.sin(i*1.9)
    tube('Dorsal ridge '+str(i),[(x,0,z-.04),(x-.07,.015,z+rise*.7),(x-lean,.015*math.sin(i),z+rise)],[.074,.043,.003],bone,bn,8)
loft('Tail base', [((-1.35,0,1.45),.105,.11,{'tail.01':1}),((-1.65,0,1.39),.09,.09,{'tail.01':1}),((-1.8,0,1.33),.075,.075,{'tail.01':.5,'tail.02':.5}),((-2.03,0,1.14),.052,.06,{'tail.02':1}),((-2.12,0,1.05),.038,.043,{'tail.02':.5,'tail.03':.5}),((-2.35,0,.82),.005,.006,{'tail.03':1})],hide,12)
for i in range(4):
    tube('Neck mane blade '+str(i),[(.48+i*.09,0,1.96+i*.06),(.36+i*.10,0,2.17+i*.05),(.23+i*.12,0,2.25+i*.05)],[.09,.045,.002],darkbone,'neck',7)

# Coarse ragged mane is geometry, not a painted texture or a borrowed fur asset.
# It intentionally remains a prototype substitute for authored groom cards.
for i in range(11):
    x=-1.20+i*.16;rz=.31+.17*math.exp(-((x-.27)/.55)**2);ry=.30+.11*math.exp(-((x-.27)/.55)**2);cz=1.38+.09*math.exp(-((x-.27)/.6)**2)
    bn='pelvis' if x<-.75 else 'spine' if x<-.15 else 'chest'
    for j in range(9):
        a=j*math.pi/8;y=math.cos(a)*ry;z=cz+math.sin(a)*rz
        length=.085+.08*(.5+.5*math.sin(i*3.5+j*2.1));w=.025+.015*(.5+.5*math.sin(i+j))
        verts=[(x-.055,y-w,z),(x+.05,y+w,z),(x-.13,y+math.cos(a)*length,z+math.sin(a)*length),
               (x-.065,y-w,z+.017),(x+.04,y+w,z+.017),(x-.16,y+math.cos(a)*length*.85,z+math.sin(a)*length*.85)]
        mesh(f'Ragged mane tuft {i} {j}',verts,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],hide,[{bn:1}]*6)
mesh('Fractured skull carapace',[(.94,-.16,2.13),(.93,.15,2.12),(1.14,-.19,2.22),(1.15,.18,2.20),(1.38,-.11,2.07),(1.36,.105,2.05),(1.02,0,2.27),(1.24,0,2.20)],[(0,2,6),(0,6,1),(1,6,3),(2,7,6),(3,6,7),(2,4,7),(3,7,5),(4,5,7)],bone,[{'head':1}]*8)
for side in [-1,1]:
    tube('Facial scar '+str(side),[(1.05,side*.228,2.08),(1.16,side*.255,2.005),(1.25,side*.22,1.92)],[.009,.013,.005],scar,'head')

# Join geometry, preserving real per-vertex skin weights.
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();skin=bpy.context.object;skin.name='CairnHound_Lab_SkinnedMesh'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
sub=skin.modifiers.new('Organic surface smoothing','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.ops.object.modifier_apply(modifier=sub.name)
armdata=bpy.data.armatures.new('CairnHound_Armature');arm=bpy.data.objects.new('CairnHound_Rig',armdata);bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active=arm;skin.select_set(False);arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n,(h,t,parent) in bones.items():
    eb=armdata.edit_bones.new(n);eb.head=h;eb.tail=t
    if parent:eb.parent=armdata.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');arm.show_in_front=True
mod=skin.modifiers.new('Weighted anatomical rig','ARMATURE');mod.object=arm;skin.parent=arm
for pb in arm.pose.bones:pb.rotation_mode='XYZ'

def reset_pose():
    for pb in arm.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)

def key(frame,changes):
    reset_pose()
    for bn,props in changes.items():
        for attr,value in props.items():setattr(arm.pose.bones[bn],attr,value)
    for pb in arm.pose.bones:
        for prop in ['location','rotation_euler','scale']:pb.keyframe_insert(prop,frame=frame,group=pb.name)

def action(name,length,keys):
    act=bpy.data.actions.new(name);arm.animation_data_create();arm.animation_data.action=act
    for frame,changes in keys:key(frame,changes)
    act.use_fake_user=True
    # Each action is a discrete exportable NLA track. No mixed clips.
    arm.animation_data.action=None
    tr=arm.animation_data.nla_tracks.new();tr.name=name;strip=tr.strips.new(name,1,act);strip.action_frame_start=1;strip.action_frame_end=length;tr.mute=True
    return act

idle=action('Idle_BreathAndWatch',49,[(1,{}),(13,{'chest':{'scale':(1.015,1.025,1.015)},'head':{'rotation_euler':(.025,0,.035)},'tail.02':{'rotation_euler':(0,.08,0)}}),(25,{}),(37,{'chest':{'scale':(.99,.985,.99)},'head':{'rotation_euler':(-.02,0,-.03)},'tail.02':{'rotation_euler':(0,-.08,0)}}),(49,{})])
crouch={'root':{'location':(-.10,-.12,0)},'neck':{'rotation_euler':(.12,0,0)},'jaw':{'rotation_euler':(.10,0,0)}}
anticipation=action('Anticipation_Crouch',13,[(1,{}),(8,crouch),(13,crouch)])
lungepose={'root':{'location':(.85,.035,0)},'neck':{'rotation_euler':(-.13,0,0)},'jaw':{'rotation_euler':(.28,0,0)},'fore.upper.L':{'rotation_euler':(-.3,0,0)},'fore.upper.R':{'rotation_euler':(-.3,0,0)},'hind.upper.L':{'rotation_euler':(.23,0,0)},'hind.upper.R':{'rotation_euler':(.23,0,0)}}
lunge=action('Lunge_CommandStrike',25,[(1,{}),(6,crouch),(12,lungepose),(18,{'root':{'location':(.35,0,0)}}),(25,{})])
hit=action('Hit_Recoil',17,[(1,{}),(5,{'root':{'location':(-.19,-.06,0)},'head':{'rotation_euler':(.10,0,-.17)},'chest':{'rotation_euler':(0,0,.08)}}),(10,{'head':{'rotation_euler':(-.035,0,.05)}}),(17,{})])
deathpose={'root':{'location':(-.15,-.77,0),'rotation_euler':(-1.43,0,-.12)},'jaw':{'rotation_euler':(.13,0,0)},'neck':{'rotation_euler':(.16,0,0)},'tail.01':{'rotation_euler':(.2,0,0)}}
death=action('Death_Collapse',41,[(1,{}),(9,{'root':{'location':(0,-.18,0)},'neck':{'rotation_euler':(.12,0,0)}}),(23,deathpose),(41,deathpose)])

scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=49
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.resolution_x=1100;scene.render.resolution_y=780;scene.render.resolution_percentage=100
scene.world.color=(.035,.035,.035);scene.view_settings.view_transform='AgX'
ground=material('Studio wet slate',(.025,.032,.036),.78)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015));floor=bpy.context.object;floor.name='Render floor (not exported)';floor.data.materials.append(ground)

def track(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def light(name,pos,power,color,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=pos;track(ob,(0,0,1));return ob
light('Cold moon key',(1.5,-3.5,5),620,(.65,.78,1),4)
light('Soft readable fill',(1,4,3),300,(.75,.82,.87),3)
light('Ember rim',(-3,1.8,3.2),850,(1,.48,.22),3)
camdata=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=5.2

# Export only the rig/skin. Noise/bump shaders are studio-only, not baked PBR maps.
arm.animation_data.action=None;reset_pose();scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);skin.select_set(True);bpy.context.view_layer.objects.active=arm
for tr in arm.animation_data.nla_tracks:tr.mute=False
bpy.ops.export_scene.gltf(filepath=str(OUT/'cairn-hound-lab.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True,export_yup=True)
for tr in arm.animation_data.nla_tracks:tr.mute=True
arm.animation_data.action=idle;scene.frame_set(1)
cam.location=(4.4,-5.3,3.2);track(cam,(-.15,0,1.15))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cairn-hound-lab.blend'))

renders=[]
def render(name,angle,act=idle,frame=1):
    arm.animation_data.action=act;scene.frame_set(frame)
    is_turntable=name.startswith('turntable-')
    scene.render.resolution_percentage=70 if is_turntable else 100;scene.cycles.samples=16 if is_turntable else 32
    cam.location=(-.15+6*math.cos(angle),6*math.sin(angle),3.3);track(cam,(-.15,0,1.12))
    scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True);renders.append(name)
render('hero-three-quarter.png',-.85)
render('profile-left.png',-math.pi/2)
render('rear-three-quarter.png',-2.6)
render('lunge-frame12.png',-.85,lunge,12)
render('death-frame41.png',-.85,death,41)
for i in range(12):render(f'turntable-{i:02}.png',-.85+i*2*math.pi/12)
arm.animation_data.action=idle;scene.frame_set(1)

skin.data.calc_loop_triangles()
weights=[]
for v in skin.data.vertices:weights.append(sum(g.weight for g in v.groups))
actions=[idle,anticipation,lunge,hit,death]
report={
    'status':'articulated procedural technical prototype; not production creature quality',
    'blender':bpy.app.version_string,'units':'metres (concept scale)',
    'vertices':len(skin.data.vertices),'triangles':len(skin.data.loop_triangles),
    'bones':len(arm.data.bones),'materials':len(skin.data.materials),
    'skinWeightRange':[min(weights),max(weights)],'unweightedVertices':sum(x<=0 for x in weights),
    'animations':[{'name':a.name,'frames':[a.frame_range[0],a.frame_range[1]],'fps':24} for a in actions],
    'renders':renders,'reference':'public/art/companions-atlas.png, top-left tone/anatomy only',
    'limitations':['Procedural assemblage lacks sculpted anatomical integration and reference-level fur/detail.',
        'No inverse kinematics/contact constraints; approximate motion may slide feet or intersect floor.',
        'Render noise/bump is procedural and is not baked into glTF PBR textures.',
        'No retopology, UV bake, LODs, facial blend shapes, authored locomotion or engine integration.',
        'Disjoint armor/tooth components are skinned rigidly; joint deformation needs artist review.']}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2(__file__,OUT/'blender_hound_lab.py')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='SHA256.json'}
(OUT/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('HOUND_LAB_REPORT '+json.dumps(report))
