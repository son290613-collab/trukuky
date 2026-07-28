<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

$user = require_login();
$pdo = db();

$todayStats = $pdo->query(
    "SELECT COUNT(*) AS order_count, COALESCE(SUM(total_amount),0) AS revenue
     FROM orders WHERE DATE(created_at) = CURDATE() AND status != 'cancelled'"
)->fetch();

$totalProducts = (int) $pdo->query('SELECT COUNT(*) FROM products')->fetchColumn();

$lowStock = $pdo->query(
    'SELECT id, name, sku, size, color, quantity, low_stock_threshold
     FROM products WHERE quantity <= low_stock_threshold
     ORDER BY quantity ASC LIMIT 6'
)->fetchAll();
$lowStockCount = (int) $pdo->query('SELECT COUNT(*) FROM products WHERE quantity <= low_stock_threshold')->fetchColumn();

$todayTasks = $pdo->prepare(
    "SELECT t.id, t.title, t.status, u.name AS assignee
     FROM tasks t LEFT JOIN users u ON u.id = t.assigned_to
     WHERE t.task_date = CURDATE() ORDER BY t.sort_order ASC, t.id ASC"
);
$todayTasks->execute();
$todayTasks = $todayTasks->fetchAll();
$doneCount = count(array_filter($todayTasks, fn($t) => $t['status'] === 'done'));

$recentOrders = $pdo->query(
    "SELECT id, order_code, customer_name, total_amount, status, created_at
     FROM orders ORDER BY created_at DESC LIMIT 6"
)->fetchAll();

$statusLabel = ['pending' => 'Đang xử lý', 'completed' => 'Hoàn thành', 'cancelled' => 'Đã huỷ'];
$statusBadge = ['pending' => 'badge-warn', 'completed' => 'badge-good', 'cancelled' => 'badge-bad'];

$pageTitle = 'Tổng quan';
$activeNav = 'dashboard';
require __DIR__ . '/includes/header.php';
?>
<div class="topbar">
  <div>
    <h1 class="page-title">Chào buổi sáng, <?= e($user['name']) ?> 👋</h1>
    <p class="page-sub">Hôm nay là <?= date('d/m/Y') ?> — đây là tình hình shop của bạn.</p>
  </div>
</div>

<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-label">Đơn hàng hôm nay</div>
    <div class="stat-value"><?= (int) $todayStats['order_count'] ?></div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Doanh thu hôm nay</div>
    <div class="stat-value"><?= format_vnd($todayStats['revenue']) ?></div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Sản phẩm đang bán</div>
    <div class="stat-value"><?= $totalProducts ?></div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Sắp hết hàng</div>
    <div class="stat-value"><?= $lowStockCount ?></div>
  </div>
</div>

<div class="grid-2">
  <div>
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Đơn hàng gần đây</h3>
        <a class="card-link" href="orders.php">Xem tất cả →</a>
      </div>
      <?php if (!$recentOrders): ?>
        <div class="empty-state">Chưa có đơn hàng nào.</div>
      <?php else: ?>
        <table>
          <thead><tr><th>Mã đơn</th><th>Khách hàng</th><th>Tổng tiền</th><th>Trạng thái</th></tr></thead>
          <tbody>
          <?php foreach ($recentOrders as $o): ?>
            <tr>
              <td><?= e($o['order_code']) ?></td>
              <td><?= e($o['customer_name'] ?: '—') ?></td>
              <td><?= format_vnd($o['total_amount']) ?></td>
              <td><span class="badge <?= $statusBadge[$o['status']] ?>"><?= $statusLabel[$o['status']] ?></span></td>
            </tr>
          <?php endforeach; ?>
          </tbody>
        </table>
      <?php endif; ?>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Việc cần làm hôm nay (<?= $doneCount ?>/<?= count($todayTasks) ?>)</h3>
        <a class="card-link" href="team.php">Quản lý →</a>
      </div>
      <?php if (!$todayTasks): ?>
        <div class="empty-state">Chưa có việc nào cho hôm nay. Thêm checklist trong mục Nhân viên &amp; Lịch.</div>
      <?php else: ?>
        <div class="checklist">
          <?php foreach ($todayTasks as $t): ?>
            <div class="check-row <?= $t['status'] === 'done' ? 'done' : '' ?>">
              <span><?= $t['status'] === 'done' ? '✅' : '⬜️' ?></span>
              <span class="check-label"><?= e($t['title']) ?></span>
              <span class="check-meta"><?= e($t['assignee'] ?: 'Chưa giao') ?></span>
            </div>
          <?php endforeach; ?>
        </div>
      <?php endif; ?>
    </div>
  </div>

  <div>
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Cảnh báo sắp hết hàng</h3>
        <a class="card-link" href="inventory.php">Xem kho →</a>
      </div>
      <?php if (!$lowStock): ?>
        <div class="empty-state">Tồn kho ổn định, không có sản phẩm sắp hết.</div>
      <?php else: ?>
        <?php foreach ($lowStock as $p): ?>
          <div class="low-stock-row">
            <div>
              <strong><?= e($p['name']) ?></strong><br>
              <span class="check-meta"><?= e($p['sku']) ?> · <?= e($p['size'] ?: '-') ?> / <?= e($p['color'] ?: '-') ?></span>
            </div>
            <span class="badge badge-bad"><?= $p['quantity'] ?> còn lại</span>
          </div>
        <?php endforeach; ?>
      <?php endif; ?>
    </div>
  </div>
</div>
<?php require __DIR__ . '/includes/footer.php'; ?>
