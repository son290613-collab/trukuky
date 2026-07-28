<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $stmt = $pdo->query('SELECT * FROM products ORDER BY name ASC');
    json_out($stmt->fetchAll());
}

check_csrf();
$input = json_input();

if ($method === 'POST') {
    $name = trim($input['name'] ?? '');
    $sku = trim($input['sku'] ?? '');
    if ($name === '' || $sku === '') {
        json_out(['error' => 'Tên và SKU là bắt buộc.'], 422);
    }

    $stmt = $pdo->prepare(
        'INSERT INTO products (name, sku, category, size, color, price, cost, quantity, low_stock_threshold, image_url)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    try {
        $stmt->execute([
            $name,
            $sku,
            $input['category'] ?? null,
            $input['size'] ?? null,
            $input['color'] ?? null,
            (float) ($input['price'] ?? 0),
            (float) ($input['cost'] ?? 0),
            (int) ($input['quantity'] ?? 0),
            (int) ($input['low_stock_threshold'] ?? 5),
            $input['image_url'] ?? null,
        ]);
    } catch (PDOException $e) {
        json_out(['error' => 'SKU đã tồn tại.'], 422);
    }
    json_out(['id' => (int) $pdo->lastInsertId()], 201);
}

if ($method === 'PUT') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);

    $stmt = $pdo->prepare(
        'UPDATE products SET name=?, sku=?, category=?, size=?, color=?, price=?, cost=?, quantity=?, low_stock_threshold=?, image_url=? WHERE id=?'
    );
    try {
        $stmt->execute([
            trim($input['name'] ?? ''),
            trim($input['sku'] ?? ''),
            $input['category'] ?? null,
            $input['size'] ?? null,
            $input['color'] ?? null,
            (float) ($input['price'] ?? 0),
            (float) ($input['cost'] ?? 0),
            (int) ($input['quantity'] ?? 0),
            (int) ($input['low_stock_threshold'] ?? 5),
            $input['image_url'] ?? null,
            $id,
        ]);
    } catch (PDOException $e) {
        json_out(['error' => 'SKU đã tồn tại.'], 422);
    }
    json_out(['ok' => true]);
}

if ($method === 'DELETE') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) json_out(['error' => 'Thiếu id.'], 422);
    $pdo->prepare('DELETE FROM products WHERE id=?')->execute([$id]);
    json_out(['ok' => true]);
}

json_out(['error' => 'Method not allowed'], 405);
