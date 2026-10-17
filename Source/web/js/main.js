// Bộ điều khiển chính: nối server, bảng, khối và giao diện lại với nhau.
// Mọi luật chơi nằm ở server. Ở đây chỉ gửi lệnh, nhận trạng thái và vẽ lại.
import { listLevels, getLevel, sendStep, solve } from './api.js';
import { createView, frameBoard } from './scene.js';
import { Board } from './board.js';
import { Block } from './block.js';
import { wait } from './anim.js';
import * as ui from './ui.js';

const ROLL_MS = [420, 260, 170, 100, 50];   // ứng với tốc độ 1..5
const AFTER_FALL_MS = 1200;                 // chờ sau khi rơi rồi tự chơi lại
const KEY_DIR = {
  ArrowUp: 'up', KeyW: 'up',
  ArrowDown: 'down', KeyS: 'down',
  ArrowLeft: 'left', KeyA: 'left',
  ArrowRight: 'right', KeyD: 'right',
};
const DELTA = { up: [-1, 0], down: [1, 0], left: [0, -1], right: [0, 1] };
const FALL_TEXT = {
  off_board: 'Khối rơi khỏi bảng!',
  void: 'Khối rơi xuống khoảng trống!',
  bridge_closed: 'Khối rơi xuống cầu đang đóng!',
  fragile: 'Ô giòn đã vỡ, khối rơi!',
};

const view = createView(document.getElementById('stage'));
const board = new Board(view.scene);
const block = new Block(view.scene);

const game = {
  levelIds: [],
  id: null,        // id màn đang chơi
  data: null,      // dữ liệu đầy đủ của màn (lưới, công tắc, trạng thái đầu)
  start: null,     // trạng thái đầu của màn
  state: null,     // trạng thái hiện tại
  selected: null,  // ô của khối con đang được điều khiển (khi đã tách)
  history: [],     // các bước đã đi, dùng cho Hoàn tác
  busy: false,     // đang chạy hoạt ảnh hoặc gọi server
  playing: false,  // đang phát lời giải của solver
  queued: null,    // một lệnh lăn chờ, khi người chơi bấm lúc đang chạy hoạt ảnh
  runToken: 0,     // tăng lên khi bấm Dừng để vòng phát lại thoát
  won: false,
};

const clone = (obj) => JSON.parse(JSON.stringify(obj));
const sameCell = (a, b) => Boolean(a && b && a[0] === b[0] && a[1] === b[1]);
const cellsOf = (state) => (state.orient === 'split' ? [state.pos, state.pos2] : [state.pos]);
const speedMs = () => ROLL_MS[Number(ui.speedValue()) - 1] ?? ROLL_MS[2];

// Chỉ số khối đang được điều khiển trong trạng thái hiện tại (0 khi chưa tách).
function activeIndex() {
  if (!game.state || game.state.orient !== 'split') return 0;
  const idx = cellsOf(game.state).findIndex((cell) => sameCell(cell, game.selected));
  return idx < 0 ? 0 : idx;
}

function refreshHighlight() {
  const split = game.state && game.state.orient === 'split';
  block.highlight(split ? cellsOf(game.state)[activeIndex()] : null);
}

function setBusy(busy) {
  game.busy = busy;
  ui.setBusy(busy);
}

function hasNext() {
  const idx = game.levelIds.indexOf(game.id);
  return idx >= 0 && idx < game.levelIds.length - 1;
}

async function loadLevel(id) {
  try {
    const data = await getLevel(id);
    game.id = id;
    game.data = data;
    game.start = data.start;
    ui.setLevelId(id);
    frameBoard(view, data.grid.length, data.grid[0].length);
    restart();
    ui.setStatus(`Màn ${id}: ${data.name}. Lăn khối tới lỗ đích để thắng.`);
  } catch (err) {
    ui.setStatus(`Không tải được màn ${id}: ${err.message}`, 'err');
  }
}

// Dựng lại bảng và đưa khối về trạng thái đầu. Dựng lại bảng để trả lại ô giòn đã vỡ.
function restart() {
  board.build(game.data);
  game.state = clone(game.start);
  game.selected = null;
  game.history = [];
  game.won = false;
  game.queued = null;
  block.snap(game.state);
  board.syncBridges(game.state.open, true);
  refreshHighlight();
  ui.showNext(false);
}

function nextLevel() {
  const idx = game.levelIds.indexOf(game.id);
  if (idx >= 0 && idx < game.levelIds.length - 1) loadLevel(game.levelIds[idx + 1]);
}

function buildAction(dir) {
  return { dir, cube: game.state.orient === 'split' ? activeIndex() : null };
}

// Người chơi bấm phím: gửi lệnh tới server, rồi chạy hoạt ảnh.
function playerMove(dir) {
  if (!game.state || game.won || game.playing) return;
  if (game.busy) {
    game.queued = dir;
    return;
  }
  runPlayerMove(dir);
}

async function runPlayerMove(dir) {
  setBusy(true);
  try {
    const action = buildAction(dir);
    const data = await sendStep(game.id, game.state, action);
    await applyStep(action, data);
  } catch (err) {
    ui.setStatus(`Lỗi: ${err.message}`, 'err');
  } finally {
    setBusy(false);
  }
  const next = game.queued;
  game.queued = null;
  if (next) playerMove(next);
}

// Áp dụng một bước đã có kết quả từ server: hoạt ảnh lăn, công tắc, rơi hoặc thắng.
// Trả về 'ok', 'fell' hoặc 'won'.
async function applyStep(action, data) {
  const before = game.state;
  const cubeIndex = action.cube ?? 0;
  const splitHappened = data.events.some((e) => e.type === 'split');
  game.history.push({ state: before, selected: game.selected });

  await block.roll(before, action.dir, speedMs(), cubeIndex);
  block.snap(data.moved);
  board.syncBridges(data.state.open);
  for (const ev of data.events) {
    if (ev.type === 'fragile_broken') board.breakFragile(ev.at);
    if (ev.type === 'switch') board.flashSwitch(ev.at);
  }

  if (data.status === 'fell') {
    const reason = data.events.find((e) => e.type === 'fell')?.reason;
    ui.setStatus(FALL_TEXT[reason] ?? 'Khối đã rơi!', 'err');
    await block.fall();
    await wait(AFTER_FALL_MS);
    restart();
    ui.setStatus('Đã đặt lại màn. Thử cách khác nhé!', 'warn');
    return 'fell';
  }

  game.state = data.state;
  game.selected = nextSelected(action, before, data, splitHappened);
  block.snap(data.state);

  if (data.status === 'won') {
    game.won = true;
    ui.setStatus(`Hoàn thành màn ${game.id} sau ${game.history.length} bước!`, 'ok');
    ui.showNext(hasNext());
    await block.sink();
    return 'won';
  }

  refreshHighlight();
  ui.setStatus(describe(data.events, game.history.length));
  return 'ok';
}

// Ô của khối con được chọn sau bước đi: khối vừa lăn, hoặc khối đầu tiên khi vừa tách.
function nextSelected(action, before, data, splitHappened) {
  if (data.state.orient !== 'split') return null;
  if (splitHappened) return data.state.pos;
  const [r, c] = cellsOf(before)[action.cube];
  const [dr, dc] = DELTA[action.dir];
  return [r + dr, c + dc];
}

function describe(events, moves) {
  const parts = [];
  if (events.some((e) => e.type === 'switch')) parts.push('Công tắc đã kích hoạt');
  if (events.some((e) => e.type === 'split')) parts.push('Khối đã tách: bấm Space để đổi khối con');
  if (events.some((e) => e.type === 'merge')) parts.push('Hai khối đã ghép lại');
  return parts.length ? parts.join(' · ') : `Bước ${moves}`;
}

function undo() {
  if (game.busy || game.history.length === 0) return;
  const prev = game.history.pop();
  game.state = prev.state;
  game.selected = prev.selected;
  game.won = false;
  block.snap(game.state);
  board.syncBridges(game.state.open, true);
  refreshHighlight();
  ui.showNext(false);
  ui.setStatus('Đã hoàn tác 1 bước.');
}

function toggleCube() {
  if (game.busy || !game.state || game.state.orient !== 'split') return;
  game.selected = cellsOf(game.state)[1 - activeIndex()];
  refreshHighlight();
}

// Gọi solver trên trạng thái hiện tại rồi phát lại lời giải bằng đúng hoạt ảnh của người chơi.
async function solveWith(algo) {
  if (game.busy || !game.state) return;
  if (game.won) {
    ui.setStatus('Màn này đã xong. Bấm Chơi lại hoặc chọn màn khác.', 'warn');
    return;
  }
  const token = ++game.runToken;
  const label = algo.toUpperCase();
  game.playing = true;
  game.queued = null;
  setBusy(true);
  ui.setPlaying(true);
  ui.setStatus(`${label} đang tìm lời giải...`);
  try {
    const res = await solve(game.id, game.state, algo);
    ui.addResult(game.id, algo, res);
    if (res.error) {
      ui.setStatus(`${label}: ${res.error}`, 'err');
      return;
    }
    if (!res.found) {
      ui.setStatus(`${label}: không tìm thấy lời giải.`, 'warn');
      return;
    }
    ui.setStatus(`${label}: lời giải ${res.stats.length} bước, đang phát lại...`);
    for (const step of res.steps) {
      if (token !== game.runToken) {
        ui.setStatus('Đã dừng phát lại.', 'warn');
        break;
      }
      const outcome = await applyStep(step.action, step);
      if (outcome !== 'ok') break;
    }
  } catch (err) {
    ui.setStatus(`Lỗi: ${err.message}`, 'err');
  } finally {
    game.playing = false;
    setBusy(false);
    ui.setPlaying(false);
  }
}

function onKey(e) {
  if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
  const dir = KEY_DIR[e.code];
  if (dir) {
    e.preventDefault();
    playerMove(dir);
  } else if (e.code === 'Space') {
    e.preventDefault();
    toggleCube();
  } else if (e.code === 'KeyR' && !game.busy) {
    restart();
    ui.setStatus('Đã chơi lại màn.');
  } else if (e.code === 'KeyZ') {
    undo();
  }
}

function bindControls() {
  document.getElementById('level').addEventListener('change', () => {
    if (!game.busy) loadLevel(ui.levelId());
  });
  document.getElementById('btn-new').addEventListener('click', () => loadLevel(ui.levelId()));
  document.getElementById('btn-restart').addEventListener('click', () => {
    if (game.busy) return;
    restart();
    ui.setStatus('Đã chơi lại màn.');
  });
  document.getElementById('btn-undo').addEventListener('click', undo);
  document.getElementById('btn-next').addEventListener('click', nextLevel);
  document.getElementById('btn-stop').addEventListener('click', () => { game.runToken++; });
  document.querySelectorAll('button.solve').forEach((btn) => {
    btn.addEventListener('click', () => solveWith(btn.dataset.algo));
  });
  window.addEventListener('keydown', onKey);
}

async function init() {
  bindControls();
  try {
    const { levels } = await listLevels();
    game.levelIds = levels.map((lv) => lv.id);
    ui.fillLevels(levels);
    // Mở thẳng màn: http://localhost:8000/?level=08
    const requested = new URLSearchParams(location.search).get('level');
    const first = levels.find((lv) => lv.id === requested) ?? levels[0];
    await loadLevel(first.id);
  } catch (err) {
    ui.setStatus(`Không kết nối được server: ${err.message}`, 'err');
  }
}

init();
