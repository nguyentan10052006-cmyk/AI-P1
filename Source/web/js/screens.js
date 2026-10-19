// Các màn hình phủ lên bảng: menu, chọn màn, hướng dẫn, cài đặt, tạm dừng, thắng, rơi, giới thiệu ô.
import { CHAPTERS, KIND_TEXT, S, TILE_TEXT } from './strings.js';
import { tileIcon } from './tiles.js';
import { navigate } from './input.js';

const SETTING_INPUTS = {
  'set-music': 'musicVol',
  'set-sfx': 'sfxVol',
  'set-mute': 'muted',
  'set-shadows': 'shadows',
  'set-camkeys': 'camKeys',
  'set-reduce': 'reduceMotion',
};

const $ = (id) => document.getElementById(id);
const SPECIAL_ORDER = ['F', 'o', 'x', '@', 'b', 'B'];

export class Screens {
  constructor({ onAction, onSetting }) {
    this.overlay = $('overlay');
    this.hud = $('hud');
    this.toastEl = $('toast');
    this.current = null;
    this.toastTimer = null;
    this.onAction = onAction;

    const dispatch = (e) => {
      const el = e.target.closest('[data-action]');
      if (!el || el.disabled) return;
      onAction(el.dataset.action, el);
    };
    this.overlay.addEventListener('click', dispatch);
    this.hud.addEventListener('click', dispatch);

    for (const [id, name] of Object.entries(SETTING_INPUTS)) {
      $(id).addEventListener('change', (e) => {
        onSetting(name, e.target.type === 'checkbox' ? e.target.checked : Number(e.target.value));
      });
    }
    $('menu-subtitle').textContent = S.subtitle;
    $('menu-footer').textContent = S.menu.footer;
    $('loading-text').textContent = S.loading;
  }

  // ---- hiển thị chung ----
  show(name) {
    this.current = name;
    this.overlay.classList.remove('hidden');
    for (const section of this.overlay.querySelectorAll('[data-screen]')) {
      section.classList.toggle('hidden', section.dataset.screen !== name);
    }
    const first = this.overlay.querySelector(`[data-screen="${name}"] button:not(:disabled)`);
    if (first) first.focus({ preventScroll: true });
  }

  hide() {
    this.current = null;
    this.overlay.classList.add('hidden');
  }

  isOpen() {
    return !this.overlay.classList.contains('hidden');
  }

  navigate(dir) {
    const section = this.overlay.querySelector(`[data-screen="${this.current}"]`);
    if (section) navigate(section, dir);
  }

  // Enter: bấm nút đang có tiêu điểm trong màn hình đang mở.
  activate() {
    const focused = document.activeElement;
    if (focused && this.overlay.contains(focused) && focused.tagName === 'BUTTON') focused.click();
  }

  showHud(on) {
    this.hud.classList.toggle('hidden', !on);
  }

  setHud({ chapter, name, steps, par, time, switchVisible, muted }) {
    if (chapter !== undefined) $('hud-chapter').textContent = chapter;
    if (name !== undefined) $('hud-name').textContent = name;
    if (steps !== undefined) $('hud-steps').textContent = S.hud.steps(steps);
    if (par !== undefined) $('hud-par').textContent = par ? S.hud.par(par) : S.hud.unrated;
    if (time !== undefined) $('hud-time').textContent = time;
    if (switchVisible !== undefined) $('btn-switch').hidden = !switchVisible;
    if (muted !== undefined) {
      $('btn-mute').textContent = muted ? '🔇' : '🔊';
      $('btn-mute').setAttribute('aria-label', muted ? 'Bật tiếng (M)' : 'Tắt tiếng (M)');
    }
  }

  // Gợi ý: làm sáng nút mũi tên tương ứng trong một lúc.
  hintDirection(dir) {
    document.querySelectorAll('.pad').forEach((el) => el.classList.toggle('hinted', el.dataset.dir === dir));
  }

  toast(text, kind = '') {
    const el = this.toastEl;
    el.textContent = text;
    el.className = `toast show ${kind}`.trim();
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => { el.classList.remove('show'); }, 2300);
  }

  // ---- chọn màn ----
  renderChapters(levels, { starsOf, isUnlocked, recordOf, nextId, totalStars, totalMax }) {
    const list = $('chapter-list');
    list.innerHTML = '';
    $('chapters-stars').textContent = `★ ${totalStars}/${totalMax}`;
    const groups = new Map();
    for (const lv of levels) {
      const key = lv.kind === 'main' ? `main-${lv.chapter}` : lv.kind;
      if (!groups.has(key)) groups.set(key, { title: this.groupTitle(lv), levels: [] });
      groups.get(key).levels.push(lv);
    }
    for (const group of groups.values()) {
      const section = document.createElement('section');
      section.className = 'chapter';
      const h3 = document.createElement('h3');
      h3.textContent = group.title.name;
      const small = document.createElement('small');
      small.textContent = group.title.note;
      h3.appendChild(small);
      section.appendChild(h3);
      const cards = document.createElement('div');
      cards.className = 'cards';
      for (const lv of group.levels) {
        const unlocked = isUnlocked(lv);
        const stars = starsOf(lv.id);
        const record = recordOf(lv.id);
        const card = document.createElement('button');
        card.className = `card${lv.id === nextId ? ' next' : ''}`;
        card.dataset.action = 'play';
        card.dataset.level = lv.id;
        card.disabled = !unlocked;
        const label = lv.kind === 'main' ? `${lv.chapter}-${lv.order}` : lv.id;
        const starText = '★'.repeat(stars) + '☆'.repeat(3 - stars);
        const meta = !unlocked
          ? S.chapters.locked(lv.unlock_stars)
          : S.chapters.best(record?.best, lv.par);
        card.innerHTML = `
          <span class="num">${label}</span>
          <span class="name"></span>
          <span class="meta"></span>
          <span class="card-stars">${unlocked ? starText : ''}</span>
          <span class="icons"></span>
          ${unlocked ? '' : '<span class="lock" aria-hidden="true">🔒</span>'}
          ${lv.id === nextId ? `<span class="badge">${S.chapters.nextBadge}</span>` : ''}`;
        card.querySelector('.name').textContent = lv.name;
        card.querySelector('.meta').textContent = meta;
        const icons = card.querySelector('.icons');
        for (const ch of SPECIAL_ORDER.filter((c) => lv.features?.includes(c)).slice(0, 4)) {
          const img = document.createElement('img');
          img.src = tileIcon(ch);
          img.alt = TILE_TEXT[ch]?.name ?? ch;
          icons.appendChild(img);
        }
        cards.appendChild(card);
      }
      section.appendChild(cards);
      list.appendChild(section);
    }
    const hint = document.createElement('p');
    hint.className = 'muted small';
    hint.textContent = S.chapters.unlockAllHint;
    list.appendChild(hint);
  }

  groupTitle(lv) {
    if (lv.kind === 'main') {
      return { name: `Chương ${lv.chapter} · ${CHAPTERS[lv.chapter]}`, note: '' };
    }
    return { name: KIND_TEXT[lv.kind], note: lv.kind === 'challenge' ? 'Dành cho người đã quen luật' : 'Mở khóa bằng sao' };
  }

  // ---- hướng dẫn ----
  renderHelp() {
    const body = $('help-body');
    body.innerHTML = '';
    const goal = document.createElement('p');
    goal.textContent = S.help.goal;
    const shapes = document.createElement('p');
    shapes.textContent = S.help.shapes;
    const split = document.createElement('p');
    split.textContent = S.help.split;
    const touch = document.createElement('p');
    touch.className = 'muted';
    touch.textContent = S.help.touch;
    body.append(goal, shapes, split);

    const tiles = document.createElement('div');
    tiles.className = 'help-tiles';
    for (const [ch, info] of Object.entries(TILE_TEXT)) {
      const item = document.createElement('div');
      item.className = 'help-tile';
      const img = document.createElement('img');
      img.src = tileIcon(ch);
      img.alt = info.name;
      const text = document.createElement('div');
      const strong = document.createElement('strong');
      strong.textContent = info.name;
      const span = document.createElement('span');
      span.textContent = info.rule;
      text.append(strong, span);
      item.append(img, text);
      tiles.appendChild(item);
    }
    body.appendChild(tiles);

    const table = document.createElement('table');
    table.className = 'keys-table';
    for (const [keyName, desc] of S.help.keys) {
      const tr = document.createElement('tr');
      const k = document.createElement('td');
      const kbdEl = document.createElement('kbd');
      kbdEl.textContent = keyName;
      k.appendChild(kbdEl);
      const d = document.createElement('td');
      d.textContent = desc;
      tr.append(k, d);
      table.appendChild(tr);
    }
    body.append(table, touch);
  }

  // ---- cài đặt ----
  fillSettings(settings) {
    $('set-music').value = settings.musicVol;
    $('set-sfx').value = settings.sfxVol;
    $('set-mute').checked = settings.muted;
    $('set-shadows').checked = settings.shadows;
    $('set-camkeys').checked = settings.camKeys;
    $('set-reduce').checked = settings.reduceMotion;
    document.querySelectorAll('[data-action="set-speed"]').forEach((el) => {
      el.classList.toggle('on', Number(el.dataset.speed) === settings.speed);
    });
    // Nhãn tốc độ được đặt từ chuỗi trong S, cùng thứ tự với các nút
    document.querySelectorAll('[data-action="set-speed"]').forEach((el, i) => {
      el.textContent = S.settings.speedNames[i];
    });
  }

  setSettingsNote(text) {
    $('settings-note').textContent = text;
  }

  // ---- thắng / rơi / giới thiệu ----
  fillWin({ steps, par, time, falls, stars, newBest, lastLevel, nextLocked, needStars }) {
    $('win-steps').textContent = String(steps);
    $('win-par').textContent = par ? String(par) : '—';
    $('win-time').textContent = time;
    $('win-falls').textContent = String(falls);
    $('win-record').classList.toggle('hidden', !newBest);
    $('btn-next').disabled = lastLevel || nextLocked;
    if (lastLevel) $('btn-next').textContent = S.win.lastLevel;
    else if (nextLocked) $('btn-next').textContent = S.win.needStars(needStars);
    else $('btn-next').textContent = `${S.win.next} ▶`;
    const spans = [...$('win-stars').querySelectorAll('span')];
    spans.forEach((s) => { s.classList.remove('on', 'pop'); });
    spans.forEach((s, i) => {
      setTimeout(() => {
        if (i < stars) s.classList.add('on');
        s.classList.add('pop');
        setTimeout(() => s.classList.remove('pop'), 220);
      }, 260 + i * 240);
    });
  }

  fillFall(reasonText) {
    $('fall-reason').textContent = reasonText;
  }

  fillIntro({ title, text, kind }) {
    $('intro-title').textContent = title;
    $('intro-text').textContent = text;
    const visual = $('intro-visual');
    visual.innerHTML = '';
    if (kind) {
      const img = document.createElement('img');
      img.src = tileIcon(kind);
      img.alt = TILE_TEXT[kind]?.name ?? kind;
      visual.appendChild(img);
    }
  }

  setError(title, detail, cmd) {
    $('error-title').textContent = title;
    $('error-detail').textContent = detail;
    $('error-cmd').textContent = cmd;
  }
}
