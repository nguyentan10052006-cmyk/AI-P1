import * as THREE from 'three';
import { OrbitControls } from '../vendor/OrbitControls.js';

// Tạo renderer, ánh sáng và vòng lặp vẽ. Các hàm "ticker" đăng ký ở view.tickers được gọi mỗi khung hình.
export function createView(container, { shadows = true } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = shadows;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0f172a, 28, 70);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 500);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 4;
  controls.maxDistance = 60;

  scene.add(new THREE.HemisphereLight(0xdbeafe, 0x1e293b, 1.15));
  const sun = new THREE.DirectionalLight(0xffffff, 1.35);
  sun.position.set(6, 14, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.bias = -0.0005;
  scene.add(sun);
  scene.add(sun.target);

  // Mặt đất tối: các ô trống (void) trông như khoảng không.
  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(120, 64),
    new THREE.MeshStandardMaterial({ color: 0x0b1224, roughness: 1 }),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -3;
  ground.receiveShadow = true;
  scene.add(ground);

  const view = { renderer, scene, camera, controls, sun, tickers: [] };

  const resize = () => {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', resize);
  resize();

  renderer.setAnimationLoop((now) => {
    controls.update();
    view.tickers = view.tickers.filter((fn) => fn(now) !== false);
    renderer.render(scene, camera);
  });

  return view;
}

export function setShadows(view, enabled) {
  view.renderer.shadowMap.enabled = enabled;
  view.scene.traverse((obj) => {
    if (obj.material) obj.material.needsUpdate = true;
  });
}
