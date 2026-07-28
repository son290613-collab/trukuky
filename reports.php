<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Báo cáo';
$activeNav = 'reports';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Báo cáo đơn hàng</h1>
    <p class="page-sub">Số đơn và doanh thu theo ngày trong khoảng thời gian bạn chọn.</p>
  </div>
</div>

<div class="card">
  <form id="report-filter" class="form-grid" style="align-items:end;">
    <div class="form-field"><label>Từ ngày</label><input id="r-from" type="date" required></div>
    <div class="form-field"><label>Đến ngày</label><input id="r-to" type="date" required></div>
    <div class="form-field"><button class="btn btn-primary" type="submit">Xem báo cáo</button></div>
  </form>
</div>

<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-label">Tổng số đơn</div>
    <div class="stat-value" id="r-total-orders">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Tổng doanh thu</div>
    <div class="stat-value" id="r-total-revenue">—</div>
  </div>
</div>

<div class="card">
  <table>
    <thead><tr><th>Ngày</th><th>Số đơn</th><th>Doanh thu</th><th></th></tr></thead>
    <tbody id="report-rows"><tr><td colspan="4" class="empty-state">Đang tải...</td></tr></tbody>
  </table>
</div>

<script src="assets/js/app.js"></script>
<script src="assets/js/reports.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
