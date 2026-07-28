<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

$user = require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

function generate_order_code(PDO $pdo): string
{
    $today = date('ymd');
    $count = (int) $pdo->query("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE()")->fetchColumn();
    return sprintf('DH%s-%03d', $today, $count + 1);
}

if ($method === 'GET') {
    $orders = $pdo->query(
        "SELECT o.*, u.name AS created_by_name FROM orders o
         LEFT JOIN users u ON u.id = o.created_by
         ORDER BY o.created_at DESC LIMIT 200"
    )->fetchAll();

    $itemsStmt = $pdo->prepare(
        "SELECT oi.product_id, oi.quantity, oi.unit_price, p.name AS product_name
         FROM order_items oi JOIN products p ON p.id = oi.product_id
         WHERE oi.order_id = ?"
    );
    foreach ($orders as &$o) {
        $itemsStmt->execute([$o['id']]);
        $o['items'] = $itemsStmt->fetchAll();
    }
    json_out($orders);
}

check_csrf();
$input = json_input();

if ($method === 'POST') {
    $items = $input['items'] ?? [];
    if (!is_array($items) || count($items) === 0) {
        json_out(['error' => 'Đơn hàng cần ít nhất 1 sản phẩm.'], 422);
    }

    $pdo->beginTransaction();
    try {
        $productStmt = $pdo->prepare('SELECT id, price, quantity FROM products WHERE id = ? FOR UPDATE');
        $total = 0;
        $rows = [];
        foreach ($items as $item) {
            $productStmt->execute([(int) $item['product_id']]);
            $product = $productStmt->fetch();
            if (!$product) {
                throw new RuntimeException('Sản phẩm không tồn tại.');
            }
            $qty = max(1, (int) $item['quantity']);
            if ($product['quantity'] < $qty) {
                throw new RuntimeException('Sản phẩm không đủ tồn kho.');
            }
            $total += $product['price'] * $qty;
            $rows[] = ['product_id' => $product['id'], 'quantity' => $qty, 'unit_price' => $product['price']];
        }

        $code = generate_order_code($pdo);
        $orderStmt = $pdo->prepare(
            'INSERT INTO orders (order_code, customer_name, customer_phone, total_amount, status, created_by)
             VALUES (?, ?, ?, ?, ?, ?)'
        );
        $orderStmt->execute([
            $code,
            $input['customer_name'] ?? null,
            $input['customer_phone'] ?? null,
            $total,
            'completed',
            $user['id'],
        ]);
        $orderId = (int) $pdo->lastInsertId();

        $itemStmt = $pdo->prepare('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)');
        $stockStmt = $pdo->prepare('UPDATE products SET quantity = quantity - ? WHERE id = ?');
        foreach ($rows as $r) {
            $itemStmt->execute([$orderId, $r['product_id'], $r['quantity'], $r['unit_price']]);
            $stockStmt->execute([$r['quantity'], $r['product_id']]);
        }

        $pdo->commit();
        json_out(['id' => $orderId, 'order_code' => $code], 201);
    } catch (Throwable $e) {
        $pdo->rollBack();
        json_out(['error' => $e->getMessage()], 422);
    }
}

if ($method === 'PUT') {
    $id = (int) ($input['id'] ?? 0);
    $status = $input['status'] ?? '';
    if (!$id || !in_array($status, ['pending', 'completed', 'cancelled'], true)) {
        json_out(['error' => 'Dữ liệu không hợp lệ.'], 422);
    }

    $pdo->beginTransaction();
    try {
        $current = $pdo->prepare('SELECT status FROM orders WHERE id = ? FOR UPDATE');
        $current->execute([$id]);
        $row = $current->fetch();
        if (!$row) throw new RuntimeException('Không tìm thấy đơn hàng.');

        $wasCancelled = $row['status'] === 'cancelled';
        $nowCancelled = $status === 'cancelled';

        if ($wasCancelled !== $nowCancelled) {
            $items = $pdo->prepare('SELECT product_id, quantity FROM order_items WHERE order_id = ?');
            $items->execute([$id]);
            $stockStmt = $pdo->prepare('UPDATE products SET quantity = quantity ' . ($nowCancelled ? '+' : '-') . ' ? WHERE id = ?');
            foreach ($items->fetchAll() as $it) {
                $stockStmt->execute([$it['quantity'], $it['product_id']]);
            }
        }

        $pdo->prepare('UPDATE orders SET status = ? WHERE id = ?')->execute([$status, $id]);
        $pdo->commit();
        json_out(['ok' => true]);
    } catch (Throwable $e) {
        $pdo->rollBack();
        json_out(['error' => $e->getMessage()], 422);
    }
}

json_out(['error' => 'Method not allowed'], 405);
