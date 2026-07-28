function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}

async function loadOutfits() {
  const outfits = await apiFetch('api/outfits.php');
  const grid = document.getElementById('outfit-grid');
  if (!outfits.length) {
    grid.innerHTML = '<div class="empty-state">Chưa có bộ phối đồ nào.</div>';
    return;
  }
  grid.innerHTML = outfits.map((o) => `
    <div class="outfit-card">
      ${o.image_url ? `<img class="thumb outfit-thumb" src="${escapeHtml(o.image_url)}">` : ''}
      <h4>${escapeHtml(o.name)}</h4>
      ${o.description ? `<p class="check-meta">${escapeHtml(o.description)}</p>` : ''}
      <ul class="outfit-items">
        ${o.items.map((i) => `<li>• ${escapeHtml(i.name)} (${escapeHtml(i.sku)})</li>`).join('')}
      </ul>
      <button class="btn btn-sm btn-danger" style="margin-top:10px;" onclick="deleteOutfit(${o.id})">Xoá</button>
    </div>`).join('');
}

async function deleteOutfit(id) {
  if (!confirmAction('Xoá bộ phối đồ này?')) return;
  await apiFetch('api/outfits.php', { method: 'DELETE', body: { id } });
  await loadOutfits();
}

async function openOutfitModal() {
  const products = await apiFetch('api/products.php');
  const select = document.getElementById('of-products');
  select.innerHTML = products.map((p) => `<option value="${p.id}">${escapeHtml(p.name)} (${escapeHtml(p.sku)})</option>`).join('');
  document.getElementById('outfit-form').reset();
  document.getElementById('of-image-url').value = '';
  document.getElementById('of-image-preview').style.display = 'none';
  openModal('outfit-modal');
}

document.getElementById('outfit-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const productIds = Array.from(document.getElementById('of-products').selectedOptions).map((o) => Number(o.value));
  try {
    let imageUrl = document.getElementById('of-image-url').value;
    const file = document.getElementById('of-image-file').files[0];
    if (file) {
      const uploaded = await apiUpload('api/upload.php', file);
      imageUrl = uploaded.url;
    }
    await apiFetch('api/outfits.php', {
      method: 'POST',
      body: {
        name: document.getElementById('of-name').value,
        description: document.getElementById('of-desc').value,
        product_ids: productIds,
        image_url: imageUrl,
      },
    });
    closeModal('outfit-modal');
    await loadOutfits();
  } catch (err) {
    alert(err.message);
  }
});

loadOutfits();
