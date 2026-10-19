// Lưu tiến trình và cài đặt trong localStorage. Mọi thao tác đều có try/catch:
// nếu trình duyệt chặn lưu thì game vẫn chạy, chỉ không nhớ tiến trình.

const PROGRESS_KEY = 'bloxorz.progress.v1';
const SETTINGS_KEY = 'bloxorz.settings.v1';

const DEFAULT_SETTINGS = {
  musicVol: 0.45,
  sfxVol: 0.8,
  muted: false,
  shadows: true,
  camKeys: true,
  reduceMotion: false,
  speed: 2,          // 1 = chậm, 2 = vừa, 3 = nhanh
  unlockAll: false,
  seenIntro: {},     // id màn -> đã xem thẻ giới thiệu
  seenControls: false,
};

function read(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? { ...fallback, ...JSON.parse(raw) } : { ...fallback };
  } catch {
    return { ...fallback };
  }
}

function write(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Không lưu được (chế độ riêng tư, bộ nhớ đầy): bỏ qua
  }
}

let settings = read(SETTINGS_KEY, DEFAULT_SETTINGS);
let progress = read(PROGRESS_KEY, { levels: {} });

export function getSettings() {
  return settings;
}

export function setSetting(name, value) {
  settings = { ...settings, [name]: value };
  write(SETTINGS_KEY, settings);
  return settings;
}

export function markIntroSeen(levelId) {
  settings = { ...settings, seenIntro: { ...settings.seenIntro, [levelId]: true } };
  write(SETTINGS_KEY, settings);
}

export function getProgress() {
  return progress;
}

// Số sao theo số bước: ★★★ không vượt par, ★★ không vượt 1,5 × par, ★ hoàn thành.
export function starsFor(steps, par) {
  if (!par) return 1;
  if (steps <= par) return 3;
  if (steps <= 1.5 * par) return 2;
  return 1;
}

export function levelRecord(levelId) {
  return progress.levels[levelId] ?? null;
}

// Ghi kết quả một lần thắng. Chỉ giữ kỷ lục tốt nhất.
export function recordWin(levelId, { steps, par, timeMs, falls }) {
  const stars = starsFor(steps, par);
  const old = progress.levels[levelId];
  const newBest = !old || steps < old.best;
  const entry = {
    best: newBest ? steps : old.best,
    stars: Math.max(stars, old?.stars ?? 0),
    bestTime: old?.bestTime && !newBest ? old.bestTime : timeMs,
    falls: newBest ? falls : old.falls,
  };
  progress = { ...progress, levels: { ...progress.levels, [levelId]: entry } };
  write(PROGRESS_KEY, progress);
  return { stars, newBest, entry };
}

export function totalStars(levels) {
  return levels.reduce((sum, lv) => sum + (progress.levels[lv.id]?.stars ?? 0), 0);
}

// Màn chính và thử thách luôn mở. Bonus mở khi đủ sao (hoặc bật mở khóa tất cả).
export function isUnlocked(level, stars) {
  if (level.kind !== 'bonus') return true;
  return settings.unlockAll || stars >= level.unlock_stars;
}

export function clearProgress() {
  progress = { levels: {} };
  write(PROGRESS_KEY, progress);
}
