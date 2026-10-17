// Camera theo nấc 90°: Q/E xoay, kéo chuột rồi nhả thì tự về nấc gần nhất,
// và phím mũi tên đi theo hướng nhìn của camera.
import * as THREE from 'three';
import { tween, easeInOut } from './anim.js';

const HALF_PI = Math.PI / 2;
// Hướng nhìn (x, z) ứng với từng nấc k: k = 0 nhìn về phía -z (hàng giảm)
const FORWARD = [[0, -1], [-1, 0], [0, 1], [1, 0]];

export class CameraRig {
  constructor(view) {
    this.view = view;
    this.target = new THREE.Vector3();
    this.radius = 12;
    this.phi = Math.acos(0.8 / Math.hypot(0.8, 0.9)); // góc từ trục đứng, tương ứng camera cao 0,8 và lùi 0,9
    this.theta = 0;
    this.home = { radius: 12, phi: this.phi };
    view.controls.addEventListener('end', () => this.snap());
  }

  setBoard(rows, cols) {
    this.target.set(cols / 2, 0, rows / 2);
    this.radius = Math.max(rows, cols) * 1.1 + 4;
    this.home = { radius: this.radius, phi: this.phi };
    this.theta = 0;
    this.apply();
  }

  // Đặt lại vị trí camera từ theta, phi, radius hiện tại.
  apply() {
    const offset = new THREE.Vector3().setFromSpherical(new THREE.Spherical(this.radius, this.phi, this.theta));
    this.view.camera.position.copy(this.target).add(offset);
    this.view.camera.lookAt(this.target);
    this.view.controls.target.copy(this.target);
    this.view.controls.update();
  }

  // Đọc lại góc từ camera (sau khi người chơi kéo chuột).
  readFromCamera() {
    const offset = this.view.camera.position.clone().sub(this.target);
    const sph = new THREE.Spherical().setFromVector3(offset);
    this.theta = sph.theta;
    this.phi = Math.min(Math.max(sph.phi, 0.3), 1.35);
    this.radius = sph.radius;
  }

  // Quay một nấc (steps = ±1), có hoạt ảnh.
  async rotateBy(steps) {
    this.readFromCamera();
    const from = this.theta;
    const to = from + steps * HALF_PI;
    await tween(260, (t) => { this.theta = from + (to - from) * t; this.apply(); });
    this.theta = Math.round(to / HALF_PI) * HALF_PI;
    this.apply();
  }

  // Sau khi kéo chuột: trượt về nấc 90° gần nhất.
  async snap() {
    this.readFromCamera();
    const from = this.theta;
    const to = Math.round(from / HALF_PI) * HALF_PI;
    if (Math.abs(to - from) < 1e-4) {
      this.apply();
      return;
    }
    await tween(220, (t) => { this.theta = from + (to - from) * t; this.apply(); }, easeInOut);
  }

  // Về góc và khoảng cách ban đầu.
  async reset() {
    this.readFromCamera();
    const fromTheta = this.theta;
    const toTheta = Math.round(fromTheta / (Math.PI * 2)) * Math.PI * 2;
    const fromRadius = this.radius;
    const toRadius = this.home.radius;
    const fromPhi = this.phi;
    const toPhi = this.home.phi;
    await tween(380, (t) => {
      this.theta = fromTheta + (toTheta - fromTheta) * t;
      this.radius = fromRadius + (toRadius - fromRadius) * t;
      this.phi = fromPhi + (toPhi - fromPhi) * t;
      this.apply();
    });
    this.theta = toTheta;
    this.radius = toRadius;
    this.phi = toPhi;
    this.apply();
  }

  // Hướng nhìn hiện tại (trên mặt bằng) và hướng "phải" tương ứng.
  axes() {
    const k = ((Math.round(this.theta / HALF_PI) % 4) + 4) % 4;
    const forward = FORWARD[k];
    const right = [-forward[1], forward[0]];
    return { forward, right };
  }

  // Phím mũi tên trên màn hình -> hướng trên bảng (hàng/cột).
  gridDirFromScreen(screenDir) {
    const { forward, right } = this.axes();
    const world = {
      up: forward,
      down: [-forward[0], -forward[1]],
      right,
      left: [-right[0], -right[1]],
    }[screenDir];
    return worldToGridDir(world);
  }

  // Hướng trên bảng -> hướng trên màn hình, để vẽ gợi ý.
  screenDirFromGrid(gridDir) {
    const world = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[gridDir];
    const { forward, right } = this.axes();
    const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
    if (dot(world, forward) > 0.5) return 'up';
    if (dot(world, forward) < -0.5) return 'down';
    if (dot(world, right) > 0.5) return 'right';
    return 'left';
  }
}

function worldToGridDir([dx, dz]) {
  if (dz < 0) return 'up';
  if (dz > 0) return 'down';
  return dx > 0 ? 'right' : 'left';
}
