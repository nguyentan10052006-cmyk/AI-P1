import * as THREE from 'three';
import { RoundedBoxGeometry } from '../vendor/RoundedBoxGeometry.js';
import { tween, easeInOut, easeIn } from './anim.js';

const INSET = 0.04;          // khoảng hở nhỏ để nhìn rõ đường ranh giữa khối và ô
const BLOCK_COLOR = 0x60a5fa;
const ACTIVE_EMISSIVE = 0xf59e0b;
// Hướng lăn trên mặt bằng: [dx, dz], với z là hàng
const MOVE = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

function makeBox(x, y, z, sx, sy, sz, cell) {
  return { center: new THREE.Vector3(x, y, z), size: new THREE.Vector3(sx, sy, sz), cell };
}

// Các hộp (tâm và kích thước) của một trạng thái. Khối nguyên có 1 hộp, khối đã tách có 2 hộp.
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

// Khối người chơi điều khiển. Luôn có sẵn hai mesh; mesh thứ hai chỉ hiện khi đã tách.
export class Block {
  constructor(view) {
    this.view = view;
    this.root = new THREE.Group();
    view.scene.add(this.root);
    const geo = new RoundedBoxGeometry(1, 1, 1, 3, 0.12);
    this.meshes = [0, 1].map(() => {
      const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: BLOCK_COLOR, roughness: 0.35, metalness: 0.05 }));
      mesh.castShadow = true;
      this.root.add(mesh);
      return mesh;
    });
    this.meshes[1].visible = false;

    // Mũi tên nổi phía trên khối đang được điều khiển (chỉ hiện khi đã tách).
    this.arrow = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.3, 16), new THREE.MeshBasicMaterial({ color: 0xfbbf24 }));
    this.arrow.rotation.x = Math.PI;
    this.arrow.visible = false;
    this.arrowBase = 0;
    this.root.add(this.arrow);
    view.tickers.push((now) => {
      if (this.arrow.visible) this.arrow.position.y = this.arrowBase + 0.06 * Math.sin(now / 200);
    });
  }

  // Đặt khối ngay vào đúng vị trí của trạng thái (không có hoạt ảnh).
  snap(state, activeCell = null) {
    const boxes = boxesOf(state);
    this.meshes.forEach((mesh, i) => {
      const box = boxes[i];
      mesh.visible = Boolean(box);
      if (!box) return;
      mesh.position.copy(box.center);
      mesh.scale.copy(box.size).subScalar(INSET);
      mesh.quaternion.identity();
      mesh.userData.cell = box.cell;
      mesh.material.emissive.setHex(0);
    });
    this.markActive(boxes, activeCell);
  }

  // Đánh dấu khối con đang được điều khiển: mũi tên và viền sáng.
  markActive(boxes, activeCell) {
    const idx = boxes.length > 1 && activeCell
      ? boxes.findIndex((b) => b.cell[0] === activeCell[0] && b.cell[1] === activeCell[1])
      : -1;
    this.meshes.forEach((mesh, i) => {
      mesh.material.emissive.setHex(i === idx ? ACTIVE_EMISSIVE : 0);
      mesh.material.emissiveIntensity = 0.25;
    });
    if (idx < 0) {
      this.arrow.visible = false;
      return;
    }
    const box = boxes[idx];
    this.arrow.visible = true;
    this.arrowBase = box.center.y + box.size.y / 2 + 0.45;
    this.arrow.position.set(box.center.x, this.arrowBase, box.center.z);
  }

  // Lăn một khối (hoặc một khối con) theo hướng dir. Khối xoay quanh mép dưới phía trước.
  async roll(state, dir, ms, cubeIndex = 0) {
    this.arrow.visible = false;
    const box = boxesOf(state)[cubeIndex];
    const mesh = this.meshes[cubeIndex];
    const [dx, dz] = MOVE[dir];
    const pivot = new THREE.Group();
    pivot.position.set(box.center.x + dx * box.size.x / 2, 0, box.center.z + dz * box.size.z / 2);
    this.root.add(pivot);
    pivot.attach(mesh);

    // Trục xoay = hướng lăn × trục lên, quay -90 độ
    const axis = new THREE.Vector3(-dz, 0, dx);
    await tween(ms, (t) => pivot.quaternion.setFromAxisAngle(axis, (-Math.PI / 2) * t));

    this.root.attach(mesh);
    pivot.removeFromParent();
  }

  // Khối rơi khỏi bảng.
  fall() {
    this.arrow.visible = false;
    const meshes = this.meshes.filter((m) => m.visible);
    const starts = meshes.map((m) => m.position.y);
    return tween(700, (t) => {
      meshes.forEach((m, i) => {
        m.position.y = starts[i] - 12 * t;
        m.rotation.x = 0.9 * t;
      });
    }, easeIn);
  }

  // Khối chìm vào lỗ đích.
  sink() {
    this.arrow.visible = false;
    const meshes = this.meshes.filter((m) => m.visible);
    const starts = meshes.map((m) => ({ y: m.position.y, scale: m.scale.clone() }));
    return tween(600, (t) => {
      meshes.forEach((m, i) => {
        m.position.y = starts[i].y - 1.6 * t;
        m.scale.copy(starts[i].scale).multiplyScalar(1 - 0.5 * t);
      });
    }, easeInOut);
  }
}
