<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/db.php';
require_once __DIR__ . '/includes/helpers.php';

$pdo = db();

$products = $pdo->query(
    'SELECT id, name, category, size, color, price, quantity, image_url FROM products ORDER BY name ASC'
)->fetchAll();

$outfits = $pdo->query('SELECT id, name, description, image_url FROM outfits ORDER BY created_at DESC')->fetchAll();
$itemStmt = $pdo->prepare(
    'SELECT p.name FROM outfit_items oi JOIN products p ON p.id = oi.product_id WHERE oi.outfit_id = ?'
);
foreach ($outfits as &$o) {
    $itemStmt->execute([$o['id']]);
    $o['item_names'] = array_column($itemStmt->fetchAll(), 'name');
}
unset($o);

$phoneDisplay = '0225 2666 669';
$phoneTel = 'tel:02252666669';
$zaloUrl = 'https://zalo.me/842252666669';
$facebookUrl = 'https://www.facebook.com/trukuky?locale=vi_VN';
?><!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trukuky · Bộ sưu tập &amp; sản phẩm</title>
<meta name="description" content="Trukuky — xem sản phẩm và các bộ phối đồ mới nhất, liên hệ để được tư vấn.">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="public-page">
  <header class="public-header">
    <div class="brand">
      <span class="brand-mark">TK</span>
      <div>
        <div class="brand-name">Trukuky</div>
        <div class="brand-sub">Thời trang quần áo</div>
      </div>
    </div>
    <div class="contact-bar">
      <a class="btn btn-primary" href="<?= e($phoneTel) ?>">📞 Gọi ngay</a>
      <a class="btn" href="<?= e($zaloUrl) ?>" target="_blank" rel="noopener">Chat Zalo</a>
      <a class="btn" href="<?= e($facebookUrl) ?>" target="_blank" rel="noopener">Facebook</a>
    </div>
  </header>

  <section class="public-hero">
    <h1>Sản phẩm &amp; bộ sưu tập mới nhất</h1>
    <p>Xem qua các mẫu quần áo và gợi ý phối đồ của Trukuky — liên hệ ngay để được tư vấn size, màu và đặt hàng.</p>
  </section>

  <main class="content" style="max-width: 1100px; margin: 0 auto; padding: 0 20px 60px;">
    <div class="topbar">
      <div>
        <h2 class="page-title">Sản phẩm</h2>
        <p class="page-sub">Tất cả mẫu hiện có tại shop.</p>
      </div>
    </div>

    <?php if (!$products): ?>
      <div class="empty-state">Shop đang cập nhật sản phẩm, quay lại sau nhé.</div>
    <?php else: ?>
      <div class="outfit-grid">
        <?php foreach ($products as $p): ?>
          <?php $inStock = (int) $p['quantity'] > 0; ?>
          <div class="outfit-card">
            <?php if ($p['image_url']): ?>
              <img class="thumb outfit-thumb" src="<?= e($p['image_url']) ?>">
            <?php endif; ?>
            <h4><?= e($p['name']) ?></h4>
            <p class="check-meta">
              <?= e($p['category'] ?: 'Chưa phân loại') ?>
              <?= $p['size'] ? ' · ' . e($p['size']) : '' ?>
              <?= $p['color'] ? ' · ' . e($p['color']) : '' ?>
            </p>
            <p style="font-weight:700; margin: 8px 0;"><?= format_vnd($p['price']) ?></p>
            <span class="badge <?= $inStock ? 'badge-good' : 'badge-bad' ?>"><?= $inStock ? 'Còn hàng' : 'Hết hàng' ?></span>
          </div>
        <?php endforeach; ?>
      </div>
    <?php endif; ?>

    <div class="topbar" style="margin-top: 36px;">
      <div>
        <h2 class="page-title">Gợi ý phối đồ</h2>
        <p class="page-sub">Những bộ phối đồ được tư vấn viên của shop gợi ý sẵn.</p>
      </div>
    </div>

    <?php if (!$outfits): ?>
      <div class="empty-state">Chưa có bộ phối đồ nào được đăng.</div>
    <?php else: ?>
      <div class="outfit-grid">
        <?php foreach ($outfits as $o): ?>
          <div class="outfit-card">
            <?php if ($o['image_url']): ?>
              <img class="thumb outfit-thumb" src="<?= e($o['image_url']) ?>">
            <?php endif; ?>
            <h4><?= e($o['name']) ?></h4>
            <?php if ($o['description']): ?><p class="check-meta"><?= e($o['description']) ?></p><?php endif; ?>
            <ul class="outfit-items">
              <?php foreach ($o['item_names'] as $name): ?>
                <li>• <?= e($name) ?></li>
              <?php endforeach; ?>
            </ul>
          </div>
        <?php endforeach; ?>
      </div>
    <?php endif; ?>
  </main>

  <footer class="public-footer">
    <p>Trukuky — Thời trang quần áo</p>
    <p>📞 <a href="<?= e($phoneTel) ?>"><?= e($phoneDisplay) ?></a> · <a href="<?= e($zaloUrl) ?>" target="_blank" rel="noopener">Zalo</a> · <a href="<?= e($facebookUrl) ?>" target="_blank" rel="noopener">Facebook</a></p>
  </footer>
</div>
</body>
</html>
