import * as THREE from 'three';
import { tween } from './anim.js';

const INSET = 0.04;       // khoảng hở nhỏ giữa khối và ô để nhìn rõ đường ranh
const BLOCK_COLOR = 0x60a5fa;
const ACTIVE_EMISSIVE = 0xf59e0b;
// Hướng lăn trong mặt phẳng nền: [dx, dz], với z là hàng
const MOVE = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

function makeBox(x, y, z, sx, sy, sz, cell) {
  return { center: new THREE.Vector3(x, y, z), size: new THREE.Vector3(sx, sy, sz), cell };
}

// Các hộp (tâm và kích thước) của một trạng thái. Một khối có 1 hộp, khối đã tách có 2 hộp.
export function boxesOf(state) {
  const [r, c] = state.pos;
  switch (state.orient) {
    case 'standing':
      return [makeBox(c + 0.5, 1, r + 0.5, 1, 2, 1, [r, c])];
    case 'horizontal':
      return [makeBox(c + 1, 0.5, r + 0.5, 2, 1, 1, [r, c])];
    case 'vertical':
      return [makeBox(c + 0.5, 0.5, r + 1, 1, 1, 2, [r, c])];
    default: {
      const [r2, c2] = state.pos2;
      return [
        makeBox(c + 0.5, 0.5, r + 0.5, 1, 1, 1, [r, c]),
        makeBox(c2 + 0.5, 0.5, r2 + 0.5, 1, 1, 1, [r2, c2]),
      ];
    }
  }
}

// Khối người chơi điều khiển. Luôn có sẵn 2 mesh, mesh thứ hai chỉ hiện khi đã tách.
export class Block {
  constructor(scene) {
    this.root = new THREE.Group();
    scene.add(this.root);
    const geo = new THREE.BoxGeometry(1, 1, 1);
    this.meshes = [0, 1].map(() => {
      const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: BLOCK_COLOR, roughness: 0.35 }));
      this.root.add(mesh);
      return mesh;
    });
    this.meshes[1].visible = false;
  }

  // Đặt khối ngay vào đúng vị trí của trạng thái (không có hoạt ảnh).
  snap(state) {
    const boxes = boxesOf(state);
    this.meshes.forEach((mesh, i) => {
      const box = boxes[i];
      mesh.visible = Boolean(box);
      if (!box) return;
      mesh.position.copy(box.center);
      mesh.scale.copy(box.size).subScalar(INSET);
      mesh.quaternion.identity();
      mesh.userData.cell = box.cell;
    });
  }

  // Làm sáng khối con đang được điều khiển. cell = null thì tắt sáng.
  highlight(cell) {
    this.meshes.forEach((mesh) => {
      const cur = mesh.userData.cell;
      const on = Boolean(cell && cur && cur[0] === cell[0] && cur[1] === cell[1]);
      mesh.material.emissive.setHex(on ? ACTIVE_EMISSIVE : 0x000000);
      mesh.material.emissiveIntensity = 0.45;
    });
  }

  // Lăn một khối (hoặc một khối con) theo hướng dir. Khối xoay quanh mép dưới phía trước.
  async roll(state, dir, ms, cubeIndex = 0) {
    const box = boxesOf(state)[cubeIndex];
    const mesh = this.meshes[cubeIndex];
    const [dx, dz] = MOVE[dir];
    const pivot = new THREE.Group();
    pivot.position.set(box.center.x + dx * box.size.x / 2, 0, box.center.z + dz * box.size.z / 2);
    this.root.add(pivot);
    pivot.attach(mesh);

    // Trục xoay = hướng lăn × trục lên, góc quay -90 độ
    const axis = new THREE.Vector3(-dz, 0, dx);
    await tween(ms, (t) => pivot.quaternion.setFromAxisAngle(axis, (-Math.PI / 2) * t));

    this.root.attach(mesh);
    pivot.removeFromParent();
  }

  // Khối rơi xuống khỏi bảng.
  fall() {
    const meshes = this.meshes.filter((m) => m.visible);
    const starts = meshes.map((m) => m.position.y);
    return tween(700, (t) => {
      meshes.forEach((m, i) => {
        m.position.y = starts[i] - 12 * t;
        m.rotation.x = 0.9 * t;
      });
    }, (t) => t * t);
  }

  // Khối chìm vào lỗ đích.
  sink() {
    const meshes = this.meshes.filter((m) => m.visible);
    const starts = meshes.map((m) => ({ y: m.position.y, scale: m.scale.clone() }));
    return tween(600, (t) => {
      meshes.forEach((m, i) => {
        m.position.y = starts[i].y - 1.6 * t;
        m.scale.copy(starts[i].scale).multiplyScalar(1 - 0.5 * t);
      });
    }, (t) => t);
  }
}
