import * as THREE from 'three';
import type { GameState } from './engine';

type ArenaUnit = GameState['allies'][number];
type Figure = {
  root: THREE.Group;
  body: THREE.Group;
  ring: THREE.Mesh;
  hp: number;
  born: number;
  hit: number;
  phase: number;
  side: 'ally' | 'enemy';
  slot: number;
};

/** Decorative battlefield. The accessible HTML roster owns all interactions. */
export function createArena(canvas: HTMLCanvasElement) {
  let disposed = false;
  let selected: string | null = null;
  let frame = 0;
  let lastTime = 0;
  let visualTime = 0;
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionOff = () => motionQuery.matches || document.documentElement.dataset.reducedMotion === 'true';
  let reduced = motionOff();
  const geometries = new Set<THREE.BufferGeometry>();
  const materials = new Set<THREE.Material>();
  const figures = new Map<string, Figure>();
  const materialCache = new Map<string, THREE.MeshStandardMaterial>();
  let renderer: THREE.WebGLRenderer;

  // A failed GPU is not a failed game: every rule and command lives in HTML.
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'low-power' });
  } catch {
    canvas.setAttribute('aria-label', 'Woodland battlefield illustration unavailable. Use the companion and enemy controls below.');
    const fallback = document.createElement('div');
    fallback.className = 'arena-fallback';
    fallback.setAttribute('role', 'status');
    fallback.textContent = 'The lanterns still burn. Battlefield graphics are unavailable; all cards and commands remain playable below.';
    Object.assign(fallback.style, { padding: '2rem', color: '#e9dcb9', background: 'radial-gradient(ellipse at center, #29493b, #0b211d)', borderRadius: '1rem', textAlign: 'center' });
    canvas.hidden = true;
    canvas.insertAdjacentElement('afterend', fallback);
    return { render(_state: GameState) {}, setSelected(_uid: string | null) {}, resize() {}, dispose() { fallback.remove(); canvas.hidden = false; } };
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  canvas.setAttribute('aria-label', 'A lantern-lit woodland stone arena with your summoned companions and woodland adversaries.');

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#101f21');
  scene.fog = new THREE.FogExp2('#101f21', 0.036);
  const camera = new THREE.PerspectiveCamera(39, 1, 0.1, 90);
  camera.position.set(0, 10.8, 15.8);
  camera.lookAt(0, 0.45, -0.75);
  scene.add(new THREE.HemisphereLight('#a8e4d7', '#35422c', 0.9));
  const moon = new THREE.DirectionalLight('#abd3db', 1.35);
  moon.position.set(-9, 14, -10);
  scene.add(moon);
  const warm = new THREE.DirectionalLight('#ffd5a0', 2.0);
  warm.position.set(2, 11, 6);
  warm.castShadow = true;
  warm.shadow.mapSize.set(1024, 1024);
  Object.assign(warm.shadow.camera, { left: -12, right: 12, top: 10, bottom: -10, near: 1, far: 35 });
  warm.shadow.bias = -0.001;
  warm.shadow.normalBias = 0.035;
  scene.add(warm);

  function own<T extends THREE.BufferGeometry>(geometry: T): T { geometries.add(geometry); return geometry; }
  const sphere = own(new THREE.IcosahedronGeometry(1, 1));
  const lowSphere = own(new THREE.IcosahedronGeometry(1, 0));
  const box = own(new THREE.BoxGeometry(1, 1, 1));
  const cone = own(new THREE.ConeGeometry(1, 1, 6));
  const cylinder = own(new THREE.CylinderGeometry(1, 1, 1, 10));
  const taper = own(new THREE.CylinderGeometry(0.6, 1, 1, 7));
  const ringGeometry = own(new THREE.TorusGeometry(0.66, 0.025, 4, 40));
  const slitGeometry = own(new THREE.TorusGeometry(0.53, 0.012, 3, 32));
  function material(color: string, glow = 0, roughness = 0.86) {
    const key = `${color}:${glow}:${roughness}`;
    let mat = materialCache.get(key);
    if (!mat) {
      mat = new THREE.MeshStandardMaterial({ color, roughness, flatShading: true, emissive: color, emissiveIntensity: glow });
      materialCache.set(key, mat); materials.add(mat);
    }
    return mat;
  }
  function part(parent: THREE.Object3D, geometry: THREE.BufferGeometry, color: string, x: number, y: number, z: number, sx: number, sy = sx, sz = sx, glow = 0) {
    const mesh = new THREE.Mesh(geometry, material(color, glow));
    mesh.position.set(x, y, z); mesh.scale.set(sx, sy, sz);
    mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
  }
  function limb(parent: THREE.Object3D, start: THREE.Vector3, end: THREE.Vector3, width: number, color: string) {
    const center = start.clone().add(end).multiplyScalar(0.5);
    const mesh = part(parent, cylinder, color, center.x, center.y, center.z, width, start.distanceTo(end), width);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), end.clone().sub(start).normalize());
    return mesh;
  }
  function eye(parent: THREE.Object3D, x: number, y: number, z: number, size = 0.045, color = '#ffde89') {
    part(parent, sphere, '#111d22', x, y, z, size * 1.6, size * 1.6, size * 0.75);
    part(parent, lowSphere, color, x, y, z + size * 0.7, size, size, size * 0.55, 0.9);
  }

  // The table is a substantial object, built from beveled octagonal stone slabs.
  const stage = new THREE.Group(); scene.add(stage);
  const slabShape = new THREE.Shape();
  slabShape.moveTo(-8.3, -3.9); slabShape.lineTo(8.3, -3.9); slabShape.lineTo(8.8, -3.4);
  slabShape.lineTo(8.8, 3.4); slabShape.lineTo(8.3, 3.9); slabShape.lineTo(-8.3, 3.9);
  slabShape.lineTo(-8.8, 3.4); slabShape.lineTo(-8.8, -3.4); slabShape.closePath();
  const slab = part(stage, own(new THREE.ExtrudeGeometry(slabShape, { depth: 0.5, bevelEnabled: true, bevelSegments: 1, steps: 1, bevelSize: 0.15, bevelThickness: 0.12 })), '#556967', 0, -0.58, 0, 1);
  slab.rotation.x = -Math.PI / 2;
  part(stage, box, '#354c48', 0, -0.62, 0, 17.2, 0.45, 7.35);
  for (const x of [-6.8, 6.8]) for (const z of [-2.7, 2.7]) {
    part(stage, taper, '#263e3b', x, -1.0, z, 0.8, 1.8, 0.8);
    part(stage, cylinder, '#768378', x, -0.22, z, 0.86, 0.16, 0.86);
  }
  part(stage, box, '#c0ae75', 0, 0.064, 0, 16.2, 0.012, 0.027, 0.12);
  const centerSeal = part(stage, own(new THREE.TorusGeometry(0.62, 0.035, 5, 6)), '#bba272', 0, 0.08, 0, 1, 1, 1, 0.25);
  centerSeal.rotation.x = -Math.PI / 2;
  for (const side of [-1, 1]) for (let i = 0; i < 6; i++) {
    const x = (i - 2.5) * 2.52;
    const z = side * 2.02;
    part(stage, cylinder, '#394e4c', x, 0.045, z, 0.85, 0.11, 0.85);
    const inset = part(stage, cylinder, side > 0 ? '#567b6b' : '#6d5c61', x, 0.108, z, 0.75, 0.025, 0.75);
    inset.castShadow = false;
    const line = part(stage, slitGeometry, side > 0 ? '#9bcaa3' : '#c79285', x, 0.13, z, 1, 1, 1, 0.28);
    line.rotation.x = -Math.PI / 2;
    // Three incised dots make each summoning seal look deliberately carved.
    for (let dot = 0; dot < 3; dot++) part(stage, lowSphere, '#ddbf7a', x + (dot - 1) * 0.14, 0.14, z + 0.62, 0.026, 0.011, 0.026, 0.2);
  }
  const ground = part(scene, own(new THREE.PlaneGeometry(150, 150)), '#142f28', 0, -1.8, 0, 1);
  ground.rotation.x = -Math.PI / 2; ground.castShadow = false;
  // Deterministic art placement; this RNG never touches engine state.
  let artSeed = 7981;
  const random = () => { artSeed = (artSeed * 1664525 + 1013904223) >>> 0; return artSeed / 4294967296; };
  for (let i = 0; i < 30; i++) {
    const tree = new THREE.Group(); scene.add(tree);
    const x = i < 20 ? (random() - 0.5) * 45 : (i % 2 ? -1 : 1) * (12 + random() * 7);
    const z = i < 20 ? -8 - random() * 20 : (random() - 0.5) * 20;
    const height = 5 + random() * 8;
    tree.position.set(x, -1.8, z);
    part(tree, taper, '#304c42', 0, height * 0.47, 0, 0.28 + random() * 0.25, height, 0.35);
    for (let tier = 0; tier < 3; tier++) {
      const radius = 2.5 - tier * 0.55 + random() * 0.5;
      const canopy = part(tree, cone, ['#234a3d', '#2c5845', '#3a6350'][tier], 0, height * 0.52 + tier * 1.55, 0, radius, 4, radius);
      canopy.rotation.y = random(); canopy.castShadow = false;
    }
  }
  // Mossy boulders and fern clusters frame the foreground.
  for (let i = 0; i < 18; i++) {
    const x = (i % 2 ? -1 : 1) * (9.8 + random() * 5);
    const z = -5 + random() * 12;
    part(scene, lowSphere, i % 3 ? '#345549' : '#61786a', x, -1.5, z, 0.4 + random(), 0.4 + random() * 0.7, 0.5 + random());
    for (let leaf = 0; leaf < 4; leaf++) {
      const blade = part(scene, cone, '#4e7c53', x + (random() - 0.5), -1.1, z + (random() - 0.5), 0.08, 0.95, 0.25);
      blade.rotation.z = (leaf - 1.5) * 0.35;
    }
  }
  const lanternFlames: THREE.Mesh[] = [];
  for (const x of [-8.55, 8.55]) for (const z of [-3.3, 3.3]) {
    part(scene, cylinder, '#374946', x, 0.43, z, 0.16, 0.8, 0.16);
    part(scene, box, '#293b36', x, 1.0, z, 0.56, 0.13, 0.56);
    part(scene, cone, '#a88450', x, 1.63, z, 0.46, 0.3, 0.46);
    for (const dx of [-0.23, 0.23]) for (const dz of [-0.23, 0.23]) part(scene, box, '#3d4636', x + dx, 1.28, z + dz, 0.038, 0.6, 0.038);
    lanternFlames.push(part(scene, sphere, '#ffbf61', x, 1.29, z, 0.17, 0.27, 0.17, 3));
    const light = new THREE.PointLight('#ffc574', 35, 8, 2); light.position.set(x, 1.5, z); scene.add(light);
  }
  // A single draw call for ambient fireflies.
  const fireflyPositions = new Float32Array(90 * 3);
  const fireflyBases: number[] = [];
  for (let i = 0; i < 90; i++) { fireflyBases.push((random() - 0.5) * 25, random() * 5, (random() - 0.5) * 16); }
  fireflyPositions.set(fireflyBases);
  const fireflyGeo = own(new THREE.BufferGeometry());
  fireflyGeo.setAttribute('position', new THREE.BufferAttribute(fireflyPositions, 3));
  const fireflyMat = new THREE.PointsMaterial({ color: '#ffe7a2', size: 0.045, transparent: true, opacity: 0.76, depthWrite: false, blending: THREE.AdditiveBlending });
  materials.add(fireflyMat); scene.add(new THREE.Points(fireflyGeo, fireflyMat));

  // Bake static scenery by material. Hundreds of authored branches, carvings,
  // stones and fern leaves become a few dozen draw calls without losing detail.
  scene.updateMatrixWorld(true);
  const batches = new Map<string, { source: THREE.Mesh[]; geometry: THREE.BufferGeometry[]; material: THREE.Material; cast: boolean; receive: boolean }>();
  scene.traverse(object => {
    if (!(object instanceof THREE.Mesh) || lanternFlames.includes(object) || Array.isArray(object.material)) return;
    const key = `${object.material.uuid}:${object.castShadow}:${object.receiveShadow}`;
    let batch = batches.get(key);
    if (!batch) {
      batch = { source: [], geometry: [], material: object.material, cast: object.castShadow, receive: object.receiveShadow };
      batches.set(key, batch);
    }
    const baked = object.geometry.index ? object.geometry.toNonIndexed() : object.geometry.clone();
    baked.applyMatrix4(object.matrixWorld); batch.geometry.push(baked); batch.source.push(object);
  });
  function mergeStaticGeometry(sources: THREE.BufferGeometry[]) {
    const keys = Object.keys(sources[0].attributes);
    if (sources.some(source => keys.some(key => !source.attributes[key] || source.attributes[key].itemSize !== sources[0].attributes[key].itemSize))) return null;
    const merged = new THREE.BufferGeometry();
    for (const key of keys) {
      const itemSize = sources[0].attributes[key].itemSize;
      const total = sources.reduce((count, source) => count + source.attributes[key].array.length, 0);
      const values = new Float32Array(total);
      let offset = 0;
      for (const source of sources) { const input = source.attributes[key].array; values.set(input, offset); offset += input.length; }
      merged.setAttribute(key, new THREE.BufferAttribute(values, itemSize));
    }
    return merged;
  }
  for (const batch of batches.values()) {
    const merged = mergeStaticGeometry(batch.geometry);
    if (merged) {
      const mesh = new THREE.Mesh(own(merged), batch.material);
      mesh.castShadow = batch.cast; mesh.receiveShadow = batch.receive; scene.add(mesh);
      batch.source.forEach(source => source.removeFromParent());
    }
    batch.geometry.forEach(geometry => geometry.dispose());
  }

  function makeCreature(unit: ArenaUnit): THREE.Group {
    const body = new THREE.Group();
    const species = `${unit.species} ${unit.name}`.toLowerCase();
    let color = /^#[0-9a-f]{3,8}$/i.test(unit.color) ? unit.color : '#829986';
    const pale = '#e0d8b4', dark = '#263d38', gold = '#d4ad64';
    const leg = (x: number, z: number, h = 0.43) => {
      part(body, taper, dark, x, h / 2, z, 0.09, h, 0.09);
      part(body, sphere, color, x, 0.065, z + 0.035, 0.13, 0.09, 0.17);
    };
    if (/wolf|fox|hound|dog|boar|badger|cat|otter|hare|rabbit/.test(species)) {
      if (species.includes('fox')) color = '#c87d45';
      part(body, sphere, color, 0, 0.6, 0, 0.35, 0.36, 0.64);
      for (const x of [-0.23, 0.23]) for (const z of [-0.37, 0.34]) leg(x, z);
      part(body, sphere, color, 0, 0.93, 0.48, 0.31, 0.34, 0.33);
      part(body, taper, species.includes('fox') ? pale : '#8c9b91', 0, 0.87, 0.74, 0.2, 0.4, 0.21).rotation.x = Math.PI / 2;
      part(body, lowSphere, dark, 0, 0.87, 0.95, 0.09, 0.065, 0.055);
      for (const x of [-0.2, 0.2]) {
        if (/hare|rabbit/.test(species)) part(body, sphere, color, x, 1.5, 0.42, 0.09, 0.45, 0.07).rotation.z = x * 0.4;
        else if (/otter/.test(species)) part(body, sphere, color, x, 1.21, 0.44, 0.08, 0.08, 0.07);
        else part(body, cone, color, x, 1.25, 0.44, 0.14, 0.4, 0.12);
        eye(body, x * 0.85, 1.0, 0.737);
      }
      const tail = part(body, taper, color, 0, 0.8, -0.78, 0.17, 0.7, 0.17); tail.rotation.x = -0.7;
      part(body, lowSphere, pale, 0, 1.08, -0.99, 0.15, 0.17, 0.17);
      if (/cat/.test(species)) {
        for (const side of [-1, 1]) for (let whisker = 0; whisker < 2; whisker++) limb(body, new THREE.Vector3(side * 0.15, 0.86 + whisker * 0.045, 0.8), new THREE.Vector3(side * 0.45, 0.88 + whisker * 0.08, 0.81), 0.009, pale);
        for (const x of [-0.22, 0, 0.22]) part(body, cone, '#71835b', x, 0.96, -0.16, 0.08, 0.24, 0.08);
      }
      part(body, sphere, pale, 0, 0.7, 0.49, 0.18, 0.2, 0.11);
      if (/boar/.test(species)) for (const x of [-0.23, 0.23]) part(body, cone, pale, x, 0.8, 0.73, 0.08, 0.32, 0.08).rotation.z = x > 0 ? -0.4 : 0.4;
    } else if (/stag|deer|elk/.test(species)) {
      part(body, sphere, color, 0, 0.7, -0.08, 0.28, 0.35, 0.53);
      for (const x of [-0.19, 0.19]) for (const z of [-0.36, 0.29]) leg(x, z, 0.62);
      part(body, taper, color, 0, 1.03, 0.35, 0.16, 0.72, 0.18).rotation.x = 0.28;
      part(body, sphere, color, 0, 1.43, 0.48, 0.23, 0.23, 0.3);
      part(body, lowSphere, dark, 0, 1.38, 0.76, 0.1, 0.08, 0.06);
      for (const x of [-0.17, 0.17]) {
        eye(body, x, 1.48, 0.67, 0.034);
        part(body, sphere, color, x * 1.8, 1.56, 0.39, 0.22, 0.06, 0.11).rotation.z = x > 0 ? 0.4 : -0.4;
        limb(body, new THREE.Vector3(x, 1.59, 0.45), new THREE.Vector3(x * 2.6, 2.1, 0.36), 0.035, gold);
        for (let branch = 0; branch < 3; branch++) limb(body, new THREE.Vector3(x * (1.4 + branch * 0.5), 1.72 + branch * 0.14, 0.4), new THREE.Vector3(x * (3 + branch * 0.6), 1.93 + branch * 0.14, 0.45), 0.025, gold);
      }
      part(body, sphere, pale, 0, 0.99, 0.44, 0.13, 0.27, 0.08);
    } else if (/raven|\bcrow\b|rook/.test(species)) {
      part(body, sphere, '#475565', 0, 0.67, 0, 0.28, 0.43, 0.28);
      part(body, sphere, color, 0, 1.14, 0.11, 0.26, 0.27, 0.25);
      const beak = part(body, cone, gold, 0, 1.1, 0.48, 0.09, 0.4, 0.11); beak.rotation.x = Math.PI / 2;
      for (const side of [-1, 1]) {
        eye(body, side * 0.16, 1.18, 0.3, 0.045, '#d9cff3');
        part(body, sphere, '#59637b', side * 0.3, 0.67, -0.02, 0.15, 0.35, 0.23).rotation.z = side * 0.2;
        for (let feather = 0; feather < 3; feather++) part(body, cone, color, side * (0.24 + feather * 0.075), 0.37, -0.11, 0.05, 0.34, 0.07).rotation.z = side * 0.28 + Math.PI;
        part(body, cylinder, gold, side * 0.12, 0.15, 0.04, 0.024, 0.25, 0.024);
        for (let toe = 0; toe < 3; toe++) part(body, box, gold, side * 0.12 + (toe - 1) * 0.04, 0.038, 0.12, 0.022, 0.025, 0.2);
      }
      for (let feather = 0; feather < 3; feather++) part(body, sphere, '#475565', (feather - 1) * 0.08, 0.38, -0.37, 0.07, 0.06, 0.34).rotation.x = -0.4;
      part(body, cone, color, 0, 1.44, 0.0, 0.09, 0.22, 0.09).rotation.z = -0.35;
    } else if (/owl|bird/.test(species)) {
      part(body, sphere, color, 0, 0.7, 0, 0.43, 0.55, 0.32);
      for (const x of [-0.43, 0.43]) { const wing = part(body, sphere, dark, x, 0.66, -0.07, 0.16, 0.43, 0.22); wing.rotation.z = x > 0 ? -0.25 : 0.25; }
      part(body, sphere, color, 0, 1.13, 0.06, 0.44, 0.34, 0.3);
      for (const x of [-0.21, 0.21]) {
        part(body, sphere, pale, x, 1.16, 0.31, 0.21, 0.23, 0.08);
        eye(body, x, 1.17, 0.394, 0.085);
        part(body, cone, color, x * 1.35, 1.45, 0.02, 0.13, 0.28, 0.1);
        for (let toe = 0; toe < 3; toe++) part(body, box, gold, x + (toe - 1) * 0.045, 0.15, 0.12, 0.029, 0.055, 0.2);
      }
      const beak = part(body, cone, gold, 0, 1.06, 0.4, 0.085, 0.22, 0.09); beak.rotation.x = Math.PI;
      for (let f = 0; f < 3; f++) part(body, sphere, pale, (f - 1) * 0.16, 0.59, 0.31, 0.065, 0.21, 0.025);
    } else if (/spider|weaver|arach/.test(species)) {
      part(body, sphere, color, 0, 0.5, -0.25, 0.39, 0.33, 0.48);
      part(body, sphere, dark, 0, 0.38, 0.31, 0.29, 0.25, 0.31);
      for (const side of [-1, 1]) for (let l = 0; l < 4; l++) {
        const z = -0.48 + l * 0.26;
        const joint = new THREE.Vector3(side * (0.58 + Math.sin(l) * 0.1), 0.55, z + (l - 1.5) * 0.17);
        limb(body, new THREE.Vector3(side * 0.23, 0.38, z), joint, 0.045, color);
        limb(body, joint, new THREE.Vector3(side * 0.83, 0.04, z + (l - 1.5) * 0.25), 0.035, dark);
      }
      for (const x of [-0.15, 0, 0.15]) eye(body, x, 0.43, 0.57, x === 0 ? 0.065 : 0.045, '#efba87');
      part(body, lowSphere, '#d5b991', 0, 0.77, -0.3, 0.16, 0.02, 0.21);
    } else if (/golem|stone|guardian|brute|root|bark|sentinel/.test(species)) {
      const bark = /root|bark/.test(species);
      const stone = bark ? '#7f785a' : color;
      part(body, lowSphere, stone, 0, 0.85, 0, 0.48, 0.63, 0.33);
      part(body, box, dark, 0, 1.32, 0, 0.23, 0.15, 0.22);
      part(body, lowSphere, stone, 0, 1.52, 0, 0.29, 0.3, 0.27);
      for (const side of [-1, 1]) {
        part(body, lowSphere, stone, side * 0.52, 1.08, 0, 0.28, 0.3, 0.29);
        part(body, lowSphere, stone, side * 0.65, 0.64, 0.07, 0.23, 0.4, 0.23).rotation.z = side * 0.17;
        part(body, lowSphere, stone, side * 0.24, 0.24, 0.01, 0.22, 0.32, 0.26);
        part(body, box, dark, side * 0.24, 0.07, 0.08, 0.35, 0.13, 0.45);
        eye(body, side * 0.12, 1.55, 0.25, 0.043, '#b4eac0');
        part(body, lowSphere, '#729360', side * 0.5, 1.29, -0.03, 0.21, 0.07, 0.2);
      }
      part(body, lowSphere, '#9de1ae', 0, 0.98, 0.32, 0.13, 0.21, 0.04, 1.4);
      if (bark) for (const side of [-1, 1]) limb(body, new THREE.Vector3(side * 0.12, 1.7, 0), new THREE.Vector3(side * 0.36, 2.0, 0), 0.045, stone);
    } else if (/crown/.test(species)) {
      const cloak = part(body, cone, '#39444b', 0, 0.84, 0, 0.63, 1.65, 0.52);
      cloak.rotation.y = Math.PI / 6;
      part(body, sphere, '#dfc88d', 0, 1.68, 0.1, 0.35, 0.44, 0.19);
      for (const x of [-0.15, 0.15]) eye(body, x, 1.75, 0.28, 0.074, '#d6f4c3');
      part(body, cylinder, gold, 0, 2.0, 0.03, 0.42, 0.18, 0.42);
      for (let spike = 0; spike < 7; spike++) {
        const a = spike * Math.PI * 2 / 7;
        part(body, cone, '#e4c574', Math.cos(a) * 0.37, 2.26, Math.sin(a) * 0.37, 0.07, 0.46, 0.07, 0.25);
      }
      for (const side of [-1, 1]) {
        const arm = part(body, cone, '#46564f', side * 0.61, 1.18, 0.02, 0.23, 0.9, 0.21); arm.rotation.z = side * 0.7;
        part(body, sphere, '#dfc88d', side * 0.91, 0.99, 0.14, 0.11, 0.18, 0.09);
        const thorn = part(body, cone, gold, side * 0.46, 1.87, -0.08, 0.08, 0.67, 0.08); thorn.rotation.z = side * -0.8;
      }
      part(body, lowSphere, '#aada9c', 0, 1.08, 0.34, 0.13, 0.25, 0.025, 0.9);
    } else if (/moth|butterfly/.test(species)) {
      part(body, sphere, '#5b6475', 0, 0.89, 0, 0.12, 0.42, 0.12);
      part(body, sphere, pale, 0, 1.2, 0.08, 0.17, 0.18, 0.14);
      for (const side of [-1, 1]) {
        const upper = part(body, sphere, color, side * 0.43, 1.12, -0.03, 0.45, 0.36, 0.055); upper.rotation.z = side * 0.4;
        const lower = part(body, sphere, '#8e829c', side * 0.34, 0.64, -0.03, 0.32, 0.29, 0.05); lower.rotation.z = side * -0.35;
        part(body, sphere, gold, side * 0.5, 1.09, 0.034, 0.13, 0.16, 0.015, 0.12);
        part(body, sphere, '#34394d', side * 0.5, 1.09, 0.054, 0.075, 0.1, 0.01);
        limb(body, new THREE.Vector3(side * 0.07, 1.32, 0.07), new THREE.Vector3(side * 0.24, 1.62, 0.05), 0.018, gold);
        part(body, lowSphere, gold, side * 0.24, 1.62, 0.05, 0.035);
        eye(body, side * 0.065, 1.22, 0.206, 0.028);
      }
    } else if (/turtle/.test(species)) {
      part(body, sphere, '#466d54', 0, 0.38, -0.12, 0.53, 0.34, 0.61);
      part(body, sphere, color, 0, 0.58, -0.12, 0.47, 0.37, 0.55);
      part(body, lowSphere, gold, 0, 0.89, -0.12, 0.2, 0.025, 0.24);
      for (const x of [-0.39, 0.39]) for (const z of [-0.39, 0.29]) part(body, sphere, '#97b588', x, 0.14, z, 0.18, 0.12, 0.2);
      part(body, sphere, '#97b588', 0, 0.46, 0.58, 0.24, 0.21, 0.29);
      for (const x of [-0.13, 0.13]) eye(body, x, 0.5, 0.8, 0.039);
      for (const side of [-1, 1]) for (let row = 0; row < 2; row++) part(body, lowSphere, '#678e70', side * 0.3, 0.75, -0.33 + row * 0.37, 0.17, 0.04, 0.17);
    } else if (/drake|dragon/.test(species)) {
      part(body, sphere, color, 0, 0.69, 0, 0.31, 0.49, 0.47);
      for (const x of [-0.25, 0.25]) for (const z of [-0.3, 0.29]) leg(x, z);
      part(body, sphere, color, 0, 1.06, 0.45, 0.29, 0.29, 0.38);
      part(body, taper, '#b4c9a2', 0, 0.99, 0.72, 0.2, 0.3, 0.16).rotation.x = Math.PI / 2;
      for (const side of [-1, 1]) {
        eye(body, side * 0.18, 1.12, 0.74, 0.046);
        part(body, cone, gold, side * 0.2, 1.47, 0.27, 0.065, 0.47, 0.06).rotation.z = side * -0.2;
        const shape = new THREE.Shape(); shape.moveTo(0, 0); shape.lineTo(side * 0.93, 0.85); shape.lineTo(side * 0.7, -0.23); shape.lineTo(side * 0.28, -0.1); shape.closePath();
        const wing = part(body, own(new THREE.ShapeGeometry(shape)), '#558979', side * 0.21, 0.86, -0.05, 1);
        const wingMat = material('#558979'); wingMat.side = THREE.DoubleSide; wing.material = wingMat;
        limb(body, new THREE.Vector3(side * 0.21, 0.86, -0.04), new THREE.Vector3(side * 1.14, 1.71, -0.04), 0.035, gold);
      }
      const tail = part(body, cone, color, 0, 0.66, -0.86, 0.2, 1.1, 0.2); tail.rotation.x = -Math.PI / 2;
      for (let spine = 0; spine < 4; spine++) part(body, cone, gold, 0, 1.14 - spine * 0.12, -0.14 - spine * 0.25, 0.07, 0.23, 0.07);
    } else if (/moss|reed/.test(species)) {
      const isReed = /reed/.test(species);
      part(body, isReed ? taper : sphere, isReed ? '#688d74' : '#769463', 0, 0.62, 0, isReed ? 0.27 : 0.33, isReed ? 0.97 : 0.46, 0.26);
      part(body, sphere, color, 0, 1.16, 0.02, 0.33, 0.31, 0.28);
      for (const side of [-1, 1]) {
        limb(body, new THREE.Vector3(side * 0.22, 0.9, 0), new THREE.Vector3(side * 0.42, 0.45, 0.08), 0.07, color);
        part(body, sphere, '#465e41', side * 0.16, 0.11, 0.1, 0.16, 0.14, 0.22);
        eye(body, side * 0.12, 1.19, 0.282, 0.052);
      }
      for (let leaf = 0; leaf < 5; leaf++) {
        const x = (leaf - 2) * 0.12;
        const sprout = part(body, isReed ? taper : sphere, isReed ? '#b8c98b' : '#a3bf71', x, 1.49 + (2 - Math.abs(leaf - 2)) * 0.09, -0.025, 0.065, isReed ? 0.6 : 0.23, 0.08);
        sprout.rotation.z = -x * 2;
      }
      if (isReed) { part(body, cylinder, '#a2ab73', 0.49, 0.86, 0, 0.025, 1.7, 0.025); part(body, sphere, '#8f714b', 0.49, 1.61, 0, 0.07, 0.22, 0.07); }
      else for (let bud = 0; bud < 3; bud++) part(body, lowSphere, '#e4c78f', (bud - 1) * 0.16, 1.47, 0.15, 0.045);
    } else if (/wisp|spirit|sprite|ghost|ember/.test(species)) {
      const core = part(body, sphere, color, 0, 0.93, 0, 0.3, 0.44, 0.27, 1.1);
      core.rotation.z = -0.18;
      const tail = part(body, cone, color, -0.12, 0.48, 0, 0.2, 0.49, 0.17, 0.7); tail.rotation.z = 0.45;
      for (const x of [-0.11, 0.11]) eye(body, x, 1.02, 0.25, 0.047, '#eaffd4');
      for (const side of [-1, 1]) { const wing = part(body, sphere, '#add1ba', side * 0.4, 1.0, -0.04, 0.29, 0.095, 0.2, 0.4); wing.rotation.z = side * 0.55; }
      const halo = part(body, ringGeometry, '#e6d5a0', 0, 1.61, 0, 0.45, 0.45, 0.45, 0.75); halo.rotation.x = Math.PI / 2;
    } else if (/mush|fung|cap|toad/.test(species)) {
      part(body, taper, pale, 0, 0.53, 0, 0.24, 0.87, 0.24);
      const cap = part(body, sphere, color, 0, 1.03, 0, 0.61, 0.31, 0.54);
      for (const x of [-0.19, 0.19]) eye(body, x, 0.67, 0.225, 0.043);
      for (let i = 0; i < 5; i++) { const a = i * 1.9; part(body, sphere, pale, Math.cos(a) * 0.36, 1.25, Math.sin(a) * 0.29, 0.065, 0.02, 0.09); }
      for (const x of [-0.2, 0.2]) part(body, sphere, dark, x, 0.1, 0.09, 0.18, 0.1, 0.2);
      cap.rotation.z = 0.08;
    } else {
      // The fallback is a crafted, masked woodland imp with a cloak and staff.
      part(body, cone, color, 0, 0.64, 0, 0.43, 1.1, 0.36);
      part(body, sphere, pale, 0, 1.28, 0.09, 0.25, 0.32, 0.17);
      for (const x of [-0.12, 0.12]) { eye(body, x, 1.29, 0.244, 0.045); part(body, cone, dark, x * 1.8, 1.62, -0.02, 0.07, 0.36, 0.08).rotation.z = x > 0 ? -0.4 : 0.4; }
      part(body, cylinder, '#98704b', 0.49, 0.7, 0.1, 0.035, 1.4, 0.035);
      part(body, lowSphere, gold, 0.49, 1.44, 0.1, 0.14, 0.16, 0.14, 0.5);
      if (/witch/.test(species)) {
        part(body, cylinder, dark, 0, 1.58, 0, 0.42, 0.045, 0.42);
        part(body, cone, '#4b435a', 0, 1.9, 0, 0.26, 0.68, 0.26).rotation.z = -0.14;
        part(body, cylinder, gold, 0, 1.67, 0, 0.235, 0.06, 0.235);
      }
      for (const x of [-0.2, 0.2]) part(body, box, dark, x, 0.1, 0.13, 0.23, 0.14, 0.36);
    }
    return body;
  }

  function updateSelection() {
    for (const [uid, figure] of figures) {
      const mat = figure.ring.material as THREE.MeshStandardMaterial;
      mat.color.set(uid === selected ? '#ffe59a' : figure.side === 'ally' ? '#87cdae' : '#c59082');
      mat.emissive.copy(mat.color); mat.emissiveIntensity = uid === selected ? 1.3 : 0.15;
      figure.ring.scale.setScalar(uid === selected ? 1.09 : 1);
    }
    drawStill();
  }

  function render(state: GameState) {
    if (disposed) return;
    const seen = new Set<string>();
    for (const side of ['ally', 'enemy'] as const) {
      const units = side === 'ally' ? state.allies : state.enemies;
      units.slice(0, 6).forEach((unit, slot) => {
        seen.add(unit.uid);
        let figure = figures.get(unit.uid);
        if (!figure) {
          const root = new THREE.Group();
          const body = makeCreature(unit); root.add(body);
          body.rotation.y = side === 'enemy' ? 0 : Math.PI * 0.075;
          const ringMat = new THREE.MeshStandardMaterial({ color: '#9bcba2', emissive: '#9bcba2', emissiveIntensity: 0.15, roughness: 0.5 });
          materials.add(ringMat);
          const ring = new THREE.Mesh(ringGeometry, ringMat); ring.rotation.x = -Math.PI / 2; ring.position.y = 0.012; root.add(ring);
          root.position.set((slot - 2.5) * 2.52, 0.15, side === 'ally' ? 2.02 : -2.02);
          scene.add(root);
          figure = { root, body, ring, hp: unit.hp, born: visualTime, hit: -10, phase: random() * Math.PI * 2, side, slot };
          figures.set(unit.uid, figure);
        } else {
          if (unit.hp < figure.hp) figure.hit = visualTime;
          figure.hp = unit.hp; figure.slot = slot; figure.side = side;
          figure.root.position.x = (slot - 2.5) * 2.52;
          figure.root.position.z = side === 'ally' ? 2.02 : -2.02;
        }
      });
    }
    for (const [uid, figure] of figures) if (!seen.has(uid)) {
      scene.remove(figure.root); figures.delete(uid);
      materials.delete(figure.ring.material as THREE.Material); (figure.ring.material as THREE.Material).dispose();
    }
    updateSelection();
  }
  function animateFigures(time: number) {
    for (const figure of figures.values()) {
      const appeared = Math.min(1, (time - figure.born) / 0.38);
      const ease = reduced ? 1 : 1 - Math.pow(1 - appeared, 3);
      figure.body.scale.setScalar(0.65 + ease * 0.35);
      const hitAge = time - figure.hit;
      const hit = !reduced && hitAge < 0.35 ? Math.sin(hitAge * 40) * Math.max(0, 1 - hitAge / 0.35) * 0.13 : 0;
      figure.body.position.x = hit;
      figure.body.position.y = reduced ? 0 : Math.sin(time * 1.7 + figure.phase) * 0.025 + (1 - ease) * 0.35;
      figure.body.rotation.z = reduced ? 0 : Math.sin(time * 1.1 + figure.phase) * 0.012 + hit * 0.2;
    }
  }
  function drawStill() {
    if (disposed || document.hidden) return;
    animateFigures(visualTime); renderer.render(scene, camera);
  }
  function tick(timestamp: number) {
    frame = 0;
    if (disposed || document.hidden || reduced) return;
    const dt = lastTime ? Math.min(0.05, (timestamp - lastTime) / 1000) : 0;
    lastTime = timestamp; visualTime += dt;
    animateFigures(visualTime);
    for (let i = 0; i < 90; i++) {
      fireflyPositions[i * 3] = fireflyBases[i * 3] + Math.sin(visualTime * 0.4 + i) * 0.35;
      fireflyPositions[i * 3 + 1] = fireflyBases[i * 3 + 1] + Math.sin(visualTime * 0.7 + i * 2.4) * 0.23;
    }
    fireflyGeo.attributes.position.needsUpdate = true;
    lanternFlames.forEach((flame, i) => { flame.scale.y = 0.27 + Math.sin(visualTime * 4 + i * 1.3) * 0.018; });
    renderer.render(scene, camera);
    frame = requestAnimationFrame(tick);
  }
  function resume() {
    if (disposed) return;
    if (frame) cancelAnimationFrame(frame);
    frame = 0; lastTime = 0;
    if (!document.hidden && !reduced) frame = requestAnimationFrame(tick);
    else drawStill();
  }
  function onMotionChange() {
    const next = motionOff();
    if (next === reduced) return;
    reduced = next;
    if (reduced) {
      // Settling now prevents an interrupted summon or hit replaying later.
      figures.forEach(figure => { figure.born = visualTime - 1; figure.hit = -10; });
      lanternFlames.forEach(flame => { flame.scale.y = 0.27; });
    }
    resume();
  }
  function resize() {
    if (disposed) return;
    const bounds = canvas.getBoundingClientRect();
    const width = Math.max(1, bounds.width || canvas.clientWidth || 900);
    const height = Math.max(1, bounds.height || canvas.clientHeight || 400);
    camera.aspect = width / height;
    // Keep all six slots visible in narrow layouts rather than cropping units.
    const distance = Math.max(15.8, 24 / camera.aspect);
    (scene.fog as THREE.FogExp2).density = 0.036 * Math.min(1, 15.8 / distance);
    camera.position.set(0, distance * 0.684, distance);
    camera.lookAt(0, 0.45, -0.75); camera.updateProjectionMatrix();
    renderer.setSize(width, height, false); drawStill();
  }
  const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : null;
  observer?.observe(canvas);
  const motionObserver = new MutationObserver(onMotionChange);
  motionObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-reduced-motion'] });
  window.addEventListener('resize', resize);
  document.addEventListener('visibilitychange', resume);
  motionQuery.addEventListener('change', onMotionChange);
  resize(); resume();
  return {
    render,
    setSelected(uid: string | null) { selected = uid; updateSelection(); },
    resize,
    dispose() {
      if (disposed) return; disposed = true;
      cancelAnimationFrame(frame); observer?.disconnect(); motionObserver.disconnect();
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', resume);
      motionQuery.removeEventListener('change', onMotionChange);
      geometries.forEach(geometry => geometry.dispose()); materials.forEach(mat => mat.dispose());
      figures.clear(); renderer.dispose();
    },
  };
}
