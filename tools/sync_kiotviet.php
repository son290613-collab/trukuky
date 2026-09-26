<?php
declare(strict_types=1);

/**
 * Kéo danh sách hàng từ KiotViet vào bảng kiotviet_products để dùng khi ghép mã.
 * Bảng này chỉ để tra — nguồn chân lý vẫn là KiotViet, script không ghi ngược lại.
 *
 * Hai đường vào, dùng cái nào cũng được:
 *
 *   1) Gọi thẳng API (cần bật kết nối trong KiotViet và đặt 3 biến môi trường):
 *        export KIOTVIET_CLIENT_ID=...
 *        export KIOTVIET_CLIENT_SECRET=...
 *        export KIOTVIET_RETAILER=...        # tên gian hàng, phần đầu của địa chỉ KiotViet
 *        php tools/sync_kiotviet.php
 *
 *   2) Nạp từ file xuất ra từ KiotViet (Hàng hoá → Xuất file), không cần mạng:
 *        php tools/sync_kiotviet.php --csv=danh_muc_hang_hoa.csv
 *
 * Thêm --dry-run để xem đọc được gì mà chưa ghi vào database.
 *
 * LƯU Ý: phần gọi API chưa được chạy thử với KiotViet thật (môi trường dựng
 * script này bị chặn mạng ra ngoài). Chạy lần đầu nên kèm --dry-run.
 */

require_once __DIR__ . '/../includes/db.php';

if (PHP_SAPI !== 'cli') {
    http_response_code(403);
    exit("Script này chỉ chạy từ dòng lệnh.\n");
}

const TOKEN_URL = 'https://id.kiotviet.vn/connect/token';
const API_URL = 'https://public.kiotapi.com';
const PAGE_SIZE = 100;

$csvFile = null;
$dryRun = false;
foreach (array_slice($argv, 1) as $arg) {
    if (str_starts_with($arg, '--csv=')) {
        $csvFile = substr($arg, 6);
    } elseif ($arg === '--dry-run') {
        $dryRun = true;
    } else {
        exit("Tham số không hiểu: $arg\n");
    }
}

/** Bỏ dấu tiếng Việt và hạ chữ thường, để so tên cột trong file xuất. */
function fold(string $s): string
{
    $from = 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ';
    $to   = 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd';
    $s = mb_strtolower(trim($s), 'UTF-8');
    $fromArr = preg_split('//u', $from, -1, PREG_SPLIT_NO_EMPTY);
    $toArr = preg_split('//u', $to, -1, PREG_SPLIT_NO_EMPTY);
    return str_replace($fromArr, $toArr, $s);
}

/**
 * Tìm chỉ số cột đầu tiên khớp một trong các tên cho trước (đã bỏ dấu).
 * Trả về null nếu không có cột nào khớp.
 */
function find_col(array $header, array $candidates): ?int
{
    foreach ($header as $i => $name) {
        $f = fold((string) $name);
        foreach ($candidates as $c) {
            if ($f === $c || str_starts_with($f, $c)) {
                return $i;
            }
        }
    }
    return null;
}

/** Số nguyên từ chuỗi có thể chứa dấu chấm/phẩy ngăn nghìn. */
function to_int(string $s): int
{
    $s = preg_replace('/[^\d-]/', '', $s) ?? '';
    return $s === '' ? 0 : (int) $s;
}

// ---------------------------------------------------------------- đọc từ CSV

function read_from_csv(string $path): array
{
    if (!is_readable($path)) {
        exit("Không đọc được file: $path\n");
    }
    $fh = fopen($path, 'r');
    if ($fh === false) {
        exit("Không mở được file: $path\n");
    }
    $header = fgetcsv($fh);
    if ($header === false) {
        exit("File rỗng.\n");
    }
    $header[0] = preg_replace('/^\xEF\xBB\xBF/', '', (string) $header[0]);

    $cols = [
        'code' => find_col($header, ['ma hang', 'ma hang hoa', 'ma', 'code']),
        'name' => find_col($header, ['ten hang', 'ten hang hoa', 'ten', 'name']),
        'category' => find_col($header, ['nhom hang', 'nhom', 'category']),
        'price' => find_col($header, ['gia ban', 'don gia', 'price']),
        'on_hand' => find_col($header, ['ton kho', 'ton cuoi', 'ton', 'onhand']),
    ];
    if ($cols['code'] === null || $cols['name'] === null) {
        fclose($fh);
        exit("Không tìm thấy cột mã hàng và tên hàng.\nCột đang có: " . implode(' | ', $header) . "\n");
    }

    echo "Đọc file: $path\n";
    foreach ($cols as $k => $i) {
        echo sprintf("  %-8s → %s\n", $k, $i === null ? '(không có)' : $header[$i]);
    }

    $rows = [];
    while (($raw = fgetcsv($fh)) !== false) {
        $get = fn(?int $i) => $i === null ? '' : trim((string) ($raw[$i] ?? ''));
        $code = $get($cols['code']);
        $name = $get($cols['name']);
        if ($code === '' || $name === '') {
            continue;
        }
        $rows[] = [
            'code' => $code,
            'name' => $name,
            'full_name' => null,
            'category' => $get($cols['category']) ?: null,
            'retail_price' => to_int($get($cols['price'])),
            'on_hand' => $cols['on_hand'] === null ? null : to_int($get($cols['on_hand'])),
        ];
    }
    fclose($fh);
    return $rows;
}

// ---------------------------------------------------------------- đọc từ API

function http_post_form(string $url, array $fields): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => http_build_query($fields),
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded'],
    ]);
    $body = curl_exec($ch);
    $err = curl_error($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($body === false) {
        exit("Không gọi được $url — $err\nNếu máy chủ chặn ra ngoài, dùng cách 2: --csv=<file xuất từ KiotViet>\n");
    }
    return [$status, (string) $body];
}

function http_get_json(string $url, array $headers): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 60,
        CURLOPT_HTTPHEADER => $headers,
    ]);
    $body = curl_exec($ch);
    $err = curl_error($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($body === false) {
        exit("Không gọi được $url — $err\n");
    }
    return [$status, (string) $body];
}

function read_from_api(): array
{
    $id = getenv('KIOTVIET_CLIENT_ID') ?: '';
    $secret = getenv('KIOTVIET_CLIENT_SECRET') ?: '';
    $retailer = getenv('KIOTVIET_RETAILER') ?: '';
    $missing = [];
    if ($id === '') $missing[] = 'KIOTVIET_CLIENT_ID';
    if ($secret === '') $missing[] = 'KIOTVIET_CLIENT_SECRET';
    if ($retailer === '') $missing[] = 'KIOTVIET_RETAILER';
    if ($missing) {
        exit('Thiếu biến môi trường: ' . implode(', ', $missing)
            . "\nĐặt chúng rồi chạy lại, hoặc dùng cách 2: --csv=<file xuất từ KiotViet>\n");
    }

    [$status, $body] = http_post_form(TOKEN_URL, [
        'scopes' => 'PublicApi.Access',
        'grant_type' => 'client_credentials',
        'client_id' => $id,
        'client_secret' => $secret,
    ]);
    $tok = json_decode($body, true);
    if ($status !== 200 || !is_array($tok) || empty($tok['access_token'])) {
        exit("KiotViet không cấp token (HTTP $status).\n"
            . "Kiểm tra client id/secret và quyền PublicApi.Access.\n"
            . 'Phản hồi: ' . mb_substr($body, 0, 300) . "\n");
    }
    $headers = [
        'Retailer: ' . $retailer,
        'Authorization: Bearer ' . $tok['access_token'],
    ];

    $rows = [];
    $cursor = 0;
    $total = null;
    do {
        $url = API_URL . '/products?' . http_build_query([
            'pageSize' => PAGE_SIZE,
            'currentItem' => $cursor,
            'includeInventory' => 'true',
        ]);
        [$status, $body] = http_get_json($url, $headers);
        if ($status !== 200) {
            exit("KiotViet trả lỗi khi lấy danh sách hàng (HTTP $status).\n"
                . 'Phản hồi: ' . mb_substr($body, 0, 300) . "\n");
        }
        $page = json_decode($body, true);
        if (!is_array($page) || !isset($page['data']) || !is_array($page['data'])) {
            exit("Phản hồi của KiotViet không có mục 'data' như mong đợi.\n"
                . 'Phản hồi: ' . mb_substr($body, 0, 300) . "\n");
        }
        if ($total === null) {
            $total = (int) ($page['total'] ?? count($page['data']));
            echo "KiotViet báo có {$total} mặt hàng\n";
        }
        foreach ($page['data'] as $p) {
            $code = trim((string) ($p['code'] ?? ''));
            $name = trim((string) ($p['name'] ?? ''));
            if ($code === '' || $name === '') {
                continue;
            }
            $onHand = null;
            if (!empty($p['inventories']) && is_array($p['inventories'])) {
                $onHand = 0;
                foreach ($p['inventories'] as $inv) {
                    $onHand += (int) ($inv['onHand'] ?? 0);
                }
            }
            $rows[] = [
                'code' => $code,
                'name' => $name,
                'full_name' => trim((string) ($p['fullName'] ?? '')) ?: null,
                'category' => trim((string) ($p['categoryName'] ?? '')) ?: null,
                'retail_price' => (int) round((float) ($p['basePrice'] ?? 0)),
                'on_hand' => $onHand,
            ];
        }
        $got = count($page['data']);
        $cursor += $got;
        echo "  đã lấy {$cursor}/{$total}\n";
    } while ($got === PAGE_SIZE && $cursor < $total);

    return $rows;
}

// ---------------------------------------------------------------------- chạy

$rows = $csvFile !== null ? read_from_csv($csvFile) : read_from_api();

if (!$rows) {
    exit("Không đọc được mặt hàng nào.\n");
}

// Mã trùng trong nguồn: giữ dòng cuối, báo cho người dùng biết.
$byCode = [];
foreach ($rows as $r) {
    $byCode[$r['code']] = $r;
}
$dupes = count($rows) - count($byCode);

if ($dryRun) {
    echo "\n--dry-run: chưa ghi gì vào database.\n";
    echo 'Đọc được ' . count($byCode) . " mã hàng. Năm dòng đầu:\n";
    foreach (array_slice($byCode, 0, 5) as $r) {
        echo sprintf("  %-20s %s  (%s)\n", $r['code'], $r['name'], $r['category'] ?? '—');
    }
    exit(0);
}

$pdo = db();
$pdo->beginTransaction();
$stmt = $pdo->prepare(
    'INSERT INTO kiotviet_products (code, name, full_name, category, retail_price, on_hand)
     VALUES (?, ?, ?, ?, ?, ?)
     ON DUPLICATE KEY UPDATE name=VALUES(name), full_name=VALUES(full_name), category=VALUES(category),
                             retail_price=VALUES(retail_price), on_hand=VALUES(on_hand)'
);
foreach ($byCode as $r) {
    $stmt->execute([$r['code'], $r['name'], $r['full_name'], $r['category'], $r['retail_price'], $r['on_hand']]);
}
$pdo->commit();

$stored = (int) $pdo->query('SELECT COUNT(*) FROM kiotviet_products')->fetchColumn();
echo "\nĐã lưu " . count($byCode) . " mã hàng";
echo $dupes > 0 ? " (bỏ {$dupes} dòng trùng mã)" : '';
echo ".\nTrong database hiện có {$stored} mã hàng KiotViet.\n";

// Mã đã ghép nhưng không còn tồn tại bên KiotViet — dấu hiệu gõ sai hoặc hàng đã xoá.
$bad = $pdo->query(
    'SELECT cm.ma_live, cm.mon, cm.kiotviet_code
     FROM code_map cm
     LEFT JOIN kiotviet_products kp ON kp.code = cm.kiotviet_code
     WHERE cm.kiotviet_code IS NOT NULL AND cm.kiotviet_code <> \'\' AND kp.id IS NULL'
)->fetchAll();
if ($bad) {
    echo "\nCảnh báo — " . count($bad) . " mã đã ghép nhưng KiotViet không có:\n";
    foreach ($bad as $b) {
        echo "  {$b['ma_live']} {$b['mon']} → {$b['kiotviet_code']}\n";
    }
}
