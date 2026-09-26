# Công cụ chốt đơn livestream

Biến bình luận của một buổi live Facebook (copy từ máy tính) thành file Excel chốt đơn: mỗi khách một dòng, kèm tin nhắn soạn sẵn, danh sách ca tranh chấp, danh sách cần đếm lại kho và các cột đo tốc độ phản hồi.

Công cụ chạy ngoài app Trukuky (Python), không đụng vào database. Thư mục `tools/` bị chặn truy cập từ web bằng `.htaccess`.

## Chạy

```bash
pip install openpyxl
python3 tools/live/live_orders.py dau_vao.txt ket_qua.xlsx
```

## File đầu vào

Mỗi phần bắt đầu bằng một dòng tiêu đề trong ngoặc vuông:

```
[SẢN PHẨM]
A1 | Bộ cotton khủng long xanh ("bộ khủng long") | 159k | 73:2, 80:3, 90:1
A2 | Váy hoa nhí vàng ("váy vàng") | 189k | 90:2, 100:2

[CÀI ĐẶT]
ten_trang = Trukuky
ship = 30k
freeship_tu = 500k
thanh_toan = COD hoặc CK
tong_binh_luan = 150
gio_het_live = 22:30

[MỚI NHẤT]
(dán nguyên bản copy bình luận với bộ lọc "Mới nhất")

[TẤT CẢ]
(dán nguyên bản copy bình luận với bộ lọc "Tất cả bình luận")
```

Các phần chỉ dùng ở vòng 2, sau khi nhân viên kiểm tra:

```
[GIỜ CHÍNH XÁC]      mã bình luận | giờ khi rê chuột vào chữ giờ dưới bình luận
C012 | 20:15
L003 | 20:14

[ĐẾM LẠI]            mã | size | số đếm thực tế
A1 | 90 | 1

[SỬA]                sửa kết quả đọc bình luận
C045 | A3 80 x1 ; A5 100
C046 | bỏ qua
```

`qua_nua_dem = co` trong `[CÀI ĐẶT]` nếu live kéo qua 0 giờ.

## Cách công cụ xử lý các điểm dễ sai

| Điểm dễ sai | Cách xử lý |
|---|---|
| Thứ tự ai chốt trước | Lấy thứ tự từ bản "Mới nhất". Khi số chốt vượt tồn, liệt kê ca tranh chấp và chỉ yêu cầu xem giờ chính xác cho các ca cần. Bình luận đã sửa được đánh dấu. |
| Bình luận bị Facebook lọc | Đối chiếu bản "Mới nhất" với "Tất cả bình luận": bình luận chỉ có ở "Tất cả" mang mã `L…`, thứ tự chưa biết, khách liên quan bị khóa "Chờ xác minh" cho đến khi có giờ chính xác. So tổng đếm được với tổng hiển thị dưới video. |
| Chỉ được gửi 1 tin/bình luận | Mỗi khách một tin nhắn duy nhất, gộp mọi món, kết thúc bằng câu hỏi để khách trả lời. |
| Số tồn sai | Danh sách "Cần đếm lại" chỉ gồm mẫu có số chốt ≥ tồn hoặc tồn ≤ 2. Không gợi ý size nhỏ hơn cho khách hết hàng. |
| Tốc độ phản hồi | Cột "Giờ gửi tin", "Phút chờ" (tự tính), "Kết quả"; trang "Kiểm tra đầy đủ" tính phút chờ trung vị và tỷ lệ xác nhận. |

## Dữ liệu khách hàng

File đầu vào và file Excel chứa tên, SĐT của khách. `.gitignore` đã chặn `*.txt`, `*.xlsx`, `*.csv` trong thư mục này. Không commit dữ liệu khách lên GitHub.

## Giới hạn đã biết

- Bộ đọc bình luận dựa trên định dạng copy của Facebook bản máy tính; cần kiểm tra lại khi Facebook đổi giao diện.
- Hai khách trùng tên Facebook bị gộp làm một (có cảnh báo nếu hai SĐT khác nhau).
- Phản hồi của khách nằm trong luồng trả lời được xếp theo vị trí bình luận gốc, không theo giờ thật.
- Mẫu "suy ra từ bình luận xung quanh" luôn cần khách xác nhận lại.
