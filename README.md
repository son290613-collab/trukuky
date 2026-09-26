# Trukuky — Quản lý shop quần áo

Ứng dụng web quản lý cửa hàng quần áo/boutique nhỏ: tồn kho, đơn hàng, phối đồ (outfit), nhân viên, lịch làm việc, checklist công việc và báo cáo doanh thu theo thời gian.

Viết bằng PHP thuần (không framework, không build step) + MySQL, giao diện tiếng Việt, tiền tệ VNĐ.

## Tính năng

- **Tổng quan (Dashboard)** — số đơn/doanh thu hôm nay, cảnh báo sắp hết hàng, việc cần làm hôm nay, đơn hàng gần đây.
- **Đơn hàng** — tạo đơn, trừ kho tự động, đổi trạng thái (đang xử lý / hoàn thành / đã huỷ) với rollback tồn kho.
- **Tồn kho** — quản lý sản phẩm (tên, SKU, size, màu, giá, tồn kho, ngưỡng cảnh báo, ảnh sản phẩm).
- **Phối đồ** — tạo bộ phối đồ (outfit) từ các sản phẩm trong kho, kèm ảnh minh hoạ.
- **Nhân viên & Lịch** — quản lý tài khoản nhân viên (chỉ quản lý), lịch làm việc 7 ngày tới, checklist công việc hàng ngày (kể cả mẫu Opening Checklist lặp lại mỗi ngày).
- **Sổ mã hàng (`codemap.php`)** — nối mã live (M01, M02...) với mã hàng trên KiotViet. Xem [Sổ mã hàng](#sổ-mã-hàng) bên dưới.
- **Báo cáo** — số đơn và doanh thu theo ngày trong một khoảng thời gian tuỳ chọn.
- **Trang khách hàng (`shop.php`)** — trang công khai, không cần đăng nhập, hiển thị danh sách sản phẩm và bộ phối đồ kèm nút gọi điện/Zalo/Facebook để khách liên hệ tư vấn. Đây là link nên chia sẻ cho khách hàng (ví dụ dán vào bio Facebook/Instagram), khác với link gốc của app (chỉ dành cho nhân viên đăng nhập).

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

## Sổ mã hàng

Sổ live gọi hàng theo mã buổi live (`M01`, `M02`...), KiotViet gọi theo mã hàng của nó. Không có bảng nối thì không tính được "mã này bán được bao nhiêu phần trăm tồn", và **hai mã live trỏ về cùng một mã KiotViet sẽ bán vượt kho mà không ai thấy** — buổi 17/09 đã dính đúng lỗi này với 33 chiếc chân váy (M06 và M14 cùng là `T6K01SD019908`).

`codemap.php` là màn hình để ghép mã, có cảnh báo tự động cho đúng cái bẫy đó.

### Cài đặt

```bash
mysql -u user -p dbname < sql/code_map.sql
```

### Nạp sổ tồn của một buổi live

CSV chép từ các tab mã của sổ live, cần các cột `ma_m, mon, cot_so, size_1, size_2, gia, sl_a, sl_b, ghi_chu_so`:

```bash
php tools/import_so_live.php tools/b12_doisoat/so_ton_live20260917.csv
# ngày live lấy từ 8 chữ số trong tên file, hoặc truyền --date=2026-09-17
```

Chạy lại nhiều lần được: số tồn được ghi đè, còn **mã bạn đã ghép không bị xoá**.

### Nạp danh mục hàng của KiotViet

Hai cách, dùng cách nào cũng được:

```bash
# 1) Gọi thẳng API — cần bật kết nối trong KiotViet
export KIOTVIET_CLIENT_ID=...
export KIOTVIET_CLIENT_SECRET=...
export KIOTVIET_RETAILER=...
php tools/sync_kiotviet.php --dry-run   # xem đọc được gì trước
php tools/sync_kiotviet.php

# 2) Nạp từ file KiotViet xuất ra (Hàng hoá → Xuất file) — không cần mạng
php tools/sync_kiotviet.php --csv=danh_muc_hang_hoa.csv
```

Script tự dò tên cột tiếng Việt (`Mã hàng`, `Tên hàng`, `Nhóm hàng`, `Giá bán`, `Tồn kho`) và in ra nó hiểu cột nào là cột nào trước khi ghi.

> **Chưa kiểm chứng:** phần gọi API chưa chạy thử với KiotViet thật. Lần đầu nên chạy kèm `--dry-run`.

**Không đồng bộ KiotViet vẫn ghép mã được** — cứ gõ tay mã vào. Khi nào đồng bộ xong, màn hình sẽ tự đối chiếu và báo mã nào gõ sai.

### Ghép mã

Mở `codemap.php`. Mỗi (mã live, món) một dòng. Gõ hoặc chọn mã KiotViet, đặt tên gọi khách, hoặc bấm **Không có** cho món KiotViet không quản lý (hàng ghi sổ giấy, hoặc món sổ live gọi nhầm tên). Sửa tới đâu lưu tới đó.

Màn hình cảnh báo hai việc:

- **Mã KiotViet bị hai món dùng chung** — kho chung, phải cộng tồn khi chốt đơn.
- **Mã không có trong danh mục KiotViet** — gõ nhầm hoặc hàng đã bị xoá (chỉ kiểm được sau khi đồng bộ).

Trạng thái do máy chủ tự suy ra từ dữ liệu, không nhận thẳng từ giao diện, nên không thể có dòng "đã ghép" mà bỏ trống mã.

Nút **Tải về CSV** xuất toàn bộ sổ mã hàng để đối chiếu hoặc gửi cho người khác.

### Ghi chú: các trang bảng khác đang bị phóng nhỏ trên điện thoại

`.content` là flex item nên mặc định `min-width: auto`, không co được dưới bề rộng nội dung. Hậu quả: trên máy rộng 390px, trình duyệt phải dàn trang rộng hơn rồi thu nhỏ lại. Đo thực tế:

| Trang | Bề rộng dàn trang trên máy 390px |
|---|---|
| `orders.php` | 654px |
| `inventory.php` | 651px |
| `team.php` | 544px |
| `reports.php` | 441px |
| `dashboard.php` | 396px |
| `outfits.php` | 390px (đúng) |
| `codemap.php` | 390px (đã sửa) |

`codemap.php` được sửa riêng bằng `.content-codemap { min-width: 0 }` cộng với khung cuộn ngang quanh bảng. Sửa cho các trang còn lại cần bọc từng bảng trong khung cuộn tương tự — chưa làm vì nằm ngoài phạm vi của sổ mã hàng.

## Triển khai lên Hostinger

Xem hướng dẫn chi tiết tại [DEPLOY.md](DEPLOY.md).
