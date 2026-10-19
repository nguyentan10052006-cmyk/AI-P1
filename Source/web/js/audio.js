// Âm thanh tạo ngay trong trình duyệt bằng Web Audio: không cần file nhạc, không vướng bản quyền.
// Nhạc nền là một vòng 4 ô nhịp (Am - F - C - G) ở 84 nhịp/phút, có bass, pad, arpeggio và hi-hat nhẹ.

const BPM = 84;
const STEP = 60 / BPM / 2;   // một bước = một nốt móc (1/8)
const PROGRESSION = [
  [220.0, 261.63, 329.63],   // Am
  [174.61, 220.0, 261.63],   // F
  [261.63, 329.63, 392.0],   // C
  [196.0, 246.94, 293.66],   // G
];
const BASS = [110.0, 87.31, 130.81, 98.0];
const MUSIC_LEVEL = 0.16;

export class Audio {
  constructor() {
    this.ctx = null;
    this.musicBus = null;
    this.sfxBus = null;
    this.noise = null;
    this.started = false;
    this.musicVol = 0.45;
    this.sfxVol = 0.8;
    this.muted = false;
    this.ducked = false;
    this.step = 0;
    this.nextTime = 0;
    this.timer = null;
  }

  // Tạo AudioContext khi người chơi đã tương tác (trình duyệt chặn âm thanh tự phát).
  ensure() {
    if (this.ctx) return true;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return false;
      this.ctx = new AudioCtx();
      const master = this.ctx.createGain();
      master.connect(this.ctx.destination);
      this.musicBus = this.ctx.createGain();
      this.musicBus.connect(master);
      this.sfxBus = this.ctx.createGain();
      this.sfxBus.connect(master);
      this.noise = this.makeNoise();
      this.applyVolumes();
      return true;
    } catch {
      this.ctx = null;
      return false;
    }
  }

  // Gọi khi có cử chỉ người dùng đầu tiên: mở âm thanh và bắt đầu nhạc nền.
  unlock() {
    if (!this.ensure()) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();
    if (!this.started) {
      this.started = true;
      this.nextTime = this.ctx.currentTime + 0.1;
      this.timer = setInterval(() => this.schedule(), 60);
    }
  }

  setVolumes({ musicVol, sfxVol, muted }) {
    if (musicVol !== undefined) this.musicVol = musicVol;
    if (sfxVol !== undefined) this.sfxVol = sfxVol;
    if (muted !== undefined) this.muted = muted;
    this.applyVolumes();
  }

  applyVolumes() {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const music = this.muted || this.ducked ? 0 : this.musicVol * MUSIC_LEVEL;
    this.musicBus.gain.setTargetAtTime(music, now, 0.05);
    this.sfxBus.gain.setTargetAtTime(this.muted ? 0 : this.sfxVol * 0.6, now, 0.02);
  }

  // Giảm nhạc nền khi thắng để tiếng chiến thắng nổi lên.
  duck(on) {
    this.ducked = on;
    this.applyVolumes();
  }

  makeNoise() {
    const length = this.ctx.sampleRate * 0.5;
    const buffer = this.ctx.createBuffer(1, length, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
    return buffer;
  }

  schedule() {
    if (!this.ctx || this.ctx.state !== 'running') return;
    while (this.nextTime < this.ctx.currentTime + 0.2) {
      this.scheduleStep(this.step, this.nextTime);
      this.nextTime += STEP;
      this.step += 1;
    }
  }

  scheduleStep(step, time) {
    const bar = Math.floor(step / 8) % PROGRESSION.length;
    const pos = step % 8;
    const chord = PROGRESSION[bar];
    if (pos === 0) {
      for (const freq of chord) this.note(this.musicBus, freq, time, STEP * 8, 'triangle', 0.5, 900);
    }
    if (pos === 0 || pos === 4) this.note(this.musicBus, BASS[bar], time, STEP * 3.5, 'sine', 0.9);
    // Arpeggio: luân phiên các nốt hợp âm, lên một quãng tám ở nửa sau
    const tones = [...chord, ...chord.map((f) => f * 2)];
    this.note(this.musicBus, tones[(step * 3) % tones.length], time, STEP * 1.6, 'sine', 0.35);
    if (pos % 2 === 1) this.hat(time, 0.05);
  }

  note(bus, freq, time, dur, type, level, cutoff = 2400) {
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();
    osc.type = type;
    osc.frequency.value = freq;
    filter.type = 'lowpass';
    filter.frequency.value = cutoff;
    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.exponentialRampToValueAtTime(level, time + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + dur);
    osc.connect(filter).connect(gain).connect(bus);
    osc.start(time);
    osc.stop(time + dur + 0.05);
  }

  hat(time, level) {
    const src = this.ctx.createBufferSource();
    const filter = this.ctx.createBiquadFilter();
    const gain = this.ctx.createGain();
    src.buffer = this.noise;
    filter.type = 'highpass';
    filter.frequency.value = 7000;
    gain.gain.setValueAtTime(level, time);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + 0.04);
    src.connect(filter).connect(gain).connect(this.musicBus);
    src.start(time, Math.random() * 0.3);
    src.stop(time + 0.05);
  }

  // Âm thanh hiệu ứng ngắn. Mỗi hàm là một ghi chú hoặc một cụm nốt.
  tone(freq, dur, type, level, endFreq = null, delay = 0) {
    if (!this.ctx || this.muted) return;
    const t = this.ctx.currentTime + delay;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (endFreq) osc.frequency.exponentialRampToValueAtTime(endFreq, t + dur);
    gain.gain.setValueAtTime(level, t);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain).connect(this.sfxBus);
    osc.start(t);
    osc.stop(t + dur + 0.02);
  }

  burst(dur, level, freq) {
    if (!this.ctx || this.muted || !this.noise) return;
    const t = this.ctx.currentTime;
    const src = this.ctx.createBufferSource();
    const filter = this.ctx.createBiquadFilter();
    const gain = this.ctx.createGain();
    src.buffer = this.noise;
    filter.type = 'lowpass';
    filter.frequency.value = freq;
    gain.gain.setValueAtTime(level, t);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(filter).connect(gain).connect(this.sfxBus);
    src.start(t);
    src.stop(t + dur + 0.02);
  }

  move() { this.tone(200, 0.12, 'triangle', 0.25, 120); }
  click() { this.tone(1400, 0.035, 'square', 0.06); }
  ui() { this.tone(880, 0.04, 'triangle', 0.1); }
  bridgeOpen() { this.tone(330, 0.25, 'sine', 0.18, 660); }
  bridgeClose() { this.tone(660, 0.25, 'sine', 0.18, 330); }
  split() {
    this.tone(523, 0.12, 'triangle', 0.2);
    this.tone(784, 0.14, 'triangle', 0.2, null, 0.08);
  }
  merge() {
    [523, 659, 784].forEach((f, i) => this.tone(f, 0.16, 'triangle', 0.18, null, i * 0.06));
  }
  crack() { this.burst(0.18, 0.3, 1200); }
  fall() { this.tone(400, 0.7, 'sine', 0.3, 60); }
  win() {
    [523, 659, 784, 1047].forEach((f, i) => this.tone(f, 0.3, 'triangle', 0.22, null, i * 0.11));
  }
}
