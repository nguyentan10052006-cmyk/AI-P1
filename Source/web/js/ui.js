// Phần giao diện HTML: danh sách màn, trạng thái, nút bấm và bảng kết quả.

const $ = (id) => document.getElementById(id);

const GROUP_LABEL = {
  basic: 'Cơ bản',
  fragile: 'Ô giòn',
  switch: 'Công tắc và cầu',
  combined: 'Kết hợp',
};

export function fillLevels(levels) {
  const select = $('level');
  select.innerHTML = '';
  const groups = [...new Set(levels.map((lv) => lv.group))];
  for (const group of groups) {
    const optgroup = document.createElement('optgroup');
    optgroup.label = GROUP_LABEL[group] ?? group;
    for (const lv of levels.filter((item) => item.group === group)) {
      const option = document.createElement('option');
      option.value = lv.id;
      option.textContent = `${lv.id} · ${lv.name}`;
      optgroup.appendChild(option);
    }
    select.appendChild(optgroup);
  }
}

export const levelId = () => $('level').value;
export const setLevelId = (id) => { $('level').value = id; };
export const speedValue = () => $('speed').value;

export function setStatus(text, kind = '') {
  const el = $('status');
  el.textContent = text;
  el.className = `status ${kind}`.trim();
}

// Khóa các nút đổi trạng thái khi đang chạy hoạt ảnh.
export function setBusy(busy) {
  for (const el of document.querySelectorAll('#level, #btn-new, #btn-restart, #btn-undo, #btn-next, button.solve')) {
    el.disabled = busy;
  }
}

export function setPlaying(playing) {
  $('btn-stop').disabled = !playing;
}

export function showNext(show) {
  $('btn-next').classList.toggle('hidden', !show);
}

// Thêm một dòng vào bảng kết quả. Lỗi thì một ô kéo dài thay cho các số liệu.
export function addResult(level, algo, res) {
  const tbody = document.querySelector('#results tbody');
  const row = document.createElement('tr');
  row.append(cell(level), cell(algo.toUpperCase()));
  if (res.error) {
    const td = cell(res.error);
    td.colSpan = 5;
    td.className = 'err';
    row.appendChild(td);
  } else {
    const s = res.stats;
    row.append(
      cell(s.time_ms.toFixed(1)),
      cell(s.peak_kb.toFixed(1)),
      cell(String(s.expanded)),
      cell(res.found ? String(s.length) : '—'),
      cell(res.found ? String(s.cost) : '—'),
    );
  }
  tbody.appendChild(row);
}

function cell(value) {
  const td = document.createElement('td');
  td.textContent = value;
  return td;
}
