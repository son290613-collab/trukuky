<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Tồn kho';
$activeNav = 'inventory';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Tồn kho</h1>
    <p class="page-sub">Theo dõi số lượng, size, màu và cảnh báo sắp hết hàng.</p>
  </div>
  <button class="btn btn-primary" onclick="openProductModal()">+ Thêm sản phẩm</button>
</div>

<div class="card">
  <table>
    <thead>
      <tr><th></th><th>Sản phẩm</th><th>SKU</th><th>Size</th><th>Màu</th><th>Giá bán</th><th>Tồn kho</th><th>Trạng thái</th><th></th></tr>
    </thead>
    <tbody id="product-rows">
      <tr><td colspan="9" class="empty-state">Đang tải...</td></tr>
    </tbody>
  </table>
</div>

<div class="modal-backdrop" id="product-modal">
  <div class="modal">
    <h3 id="product-modal-title">Thêm sản phẩm</h3>
    <form id="product-form">
      <input type="hidden" id="p-id">
      <div class="form-grid">
        <div class="form-field"><label>Tên sản phẩm</label><input id="p-name" required></div>
        <div class="form-field"><label>SKU</label><input id="p-sku" required></div>
        <div class="form-field"><label>Danh mục</label><input id="p-category" placeholder="Áo thun, Quần jean,..."></div>
        <div class="form-field"><label>Size</label><input id="p-size" placeholder="S, M, L, 29, 30..."></div>
        <div class="form-field"><label>Màu</label><input id="p-color"></div>
        <div class="form-field"><label>Giá bán (₫)</label><input id="p-price" type="number" min="0" required></div>
        <div class="form-field"><label>Giá vốn (₫)</label><input id="p-cost" type="number" min="0"></div>
        <div class="form-field"><label>Số lượng tồn</label><input id="p-quantity" type="number" min="0" required></div>
        <div class="form-field"><label>Ngưỡng cảnh báo</label><input id="p-threshold" type="number" min="0" value="5"></div>
        <div class="form-field">
          <label>Ảnh sản phẩm</label>
          <input type="hidden" id="p-image-url">
          <img id="p-image-preview" class="thumb" style="display:none; margin-bottom:8px;">
          <input type="file" id="p-image-file" accept="image/png,image/jpeg,image/webp">
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn" onclick="closeModal('product-modal')">Huỷ</button>
        <button type="submit" class="btn btn-primary">Lưu</button>
      </div>
    </form>
  </div>
</div>

<script src="assets/js/app.js"></script>
<script src="assets/js/inventory.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
