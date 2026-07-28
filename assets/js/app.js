// Shared front-end helpers used across pages.

const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || '';

async function apiFetch(url, options = {}) {
  const opts = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': CSRF_TOKEN,
    },
  };
  if (options.body) opts.body = JSON.stringify(options.body);

  const res = await fetch(url, opts);
  let data = null;
  try { data = await res.json(); } catch (e) { /* no body */ }
  if (!res.ok) {
    throw new Error((data && data.error) || `Request failed (${res.status})`);
  }
  return data;
}

async function apiUpload(url, file) {
  const formData = new FormData();
  formData.append('image', file);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-CSRF-Token': CSRF_TOKEN },
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error((data && data.error) || `Request failed (${res.status})`);
  }
  return data;
}

function openModal(id) {
  document.getElementById(id)?.classList.add('open');
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
});

function confirmAction(message) {
  return window.confirm(message);
}
