<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();
$pdo = db();
$method = $_SERVER['REQUEST_METHOD'];

/** Một dòng cho mỗi (mã live, món), kèm số liệu buổi live gần nhất và tên hàng bên KiotViet. */
function code_map_rows(PDO $pdo): array
{
    return $pdo->query(
        "SELECT cm.id, cm.ma_live, cm.mon, cm.kiotviet_code, cm.ten_mon_dung, cm.status, cm.note, cm.updated_at,
                li.live_date, li.sizes, li.size_count, li.ton, li.gia_min, li.gia_max, li.ghi_chu,
                kp.name AS kiotviet_name, kp.category AS kiotviet_category, kp.on_hand AS kiotviet_on_hand
         FROM code_map cm
         LEFT JOIN live_items li
                ON li.ma_live = cm.ma_live AND li.mon = cm.mon
               AND li.live_date = (SELECT MAX(l2.live_date) FROM live_items l2
                                   WHERE l2.ma_live = cm.ma_live AND l2.mon = cm.mon)
         LEFT JOIN kiotviet_products kp ON kp.code = cm.kiotviet_code
         ORDER BY cm.ma_live ASC, cm.mon ASC"
    )->fetchAll();
}

if ($method === 'GET') {
    $rows = code_map_rows($pdo);
    $kvCount = (int) $pdo->query('SELECT COUNT(*) FROM kiotviet_products')->fetchColumn();

    // Hai (mã live, món) trỏ về cùng một mã KiotViet = chung một kho.
    // Đây là cái bẫy đã làm 33 chiếc bán vượt kho mà không ai thấy ở buổi 17/09.
    $byCode = [];
    foreach ($rows as $r) {
        $code = trim((string) ($r['kiotviet_code'] ?? ''));
        if ($code !== '') {
            $byCode[$code][] = $r['ma_live'] . ' ' . $r['mon'];
        }
    }
    $shared = [];
    foreach ($byCode as $code => $names) {
        if (count($names) > 1) {
            $shared[] = ['kiotviet_code' => $code, 'items' => $names];
        }
    }

    // Mã đã gõ nhưng KiotViet không có — chỉ kiểm được khi đã đồng bộ danh mục.
    $unknown = [];
    if ($kvCount > 0) {
        foreach ($rows as $r) {
            $code = trim((string) ($r['kiotviet_code'] ?? ''));
            if ($code !== '' && $r['kiotviet_name'] === null) {
                $unknown[] = ['ma_live' => $r['ma_live'], 'mon' => $r['mon'], 'kiotviet_code' => $code];
            }
        }
    }

    $counts = ['chua_ghep' => 0, 'da_ghep' => 0, 'khong_co' => 0];
    foreach ($rows as $r) {
        $counts[$r['status']] = ($counts[$r['status']] ?? 0) + 1;
    }

    if (($_GET['export'] ?? '') === 'csv') {
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="so_ma_hang_' . date('Ymd') . '.csv"');
        $out = fopen('php://output', 'w');
        fwrite($out, "\xEF\xBB\xBF"); // BOM để Excel đọc đúng tiếng Việt
        fputcsv($out, ['ma_live', 'mon', 'kiotviet_code', 'ten_tren_kiotviet', 'ten_mon_dung',
                       'trang_thai', 'sizes', 'ton_dau_buoi', 'gia_min', 'gia_max', 'ghi_chu']);
        foreach ($rows as $r) {
            fputcsv($out, [
                $r['ma_live'], $r['mon'], $r['kiotviet_code'], $r['kiotviet_name'], $r['ten_mon_dung'],
                $r['status'], $r['sizes'], $r['ton'], $r['gia_min'], $r['gia_max'], $r['note'],
            ]);
        }
        fclose($out);
        exit;
    }

    json_out([
        'items' => $rows,
        'kiotviet' => $pdo->query(
            'SELECT code, name, category, retail_price, on_hand FROM kiotviet_products ORDER BY code ASC LIMIT 3000'
        )->fetchAll(),
        'kiotviet_total' => $kvCount,
        'counts' => $counts,
        'warnings' => ['shared' => $shared, 'unknown' => $unknown],
    ]);
}

check_csrf();
$input = json_input();

if ($method === 'PUT') {
    $id = (int) ($input['id'] ?? 0);
    if (!$id) {
        json_out(['error' => 'Thiếu id.'], 422);
    }

    $code = trim((string) ($input['kiotviet_code'] ?? ''));
    $status = (string) ($input['status'] ?? '');
    $tenDung = trim((string) ($input['ten_mon_dung'] ?? ''));
    $note = trim((string) ($input['note'] ?? ''));

    // Trạng thái suy ra từ dữ liệu, không nhận thẳng từ giao diện — như vậy
    // không thể có dòng "đã ghép" mà bỏ trống mã.
    if ($status === 'khong_co') {
        $code = '';
        $status = 'khong_co';
    } else {
        $status = $code !== '' ? 'da_ghep' : 'chua_ghep';
    }

    if (mb_strlen($code) > 60 || mb_strlen($tenDung) > 255 || mb_strlen($note) > 500) {
        json_out(['error' => 'Nội dung quá dài.'], 422);
    }

    $user = current_user();
    $pdo->prepare(
        'UPDATE code_map SET kiotviet_code=?, ten_mon_dung=?, status=?, note=?, updated_by=? WHERE id=?'
    )->execute([
        $code !== '' ? $code : null,
        $tenDung !== '' ? $tenDung : null,
        $status,
        $note !== '' ? $note : null,
        $user['id'] ?? null,
        $id,
    ]);

    json_out(['ok' => true, 'status' => $status]);
}

json_out(['error' => 'Method not allowed'], 405);
