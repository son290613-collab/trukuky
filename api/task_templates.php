<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    json_out($pdo->query('SELECT * FROM task_templates ORDER BY sort_order ASC, id ASC')->fetchAll());
}

check_csrf();
$input = json_input();

if ($method === 'POST' && ($input['action'] ?? '') === 'generate') {
    $date = $input['task_date'] ?? date('Y-m-d');
    $exists = $pdo->prepare('SELECT COUNT(*) FROM tasks WHERE task_date = ? AND source_template_id IS NOT NULL');
    $exists->execute([$date]);
    if ((int) $exists->fetchColumn() > 0) {
        json_out(['created' => 0, 'message' => 'Checklist mở cửa cho ngày này đã được tạo trước đó.']);
    }

    $templates = $pdo->query(
        'SELECT id, title, sort_order FROM task_templates WHERE active = 1 ORDER BY sort_order ASC, id ASC'
    )->fetchAll();
    $stmt = $pdo->prepare(
        'INSERT INTO tasks (title, task_date, sort_order, source_template_id) VALUES (?, ?, ?, ?)'
    );
    foreach ($templates as $t) {
        $stmt->execute([$t['title'], $date, $t['sort_order'], $t['id']]);
    }
    json_out(['created' => count($templates)], 201);
}

require_manager();

if ($method === 'POST') {
    $title = trim($input['title'] ?? '');
    if ($title === '') json_out(['error' => 'Tên mục checklist là bắt buộc.'], 422);

    $stmt = $pdo->prepare('INSERT INTO task_templates (title, sort_order) VALUES (?, ?)');
    $stmt->execute([$title, (int) ($input['sort_order'] ?? 0)]);
    json_out(['id' => (int) $pdo->lastInsertId()], 201);
}

if ($method === 'PUT') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);

    $title = trim($input['title'] ?? '');
    if ($title === '') json_out(['error' => 'Tên mục checklist là bắt buộc.'], 422);

    $stmt = $pdo->prepare('UPDATE task_templates SET title=?, sort_order=?, active=? WHERE id=?');
    $stmt->execute([
        $title,
        (int) ($input['sort_order'] ?? 0),
        !empty($input['active']) ? 1 : 0,
        $id,
    ]);
    json_out(['ok' => true]);
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $pdo->prepare('DELETE FROM task_templates WHERE id = ?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
