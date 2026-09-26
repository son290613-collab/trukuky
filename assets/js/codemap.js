let state = { items: [], kiotviet: [], kiotviet_total: 0, counts: {}, warnings: { shared: [], unknown: [] } };

/**
 * Thoát ký tự cho cả nội dung lẫn giá trị thuộc tính.
 * Khác escapeHtml ở inventory.js: có thoát cả dấu nháy, vì ở đây dữ liệu
 * người dùng nhập được đặt thẳng vào value="..." của ô nhập.
 */
function esc(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function vnd(n) {
  return Number(n || 0).toLocaleString('vi-VN') + '₫';
}

async function load() {
  state = await apiFetch('api/codemap.php');
}

function renderKiotvietList() {
  document.getElementById('cm-kv-list').innerHTML = state.kiotviet
    .map((p) => `<option value="${esc(p.code)}">${esc(p.name)}</option>`)
    .join('');

  const el = document.getElementById('cm-kv-status');
  el.textContent = state.kiotviet_total > 0
    ? `Đã đồng bộ ${state.kiotviet_total} mã hàng từ KiotViet`
    : 'Chưa đồng bộ KiotViet — bạn vẫn gõ tay mã được, đồng bộ sau sẽ tự kiểm lại';
}

function renderProgress() {
  const c = state.counts || {};
  const done = (c.da_ghep || 0) + (c.khong_co || 0);
  const total = done + (c.chua_ghep || 0);
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById('cm-progress').innerHTML = `
    <div class="cm-progress-line">
      <strong>${done}/${total}</strong> món đã xử lý — ${pct}%
      <span class="check-meta">(${c.da_ghep || 0} đã ghép · ${c.khong_co || 0} không có trên KiotViet · ${c.chua_ghep || 0} chưa ghép)</span>
    </div>
    <div class="cm-progress-track"><div class="cm-progress-bar" style="width:${pct}%"></div></div>`;
}

function renderAlerts() {
  const w = state.warnings || { shared: [], unknown: [] };
  const blocks = [];

  if (w.shared.length) {
    blocks.push(`
      <div class="cm-alert cm-alert-bad">
        <strong>${w.shared.length} mã KiotViet đang bị hai món dùng chung — đây là kho chung, rất dễ bán vượt mà không ai thấy.</strong>
        <ul>${w.shared.map((s) => `<li><code>${esc(s.kiotviet_code)}</code> ← ${esc(s.items.join('  ·  '))}</li>`).join('')}</ul>
        Nếu đúng là một mặt hàng thì từ buổi sau phải cộng tồn chung khi chốt đơn. Nếu sai thì sửa lại một trong hai.
      </div>`);
  }

  if (w.unknown.length) {
    blocks.push(`
      <div class="cm-alert cm-alert-warn">
        <strong>${w.unknown.length} mã không có trong danh mục KiotViet đã đồng bộ</strong> — nhiều khả năng gõ nhầm, hoặc hàng đã bị xoá.
        <ul>${w.unknown.map((u) => `<li>${esc(u.ma_live)} ${esc(u.mon)} → <code>${esc(u.kiotviet_code)}</code></li>`).join('')}</ul>
      </div>`);
  }

  document.getElementById('cm-alerts').innerHTML = blocks.join('');
}

function renderRows() {
  const onlyTodo = document.getElementById('cm-only-todo').checked;
  const rows = onlyTodo ? state.items.filter((i) => i.status === 'chua_ghep') : state.items;
  const tbody = document.getElementById('cm-rows');

  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">${
      onlyTodo ? 'Không còn món nào chưa ghép.' : 'Chưa có dữ liệu. Chạy tools/import_so_live.php để nạp sổ live.'
    }</td></tr>`;
    return;
  }

  const sharedCodes = new Set((state.warnings.shared || []).map((s) => s.kiotviet_code));

  tbody.innerHTML = rows.map((r) => {
    const badge = {
      da_ghep: '<span class="badge badge-good">Đã ghép</span>',
      khong_co: '<span class="badge badge-muted">Không có</span>',
      chua_ghep: '<span class="badge badge-warn">Chưa ghép</span>',
    }[r.status];

    const gia = Number(r.gia_min) === Number(r.gia_max)
      ? vnd(r.gia_min)
      : `${vnd(r.gia_min)}–${vnd(r.gia_max)}`;

    const kvLine = r.kiotviet_name
      ? `<div class="check-meta">${esc(r.kiotviet_name)}${r.kiotviet_on_hand !== null ? ` · tồn KiotViet ${r.kiotviet_on_hand}` : ''}</div>`
      : (r.kiotviet_code && state.kiotviet_total > 0
          ? '<div class="check-meta cm-bad">KiotViet không có mã này</div>'
          : '');

    const isShared = r.kiotviet_code && sharedCodes.has(r.kiotviet_code);

    return `
      <tr data-id="${r.id}"${isShared ? ' class="cm-row-shared"' : ''}>
        <td><strong>${esc(r.ma_live)}</strong></td>
        <td>
          ${esc(r.mon)}
          ${r.ghi_chu ? `<div class="check-meta">${esc(r.ghi_chu)}</div>` : ''}
        </td>
        <td>
          ${esc(r.sizes || '—')}
          <div class="check-meta">tồn ${r.ton ?? 0} · ${gia}</div>
        </td>
        <td>
          <input class="cm-field cm-code" list="cm-kv-list" value="${esc(r.kiotviet_code)}"
                 placeholder="Gõ hoặc dán mã" ${r.status === 'khong_co' ? 'disabled' : ''}>
          ${kvLine}
        </td>
        <td><input class="cm-field cm-ten" value="${esc(r.ten_mon_dung)}" placeholder="Tên gửi khách"></td>
        <td><input class="cm-field cm-note" value="${esc(r.note)}" placeholder="Ghi chú"></td>
        <td class="cm-actions">
          ${badge}
          <button class="btn btn-sm" data-action="${r.status === 'khong_co' ? 'undo' : 'none'}">
            ${r.status === 'khong_co' ? 'Ghép lại' : 'Không có'}
          </button>
        </td>
      </tr>`;
  }).join('');
}

function render() {
  renderKiotvietList();
  renderProgress();
  renderAlerts();
  renderRows();
}

/** Lưu một dòng rồi tải lại, giữ con trỏ ở đúng ô người dùng đang gõ. */
async function saveRow(tr, statusOverride) {
  const id = Number(tr.dataset.id);
  const payload = {
    id,
    kiotviet_code: tr.querySelector('.cm-code').value.trim(),
    ten_mon_dung: tr.querySelector('.cm-ten').value.trim(),
    note: tr.querySelector('.cm-note').value.trim(),
  };
  if (statusOverride) payload.status = statusOverride;

  const active = document.activeElement;
  const keepClass = active && active.classList.contains('cm-field')
    ? [...active.classList].find((c) => c.startsWith('cm-') && c !== 'cm-field')
    : null;
  const keepId = keepClass ? active.closest('tr')?.dataset.id : null;

  try {
    await apiFetch('api/codemap.php', { method: 'PUT', body: payload });
    await load();
    render();
    if (keepId && keepClass) {
      const el = document.querySelector(`tr[data-id="${keepId}"] .${keepClass}`);
      if (el) {
        el.focus();
        if (el.setSelectionRange) el.setSelectionRange(el.value.length, el.value.length);
      }
    }
  } catch (err) {
    alert(err.message);
  }
}

document.getElementById('cm-rows').addEventListener('change', (e) => {
  if (!e.target.classList.contains('cm-field')) return;
  saveRow(e.target.closest('tr'));
});

document.getElementById('cm-rows').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-action]');
  if (!btn) return;
  const tr = btn.closest('tr');
  // "Không có" xoá mã đã gõ, nên hỏi lại khi có mã.
  if (btn.dataset.action === 'none') {
    const code = tr.querySelector('.cm-code').value.trim();
    if (code && !confirmAction(`Đánh dấu món này không có trên KiotViet? Mã ${code} đang gõ sẽ bị xoá.`)) return;
    saveRow(tr, 'khong_co');
  } else {
    saveRow(tr, '');
  }
});

document.getElementById('cm-only-todo').addEventListener('change', renderRows);

load().then(render).catch((err) => {
  document.getElementById('cm-rows').innerHTML =
    `<tr><td colspan="7" class="empty-state">Không tải được: ${esc(err.message)}</td></tr>`;
});
