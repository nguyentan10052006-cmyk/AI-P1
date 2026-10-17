// Hoạt ảnh đơn giản. Mọi thời lượng đều nhân với motionScale để tôn trọng cài đặt
// "Giảm chuyển động" và "Tốc độ hoạt ảnh" (0 nghĩa là đặt ngay, không chạy hoạt ảnh).

let motionScale = 1;

export function setMotionScale(value) {
  motionScale = Math.max(0, value);
}

export function getMotionScale() {
  return motionScale;
}

export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms * motionScale));

export function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

export const easeIn = (t) => t * t;
export const linear = (t) => t;

// Gọi onFrame(giá trị đã làm mượt từ 0 tới 1) trong khoảng ms mili giây, rồi kết thúc.
export function tween(ms, onFrame, ease = easeInOut) {
  return new Promise((resolve) => {
    const duration = ms * motionScale;
    if (duration <= 0) {
      onFrame(1);
      resolve();
      return;
    }
    const start = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - start) / duration);
      onFrame(ease(t));
      if (t < 1) requestAnimationFrame(frame);
      else resolve();
    };
    requestAnimationFrame(frame);
  });
}
