<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Đơn hàng';
$activeNav = 'orders';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Đơn hàng</h1>
    <p class="page-sub">Theo dõi số lượng đơn mỗi ngày và trạng thái xử lý.</p>
  </div>
  <button class="btn btn-primary" onclick="openOrderModal()">+ Tạo đơn hàng</button>
</div>

<div class="card">
  <table>
    <thead>
      <tr><th>Mã đơn</th><th>Khách hàng</th><th>Sản phẩm</th><th>Tổng tiền</th><th>Trạng thái</th><th>Thời gian</th><th></th></tr>
    </thead>
    <tbody id="order-rows">
      <tr><td colspan="7" class="empty-state">Đang tải...</td></tr>
    </tbody>
  </table>
</div>

<div class="modal-backdrop" id="order-modal">
  <div class="modal" style="max-width: 560px;">
    <h3>Tạo đơn hàng mới</h3>
    <form id="order-form">
      <div class="form-grid">
        <div class="form-field"><label>Tên khách hàng</label><input id="o-customer"></div>
        <div class="form-field"><label>Số điện thoại</label><input id="o-phone"></div>
      </div>
      <div id="order-items"></div>
      <button type="button" class="btn btn-sm" onclick="addOrderItemRow()">+ Thêm sản phẩm</button>
      <div class="modal-actions">
        <button type="button" class="btn" onclick="closeModal('order-modal')">Huỷ</button>
        <button type="submit" class="btn btn-primary">Tạo đơn</button>
      </div>
    </form>
  </div>
</div>

<script src="assets/js/app.js"></script>
<script src="assets/js/orders.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
