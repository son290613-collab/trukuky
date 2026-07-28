<?php
/** Expects $pageTitle (string) and $activeNav (string) to be set before include. */
$user = current_user();
?><!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="csrf-token" content="<?= csrf_token() ?>">
<title><?= htmlspecialchars($pageTitle ?? 'Trukuky') ?> · Trukuky</title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <span class="brand-mark">TK</span>
      <div>
        <div class="brand-name">Trukuky</div>
        <div class="brand-sub">Quản lý shop quần áo</div>
      </div>
    </div>
    <nav class="nav">
      <a href="dashboard.php" class="nav-item <?= $activeNav === 'dashboard' ? 'active' : '' ?>">Tổng quan</a>
      <a href="orders.php" class="nav-item <?= $activeNav === 'orders' ? 'active' : '' ?>">Đơn hàng</a>
      <a href="inventory.php" class="nav-item <?= $activeNav === 'inventory' ? 'active' : '' ?>">Tồn kho</a>
      <a href="outfits.php" class="nav-item <?= $activeNav === 'outfits' ? 'active' : '' ?>">Phối đồ</a>
      <a href="reports.php" class="nav-item <?= $activeNav === 'reports' ? 'active' : '' ?>">Báo cáo</a>
      <a href="team.php" class="nav-item <?= $activeNav === 'team' ? 'active' : '' ?>">Nhân viên &amp; Lịch</a>
    </nav>
    <div class="sidebar-footer">
      <div class="user-chip">
        <div class="avatar"><?= htmlspecialchars(mb_substr($user['name'] ?? '?', 0, 1)) ?></div>
        <div>
          <div class="user-name"><?= htmlspecialchars($user['name'] ?? '') ?></div>
          <div class="user-role"><?= $user['role'] === 'manager' ? 'Quản lý' : 'Nhân viên' ?></div>
        </div>
      </div>
      <a href="logout.php" class="logout-link">Đăng xuất</a>
    </div>
  </aside>
  <main class="content">
