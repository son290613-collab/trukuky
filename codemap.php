<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Sổ mã hàng';
$activeNav = 'codemap';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Sổ mã hàng</h1>
    <p class="page-sub">Nối mã live (M01, M02...) với mã hàng trên KiotViet. Sửa tới đâu lưu tới đó.</p>
  </div>
  <a class="btn" href="api/codemap.php?export=csv">Tải về CSV</a>
</div>

<div id="cm-alerts"></div>

<div class="card">
  <div class="card-header">
    <h3 class="card-title">Tiến độ ghép mã</h3>
    <span class="check-meta" id="cm-kv-status">Đang tải...</span>
  </div>
  <div id="cm-progress"></div>
</div>

<div class="card">
  <div class="card-header">
    <h3 class="card-title">Các món trong sổ live</h3>
    <label class="check-meta" style="display:flex; align-items:center; gap:6px;">
      <input type="checkbox" id="cm-only-todo"> Chỉ hiện món chưa ghép
    </label>
  </div>
  <div class="cm-table-wrap">
  <table>
    <thead>
      <tr>
        <th>Mã live</th>
        <th>Món trong sổ</th>
        <th>Size &amp; tồn</th>
        <th>Mã KiotViet</th>
        <th>Tên gọi khách</th>
        <th>Ghi chú</th>
        <th></th>
      </tr>
    </thead>
    <tbody id="cm-rows">
      <tr><td colspan="7" class="empty-state">Đang tải...</td></tr>
    </tbody>
  </table>
  </div>
</div>

<datalist id="cm-kv-list"></datalist>

<script src="assets/js/app.js"></script>
<script src="assets/js/codemap.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
