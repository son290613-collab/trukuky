<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    json_out(['error' => 'Method not allowed'], 405);
}

$from = $_GET['from'] ?? date('Y-m-d', strtotime('-6 days'));
$to = $_GET['to'] ?? date('Y-m-d');

if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $from) || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $to) || $from > $to) {
    json_out(['error' => 'Khoảng thời gian không hợp lệ.'], 422);
}

$stmt = $pdo->prepare(
    "SELECT DATE(created_at) AS day, COUNT(*) AS order_count, COALESCE(SUM(total_amount),0) AS revenue
     FROM orders
     WHERE DATE(created_at) BETWEEN ? AND ? AND status != 'cancelled'
     GROUP BY DATE(created_at) ORDER BY day ASC"
);
$stmt->execute([$from, $to]);
$rows = $stmt->fetchAll();

$totals = [
    'order_count' => (int) array_sum(array_column($rows, 'order_count')),
    'revenue' => array_sum(array_column($rows, 'revenue')),
];

json_out(['from' => $from, 'to' => $to, 'rows' => $rows, 'totals' => $totals]);
