<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Phối đồ';
$activeNav = 'outfits';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Phối đồ</h1>
    <p class="page-sub">Gợi ý các bộ phối đồ từ sản phẩm trong kho để tư vấn và bán kèm cho khách.</p>
  </div>
  <button class="btn btn-primary" onclick="openOutfitModal()">+ Tạo bộ phối đồ</button>
</div>

<div class="outfit-grid" id="outfit-grid">
  <div class="empty-state">Đang tải...</div>
</div>

<div class="modal-backdrop" id="outfit-modal">
  <div class="modal">
    <h3>Tạo bộ phối đồ</h3>
    <form id="outfit-form">
      <div class="form-field"><label>Tên bộ phối đồ</label><input id="of-name" required placeholder="VD: Set đi làm mùa hè"></div>
      <div class="form-field"><label>Mô tả</label><textarea id="of-desc" rows="2"></textarea></div>
      <div class="form-field">
        <label>Chọn sản phẩm (tối thiểu 2)</label>
        <select id="of-products" multiple size="6"></select>
      </div>
      <div class="form-field">
        <label>Ảnh bộ phối đồ</label>
        <input type="hidden" id="of-image-url">
        <img id="of-image-preview" class="thumb outfit-thumb" style="display:none;">
        <input type="file" id="of-image-file" accept="image/png,image/jpeg,image/webp">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn" onclick="closeModal('outfit-modal')">Huỷ</button>
        <button type="submit" class="btn btn-primary">Lưu</button>
      </div>
    </form>
  </div>
</div>

<script src="assets/js/app.js"></script>
<script src="assets/js/outfits.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
