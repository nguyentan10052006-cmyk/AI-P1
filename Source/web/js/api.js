// Gọi API của server Python. Luật chơi nằm hết ở server, GUI chỉ hiển thị kết quả.

export class ServerError extends Error {}

async function request(url, options) {
  let res;
  try {
    res = await fetch(url, options);
  } catch {
    throw new ServerError('Mất kết nối với server');
  }
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`Phản hồi không hợp lệ (HTTP ${res.status})`);
  }
  if (!res.ok) throw new Error(data.error || `Lỗi HTTP ${res.status}`);
  return data;
}

function post(body) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
}

export const listLevels = () => request('/api/levels');

export const getLevel = (id) => request(`/api/levels/${encodeURIComponent(id)}`);

export const sendStep = (level, state, action) => request('/api/step', post({ level, state, action }));

export const solve = (level, state, algorithm) => request('/api/solve', post({ level, state, algorithm }));

export const cancelSolve = () => request('/api/solve/cancel', post({}));
