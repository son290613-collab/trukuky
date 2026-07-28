let orders = [];
let availableProducts = [];

const statusLabel = { pending: 'Đang xử lý', completed: 'Hoàn thành', cancelled: 'Đã huỷ' };
const statusBadgeClass = { pending: 'badge-warn', completed: 'badge-good', cancelled: 'badge-bad' };

async function loadOrders() {
  orders = await apiFetch('api/orders.php');
  renderOrders();
}

function renderOrders() {
  const tbody = document.getElementById('order-rows');
  if (!orders.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Chưa có đơn hàng nào hôm nay.</td></tr>';
    return;
  }
  tbody.innerHTML = orders.map((o) => {
    const items = o.items.map((i) => `${escapeHtml(i.product_name)} ×${i.quantity}`).join(', ');
    const statusOptions = Object.keys(statusLabel).map((s) =>
      `<option value="${s}" ${s === o.status ? 'selected' : ''}>${statusLabel[s]}</option>`
    ).join('');
    return `
      <tr>
        <td><strong>${escapeHtml(o.order_code)}</strong></td>
        <td>${escapeHtml(o.customer_name || '—')}</td>
        <td>${items}</td>
        <td>${formatVnd(o.total_amount)}</td>
        <td><span class="badge ${statusBadgeClass[o.status]}">${statusLabel[o.status]}</span></td>
        <td>${new Date(o.created_at).toLocaleString('vi-VN')}</td>
        <td><select onchange="updateOrderStatus(${o.id}, this.value)">${statusOptions}</select></td>
      </tr>`;
  }).join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

function formatVnd(n) {
  return Number(n).toLocaleString('vi-VN') + '₫';
}

async function updateOrderStatus(id, status) {
  await apiFetch('api/orders.php', { method: 'PUT', body: { id, status } });
  await loadOrders();
}

async function openOrderModal() {
  if (!availableProducts.length) {
    availableProducts = await apiFetch('api/products.php');
  }
  document.getElementById('order-form').reset();
  document.getElementById('order-items').innerHTML = '';
  addOrderItemRow();
  openModal('order-modal');
}

function addOrderItemRow() {
  const wrap = document.getElementById('order-items');
  const row = document.createElement('div');
  row.className = 'form-grid';
  row.style.gridTemplateColumns = '2fr 1fr auto';
  row.style.alignItems = 'end';
  const options = availableProducts.map((p) =>
    `<option value="${p.id}">${escapeHtml(p.name)} (${escapeHtml(p.sku)}) — còn ${p.quantity}</option>`
  ).join('');
  row.innerHTML = `
    <div class="form-field"><label>Sản phẩm</label><select class="oi-product">${options}</select></div>
    <div class="form-field"><label>Số lượng</label><input class="oi-qty" type="number" min="1" value="1"></div>
    <button type="button" class="btn btn-sm btn-danger" style="margin-bottom:12px;" onclick="this.parentElement.remove()">Xoá</button>
  `;
  wrap.appendChild(row);
}

document.getElementById('order-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const rows = document.querySelectorAll('#order-items > div');
  const items = Array.from(rows).map((row) => ({
    product_id: Number(row.querySelector('.oi-product').value),
    quantity: Number(row.querySelector('.oi-qty').value),
  }));
  const payload = {
    customer_name: document.getElementById('o-customer').value,
    customer_phone: document.getElementById('o-phone').value,
    items,
  };
  try {
    await apiFetch('api/orders.php', { method: 'POST', body: payload });
    closeModal('order-modal');
    availableProducts = [];
    await loadOrders();
  } catch (err) {
    alert(err.message);
  }
});

loadOrders();
