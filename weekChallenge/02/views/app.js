const API = 'http://localhost:8000';

function getUser() {
  return localStorage.getItem('username');
}

function requireAuth() {
  if (!getUser()) {
    location.href = '/login';
  }
}

function logout() {
  localStorage.removeItem('username');
  location.href = '/login';
}

async function api(method, path, body = null, params = null) {
  let url = API + path;
  if (params) {
    url += '?' + new URLSearchParams(params).toString();
  }
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return res.json();
}

function nowIso() {
  return new Date().toISOString();
}

function formatDate(dt) {
  if (!dt) return '';
  const d = new Date(dt);
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
    + ' ' + d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
}

function getParam(key) {
  return new URLSearchParams(location.search).get(key);
}
