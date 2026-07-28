# Triển khai Trukuky lên Hostinger

App là PHP thuần, mọi đường dẫn trong code (link menu, `assets/css/...`, `assets/js/...`, `api/...`) đều là **relative path**, nên deploy vào `public_html` gốc hay vào một thư mục con (ví dụ `public_html/trukuky`) đều chạy được bình thường.

Trước khi bắt đầu, trong hPanel: **Advanced → PHP Configuration**, đặt PHP version **8.1 trở lên** (bắt buộc, code dùng tính năng `never` return type chỉ có từ PHP 8.1).

Chọn 1 trong 2 cách bên dưới.

## Cách 1 — Git Auto Deploy (khuyến nghị)

1. Đẩy code lên GitHub trước (xem hướng dẫn ở cuối README hoặc phần "Publish lên GitHub" bên dưới).
2. Trong hPanel: **Advanced → Git**.
3. Chọn "Create a new repository", dán URL repo GitHub (public thì dán thẳng; private thì Hostinger sẽ yêu cầu deploy key/token — hPanel có hướng dẫn thêm deploy key vào GitHub repo Settings → Deploy keys).
4. Chọn nhánh (branch) `main` và thư mục đích (thường là `public_html` hoặc một subfolder).
5. Bấm **Deploy** — Hostinger sẽ `git clone`/`pull` toàn bộ code vào thư mục đó. Mỗi lần bạn push code mới lên GitHub, quay lại hPanel bấm **Deploy** (hoặc bật auto-deploy nếu gói hosting hỗ trợ webhook).
6. Vì `config/config.php` nằm trong `.gitignore`, nó **sẽ không có sẵn** sau khi deploy — làm tiếp bước 7-9 của Cách 2 (tạo DB, import schema, tạo `config.php`, chạy `install.php`).

## Cách 2 — Upload thủ công (File Manager / FTP)

1. Trong hPanel: **Databases → MySQL Databases**, tạo database mới (tên dạng `u123456789_trukuky`) và một user MySQL gắn với DB đó, ghi lại host/tên DB/user/mật khẩu.
2. Mở **phpMyAdmin** từ hPanel, chọn DB vừa tạo, vào tab **Import**, chọn file `sql/schema.sql` trong repo và Import.
3. Nén toàn bộ thư mục project (trừ `config/config.php` nếu có, trừ `.git/`) thành file `.zip`.
4. Trong hPanel: **Files → File Manager**, vào `public_html` (hoặc subfolder bạn muốn dùng), Upload file zip rồi Extract. (Hoặc dùng FTP/SFTP với thông tin trong hPanel → Files → FTP Accounts.)
5. Trong File Manager, vào thư mục `config/`, đổi tên (hoặc tạo mới) `config.sample.php` → `config.php`, mở bằng trình sửa file tích hợp và điền đúng `db_host`, `db_name`, `db_user`, `db_pass` (dùng thông tin ở bước 1), cùng `app_url` (domain thật của bạn).
6. Đảm bảo quyền ghi cho `assets/uploads/` (dùng cho upload ảnh sản phẩm/outfit): chuột phải → Permissions → `755`. Nếu upload ảnh báo lỗi, thử `775`.
7. Mở `https://<domain-của-bạn>/install.php` trên trình duyệt, tạo tài khoản quản lý đầu tiên.
8. **Xoá `install.php`** khỏi File Manager ngay sau khi tạo tài khoản thành công.
9. Đăng nhập tại `https://<domain-của-bạn>/login.php`.

## Sau khi deploy

- Nếu trang trắng hoặc lỗi 500: kiểm tra PHP version (bước đầu tiên ở trên) và bật hiển thị lỗi tạm thời qua hPanel → PHP Configuration → `display_errors` (nhớ tắt lại sau khi debug xong).
- Nếu upload ảnh sản phẩm/outfit báo lỗi "Không thể lưu ảnh": kiểm tra quyền thư mục `assets/uploads/` (phải ghi được, thường `755`).
- `config/config.php`, `install.php` (sau khi dùng), và mọi ảnh trong `assets/uploads/` không nằm trong git — chúng chỉ tồn tại trên server, không bị mất khi bạn deploy lại qua Git Auto Deploy (miễn là không xoá thư mục đích trước khi pull).
