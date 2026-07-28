<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $date = $_GET['date'] ?? date('Y-m-d');
    $stmt = $pdo->prepare(
        "SELECT t.id, t.title, t.status, t.task_date, t.assigned_to, u.name AS assignee
         FROM tasks t LEFT JOIN users u ON u.id = t.assigned_to
         WHERE t.task_date = ? ORDER BY t.sort_order ASC, t.id ASC"
    );
    $stmt->execute([$date]);
    json_out($stmt->fetchAll());
}

check_csrf();
$input = json_input();

if ($method === 'POST') {
    $title = trim($input['title'] ?? '');
    $date = $input['task_date'] ?? date('Y-m-d');
    if ($title === '') json_out(['error' => 'Tên việc cần làm là bắt buộc.'], 422);

    $stmt = $pdo->prepare('INSERT INTO tasks (title, assigned_to, task_date, sort_order) VALUES (?, ?, ?, ?)');
    $stmt->execute([
        $title,
        !empty($input['assigned_to']) ? (int) $input['assigned_to'] : null,
        $date,
        (int) ($input['sort_order'] ?? 0),
    ]);
    json_out(['id' => (int) $pdo->lastInsertId()], 201);
}

if ($method === 'PUT') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $status = ($input['status'] ?? '') === 'done' ? 'done' : 'pending';
    $pdo->prepare('UPDATE tasks SET status = ? WHERE id = ?')->execute([$status, $id]);
    json_out(['ok' => true]);
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $pdo->prepare('DELETE FROM tasks WHERE id = ?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
