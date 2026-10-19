// Bảng AI giải tự động: chạy solver, phát lại lời giải (phát/tạm dừng/từng bước), hủy, so sánh và xuất CSV.
import { cancelSolve, solve } from './api.js';
import { S } from './strings.js';

const PLAYBACK_MS = { 1: 480, 2: 280, 3: 120 };
const ALGO_NAME = { bfs: 'BFS', dfs: 'DFS', ucs: 'UCS', astar: 'A*' };
const $ = (id) => document.getElementById(id);

export class AIPanel {
  constructor(game) {
    this.game = game;
    this.body = $('ai-body');
    this.toggleBtn = $('ai-toggle');
    this.statusEl = $('ai-status');
    this.progressEl = $('ai-progress');
    this.playBtn = $('ai-playpause');
    this.cancelBtn = $('ai-cancel');
    this.tableBody = document.querySelector('#ai-table tbody');
    this.speed = 2;
    this.steps = null;        // lời giải đang phát
    this.fromState = null;    // trạng thái bắt đầu của lời giải
    this.index = 0;           // bước tiếp theo sẽ phát
    this.playing = false;
    this.solving = null;      // tên thuật toán đang chạy, hoặc null
    this.rows = [];           // dữ liệu bảng so sánh (để xuất CSV)
    this.levelId = null;
    this.cancelRequested = false;  // người chơi đã bấm Hủy trong lúc chạy cả 4
  }

  // Khi đổi màn: xóa lời giải, vệt đường đi và bảng so sánh.
  reset(levelId) {
    this.steps = null;
    this.fromState = null;
    this.index = 0;
    this.playing = false;
    this.game.board.clearTrail();
    if (this.levelId !== levelId) {
      this.rows = [];
      this.tableBody.innerHTML = '';
      this.levelId = levelId;
    }
    this.updateButtons();
    this.setProgress();
    this.setStatus('');
  }

  busy() {
    return Boolean(this.solving) || this.playing;
  }

  isOpen() {
    return !this.body.classList.contains('hidden');
  }

  toggle() {
    const open = !this.isOpen();
    this.body.classList.toggle('hidden', !open);
    this.toggleBtn.setAttribute('aria-expanded', String(open));
    this.toggleBtn.textContent = open ? '▴' : '▾';
  }

  setSpeed(speed) {
    this.speed = speed;
    document.querySelectorAll('[data-action="ai-speed"]').forEach((el) => {
      el.classList.toggle('on', Number(el.dataset.speed) === speed);
    });
  }

  playbackMs() {
    return PLAYBACK_MS[this.speed];
  }

  fromStart() {
    return document.querySelector('input[name="from"][value="start"]').checked;
  }

  setStatus(text, kind = '') {
    this.statusEl.textContent = text;
    this.statusEl.className = `ai-status ${kind}`.trim();
  }

  setProgress() {
    const total = this.steps?.length ?? 0;
    this.progressEl.style.width = total ? `${Math.round((this.index / total) * 100)}%` : '0';
  }

  updateButtons() {
    const hasSteps = Boolean(this.steps);
    this.playBtn.disabled = !hasSteps || this.solving !== null;
    this.playBtn.textContent = this.playing ? '❚❚ Tạm dừng' : '▶ Phát';
    this.cancelBtn.disabled = this.solving === null;
    document.querySelectorAll('[data-action="ai-solve"], [data-action="ai-runall"]').forEach((el) => {
      el.disabled = this.busy();
    });
  }

  // Giải một thuật toán từ đầu màn hoặc từ vị trí hiện tại, rồi phát lời giải nếu tìm được.
  async solveOne(algo, { playAfter = true, fromStart = this.fromStart() } = {}) {
    if (this.busy()) return null;
    const game = this.game;
    const from = fromStart ? game.startState() : game.state;
    const name = ALGO_NAME[algo] ?? algo;
    this.solving = algo;
    this.updateButtons();
    this.setStatus(S.ai.running(name));
    let res;
    try {
      res = await solve(game.levelId, from, algo);
    } catch (err) {
      res = { algorithm: algo, error: err.message };
    } finally {
      this.solving = null;
    }
    this.addRow(algo, fromStart, res);
    this.updateButtons();

    if (res.cancelled) {
      this.setStatus(S.ai.cancelled, 'warn');
      return res;
    }
    if (res.error) {
      this.setStatus(`${name}: ${res.error}`, 'err');
      return res;
    }
    if (!res.found) {
      this.setStatus(S.ai.notFound(name), 'warn');
      return res;
    }
    this.steps = res.steps;
    this.fromState = from;
    this.index = 0;
    this.game.board.drawTrail([from.pos, ...res.steps.map((s) => s.state.pos)], 0x38bdf8);
    this.setProgress();
    this.updateButtons();
    if (playAfter) {
      this.play();   // tự phát ngay, trạng thái do play() cập nhật
    } else {
      this.setStatus(S.ai.found(name, res.steps.length), 'ok');
    }
    return res;
  }

  // Chạy cả bốn thuật toán từ đầu màn để so sánh công bằng.
  async runAll() {
    if (this.busy()) return;
    this.cancelRequested = false;
    for (const algo of ['bfs', 'dfs', 'ucs', 'astar']) {
      if (this.cancelRequested) break;
      await this.solveOne(algo, { playAfter: false, fromStart: true });
    }
    if (this.cancelRequested) this.setStatus(S.ai.cancelled, 'warn');
    else this.setStatus(S.ai.compareDone, 'ok');
    this.cancelRequested = false;
  }

  addRow(algo, fromStart, res) {
    const tr = document.createElement('tr');
    const name = ALGO_NAME[algo] ?? algo;
    const cells = [name];
    if (res.error) {
      const td = document.createElement('td');
      td.colSpan = 5;
      td.className = 'err';
      td.textContent = res.cancelled ? S.ai.cancelled : res.error;
      tr.append(cellOf(name), td);
      this.tableBody.appendChild(tr);
      return;
    }
    const s = res.stats;
    const found = Boolean(res.found);
    const values = [
      s.time_ms.toFixed(2),
      s.peak_kb.toFixed(1),
      String(s.expanded),
      found ? String(s.length) : '—',
      found ? String(s.cost) : '—',
    ];
    cells.push(...values);
    tr.append(...cells.map((value) => cellOf(value)));
    this.tableBody.appendChild(tr);
    this.rows.push({
      level: this.game.levelId,
      algorithm: name,
      from: fromStart ? 'đầu màn' : 'vị trí hiện tại',
      found: found ? 'có' : 'không',
      time_ms: s.time_ms,
      peak_kb: s.peak_kb,
      expanded: s.expanded,
      length: found ? s.length : '',
      cost: found ? s.cost : '',
    });
  }

  // Xuất bảng so sánh ra CSV (có BOM để Excel đọc được tiếng Việt).
  exportCsv() {
    const header = ['màn', 'thuật toán', 'giải từ', 'tìm được', 'thời gian (ms)', 'bộ nhớ (KB)', 'node mở rộng', 'độ dài', 'chi phí'];
    const lines = [header.join(',')];
    for (const r of this.rows) {
      lines.push([r.level, r.algorithm, r.from, r.found, r.time_ms, r.peak_kb, r.expanded, r.length, r.cost].join(','));
    }
    const blob = new Blob(['﻿' + lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bloxorz-so-sanh-${this.game.levelId}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    this.setStatus(`Đã xuất ${this.rows.length} dòng ra CSV.`, 'ok');
  }

  // Phát lời giải từ bước hiện tại tới cuối. Dừng ngay khi thắng hoặc rơi.
  async play() {
    if (!this.steps || this.playing || this.solving) return;
    if (this.index >= this.steps.length) {
      await this.restartPlayback();
      return;
    }
    this.playing = true;
    this.game.setAutomating(true);
    this.updateButtons();
    this.setStatus(S.ai.playing);
    while (this.playing && this.index < this.steps.length) {
      const step = this.steps[this.index];
      const status = await this.game.animateStep(step.action, step, { rollMs: this.playbackMs() });
      this.index += 1;
      this.setProgress();
      if (status !== 'ok') break;
    }
    this.playing = false;
    this.game.setAutomating(false);
    this.updateButtons();
    if (this.steps && this.index >= this.steps.length) this.setStatus('Đã phát xong lời giải.', 'ok');
    else this.setStatus(S.ai.paused);
  }

  pause() {
    this.playing = false;
    this.updateButtons();
  }

  togglePlay() {
    if (this.playing) this.pause();
    else this.play();
  }

  // Đi một bước rồi dừng (khi đang tạm dừng).
  async stepOne() {
    if (!this.steps || this.playing || this.solving) return;
    if (this.index >= this.steps.length) return;
    this.game.setAutomating(true);
    const step = this.steps[this.index];
    const status = await this.game.animateStep(step.action, step, { rollMs: this.playbackMs() });
    this.index += 1;
    this.setProgress();
    this.game.setAutomating(false);
    this.updateButtons();
    if (status !== 'ok') this.setStatus(status === 'won' ? S.win.title : '');
  }

  // Về trạng thái đầu của lời giải rồi phát lại từ đầu.
  async restartPlayback() {
    if (!this.steps) return;
    this.pause();
    await this.game.resetBoardTo(this.fromState);
    this.index = 0;
    this.setProgress();
    this.playing = false;
    await this.play();
  }

  // Hủy lời giải đang chạy ở server. Nếu đang chạy cả 4 thì dừng luôn vòng lặp.
  async cancel() {
    if (this.solving === null) return;
    this.cancelRequested = true;
    try {
      await cancelSolve();
    } catch {
      // Server không phản hồi: lời giải sẽ tự hết hạn theo giới hạn thời gian
    }
  }
}

function cellOf(value) {
  const td = document.createElement('td');
  td.textContent = value;
  return td;
}
