// Nguồn duy nhất cho hình ảnh các loại ô. Bảng 3D, chú thích và thẻ màn đều dựng từ file này.
import * as THREE from 'three';
import { RoundedBoxGeometry } from '../vendor/RoundedBoxGeometry.js';

export const TILE_W = 0.94;
export const SLAB_H = 0.22;
export const LINK_PALETTE = [0xf472b6, 0x38bdf8, 0xfacc15, 0x34d399, 0xfb7185, 0xa78bfa];
const ICON_LINK = { o: 0xf472b6, x: 0xef4444, '@': 0x38bdf8 };

function mat(color, extra = {}) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.05, ...extra });
}

function box(w, h, d, material, x = 0, y = 0, z = 0) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  mesh.position.set(x, y, z);
  return mesh;
}

// Tấm nền bo cạnh, mặt trên nằm đúng ở y = 0.
function slab(color, extra = {}) {
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(TILE_W, SLAB_H, TILE_W, 3, 0.06), mat(color, extra));
  mesh.position.y = -SLAB_H / 2;
  mesh.receiveShadow = true;
  return mesh;
}

// Khung viền bốn cạnh (dùng cho cầu đóng và lỗ đích).
function frame(size, thick, material, y) {
  const group = new THREE.Group();
  const half = size / 2 - thick / 2;
  group.add(
    box(size, thick, thick, material, 0, y, -half),
    box(size, thick, thick, material, 0, y, half),
    box(thick, thick, size, material, -half, y, 0),
    box(thick, thick, size, material, half, y, 0),
  );
  return group;
}

function ring(inner, outer, color, opacity = 1) {
  const material = new THREE.MeshBasicMaterial({ color, transparent: opacity < 1, opacity, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(new THREE.RingGeometry(inner, outer, 40), material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.006;
  return mesh;
}

function softGlyph(color) {
  const group = new THREE.Group();
  const disc = new THREE.Mesh(
    new THREE.CylinderGeometry(0.26, 0.26, 0.07, 8),
    mat(color, { emissive: color, emissiveIntensity: 0.25 }),
  );
  disc.position.y = 0.035;
  group.add(disc);
  return group;
}

function heavyGlyph(color) {
  const group = new THREE.Group();
  const material = mat(color, { emissive: color, emissiveIntensity: 0.25 });
  for (const angle of [Math.PI / 4, -Math.PI / 4]) {
    const bar = box(0.62, 0.07, 0.13, material, 0, 0.04, 0);
    bar.rotation.y = angle;
    group.add(bar);
  }
  return group;
}

function splitGlyph(color) {
  const group = new THREE.Group();
  const material = mat(color, { emissive: color, emissiveIntensity: 0.25 });
  for (const [offset, angle] of [[-0.1, Math.PI / 2], [0.1, -Math.PI / 2]]) {
    const arc = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.04, 8, 24, Math.PI), material);
    arc.rotation.set(-Math.PI / 2, 0, angle);
    arc.position.set(offset, 0.04, 0);
    group.add(arc);
  }
  return group;
}

// Lỗ đích vuông: hố tối có khung vàng phát sáng.
function goalTile() {
  const group = new THREE.Group();
  group.add(slab(0x1e293b));
  const hole = box(0.56, 0.01, 0.56, mat(0x020617), 0, 0.004, 0);
  group.add(hole);
  group.add(frame(0.66, 0.05, mat(0xfacc15, { emissive: 0xfacc15, emissiveIntensity: 0.9 }), 0.02));
  return group;
}

function fragileTile() {
  const group = new THREE.Group();
  group.add(slab(0xfb923c));
  const crack = mat(0x7c2d12);
  for (const [x, z, rot] of [[-0.12, 0.05, 0.6], [0.18, -0.1, -0.4], [0.02, 0.22, 1.1]]) {
    const line = box(0.42, 0.012, 0.025, crack, x, 0.005, z);
    line.rotation.y = rot;
    group.add(line);
  }
  return group;
}

function startTile() {
  const group = new THREE.Group();
  group.add(slab(0x86efac));
  group.add(ring(0.24, 0.3, 0x16a34a, 0.85));
  return group;
}

// Cầu có hai trạng thái: open (ván gỗ) và closed (khung viền mờ). Viền màu theo công tắc điều khiển.
export function buildBridge(linkColor) {
  const group = new THREE.Group();
  const open = new THREE.Group();
  open.add(slab(0xa16207));
  for (const x of [-0.3, -0.1, 0.1, 0.3]) open.add(box(0.03, 0.012, TILE_W, mat(0x713f12), x, 0.004, 0));
  open.add(frame(TILE_W, 0.05, mat(linkColor, { emissive: linkColor, emissiveIntensity: 0.35 }), 0.012));
  const closed = new THREE.Group();
  closed.add(frame(TILE_W, 0.05, mat(linkColor, { transparent: true, opacity: 0.7, emissive: linkColor, emissiveIntensity: 0.25 }), 0.01));
  group.add(open, closed);
  return { group, open, closed };
}

// Công tắc: nền sáng và hình riêng của loại công tắc, tô màu theo đường nối.
export function buildSwitch(ch, linkColor) {
  const group = new THREE.Group();
  group.add(slab(0xe2e8f0));
  const glyphColor = linkColor;
  if (ch === 'o') group.add(softGlyph(glyphColor));
  else if (ch === 'x') group.add(heavyGlyph(glyphColor));
  else group.add(splitGlyph(glyphColor));
  return group;
}

export function buildTile(ch, linkColor = ICON_LINK.o) {
  switch (ch) {
    case 'S': return startTile();
    case 'G': return goalTile();
    case 'F': return fragileTile();
    case 'o':
    case 'x':
    case '@': return buildSwitch(ch, linkColor);
    default: {
      const group = new THREE.Group();
      group.add(slab(0xcbd5e1));
      return group;
    }
  }
}

// Điểm đến của khối con: ô vuông mờ có viền đứt.
export function buildTargetMarker() {
  const group = new THREE.Group();
  const fill = new THREE.Mesh(
    new THREE.PlaneGeometry(0.46, 0.46),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.3, depthWrite: false }),
  );
  fill.rotation.x = -Math.PI / 2;
  fill.position.y = 0.01;
  group.add(fill);
  const edge = frame(0.46, 0.03, new THREE.MeshBasicMaterial({ color: 0x22d3ee }), 0.012);
  group.add(edge);
  return group;
}

// ---- Chú thích: chụp ảnh từ chính mô hình 3D ----
let iconRenderer = null;
const iconCache = new Map();

function iconScene(ch, linkColor) {
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x334155, 1.4));
  const sun = new THREE.DirectionalLight(0xffffff, 1.2);
  sun.position.set(2, 4, 3);
  scene.add(sun);
  if (ch === 'target') {
    scene.add(slab(0xcbd5e1), buildTargetMarker());
  } else if (ch === 'b' || ch === 'B') {
    const bridge = buildBridge(0x38bdf8);
    bridge.open.visible = ch === 'B';
    bridge.closed.visible = ch === 'b';
    scene.add(bridge.group);
  } else {
    scene.add(buildTile(ch, linkColor));
  }
  return scene;
}

// Trả về chuỗi data-URL của ảnh ô, có cache.
export function tileIcon(ch, linkColor = ICON_LINK[ch] ?? 0xf472b6) {
  const key = `${ch}:${linkColor}`;
  if (iconCache.has(key)) return iconCache.get(key);
  if (!iconRenderer) {
    iconRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    iconRenderer.setSize(128, 128, false);
    iconRenderer.shadowMap.enabled = false;
  }
  const scene = iconScene(ch, linkColor);
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
  camera.position.set(1.25, 1.9, 1.85);
  camera.lookAt(0, 0.05, 0);
  iconRenderer.render(scene, camera);
  const url = iconRenderer.domElement.toDataURL('image/png');
  iconCache.set(key, url);
  return url;
}

export const ICON_KINDS = ['#', 'S', 'G', 'F', 'B', 'b', 'o', 'x', '@', 'target'];
