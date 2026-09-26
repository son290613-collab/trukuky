<?php
declare(strict_types=1);

/**
 * Nạp sổ tồn của một buổi live vào bảng live_items, rồi tạo sẵn một dòng trống
 * trong code_map cho từng (mã live, món) để bạn ngồi ghép mã.
 *
 * Dùng:
 *   php tools/import_so_live.php tools/b12_doisoat/so_ton_live20260917.csv
 *   php tools/import_so_live.php <file.csv> --date=2026-09-17
 *
 * Không có --date thì ngày lấy từ 8 chữ số trong tên file (so_ton_live20260917).
 *
 * Cột CSV cần có: ma_m, mon, cot_so, size_1, size_2, gia, sl_a, sl_b, ghi_chu_so
 *
 * Chạy lại nhiều lần được: live_items ghi đè theo (ngày, mã, món), còn code_map
 * chỉ thêm dòng mới — mã bạn đã ghép trước đó không bị xoá.
 */

require_once __DIR__ . '/../includes/db.php';

if (PHP_SAPI !== 'cli') {
    http_response_code(403);
    exit("Script này chỉ chạy từ dòng lệnh.\n");
}

$args = array_slice($argv, 1);
$csvPath = null;
$liveDate = null;

foreach ($args as $arg) {
    if (str_starts_with($arg, '--date=')) {
        $liveDate = substr($arg, 7);
    } elseif ($csvPath === null) {
        $csvPath = $arg;
    }
}

if ($csvPath === null) {
    exit("Thiếu đường dẫn file CSV.\nVí dụ: php tools/import_so_live.php tools/b12_doisoat/so_ton_live20260917.csv\n");
}
if (!is_readable($csvPath)) {
    exit("Không đọc được file: $csvPath\n");
}

if ($liveDate === null) {
    if (preg_match('/(\d{8})/', basename($csvPath), $m)) {
        $liveDate = substr($m[1], 0, 4) . '-' . substr($m[1], 4, 2) . '-' . substr($m[1], 6, 2);
    } else {
        exit("Không đoán được ngày live từ tên file. Thêm --date=YYYY-MM-DD.\n");
    }
}
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $liveDate) || !strtotime($liveDate)) {
    exit("Ngày live không hợp lệ: $liveDate (cần dạng YYYY-MM-DD)\n");
}

$fh = fopen($csvPath, 'r');
if ($fh === false) {
    exit("Không mở được file: $csvPath\n");
}

$header = fgetcsv($fh);
if ($header === false) {
    exit("File CSV rỗng.\n");
}
// Excel hay thêm BOM vào đầu file.
$header[0] = preg_replace('/^\xEF\xBB\xBF/', '', (string) $header[0]);
$header = array_map(fn($h) => trim((string) $h), $header);

$required = ['ma_m', 'mon', 'gia', 'sl_a'];
$missing = array_diff($required, $header);
if ($missing) {
    exit('File thiếu cột bắt buộc: ' . implode(', ', $missing) . "\nCột đang có: " . implode(', ', $header) . "\n");
}

/** Số nguyên từ ô CSV; ô rỗng hoặc chữ trả về 0. */
function cell_int(array $row, string $key): int
{
    $v = trim((string) ($row[$key] ?? ''));
    return ctype_digit($v) ? (int) $v : 0;
}

$groups = [];
$lineNo = 1;
$skipped = 0;

while (($raw = fgetcsv($fh)) !== false) {
    $lineNo++;
    if (count($raw) === 1 && trim((string) $raw[0]) === '') {
        continue;
    }
    $row = @array_combine($header, array_pad(array_slice($raw, 0, count($header)), count($header), ''));
    if ($row === false) {
        $skipped++;
        continue;
    }

    $ma = trim((string) ($row['ma_m'] ?? ''));
    $mon = trim((string) ($row['mon'] ?? ''));
    if ($ma === '' || $mon === '') {
        $skipped++;
        continue;
    }

    $key = $ma . '|' . $mon;
    if (!isset($groups[$key])) {
        $groups[$key] = ['ma' => $ma, 'mon' => $mon, 'sizes' => [], 'ton' => 0, 'gia' => [], 'ghi_chu' => ''];
    }
    $g = &$groups[$key];

    foreach (['size_1', 'size_2'] as $col) {
        $s = trim((string) ($row[$col] ?? ''));
        if ($s !== '' && !in_array($s, $g['sizes'], true)) {
            $g['sizes'][] = $s;
        }
    }
    // Dòng nào sổ không ghi size riêng thì lấy tên cột sổ làm size.
    if (!$g['sizes']) {
        $s = trim((string) ($row['cot_so'] ?? ''));
        if ($s !== '' && !in_array($s, $g['sizes'], true)) {
            $g['sizes'][] = $s;
        }
    }

    $g['ton'] += cell_int($row, 'sl_a') + cell_int($row, 'sl_b');

    $gia = cell_int($row, 'gia');
    if ($gia > 0) {
        $g['gia'][] = $gia;
    }

    $note = trim((string) ($row['ghi_chu_so'] ?? ''));
    if ($note !== '' && $g['ghi_chu'] === '') {
        $g['ghi_chu'] = $note;
    }
    unset($g);
}
fclose($fh);

if (!$groups) {
    exit("Không đọc được dòng dữ liệu nào.\n");
}

$pdo = db();
$pdo->beginTransaction();

$insItem = $pdo->prepare(
    'INSERT INTO live_items (live_date, ma_live, mon, sizes, size_count, ton, gia_min, gia_max, ghi_chu)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
     ON DUPLICATE KEY UPDATE sizes=VALUES(sizes), size_count=VALUES(size_count), ton=VALUES(ton),
                             gia_min=VALUES(gia_min), gia_max=VALUES(gia_max), ghi_chu=VALUES(ghi_chu)'
);
// Giữ nguyên dòng đã ghép: chỉ thêm dòng chưa có.
$insMap = $pdo->prepare(
    'INSERT INTO code_map (ma_live, mon) VALUES (?, ?)
     ON DUPLICATE KEY UPDATE id = id'
);

$newMappings = 0;
foreach ($groups as $g) {
    $insItem->execute([
        $liveDate,
        $g['ma'],
        $g['mon'],
        implode(' · ', $g['sizes']),
        count($g['sizes']),
        $g['ton'],
        $g['gia'] ? min($g['gia']) : 0,
        $g['gia'] ? max($g['gia']) : 0,
        $g['ghi_chu'] !== '' ? $g['ghi_chu'] : null,
    ]);
    $insMap->execute([$g['ma'], $g['mon']]);
    if ($insMap->rowCount() === 1) {
        $newMappings++;
    }
}

$pdo->commit();

$totalTon = array_sum(array_column($groups, 'ton'));
$unmapped = (int) $pdo->query("SELECT COUNT(*) FROM code_map WHERE status = 'chua_ghep'")->fetchColumn();

echo "Buổi live {$liveDate}\n";
echo '  ' . count($groups) . " (mã live, món), tổng tồn {$totalTon} món\n";
if ($skipped) {
    echo "  bỏ qua {$skipped} dòng thiếu mã hoặc món\n";
}
echo "  thêm {$newMappings} dòng mới vào sổ mã hàng\n";
echo "  còn {$unmapped} món chưa ghép mã — mở codemap.php để ghép\n";
