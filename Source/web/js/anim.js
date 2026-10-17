// Hoạt ảnh đơn giản: nội suy theo thời gian bằng requestAnimationFrame.

export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export function easeInOut(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

// Gọi onFrame(giá trị đã làm mượt từ 0 tới 1) trong khoảng ms mili giây, rồi kết thúc.
export function tween(ms, onFrame, ease = easeInOut) {
  return new Promise((resolve) => {
    if (ms <= 0) {
      onFrame(1);
      resolve();
      return;
    }
    const start = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - start) / ms);
      onFrame(ease(t));
      if (t < 1) requestAnimationFrame(frame);
      else resolve();
    };
    requestAnimationFrame(frame);
  });
}
