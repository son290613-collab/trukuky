<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

$user = require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    json_out($pdo->query('SELECT id, name, email, role, created_at FROM users ORDER BY role DESC, name ASC')->fetchAll());
}

check_csrf();
require_manager();
$input = json_input();

if ($method === 'POST') {
    $name = trim($input['name'] ?? '');
    $email = trim($input['email'] ?? '');
    $password = (string) ($input['password'] ?? '');
    $role = in_array($input['role'] ?? '', ['manager', 'staff'], true) ? $input['role'] : 'staff';

    if ($name === '' || $email === '' || strlen($password) < 6) {
        json_out(['error' => 'Vui lòng nhập đầy đủ tên, email, mật khẩu (tối thiểu 6 ký tự).'], 422);
    }

    $stmt = $pdo->prepare('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)');
    try {
        $stmt->execute([$name, $email, password_hash($password, PASSWORD_BCRYPT), $role]);
    } catch (PDOException $e) {
        json_out(['error' => 'Email đã tồn tại.'], 422);
    }
    json_out(['id' => (int) $pdo->lastInsertId()], 201);
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id || $id === $user['id']) {
        json_out(['error' => 'Không thể xoá tài khoản này.'], 422);
    }
    $pdo->prepare('DELETE FROM users WHERE id = ?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
