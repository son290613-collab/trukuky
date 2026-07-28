# Trukuky — Quản lý shop quần áo

Ứng dụng web quản lý cửa hàng quần áo/boutique nhỏ: tồn kho, đơn hàng, phối đồ (outfit), nhân viên, lịch làm việc, checklist công việc và báo cáo doanh thu theo thời gian.

Viết bằng PHP thuần (không framework, không build step) + MySQL, giao diện tiếng Việt, tiền tệ VNĐ.

## Tính năng

- **Tổng quan (Dashboard)** — số đơn/doanh thu hôm nay, cảnh báo sắp hết hàng, việc cần làm hôm nay, đơn hàng gần đây.
- **Đơn hàng** — tạo đơn, trừ kho tự động, đổi trạng thái (đang xử lý / hoàn thành / đã huỷ) với rollback tồn kho.
- **Tồn kho** — quản lý sản phẩm (tên, SKU, size, màu, giá, tồn kho, ngưỡng cảnh báo, ảnh sản phẩm).
- **Phối đồ** — tạo bộ phối đồ (outfit) từ các sản phẩm trong kho, kèm ảnh minh hoạ.
- **Nhân viên & Lịch** — quản lý tài khoản nhân viên (chỉ quản lý), lịch làm việc 7 ngày tới, checklist công việc hàng ngày (kể cả mẫu Opening Checklist lặp lại mỗi ngày).
- **Báo cáo** — số đơn và doanh thu theo ngày trong một khoảng thời gian tuỳ chọn.

## Yêu cầu hệ thống

- PHP **8.1+** (code dùng return type `never`, bắt buộc PHP 8.1 trở lên)
- MySQL 5.7+ hoặc MariaDB tương đương, extension `pdo_mysql`
- Apache/LiteSpeed hỗ trợ `.htaccess` (dùng để chặn truy cập trực tiếp vào `config/`, `includes/` và ngăn thực thi PHP trong `assets/uploads/`)

## Cài đặt local

```bash
git clone <repo-url> trukuky
cd trukuky
cp config/config.sample.php config/config.php
```

Mở `config/config.php` và điền thông tin database local (`db_host`, `db_name`, `db_user`, `db_pass`).

```bash
mysql -u root -e "CREATE DATABASE trukuky CHARACTER SET utf8mb4"
mysql -u root trukuky < sql/schema.sql
php -S localhost:8000
```

Mở `http://localhost:8000/install.php` để tạo tài khoản quản lý đầu tiên, sau đó đăng nhập tại `login.php`. **Xoá `install.php`** khỏi server thật sau khi đã tạo xong tài khoản đầu tiên (script tự chặn nếu đã có user, nhưng xoá hẳn là an toàn nhất).

## Cấu trúc thư mục

```
api/            Các endpoint JSON (CRUD, auth qua session + CSRF token)
assets/         css/js tĩnh + assets/uploads/ (ảnh sản phẩm/outfit do người dùng tải lên, không commit)
config/         config.sample.php (mẫu) — copy thành config.php (gitignored, chứa thông tin DB thật)
includes/       Header/footer dùng chung, helper auth/db/format
sql/schema.sql  Toàn bộ schema database
*.php           Các trang: dashboard, inventory, orders, outfits, reports, team, login...
```

## Triển khai lên Hostinger

Xem hướng dẫn chi tiết tại [DEPLOY.md](DEPLOY.md).
