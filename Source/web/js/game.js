// Bộ điều khiển chính: trạng thái màn chơi, luật (qua server), hoạt ảnh và luồng giữa các màn hình.
// Mọi luật nằm ở server. Ở đây chỉ gửi lệnh, nhận trạng thái mới và vẽ lại.
import * as THREE from 'three';
import { getLevel, listLevels, sendStep, solve, ServerError } from './api.js';
import { createView, setShadows } from './scene.js';
import { CameraRig } from './camera.js';
import { Board } from './board.js';
import { Block } from './block.js';
import { Audio } from './audio.js';
import { Input } from './input.js';
import { Screens } from './screens.js';
import { AIPanel } from './ai-panel.js';
import { confetti } from './effects.js';
import { setMotionScale, wait } from './anim.js';
import * as store from './storage.js';
import { CHAPTERS, FALL_TEXT, KIND_TEXT, S, TILE_TEXT } from './strings.js';

const ROLL_MS = { 1: 480, 2: 280, 3: 160 };   // tốc độ hoạt ảnh khi người chơi lăn
const AFTER_FALL_MS = 900;
const HINT_ALGOS = ['astar', 'bfs', 'ucs', 'dfs'];
const DIRS = ['up', 'down', 'left', 'right'];
const DEMO_LEVEL = '1-1';
const DEMO_ACTIONS = ['right', 'right', 'right', 'right'];

const clone = (obj) => JSON.parse(JSON.stringify(obj));
const sameCell = (a, b) => Boolean(a && b && a[0] === b[0] && a[1] === b[1]);
const cellsOf = (state) => (state.orient === 'split' ? [state.pos, state.pos2] : [state.pos]);

export function formatTime(ms) {
  const total = Math.floor(ms / 1000);
  const minutes = String(Math.floor(total / 60)).padStart(2, '0');
  const seconds = String(total % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

export class Game {
  constructor() {
    this.stage = document.getElementById('stage');
    this.settings = store.getSettings();
    this.view = createView(this.stage, { shadows: this.settings.shadows });
    this.rig = new CameraRig(this.view);
    this.board = new Board(this.view);
    this.block = new Block(this.view);
    this.audio = new Audio();
    this.raycaster = new THREE.Raycaster();
    this.screens = new Screens({
      onAction: (action, el) => this.onAction(action, el),
      onSetting: (name, value) => this.onSetting(name, value),
    });
    this.ai = new AIPanel(this);
    this.input = new Input((action, ev) => this.onKey(action, ev));

    this.levels = [];
    this.levelId = null;
    this.level = null;     // dữ liệu đầy đủ của màn từ server
    this.start = null;     // trạng thái đầu của màn
    this.state = null;     // trạng thái hiện tại
    this.selected = null;  // ô của khối con đang điều khiển
    this.history = [];     // các bước đã đi, dùng cho Hoàn tác
    this.falls = 0;
    this.won = false;
    this.lastWin = null;
    this.mode = 'loading';
    this.stack = [];
    this.busy = false;     // đang gửi lệnh hoặc chạy hoạt ảnh của người chơi
    this.automating = false; // đang phát lời giải của AI
    this.queued = null;
    this.timeMs = 0;
    this.timerStart = null;
    this.demoToken = 0;
    this.introQueue = [];
    this.hoverSwitch = null;

    this.applySettings();
    this.screens.setHud({ muted: this.settings.muted });
    this.stage.addEventListener('pointermove', (e) => this.onHover(e));
    this.stage.addEventListener('pointerdown', () => this.audio.unlock());
    this.input.attachSwipe(this.stage, (dir) => this.movePlayer(dir));
    setInterval(() => this.tickClock(), 250);
  }

  // ---------- khởi động ----------
  async boot() {
    this.mode = 'loading';
    this.screens.show('loading');
    try {
      const { levels } = await listLevels();
      this.levels = levels;
    } catch (err) {
      this.showError(err);
      return;
    }
    // Mở thẳng một màn bằng ?level=2-1 (dùng khi thử màn hoặc quay video).
    const requested = new URLSearchParams(location.search).get('level');
    if (requested && this.levels.some((lv) => lv.id === requested)) {
      this.play(requested);
      return;
    }
    this.goMenu();
  }

  showError(err) {
    const offline = err instanceof ServerError;
    this.mode = 'error';
    this.stack = [];
    this.screens.setError(
      S.error.title,
      offline ? S.error.body : err.message,
      S.error.command,
    );
    this.screens.show('error');
    this.screens.showHud(false);
  }

  applySettings() {
    const s = store.getSettings();
    this.settings = s;
    setMotionScale(s.reduceMotion ? 0 : 1);
    this.audio.setVolumes({ musicVol: s.musicVol, sfxVol: s.sfxVol, muted: s.muted });
    setShadows(this.view, s.shadows);
    this.screens.fillSettings(s);
    this.screens.setHud({ muted: s.muted });
  }

  onSetting(name, value) {
    store.setSetting(name, value);
    this.applySettings();
    if (name === 'unlockAll' || name === 'muted') this.renderChapters();
  }

  // ---------- chuyển màn hình ----------
  // Mỗi chế độ là một màn hình: menu, chapters, help, settings, paused, playing, won, fell, intro.
  pushMode(next) {
    this.stack.push(this.mode);
    this.enterMode(next);
  }

  popMode() {
    this.enterMode(this.stack.pop() ?? 'menu');
  }

  enterMode(mode) {
    this.mode = mode;
    this.screens.showHud(mode === 'playing');
    if (mode !== 'playing') this.stopTimer();
    switch (mode) {
      case 'menu':
        this.stack = [];
        this.screens.show('menu');
        this.startDemo();
        break;
      case 'chapters':
        this.renderChapters();
        this.screens.show('chapters');
        break;
      case 'help':
        this.screens.renderHelp();
        this.screens.show('help');
        break;
      case 'settings':
        this.screens.fillSettings(store.getSettings());
        this.screens.show('settings');
        break;
      case 'paused':
        this.screens.show('pause');
        break;
      case 'playing':
        this.screens.hide();
        this.startTimer();
        this.updateHud();
        break;
      case 'won':
        this.screens.fillWin(this.lastWin);
        this.screens.show('win');
        break;
      case 'fell':
        this.screens.show('fall');
        break;
      default:
        break;
    }
  }

  goMenu() {
    this.stack = [];
    this.enterMode('menu');
  }

  openPause() {
    if (this.mode !== 'playing') return;
    this.pushMode('paused');
  }

  // Màn hình chọn màn: luôn hiển thị tiến trình mới nhất.
  renderChapters() {
    const stars = (id) => store.levelRecord(id)?.stars ?? 0;
    const totalStars = store.totalStars(this.levels);
    const nextId = this.levels.find((lv) => store.isUnlocked(lv, totalStars) && !store.levelRecord(lv.id))?.id ?? null;
    this.screens.renderChapters(this.levels, {
      starsOf: stars,
      isUnlocked: (lv) => store.isUnlocked(lv, totalStars),
      recordOf: (id) => store.levelRecord(id),
      nextId,
      totalStars,
      totalMax: this.levels.length * 3,
    });
  }

  // ---------- màn chơi ----------
  async play(id) {
    this.stack = [];
    await this.loadLevel(id);
  }

  async loadLevel(id) {
    this.stopDemo();
    let data;
    try {
      data = await getLevel(id);
    } catch (err) {
      this.handleError(err);
      return;
    }
    this.levelId = id;
    this.level = data;
    this.start = data.start;
    this.audio.duck(false);
    this.board.build(data);
    this.rig.setBoard(data.grid.length, data.grid[0].length);
    this.ai.reset(id);
    this.resetRun();
    this.state = clone(this.start);
    this.block.snap(this.state);
    this.board.syncBridges(this.state.open, true);
    this.screens.hintDirection(null);
    this.queueIntros(data);
    if (this.introQueue.length) this.showNextIntro();
    else this.enterMode('playing');
  }

  // Chơi lại từ đầu màn (không cần tải lại dữ liệu).
  restartLevel() {
    if (!this.level || this.automating) return;
    this.stack = [];
    this.ai.reset(this.levelId);
    this.resetRun();
    this.state = clone(this.start);
    this.board.build(this.level, { animate: false });
    this.block.snap(this.state);
    this.board.syncBridges(this.state.open, true);
    this.screens.hintDirection(null);
    this.enterMode('playing');
    this.screens.toast(S.toast.reset);
  }

  resetRun() {
    this.history = [];
    this.selected = null;
    this.falls = 0;
    this.won = false;
    this.lastWin = null;
    this.timeMs = 0;
    this.timerStart = null;
    this.queued = null;
  }

  // Đưa bảng về một trạng thái bất kỳ (dùng khi phát lại lời giải từ đầu).
  async resetBoardTo(state) {
    this.history = [];
    this.selected = null;
    this.state = clone(state);
    this.board.build(this.level, { animate: false });
    this.block.snap(this.state);
    this.board.syncBridges(this.state.open, true);
    this.updateHud();
  }

  startState() {
    return clone(this.start);
  }

  // Màn đứng ngay sau màn hiện tại trong danh sách (kể cả khi còn khóa), hoặc null nếu là màn cuối.
  nextLevelInfo() {
    const idx = this.levels.findIndex((lv) => lv.id === this.levelId);
    return idx >= 0 ? this.levels[idx + 1] ?? null : null;
  }

  nextLevelId() {
    const next = this.nextLevelInfo();
    return next && store.isUnlocked(next, store.totalStars(this.levels)) ? next.id : null;
  }

  // ---------- giới thiệu ----------
  queueIntros(data) {
    this.introQueue = [];
    if (!store.getSettings().seenControls) {
      this.introQueue.push({ title: S.intro.controlsTitle, text: S.intro.controls, kind: null, onDismiss: () => store.setSetting('seenControls', true) });
    }
    if (data.intro && !store.getSettings().seenIntro[data.id]) {
      const special = ['F', 'o', 'x', '@', 'b'].find((ch) => data.grid.some((row) => row.includes(ch)));
      this.introQueue.push({
        title: special ? `Mới gặp: ${TILE_TEXT[special].name}` : 'Luật mới',
        text: data.intro,
        kind: special ?? null,
        onDismiss: () => store.markIntroSeen(data.id),
      });
    }
  }

  showNextIntro() {
    const item = this.introQueue.shift();
    if (!item) {
      this.enterMode('playing');
      return;
    }
    this.currentIntro = item;
    this.mode = 'intro';
    this.screens.showHud(false);
    this.screens.fillIntro(item);
    this.screens.show('intro');
  }

  dismissIntro() {
    this.currentIntro?.onDismiss();
    this.currentIntro = null;
    this.showNextIntro();
  }

  // ---------- lăn khối ----------
  activeIndex() {
    if (!this.state || this.state.orient !== 'split') return 0;
    const idx = cellsOf(this.state).findIndex((cell) => sameCell(cell, this.selected));
    return idx < 0 ? 0 : idx;
  }

  movePlayer(screenDir) {
    if (this.mode !== 'playing') return;
    if (this.automating) {
      this.screens.toast(S.toast.busy);
      return;
    }
    const dir = this.settings.camKeys ? this.rig.gridDirFromScreen(screenDir) : screenDir;
    this.screens.hintDirection(null);
    if (this.busy) {
      this.queued = dir;
      return;
    }
    this.runMove(dir);
  }

  async runMove(dir) {
    this.busy = true;
    try {
      const action = { dir, cube: this.state.orient === 'split' ? this.activeIndex() : null };
      const data = await sendStep(this.levelId, this.state, action);
      await this.animateStep(action, data, { rollMs: ROLL_MS[this.settings.speed] });
    } catch (err) {
      this.handleError(err);
    } finally {
      this.busy = false;
    }
    const next = this.queued;
    this.queued = null;
    if (next && this.mode === 'playing' && !this.automating) this.runMove(next);
  }

  // Hoạt ảnh một bước đã có kết quả từ server. Trả về 'ok', 'fell' hoặc 'won'.
  async animateStep(action, data, { rollMs = 280 } = {}) {
    const before = this.state;
    const cubeIndex = action.cube ?? 0;
    this.history.push({ state: before, selected: this.selected });
    const nextSelected = this.nextSelected(action, before, data);

    this.audio.move();
    await this.block.roll(before, action.dir, rollMs, cubeIndex);
    this.block.snap(data.moved, nextSelected);
    this.board.syncBridges(data.state.open);
    for (const ev of data.events) this.playEvent(ev);

    if (data.status === 'fell') {
      this.state = data.state;
      this.mode = 'animating';
      this.audio.fall();
      await this.block.fall();
      await wait(AFTER_FALL_MS);
      this.enterFall(data.events.find((e) => e.type === 'fell')?.reason);
      return 'fell';
    }

    this.state = data.state;
    this.selected = nextSelected;
    this.block.snap(data.state, nextSelected);
    this.updateHud();

    if (data.status === 'won') {
      this.won = true;
      this.mode = 'animating';
      this.audio.win();
      this.audio.duck(true);
      await this.block.sink();
      this.finishWin();
      return 'won';
    }
    return 'ok';
  }

  playEvent(ev) {
    switch (ev.type) {
      case 'switch':
        this.board.flashSwitch(ev.at);
        this.audio.click();
        break;
      case 'fragile_broken':
        this.board.breakFragile(ev.at);
        this.audio.crack();
        break;
      case 'split':
        this.audio.split();
        this.screens.toast(S.toast.split);
        break;
      case 'merge':
        this.audio.merge();
        this.screens.toast(S.toast.merge);
        break;
      default:
        break;
    }
  }

  // Khối con được chọn sau bước đi: khối vừa lăn, hoặc khối đầu tiên khi vừa tách.
  nextSelected(action, before, data) {
    if (data.state.orient !== 'split') return null;
    if (data.events.some((e) => e.type === 'split')) return data.state.pos;
    const [r, c] = cellsOf(before)[action.cube ?? 0];
    const [dr, dc] = { up: [-1, 0], down: [1, 0], left: [0, -1], right: [0, 1] }[action.dir];
    return [r + dr, c + dc];
  }

  // ---------- kết thúc màn ----------
  enterFall(reason) {
    this.falls += 1;
    this.stack = [];
    this.screens.fillFall(FALL_TEXT[reason] ?? 'Khối đã rơi.');
    this.enterMode('fell');
  }

  finishWin() {
    const steps = this.history.length;
    const timeMs = this.elapsed();
    const par = this.level.par;
    const { stars, newBest } = store.recordWin(this.levelId, { steps, par, timeMs, falls: this.falls });
    const next = this.nextLevelInfo();
    const nextLocked = !!next && !store.isUnlocked(next, store.totalStars(this.levels));
    this.lastWin = {
      steps,
      par,
      time: formatTime(timeMs),
      falls: this.falls,
      stars,
      newBest,
      lastLevel: !next,
      nextLocked,
      needStars: next?.unlock_stars ?? 0,
    };
    this.stack = [];
    const goal = this.level.goal;
    confetti(this.view, { x: goal[1] + 0.5, y: 0, z: goal[0] + 0.5 });
    this.enterMode('won');
  }

  nextLevel() {
    const next = this.nextLevelId();
    if (next) this.play(next);
    else this.openChapters();
  }

  undo() {
    if (this.busy || this.automating) return;
    if (this.history.length === 0) {
      this.screens.toast(S.toast.undo);
      return;
    }
    const prev = this.history.pop();
    this.state = prev.state;
    this.selected = prev.selected;
    this.won = false;
    this.lastWin = null;
    this.queued = null;
    this.board.build(this.level, { animate: false });
    this.block.snap(this.state, this.currentActiveCell());
    this.board.syncBridges(this.state.open, true);
    this.screens.hintDirection(null);
    this.audio.ui();
    this.enterMode('playing');
    this.screens.toast(S.toast.undo);
  }

  currentActiveCell() {
    return this.state.orient === 'split' ? cellsOf(this.state)[this.activeIndex()] : null;
  }

  toggleCube() {
    if (this.mode !== 'playing' || this.busy || this.automating) return;
    if (this.state.orient !== 'split') return;
    const cells = cellsOf(this.state);
    this.selected = cells[1 - this.activeIndex()];
    this.block.snap(this.state, this.currentActiveCell());
    this.audio.ui();
  }

  // Gợi ý nước đi tiếp theo, lấy từ solver đầu tiên có kết quả.
  async hint() {
    if (this.mode !== 'playing' || this.busy || this.automating) return;
    this.screens.toast(S.ai.hintSearching);
    for (const algo of HINT_ALGOS) {
      let res;
      try {
        res = await solve(this.levelId, this.state, algo);
      } catch (err) {
        this.handleError(err);
        return;
      }
      if (res.found && res.steps?.length) {
        const screenDir = this.settings.camKeys
          ? this.rig.screenDirFromGrid(res.steps[0].action.dir)
          : res.steps[0].action.dir;
        this.screens.hintDirection(screenDir);
        this.screens.toast(`${S.ai.hintFound(`${S.dirs[screenDir]} ${S.dirArrows[screenDir]}`)} (${algo.toUpperCase()})`);
        return;
      }
    }
    this.screens.toast(S.ai.hintNone, 'warn');
  }

  // ---------- đồng hồ và HUD ----------
  startTimer() {
    if (this.timerStart === null) this.timerStart = performance.now();
  }

  stopTimer() {
    if (this.timerStart !== null) {
      this.timeMs += performance.now() - this.timerStart;
      this.timerStart = null;
    }
  }

  elapsed() {
    return this.timeMs + (this.timerStart !== null ? performance.now() - this.timerStart : 0);
  }

  tickClock() {
    if (this.mode === 'playing') this.screens.setHud({ time: formatTime(this.elapsed()) });
  }

  updateHud() {
    if (!this.level) return;
    const lv = this.level;
    const chapter = lv.kind === 'main' ? `Chương ${lv.chapter} · ${CHAPTERS[lv.chapter]}` : KIND_TEXT[lv.kind];
    this.screens.setHud({
      chapter,
      name: lv.name,
      steps: this.history.length,
      par: lv.par,
      time: formatTime(this.elapsed()),
      switchVisible: Boolean(this.state && this.state.orient === 'split'),
    });
  }

  handleError(err) {
    if (err instanceof ServerError) this.screens.toast(S.toast.offline, 'err');
    else this.screens.toast(err.message, 'err');
  }

  // Di chuột lên công tắc: làm sáng các cầu nó điều khiển.
  onHover(e) {
    if (this.mode !== 'playing') return;
    const rect = this.stage.getBoundingClientRect();
    const ndc = [((e.clientX - rect.left) / rect.width) * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1];
    const cell = this.board.pick(ndc, this.view.camera, this.raycaster);
    const key = cell ? cell.join(',') : null;
    if (key === this.hoverSwitch) return;
    this.hoverSwitch = key;
    this.board.highlightSwitch(cell, cell !== null);
  }

  // ---------- phím và nút ----------
  onKey(action, ev) {
    this.audio.unlock();
    switch (this.mode) {
      case 'playing':
        return this.onPlayingKey(action);
      case 'animating':
        return undefined;   // đang chạy hoạt ảnh thắng/rơi: bỏ qua phím
      case 'intro':
        if (action === 'enter' || action === 'escape') this.dismissIntro();
        return undefined;
      case 'fell':
        if (action === 'undo' || action === 'enter') return this.undo();
        if (action === 'restart') return this.restartLevel();
        if (action === 'escape') return this.undo();
        return this.navigateOrActivate(action);
      case 'won':
        if (action === 'restart') return this.restartLevel();
        if (action === 'escape') return this.openChapters();
        return this.navigateOrActivate(action);
      case 'error':
        if (action === 'enter') return this.boot();
        return undefined;
      case 'loading':
        return undefined;
      default:
        if (action === 'escape') return this.popMode();
        if (action === 'mute') return this.onSetting('muted', !this.settings.muted);
        return this.navigateOrActivate(action);
    }
  }

  onPlayingKey(action) {
    if (DIRS.includes(action)) return this.movePlayer(action);
    switch (action) {
      case 'switch': return this.toggleCube();
      case 'restart': return this.restartLevel();
      case 'undo': return this.undo();
      case 'rotateLeft': return this.rig.rotateBy(-1);
      case 'rotateRight': return this.rig.rotateBy(1);
      case 'camReset': return this.rig.reset();
      case 'hint': return this.hint();
      case 'escape': return this.openPause();
      case 'mute': return this.onSetting('muted', !this.settings.muted);
      default: return undefined;
    }
  }

  navigateOrActivate(action) {
    if (DIRS.includes(action)) return this.screens.navigate(action);
    if (action === 'enter') return this.screens.activate();
    if (action === 'escape') return this.popMode();
    return undefined;
  }

  onAction(action, el) {
    this.audio.unlock();
    this.audio.ui();
    switch (action) {
      case 'move': return this.movePlayer(el.dataset.dir);
      case 'play': return this.play(el.dataset.level);
      case 'menu-play': return this.continueGame();
      case 'menu-levels': return this.openChapters();
      case 'menu-help': return this.pushMode('help');
      case 'menu-settings': return this.pushMode('settings');
      case 'back': return this.popMode();
      case 'resume': return this.popMode();
      case 'pause': return this.openPause();
      case 'restart': return this.restartLevel();
      case 'replay': return this.restartLevel();
      case 'chapters': return this.openChapters();
      case 'help': return this.pushMode('help');
      case 'settings': return this.pushMode('settings');
      case 'menu': return this.goMenu();
      case 'next': return this.nextLevel();
      case 'undo': return this.undo();
      case 'camReset': return this.rig.reset();
      case 'mute': return this.onSetting('muted', !this.settings.muted);
      case 'switch': return this.toggleCube();
      case 'hint': return this.hint();
      case 'retry': return this.boot();
      case 'dismiss-intro': return this.dismissIntro();
      case 'set-speed': return this.onSetting('speed', Number(el.dataset.speed));
      case 'unlock-all': return this.onSetting('unlockAll', true);
      case 'clear-progress': return this.clearProgress();
      case 'ai-solve': return this.runAi(() => this.ai.solveOne(el.dataset.algo));
      case 'ai-toggle': return this.ai.toggle();
      case 'ai-runall': return this.runAi(() => this.ai.runAll());
      case 'ai-cancel': return this.ai.cancel();
      case 'ai-playpause': return this.ai.togglePlay();
      case 'ai-step': return this.ai.stepOne();
      case 'ai-restart': return this.ai.restartPlayback();
      case 'ai-speed': return this.ai.setSpeed(Number(el.dataset.speed));
      case 'ai-csv': return this.ai.exportCsv();
      default: return undefined;
    }
  }

  // Nút AI chỉ dùng được trong màn chơi. Các kiểm tra đang bận nằm trong AIPanel.
  runAi(fn) {
    if (this.mode !== 'playing') return undefined;
    return fn();
  }

  openChapters() {
    if (this.mode === 'chapters') return;
    this.pushMode('chapters');
  }

  continueGame() {
    const totalStars = store.totalStars(this.levels);
    const pick = this.levels.find((lv) => store.isUnlocked(lv, totalStars) && !store.levelRecord(lv.id))
      ?? this.levels[0];
    this.play(pick.id);
  }

  clearProgress() {
    if (!window.confirm(S.settings.clearConfirm)) return;
    store.clearProgress();
    this.renderChapters();
    this.screens.setSettingsNote(S.settings.cleared);
  }

  // Ai-panel đang phát lời giải: khóa điều khiển của người chơi.
  setAutomating(on) {
    this.automating = on;
    if (on) this.queued = null;
  }

  // ---------- màn hình chờ với khối tự lăn ----------
  async startDemo() {
    const token = ++this.demoToken;
    if (!this.demo) {
      try {
        const data = await getLevel(DEMO_LEVEL);
        const states = [];
        let state = clone(data.start);
        for (const dir of DEMO_ACTIONS) {
          const res = await sendStep(DEMO_LEVEL, state, { dir, cube: null });
          states.push({ dir, moved: res.moved, state: res.state });
          state = res.state;
        }
        this.demo = { data, states };
      } catch {
        return;   // không có server: menu vẫn dùng được, chỉ không có khối chạy nền
      }
    }
    if (token !== this.demoToken || this.mode !== 'menu') return;
    this.board.build(this.demo.data);
    this.rig.setBoard(this.demo.data.grid.length, this.demo.data.grid[0].length);
    const loop = async () => {
      while (token === this.demoToken && this.mode === 'menu') {
        let from = this.demo.data.start;
        this.block.snap(from);
        this.board.syncBridges(from.open, true);
        for (const step of this.demo.states) {
          if (token !== this.demoToken) return;
          await this.block.roll(from, step.dir, 600, 0);
          this.block.snap(step.state);
          from = step.state;
        }
        await wait(1400);
      }
    };
    loop();
  }

  stopDemo() {
    this.demoToken += 1;
  }
}
