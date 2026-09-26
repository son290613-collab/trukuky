# B12 — Đối soát buổi live

Dựng file `TRUKUKY_DOISOATLIVE_LIVE<YYYYMMDD>_<ngày lập>_v<N>.xlsx` từ 3 nguồn:

| Nguồn | Lấy ở đâu | Có trong kho mã? |
|---|---|---|
| Phiếu bình luận (`custs`, `lines`, `matrix`, `stats`) | khối JSON trong trang "Chốt đơn live" | Không — có tên khách |
| Tab "ĐƠN OK" của sổ live | Google Sheet sổ live → xuất CSV | Không — có tên khách |
| Tồn + giá từng size | chép tay từ các tab mã của sổ live → `so_ton_live<ngày>.csv` | Có — không có tên khách |

```bash
python build_doisoat.py phieu.json don_ok.csv so_ton_live20260917.csv TRUKUKY_DOISOATLIVE_LIVE20260917_20260926_v2.xlsx
python <xlsx-skill>/scripts/recalc.py TRUKUKY_DOISOATLIVE_LIVE20260917_20260926_v2.xlsx 300
```

File ra có 13 sheet:

| Nhóm | Sheet |
|---|---|
| Đọc trước | `DOC-TRUOC` · `TOM-TAT` |
| Việc cần làm | `KHACH` (mỗi khách 1 dòng, cột nhập kết quả) · `TIN-NHAN` (bản nháp B12 §8.2, chờ duyệt) · `DANH-SACH-CHO` (B12 §8.4) |
| Phân tích | `TON-SIZE` · `MAU-MA` (nhập thêm / giữ / dừng) · `BAO-CAO-LIVE` (B12 §8.3) · `LOI-BAN-CU` |
| Dữ liệu gốc | `GOC-BINH-LUAN` · `GOC-SO-TON` · `GOC-DON-OK` · `QUY-DOI-MA` |

Mọi số tổng hợp là công thức; sửa `GOC-SO-TON`, `QUY-DOI-MA` hoặc tham số ô vàng ở `TOM-TAT` thì cả file tính lại.

Quy tắc đối soát:

- Mỗi dòng đặt được gán vào một ô size của sổ (`Mã|Món|Size`). Cột sổ gộp hai size
  (vd M01 "110" = 1-2 và 2-4) có hai "size khách gọi".
- Cộng dồn số lượng theo `STT dòng` (thứ tự bình luận, duy nhất cho từng dòng — sắp xếp lại sheet không làm đổi kết quả);
  cộng dồn ≤ tồn → `TRONG TỒN`, > tồn → `VƯỢT TỒN`. Size bắt đầu bằng `?` → `THIẾU SIZE`.
- Khách "có trong ĐƠN OK" = tên Facebook khớp đúng chữ với tên đã làm sạch ở tab ĐƠN OK.

Không commit file xlsx hay dữ liệu nguồn có tên khách (nội quy 00 §8.1, B10 §6).
