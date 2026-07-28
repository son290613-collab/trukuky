<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/auth.php';
require_once __DIR__ . '/includes/helpers.php';

if (current_user()) {
    header('Location: dashboard.php');
    exit;
}

$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = (string) ($_POST['password'] ?? '');

    if ($email === '' || $password === '') {
        $error = 'Vui lòng nhập đầy đủ email và mật khẩu.';
    } elseif (attempt_login($email, $password)) {
        header('Location: dashboard.php');
        exit;
    } else {
        $error = 'Email hoặc mật khẩu không đúng.';
    }
}
?><!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đăng nhập · Trukuky</title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="auth-wrap">
  <div class="auth-card">
    <h1>Trukuky</h1>
    <p class="sub">Đăng nhập để quản lý shop quần áo</p>
    <?php if ($error): ?>
      <div class="error-box"><?= e($error) ?></div>
    <?php endif; ?>
    <form method="post">
      <div class="form-field">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required autofocus value="<?= e($_POST['email'] ?? '') ?>">
      </div>
      <div class="form-field">
        <label for="password">Mật khẩu</label>
        <input type="password" id="password" name="password" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center;">Đăng nhập</button>
    </form>
  </div>
</div>
</body>
</html>
