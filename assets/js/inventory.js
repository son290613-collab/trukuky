let products = [];

async function loadProducts() {
  products = await apiFetch('api/products.php');
  renderProducts();
}

function renderProducts() {
  const tbody = document.getElementById('product-rows');
  if (!products.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-state">Chưa có sản phẩm nào. Bấm "Thêm sản phẩm" để bắt đầu.</td></tr>';
    return;
  }
  tbody.innerHTML = products.map((p) => {
    const low = Number(p.quantity) <= Number(p.low_stock_threshold);
    const statusBadge = low
      ? `<span class="badge badge-bad">Sắp hết</span>`
      : `<span class="badge badge-good">Còn hàng</span>`;
    return `
      <tr>
        <td>${p.image_url ? `<img class="thumb" src="${escapeHtml(p.image_url)}">` : '<div class="thumb thumb-placeholder"></div>'}</td>
        <td><strong>${escapeHtml(p.name)}</strong>${p.category ? `<br><span class="check-meta">${escapeHtml(p.category)}</span>` : ''}</td>
        <td>${escapeHtml(p.sku)}</td>
        <td>${escapeHtml(p.size || '-')}</td>
        <td>${escapeHtml(p.color || '-')}</td>
        <td>${formatVnd(p.price)}</td>
        <td>${p.quantity}</td>
        <td>${statusBadge}</td>
        <td>
          <button class="btn btn-sm" onclick="editProduct(${p.id})">Sửa</button>
          <button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id})">Xoá</button>
        </td>
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

function openProductModal() {
  document.getElementById('product-modal-title').textContent = 'Thêm sản phẩm';
  document.getElementById('product-form').reset();
  document.getElementById('p-id').value = '';
  document.getElementById('p-threshold').value = 5;
  document.getElementById('p-image-url').value = '';
  document.getElementById('p-image-preview').style.display = 'none';
  openModal('product-modal');
}

function editProduct(id) {
  const p = products.find((x) => x.id === id);
  if (!p) return;
  document.getElementById('product-modal-title').textContent = 'Sửa sản phẩm';
  document.getElementById('p-id').value = p.id;
  document.getElementById('p-name').value = p.name;
  document.getElementById('p-sku').value = p.sku;
  document.getElementById('p-category').value = p.category || '';
  document.getElementById('p-size').value = p.size || '';
  document.getElementById('p-color').value = p.color || '';
  document.getElementById('p-price').value = p.price;
  document.getElementById('p-cost').value = p.cost;
  document.getElementById('p-quantity').value = p.quantity;
  document.getElementById('p-threshold').value = p.low_stock_threshold;
  document.getElementById('p-image-url').value = p.image_url || '';
  const preview = document.getElementById('p-image-preview');
  if (p.image_url) {
    preview.src = p.image_url;
    preview.style.display = 'block';
  } else {
    preview.style.display = 'none';
  }
  openModal('product-modal');
}

async function deleteProduct(id) {
  if (!confirmAction('Xoá sản phẩm này?')) return;
  await apiFetch('api/products.php', { method: 'DELETE', body: { id } });
  await loadProducts();
}

document.getElementById('product-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('p-id').value;
  try {
    let imageUrl = document.getElementById('p-image-url').value;
    const file = document.getElementById('p-image-file').files[0];
    if (file) {
      const uploaded = await apiUpload('api/upload.php', file);
      imageUrl = uploaded.url;
    }
    const payload = {
      id: id || undefined,
      name: document.getElementById('p-name').value,
      sku: document.getElementById('p-sku').value,
      category: document.getElementById('p-category').value,
      size: document.getElementById('p-size').value,
      color: document.getElementById('p-color').value,
      price: document.getElementById('p-price').value,
      cost: document.getElementById('p-cost').value,
      quantity: document.getElementById('p-quantity').value,
      low_stock_threshold: document.getElementById('p-threshold').value,
      image_url: imageUrl,
    };
    await apiFetch('api/products.php', { method: id ? 'PUT' : 'POST', body: payload });
    closeModal('product-modal');
    await loadProducts();
  } catch (err) {
    alert(err.message);
  }
});

loadProducts();
