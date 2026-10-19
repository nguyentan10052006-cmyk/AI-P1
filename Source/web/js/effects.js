// Hiệu ứng hình: pháo giấy khi thắng, tia sáng từ công tắc tới cầu khi kích hoạt.
import * as THREE from 'three';

const CONFETTI = [0xfacc15, 0x38bdf8, 0xf472b6, 0x34d399, 0xfb7185, 0xa78bfa];

// Pháo giấy rơi từ điểm center, tự xóa sau khoảng 2,2 giây.
export function confetti(view, center) {
  const geo = new THREE.BoxGeometry(0.09, 0.02, 0.14);
  const pieces = [];
  for (let i = 0; i < 42; i++) {
    const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: CONFETTI[i % CONFETTI.length] }));
    mesh.position.set(center.x, center.y + 0.6, center.z);
    view.scene.add(mesh);
    pieces.push({
      mesh,
      vx: (Math.random() - 0.5) * 4,
      vy: 3 + Math.random() * 3,
      vz: (Math.random() - 0.5) * 4,
      rx: Math.random() * 6,
      rz: Math.random() * 6,
    });
  }
  const start = performance.now();
  let last = start;
  view.tickers.push((now) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const age = (now - start) / 1000;
    for (const p of pieces) {
      p.vy -= 9.8 * dt;
      p.mesh.position.x += p.vx * dt;
      p.mesh.position.y += p.vy * dt;
      p.mesh.position.z += p.vz * dt;
      p.mesh.rotation.x += p.rx * dt;
      p.mesh.rotation.z += p.rz * dt;
    }
    if (age < 2.2) return true;
    for (const p of pieces) {
      view.scene.remove(p.mesh);
      p.mesh.material.dispose();
    }
    geo.dispose();
    return false;
  });
}

// Tia sáng từ công tắc (from) tới các cầu nó điều khiển (targets). Mỗi toạ độ là [x, z].
export function linkFlash(view, from, targets, color) {
  if (targets.length === 0) return;
  const start = performance.now();
  const lines = targets.map(([x, z]) => {
    const geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(from[0], 0.4, from[1]),
      new THREE.Vector3(x, 0.4, z),
    ]);
    const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color, transparent: true, opacity: 1 }));
    view.scene.add(line);
    return line;
  });
  view.tickers.push((now) => {
    const t = (now - start) / 600;
    for (const line of lines) line.material.opacity = Math.max(0, 1 - t);
    if (t < 1) return true;
    for (const line of lines) {
      view.scene.remove(line);
      line.geometry.dispose();
      line.material.dispose();
    }
    return false;
  });
}
