<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/auth.php';
require_once __DIR__ . '/../includes/helpers.php';

require_login();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_out(['error' => 'Method not allowed'], 405);
}
check_csrf();

if (empty($_FILES['image']) || $_FILES['image']['error'] !== UPLOAD_ERR_OK) {
    json_out(['error' => 'Vui lòng chọn một ảnh hợp lệ.'], 422);
}

$file = $_FILES['image'];
if ($file['size'] > 2 * 1024 * 1024) {
    json_out(['error' => 'Ảnh không được vượt quá 2MB.'], 422);
}

$info = @getimagesize($file['tmp_name']);
$allowed = [IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp'];
if (!$info || !isset($allowed[$info[2]])) {
    json_out(['error' => 'Tệp không phải là ảnh JPG/PNG/WEBP hợp lệ.'], 422);
}
$ext = $allowed[$info[2]];

$dir = __DIR__ . '/../assets/uploads/';
if (!is_dir($dir)) {
    mkdir($dir, 0755, true);
}

$filename = bin2hex(random_bytes(16)) . '.' . $ext;
if (!move_uploaded_file($file['tmp_name'], $dir . $filename)) {
    json_out(['error' => 'Không thể lưu ảnh.'], 500);
}

json_out(['url' => 'assets/uploads/' . $filename], 201);
