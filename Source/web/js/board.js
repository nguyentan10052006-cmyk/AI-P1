// Bảng 3D: dựng các ô từ lưới của server, đồng bộ trạng thái cầu, vẽ vệt đường đi.
import * as THREE from 'three';
import { tween, easeIn, getMotionScale } from './anim.js';
import { buildBridge, buildTargetMarker, buildTile, LINK_PALETTE } from './tiles.js';
import { linkFlash } from './effects.js';

const key = (r, c) => `${r},${c}`;
const cellXZ = (r, c) => [c + 0.5, r + 0.5];

export class Board {
  constructor(view) {
    this.view = view;
    this.group = null;
    this.bridges = new Map();   // key -> {open, closed, isOpen, color, links}
    this.fragile = new Map();   // key -> nhóm hình của ô giòn
    this.switches = new Map();  // key -> {group, color, links: [[r, c]...], owners}
    this.trail = null;
    this.rows = 0;
    this.cols = 0;
  }

  clear() {
    if (!this.group) return;
    this.view.scene.remove(this.group);
    this.group.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    this.group = null;
    this.bridges.clear();
    this.fragile.clear();
    this.switches.clear();
  }

  // Dựng bảng cho màn. Các ô hiện dần từ điểm xuất phát ra ngoài.
  build(level, { animate = true } = {}) {
    this.clear();
    this.rows = level.grid.length;
    this.cols = level.grid[0].length;
    this.group = new THREE.Group();
    this.view.scene.add(this.group);
    const links = this.linkColors(level);
    const [sr, sc] = level.start.pos;
    const pops = [];

    level.grid.forEach((row, r) => {
      [...row].forEach((ch, c) => {
        if (ch === '.') return;
        const k = key(r, c);
        let obj;
        if (ch === 'b' || ch === 'B') {
          const color = links.bridgeColor.get(k) ?? LINK_PALETTE[0];
          const bridge = buildBridge(color);
          const isOpen = ch === 'B';
          bridge.open.visible = isOpen;
          bridge.closed.visible = !isOpen;
          this.bridges.set(k, { open: bridge.open, closed: bridge.closed, isOpen, color, owners: links.bridgeOwners.get(k) ?? [] });
          obj = bridge.group;
        } else if (ch === 'F') {
          obj = buildTile('F');
          this.fragile.set(k, obj);
        } else if (ch === 'o' || ch === 'x' || ch === '@') {
          const color = links.switchColor.get(k) ?? LINK_PALETTE[0];
          obj = buildTile(ch, color);
          this.switches.set(k, { group: obj, color, links: links.switchLinks.get(k) ?? [] });
          obj.userData.switchKey = k;
        } else {
          obj = buildTile(ch);
        }
        const [x, z] = cellXZ(r, c);
        obj.position.set(x, 0, z);
        this.group.add(obj);
        pops.push({ obj, dist: Math.abs(r - sr) + Math.abs(c - sc) });
      });
    });

    for (const sw of level.switches) {
      if (sw.kind !== 'split') continue;
      for (const [tr, tc] of sw.targets) {
        const marker = buildTargetMarker();
        marker.position.set(tc + 0.5, 0, tr + 0.5);
        this.group.add(marker);
      }
    }
    this.animateIn(pops, animate);
  }

  // Màu nối: mỗi công tắc một màu, cầu lấy màu của công tắc đầu tiên điều khiển nó.
  linkColors(level) {
    const bridgeColor = new Map();
    const bridgeOwners = new Map();
    const switchColor = new Map();
    const switchLinks = new Map();
    const ordered = [...level.switches].sort((a, b) => a.at[0] - b.at[0] || a.at[1] - b.at[1]);
    ordered.forEach((sw, i) => {
      const color = LINK_PALETTE[i % LINK_PALETTE.length];
      const k = key(sw.at[0], sw.at[1]);
      switchColor.set(k, color);
      switchLinks.set(k, sw.bridges ?? []);
      for (const [br, bc] of sw.bridges ?? []) {
        const bk = key(br, bc);
        if (!bridgeColor.has(bk)) bridgeColor.set(bk, color);
        bridgeOwners.set(bk, [...(bridgeOwners.get(bk) ?? []), k]);
      }
    });
    return { bridgeColor, bridgeOwners, switchColor, switchLinks };
  }

  animateIn(pops, animate) {
    if (!animate) return;
    const scale = getMotionScale();
    for (const p of pops) {
      p.obj.position.y = -1.2;
      setTimeout(() => {
        tween(380, (t) => { p.obj.position.y = -1.2 * (1 - t); });
      }, p.dist * 60 * scale);
    }
  }

  // Đưa mọi cầu về trạng thái trong openList. instant = true thì đặt ngay, không có hoạt ảnh.
  syncBridges(openList, instant = false) {
    const open = new Set(openList.map(([r, c]) => key(r, c)));
    const jobs = [];
    for (const [k, e] of this.bridges) {
      const on = open.has(k);
      if (instant) {
        e.isOpen = on;
        e.open.visible = on;
        e.closed.visible = !on;
        e.open.position.y = on ? 0 : -0.5;
        continue;
      }
      if (on === e.isOpen) continue;
      e.isOpen = on;
      if (on) {
        e.open.visible = true;
        e.closed.visible = false;
        jobs.push(tween(300, (t) => { e.open.position.y = -0.5 * (1 - t); }));
      } else {
        e.closed.visible = true;
        jobs.push(tween(300, (t) => { e.open.position.y = -0.5 * t; }).then(() => {
          if (!e.isOpen) e.open.visible = false;
        }));
      }
    }
    return Promise.all(jobs);
  }

  // Ô giòn vỡ: tấm nền rơi xuống và nghiêng.
  breakFragile([r, c]) {
    const obj = this.fragile.get(key(r, c));
    if (!obj) return Promise.resolve();
    const y0 = obj.position.y;
    return tween(420, (t) => {
      obj.position.y = y0 - 1.6 * t;
      obj.rotation.x = 0.5 * t;
    }, easeIn).then(() => { obj.visible = false; });
  }

  // Công tắc vừa kích hoạt: phóng to nhẹ và vẽ tia sáng tới các cầu nó điều khiển.
  flashSwitch([r, c]) {
    const sw = this.switches.get(key(r, c));
    if (!sw) return Promise.resolve();
    linkFlash(this.view, cellXZ(r, c), sw.links.map(([br, bc]) => cellXZ(br, bc)), sw.color);
    return tween(260, (t) => {
      sw.group.scale.setScalar(1 + 0.18 * Math.sin(Math.PI * t));
    }, (t) => t).then(() => sw.group.scale.setScalar(1));
  }

  // Làm sáng công tắc và các cầu nó điều khiển (khi rê chuột tới).
  highlightSwitch(cell, on) {
    const sw = cell ? this.switches.get(key(cell[0], cell[1])) : null;
    for (const [k, e] of this.bridges) {
      const linked = sw && sw.links.some(([br, bc]) => key(br, bc) === k);
      setEmissive(e.open, linked && on ? 0.8 : 0);
      setEmissive(e.closed, linked && on ? 0.8 : 0);
    }
    for (const s of this.switches.values()) setEmissive(s.group, sw === s && on ? 0.8 : 0.25);
  }

  // Tìm công tắc dưới con trỏ. ndc là tọa độ chuẩn hóa [-1, 1].
  pick(ndc, camera, raycaster) {
    raycaster.setFromCamera(new THREE.Vector2(ndc[0], ndc[1]), camera);
    const groups = [...this.switches.values()].map((s) => s.group);
    const hits = raycaster.intersectObjects(groups, true);
    if (hits.length === 0) return null;
    let obj = hits[0].object;
    while (obj && !obj.userData.switchKey) obj = obj.parent;
    return obj ? obj.userData.switchKey.split(',').map(Number) : null;
  }

  // Vệt đường đi của lời giải: chấm tại mỗi bước nối với nhau.
  drawTrail(cells, color) {
    this.clearTrail();
    const group = new THREE.Group();
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85 });
    const geo = new THREE.SphereGeometry(0.07, 10, 8);
    cells.forEach(([r, c]) => {
      const dot = new THREE.Mesh(geo, mat);
      dot.position.set(c + 0.5, 0.12, r + 0.5);
      group.add(dot);
    });
    if (cells.length > 1) {
      const pts = cells.map(([r, c]) => new THREE.Vector3(c + 0.5, 0.12, r + 0.5));
      group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.7 })));
    }
    this.view.scene.add(group);
    this.trail = group;
  }

  clearTrail() {
    if (!this.trail) return;
    this.view.scene.remove(this.trail);
    this.trail.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    this.trail = null;
  }
}

// Chỉnh độ sáng phát xạ của mọi vật liệu trong nhóm (không đổi nếu nhóm không có vật liệu).
function setEmissive(group, value) {
  if (!group) return;
  group.traverse((obj) => {
    if (obj.material && obj.material.emissiveIntensity !== undefined) {
      obj.material.emissiveIntensity = value;
    }
  });
}
