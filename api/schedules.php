<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $from = $_GET['from'] ?? date('Y-m-d');
    $to = $_GET['to'] ?? date('Y-m-d', strtotime('+6 days'));
    $stmt = $pdo->prepare(
        "SELECT s.*, u.name AS employee_name FROM schedules s
         JOIN users u ON u.id = s.employee_id
         WHERE s.work_date BETWEEN ? AND ? ORDER BY s.work_date ASC, s.shift_start ASC"
    );
    $stmt->execute([$from, $to]);
    json_out($stmt->fetchAll());
}

check_csrf();
$input = json_input();

if ($method === 'POST') {
    $employeeId = (int) ($input['employee_id'] ?? 0);
    $workDate = $input['work_date'] ?? '';
    if (!$employeeId || !$workDate) json_out(['error' => 'Thiếu nhân viên hoặc ngày làm.'], 422);

    $stmt = $pdo->prepare('INSERT INTO schedules (employee_id, work_date, shift_start, shift_end, note) VALUES (?, ?, ?, ?, ?)');
    $stmt->execute([
        $employeeId,
        $workDate,
        $input['shift_start'] ?: null,
        $input['shift_end'] ?: null,
        $input['note'] ?? null,
    ]);
    json_out(['id' => (int) $pdo->lastInsertId()], 201);
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $pdo->prepare('DELETE FROM schedules WHERE id = ?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
