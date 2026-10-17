import * as THREE from 'three';
import { tween } from './anim.js';

const TILE_THICK = 0.2;
const TILE_TOP = 0;   // mặt trên của ô nền nằm ở y = 0
const SUNK = -0.6;    // độ hạ của cầu đang đóng

const COLOR = {
  floor: 0xcbd5e1,
  start: 0x86efac,
  fragile: 0xfb923c,
  bridge: 0xa78bfa,
  soft: 0xf472b6,
  heavy: 0xef4444,
  split: 0x38bdf8,
  ring: 0xfacc15,
  hole: 0x020617,
  target: 0x22d3ee,
};

const key = (r, c) => `${r},${c}`;

function tileColor(ch) {
  if (ch === 'S') return COLOR.start;
  if (ch === 'F') return COLOR.fragile;
  if (ch === 'b' || ch === 'B') return COLOR.bridge;
  return COLOR.floor;
}

// Bảng 3D: mỗi ô là một khối hộp mỏng, cộng thêm lỗ đích, công tắc và điểm đến.
export class Board {
  constructor(scene) {
    this.scene = scene;
    this.group = null;
    this.bridges = new Map();   // key -> mesh của cầu
    this.fragile = new Map();   // key -> mesh của ô giòn
    this.switches = new Map();  // key -> nhóm hình vẽ của công tắc
  }

  clear() {
    if (!this.group) return;
    this.scene.remove(this.group);
    this.group.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    this.group = null;
    this.bridges.clear();
    this.fragile.clear();
    this.switches.clear();
  }

  build(level) {
    this.clear();
    this.group = new THREE.Group();
    this.scene.add(this.group);

    const tileGeo = new THREE.BoxGeometry(0.96, TILE_THICK, 0.96);
    level.grid.forEach((row, r) => {
      [...row].forEach((ch, c) => {
        if (ch === '.') return;
        const x = c + 0.5;
        const z = r + 0.5;
        const k = key(r, c);
        const material = new THREE.MeshStandardMaterial({ color: tileColor(ch), roughness: 0.7 });
        const tile = new THREE.Mesh(tileGeo, material);
        tile.position.set(x, TILE_TOP - TILE_THICK / 2, z);
        this.group.add(tile);

        if (ch === 'b' || ch === 'B') this.bridges.set(k, tile);
        if (ch === 'F') this.fragile.set(k, tile);
        if (ch === 'G') this.addGoal(x, z);
      });
    });

    for (const sw of level.switches) {
      const [r, c] = sw.at;
      const marker = this.addSwitch(sw.kind, c + 0.5, r + 0.5);
      this.switches.set(key(r, c), marker);
      if (sw.kind === 'split') {
        for (const [tr, tc] of sw.targets) this.addTarget(tc + 0.5, tr + 0.5);
      }
    }
  }

  // Đưa mỗi cầu về trạng thái trong danh sách open. Có thể chạy hoạt ảnh hoặc đặt ngay.
  syncBridges(openList, instant = false) {
    const open = new Set(openList.map(([r, c]) => key(r, c)));
    const jobs = [];
    for (const [k, tile] of this.bridges) {
      const y = (open.has(k) ? TILE_TOP : SUNK) - TILE_THICK / 2;
      if (instant) {
        tile.position.y = y;
        continue;
      }
      const y0 = tile.position.y;
      if (Math.abs(y0 - y) < 1e-3) continue;
      jobs.push(tween(320, (t) => { tile.position.y = y0 + (y - y0) * t; }));
    }
    return Promise.all(jobs);
  }

  // Ô giòn vỡ: tấm nền rơi xuống và nghiêng.
  breakFragile([r, c]) {
    const tile = this.fragile.get(key(r, c));
    if (!tile) return Promise.resolve();
    const y0 = tile.position.y;
    return tween(450, (t) => {
      tile.position.y = y0 - 2 * t;
      tile.rotation.x = 0.4 * t;
    }, (t) => t * t);
  }

  // Công tắc vừa được kích hoạt: phóng to nhẹ rồi trở lại.
  flashSwitch([r, c]) {
    const marker = this.switches.get(key(r, c));
    if (!marker) return Promise.resolve();
    return tween(260, (t) => {
      marker.scale.setScalar(1 + 0.25 * Math.sin(Math.PI * t));
    }, (t) => t);
  }

  addGoal(x, z) {
    const hole = new THREE.Mesh(
      new THREE.CylinderGeometry(0.3, 0.3, 0.02, 32),
      new THREE.MeshStandardMaterial({ color: COLOR.hole }),
    );
    hole.position.set(x, 0.011, z);
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.36, 0.04, 8, 40),
      new THREE.MeshStandardMaterial({ color: COLOR.ring, emissive: COLOR.ring, emissiveIntensity: 0.4 }),
    );
    ring.rotation.x = Math.PI / 2;
    ring.position.set(x, 0.02, z);
    this.group.add(hole, ring);
  }

  addSwitch(kind, x, z) {
    const marker = new THREE.Group();
    marker.position.set(x, 0.02, z);
    if (kind === 'soft') {
      // Công tắc mềm: đĩa bát giác
      const disc = new THREE.Mesh(
        new THREE.CylinderGeometry(0.26, 0.26, 0.06, 8),
        new THREE.MeshStandardMaterial({ color: COLOR.soft }),
      );
      disc.position.y = 0.03;
      marker.add(disc);
    } else if (kind === 'heavy') {
      // Công tắc nặng: chữ X
      const mat = new THREE.MeshStandardMaterial({ color: COLOR.heavy });
      for (const angle of [Math.PI / 4, -Math.PI / 4]) {
        const bar = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.06, 0.12), mat);
        bar.position.y = 0.04;
        bar.rotation.y = angle;
        marker.add(bar);
      }
    } else {
      // Công tắc tách: hai cung tròn tạo thành "( )"
      const mat = new THREE.MeshStandardMaterial({ color: COLOR.split });
      for (const [offset, angle] of [[-0.1, Math.PI / 2], [0.1, -Math.PI / 2]]) {
        const arc = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.04, 8, 24, Math.PI), mat);
        arc.rotation.set(-Math.PI / 2, 0, angle);
        arc.position.set(offset, 0.04, 0);
        marker.add(arc);
      }
    }
    this.group.add(marker);
    return marker;
  }

  addTarget(x, z) {
    const mark = new THREE.Mesh(
      new THREE.PlaneGeometry(0.5, 0.5),
      new THREE.MeshBasicMaterial({ color: COLOR.target, transparent: true, opacity: 0.35, depthWrite: false }),
    );
    mark.rotation.x = -Math.PI / 2;
    mark.position.set(x, 0.015, z);
    this.group.add(mark);
  }
}
