<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/db.php';
require_once __DIR__ . '/includes/helpers.php';

// One-time setup: creates the first manager account.
// Delete this file from the server once you've logged in successfully.

$error = null;
$success = false;

try {
    $count = (int) db()->query('SELECT COUNT(*) FROM users')->fetchColumn();
} catch (PDOException $e) {
    $error = 'Chưa kết nối được database. Hãy chắc chắn bạn đã import sql/schema.sql và cấu hình config/config.php đúng. Chi tiết lỗi: ' . $e->getMessage();
    $count = null;
}

if ($count !== null && $count > 0) {
    $error = 'Hệ thống đã có tài khoản. Vì lý do an toàn, hãy xoá file install.php khỏi server.';
}

if ($error === null && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $password = (string) ($_POST['password'] ?? '');

    if ($name === '' || $email === '' || strlen($password) < 6) {
        $error = 'Vui lòng nhập đầy đủ tên, email và mật khẩu (tối thiểu 6 ký tự).';
    } else {
        $stmt = db()->prepare('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)');
        $stmt->execute([$name, $email, password_hash($password, PASSWORD_BCRYPT), 'manager']);
        $success = true;
    }
}
?><!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cài đặt ban đầu · Trukuky</title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="auth-wrap">
  <div class="auth-card">
    <h1>Cài đặt Trukuky</h1>
    <p class="sub">Tạo tài khoản quản lý đầu tiên</p>

    <?php if ($success): ?>
      <div class="error-box" style="background: var(--good-soft); color: var(--good);">
        Tạo tài khoản thành công! Hãy <strong>xoá file install.php</strong> khỏi server ngay bây giờ, sau đó <a href="login.php">đăng nhập</a>.
      </div>
    <?php elseif ($error): ?>
      <div class="error-box"><?= e($error) ?></div>
    <?php else: ?>
      <form method="post">
        <div class="form-field">
          <label for="name">Họ tên</label>
          <input type="text" id="name" name="name" required autofocus value="<?= e($_POST['name'] ?? '') ?>">
        </div>
        <div class="form-field">
          <label for="email">Email</label>
          <input type="email" id="email" name="email" required value="<?= e($_POST['email'] ?? '') ?>">
        </div>
        <div class="form-field">
          <label for="password">Mật khẩu</label>
          <input type="password" id="password" name="password" required minlength="6">
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center;">Tạo tài khoản quản lý</button>
      </form>
    <?php endif; ?>
  </div>
</div>
</body>
</html>
