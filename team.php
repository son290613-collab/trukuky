<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();

$pageTitle = 'Nhân viên & Lịch';
$activeNav = 'team';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Nhân viên &amp; Lịch làm việc</h1>
    <p class="page-sub">Checklist công việc hàng ngày, lịch làm và danh sách nhân viên.</p>
  </div>
</div>

<div class="grid-2">
  <div>
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Checklist công việc</h3>
        <div style="display:flex; gap:8px; align-items:center;">
          <input type="date" id="task-date" style="width:auto;">
          <button class="btn btn-sm" type="button" onclick="generateFromTemplates()">Tạo checklist hôm nay từ mẫu</button>
        </div>
      </div>
      <div class="checklist" id="task-rows"></div>
      <form id="task-form" style="display:flex; gap:8px; margin-top:12px;">
        <input id="task-title" placeholder="Thêm việc mới..." style="flex:1;" required>
        <select id="task-assignee" style="width:160px;"><option value="">Chưa giao</option></select>
        <button class="btn btn-primary btn-sm" type="submit">Thêm</button>
      </form>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Lịch làm việc (7 ngày tới)</h3>
      </div>
      <table>
        <thead><tr><th>Nhân viên</th><th>Ngày</th><th>Ca làm</th><th>Ghi chú</th><th></th></tr></thead>
        <tbody id="schedule-rows"><tr><td colspan="5" class="empty-state">Đang tải...</td></tr></tbody>
      </table>
      <form id="schedule-form" class="form-grid" style="margin-top:14px;">
        <div class="form-field"><label>Nhân viên</label><select id="s-employee" required></select></div>
        <div class="form-field"><label>Ngày làm</label><input id="s-date" type="date" required></div>
        <div class="form-field"><label>Bắt đầu ca</label><input id="s-start" type="time"></div>
        <div class="form-field"><label>Kết thúc ca</label><input id="s-end" type="time"></div>
        <div class="form-field" style="grid-column: 1 / -1;"><label>Ghi chú</label><input id="s-note"></div>
      </form>
      <button class="btn btn-primary btn-sm" type="submit" form="schedule-form">Thêm lịch làm</button>
    </div>
  </div>

  <div>
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Nhân viên</h3>
      </div>
      <table>
        <thead><tr><th>Tên</th><th>Vai trò</th><?php if ($user['role'] === 'manager'): ?><th></th><?php endif; ?></tr></thead>
        <tbody id="employee-rows"><tr><td colspan="3" class="empty-state">Đang tải...</td></tr></tbody>
      </table>
      <?php if ($user['role'] === 'manager'): ?>
        <button class="btn btn-sm" style="margin-top:12px;" onclick="openModal('employee-modal')">+ Thêm nhân viên</button>
      <?php endif; ?>
    </div>

    <?php if ($user['role'] === 'manager'): ?>
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Mẫu Opening Checklist</h3>
      </div>
      <p class="page-sub" style="margin:-6px 0 12px;">Các mục cố định sẽ được sinh vào checklist mỗi khi bạn bấm "Tạo checklist hôm nay từ mẫu".</p>
      <div class="checklist" id="template-rows"></div>
      <form id="template-form" style="display:flex; gap:8px; margin-top:12px;">
        <input id="tpl-title" placeholder="Tên mục (VD: Bật đèn, kiểm kê quầy...)" style="flex:1;" required>
        <input id="tpl-sort" type="number" placeholder="Thứ tự" style="width:90px;" value="0">
        <button class="btn btn-primary btn-sm" type="submit">Thêm mẫu</button>
      </form>
    </div>
    <?php endif; ?>
  </div>
</div>

<?php if ($user['role'] === 'manager'): ?>
<div class="modal-backdrop" id="employee-modal">
  <div class="modal">
    <h3>Thêm nhân viên</h3>
    <form id="employee-form">
      <div class="form-field"><label>Họ tên</label><input id="e-name" required></div>
      <div class="form-field"><label>Email</label><input id="e-email" type="email" required></div>
      <div class="form-field"><label>Mật khẩu tạm</label><input id="e-password" type="password" required minlength="6"></div>
      <div class="form-field"><label>Vai trò</label>
        <select id="e-role"><option value="staff">Nhân viên</option><option value="manager">Quản lý</option></select>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn" onclick="closeModal('employee-modal')">Huỷ</button>
        <button type="submit" class="btn btn-primary">Tạo tài khoản</button>
      </div>
    </form>
  </div>
</div>
<?php endif; ?>

<script>const IS_MANAGER = <?= $user['role'] === 'manager' ? 'true' : 'false' ?>;</script>
<script src="assets/js/app.js"></script>
<script src="assets/js/team.js"></script>
<?php require __DIR__ . '/includes/footer.php'; ?>
