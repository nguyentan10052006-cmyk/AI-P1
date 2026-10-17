// Đầu vào: bàn phím, vuốt cảm ứng và điều hướng menu bằng phím mũi tên.

const KEYMAP = {
  ArrowUp: 'up', KeyW: 'up',
  ArrowDown: 'down', KeyS: 'down',
  ArrowLeft: 'left', KeyA: 'left',
  ArrowRight: 'right', KeyD: 'right',
  Space: 'switch',
  KeyR: 'restart',
  KeyZ: 'undo', Backspace: 'undo',
  KeyQ: 'rotateLeft', KeyE: 'rotateRight',
  KeyC: 'camReset',
  KeyH: 'hint',
  KeyM: 'mute',
  Escape: 'escape',
  Enter: 'enter', NumpadEnter: 'enter',
};

const ARROWS = new Set(['up', 'down', 'left', 'right']);

export class Input {
  // onAction(action, event) được gọi cho mỗi phím đã biết.
  constructor(onAction) {
    this.onAction = onAction;
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName) && e.code !== 'Escape') return;
      const action = KEYMAP[e.code];
      if (!action) return;
      if (ARROWS.has(action) || action === 'switch' || action === 'enter') e.preventDefault();
      this.onAction(action, e);
    });
  }

  // Vuốt trên màn hình cảm ứng: trả về hướng theo màn hình (up/down/left/right).
  attachSwipe(element, onSwipe) {
    let start = null;
    element.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'touch') start = { x: e.clientX, y: e.clientY };
    });
    element.addEventListener('pointerup', (e) => {
      if (!start) return;
      const dx = e.clientX - start.x;
      const dy = e.clientY - start.y;
      start = null;
      if (Math.hypot(dx, dy) < 30) return;
      if (Math.abs(dx) > Math.abs(dy)) onSwipe(dx > 0 ? 'right' : 'left');
      else onSwipe(dy > 0 ? 'down' : 'up');
    });
  }
}

// Di chuyển tiêu điểm trong một vùng (dùng cho menu): phím mũi tên chọn nút gần nhất theo hướng đó.
export function navigate(container, dir) {
  const items = [...container.querySelectorAll('button:not(:disabled), [tabindex="0"]')]
    .filter((el) => el.offsetParent !== null);
  if (items.length === 0) return;
  const current = items.includes(document.activeElement) ? document.activeElement : items[0];
  const c = center(current);
  let best = null;
  let bestScore = Infinity;
  for (const el of items) {
    if (el === current) continue;
    const p = center(el);
    const dx = p.x - c.x;
    const dy = p.y - c.y;
    const ahead = { up: -dy, down: dy, left: -dx, right: dx }[dir];
    if (ahead <= 1) continue;
    const score = Math.hypot(dx, dy) + Math.abs({ up: dx, down: dx, left: dy, right: dy }[dir]) * 2;
    if (score < bestScore) {
      bestScore = score;
      best = el;
    }
  }
  (best ?? items[(items.indexOf(current) + (dir === 'up' || dir === 'left' ? -1 : 1) + items.length) % items.length]).focus();
}

function center(el) {
  const r = el.getBoundingClientRect();
  return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
}
