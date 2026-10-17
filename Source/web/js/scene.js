import * as THREE from 'three';
import { OrbitControls } from '../vendor/OrbitControls.js';

// Tạo renderer, camera, ánh sáng và vòng lặp vẽ. Trả về các đối tượng cần dùng chung.
export function createView(container) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f172a);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 500);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.48; // không cho xoay xuống dưới mặt bàn

  scene.add(new THREE.HemisphereLight(0xffffff, 0x334155, 1.1));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4);
  sun.position.set(6, 12, 8);
  scene.add(sun);

  // Nền tối phía dưới: các ô trống (void) trông như khoảng không.
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 400),
    new THREE.MeshStandardMaterial({ color: 0x111827 }),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -3;
  scene.add(ground);

  const resize = () => {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', resize);
  resize();

  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });

  return { renderer, scene, camera, controls };
}

// Đặt camera nhìn cả bảng từ phía trước, hơi nghiêng xuống.
export function frameBoard(view, rows, cols) {
  const cx = cols / 2;
  const cz = rows / 2;
  const dist = Math.max(rows, cols) * 1.1 + 4;
  view.controls.target.set(cx, 0, cz);
  view.camera.position.set(cx, dist * 0.8, cz + dist * 0.9);
  view.controls.update();
}
