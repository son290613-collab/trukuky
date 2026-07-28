<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $outfits = $pdo->query('SELECT * FROM outfits ORDER BY created_at DESC')->fetchAll();
    $itemStmt = $pdo->prepare(
        'SELECT p.id, p.name, p.sku FROM outfit_items oi JOIN products p ON p.id = oi.product_id WHERE oi.outfit_id = ?'
    );
    foreach ($outfits as &$o) {
        $itemStmt->execute([$o['id']]);
        $o['items'] = $itemStmt->fetchAll();
    }
    json_out($outfits);
}

check_csrf();
$input = json_input();

if ($method === 'POST') {
    $name = trim($input['name'] ?? '');
    $productIds = array_filter(array_map('intval', $input['product_ids'] ?? []));
    if ($name === '' || count($productIds) < 2) {
        json_out(['error' => 'Tên bộ phối đồ và tối thiểu 2 sản phẩm là bắt buộc.'], 422);
    }

    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare('INSERT INTO outfits (name, description, image_url) VALUES (?, ?, ?)');
        $stmt->execute([$name, $input['description'] ?? null, $input['image_url'] ?? null]);
        $outfitId = (int) $pdo->lastInsertId();

        $itemStmt = $pdo->prepare('INSERT INTO outfit_items (outfit_id, product_id) VALUES (?, ?)');
        foreach ($productIds as $pid) {
            $itemStmt->execute([$outfitId, $pid]);
        }
        $pdo->commit();
        json_out(['id' => $outfitId], 201);
    } catch (Throwable $e) {
        $pdo->rollBack();
        json_out(['error' => 'Không thể tạo bộ phối đồ.'], 422);
    }
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $pdo->prepare('DELETE FROM outfits WHERE id = ?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
