-- Sổ mã hàng: nối mã live (M01, M02...) với mã hàng trên KiotViet.
-- Import sau sql/schema.sql:  mysql -u user -p dbname < sql/code_map.sql
--
-- Vì sao cần bảng này: sổ live gọi hàng theo mã buổi live, KiotViet gọi theo mã
-- hàng của nó. Không có bảng nối thì không tính được "mã này bán bao nhiêu phần
-- trăm tồn", và hai mã live trỏ về cùng một mã KiotViet sẽ bán vượt kho mà
-- không ai thấy.

-- Tồn đầu buổi của một buổi live, gộp theo (mã live, món) — nguồn là các tab mã
-- của sổ live, chép ra CSV rồi nạp bằng tools/import_so_live.php
CREATE TABLE IF NOT EXISTS live_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  live_date DATE NOT NULL,
  ma_live VARCHAR(20) NOT NULL,
  mon VARCHAR(120) NOT NULL,
  sizes VARCHAR(255) DEFAULT NULL,
  size_count INT NOT NULL DEFAULT 0,
  ton INT NOT NULL DEFAULT 0,
  gia_min DECIMAL(12,0) NOT NULL DEFAULT 0,
  gia_max DECIMAL(12,0) NOT NULL DEFAULT 0,
  ghi_chu TEXT,
  UNIQUE KEY uniq_live_item (live_date, ma_live, mon)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bản sao danh sách hàng trên KiotViet, chỉ để tra khi ghép mã.
-- Không sửa ở đây — nguồn chân lý vẫn là KiotViet.
CREATE TABLE IF NOT EXISTS kiotviet_products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(60) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) DEFAULT NULL,
  category VARCHAR(120) DEFAULT NULL,
  retail_price DECIMAL(12,0) NOT NULL DEFAULT 0,
  on_hand INT DEFAULT NULL,
  synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sổ mã hàng. Một dòng cho mỗi (mã live, món) từng xuất hiện trong sổ live.
-- status:
--   chua_ghep = chưa ai xác nhận mã KiotViet tương ứng
--   da_ghep   = đã xác nhận
--   khong_co  = món này không có trên KiotViet (hàng ghi sổ giấy, hoặc món
--               không tồn tại — sổ live gọi nhầm tên)
CREATE TABLE IF NOT EXISTS code_map (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ma_live VARCHAR(20) NOT NULL,
  mon VARCHAR(120) NOT NULL,
  kiotviet_code VARCHAR(60) DEFAULT NULL,
  ten_mon_dung VARCHAR(255) DEFAULT NULL,
  status ENUM('chua_ghep','da_ghep','khong_co') NOT NULL DEFAULT 'chua_ghep',
  note VARCHAR(500) DEFAULT NULL,
  updated_by INT DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_code_map (ma_live, mon),
  KEY idx_code_map_kiotviet (kiotviet_code),
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
