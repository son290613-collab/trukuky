function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function formatVnd(n) {
  return Number(n).toLocaleString('vi-VN') + '₫';
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

async function loadReport() {
  const from = document.getElementById('r-from').value;
  const to = document.getElementById('r-to').value;
  const tbody = document.getElementById('report-rows');
  tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Đang tải...</td></tr>';

  let data;
  try {
    data = await apiFetch(`api/reports.php?from=${from}&to=${to}`);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-state">${escapeHtml(err.message)}</td></tr>`;
    return;
  }

  document.getElementById('r-total-orders').textContent = data.totals.order_count;
  document.getElementById('r-total-revenue').textContent = formatVnd(data.totals.revenue);

  if (!data.rows.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Không có đơn hàng nào trong khoảng thời gian này.</td></tr>';
    return;
  }

  const maxRevenue = Math.max(...data.rows.map((r) => Number(r.revenue))) || 1;
  tbody.innerHTML = data.rows.map((r) => {
    const pct = Math.max(4, Math.round((Number(r.revenue) / maxRevenue) * 100));
    return `
      <tr>
        <td>${new Date(r.day).toLocaleDateString('vi-VN')}</td>
        <td>${r.order_count}</td>
        <td>${formatVnd(r.revenue)}</td>
        <td><div class="report-bar-track"><div class="report-bar" style="width:${pct}%"></div></div></td>
      </tr>`;
  }).join('');
}

document.getElementById('report-filter').addEventListener('submit', (e) => {
  e.preventDefault();
  loadReport();
});

document.getElementById('r-to').value = todayStr();
document.getElementById('r-from').value = new Date(Date.now() - 6 * 86400000).toISOString().slice(0, 10);
loadReport();
