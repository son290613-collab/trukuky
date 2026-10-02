# Tổng hợp bình luận live → phiếu chốt đơn

Biến bình luận một buổi live thành phiếu chốt đơn, bảng cầu theo mã × size và danh
sách khách cần nhắn lại. Dùng cho Ban 3 (Live) và Ban 1 (Dữ liệu) trong quy trình
`trukuky-daily-ops`, trước bước đối soát của `tools/b12_doisoat`.

```bash
python parse_comments.py <binh_luan.csv> <thu_muc_ra> ["Tên page của shop"]
python parse_comments.py --selftest        # 13 phép kiểm, không cần dữ liệu thật
```

Tham số thứ ba là tên hiển thị của shop trong bình luận (ví dụ `Trukuky`). Có tham số
này thì mọi bình luận của shop được đánh dấu **niêm yết** và trở thành mốc mã — phần
quan trọng nhất của công cụ, xem mục "Mã suy luận".

## Vì sao cần bước này

Đơn live được chốt ngay trong bình luận, nhưng bình luận là thứ **mất nhanh nhất** trong
cả hệ thống: video live 24/9 và 30/9 đã không còn xem được trước khi kịp xử lý
(ghi nhận trong lần chạy 02/10/2026). Khi video mất mà sổ chốt đơn chưa có, buổi live đó
chỉ còn dấu vết trong KiotViet — không còn biết khách nào hỏi mà chưa được trả lời, mã nào
cầu cao hơn tồn, size nào khách gọi mà shop không có.

Vì vậy: **lấy bình luận ngay trong hoặc ngay sau buổi live**, trước khi video có thể bị gỡ.

## Cách lấy bình luận (5 phút, không cần công cụ gì thêm)

1. Mở lại video live trên page, mở phần bình luận, cuộn tới hết (Facebook tải dần).
2. Bôi đen toàn bộ khung bình luận → sao chép.
3. Dán vào một Google Sheet mới tên `binh luan live dd-mm`, rồi tách thành 6 cột theo
   `fixtures/mau_so_binh_luan.csv`:

   | Cột | Nội dung | Bắt buộc |
   |---|---|---|
   | Phút trong video | `mm:ss` hoặc `h:mm:ss` | có — không có thì mất phần suy luận mã |
   | Người bình luận | tên Facebook | có |
   | Trang cá nhân | link | không (giúp nhắn lại khách) |
   | Nội dung bình luận | nguyên văn, không sửa | có |
   | Có ghi mã? | để trống, máy tự điền | không |
   | Là shop niêm yết? | `x` ở các bình luận shop niêm yết mã | nên có |
4. Tải về dạng CSV, đưa vào thư mục Drive `1. Sổ live`.

Buổi live 09/09 đã làm đúng cách này (sổ `binh-luan-live-0909-day-du`, 1.208 bình luận) —
đó là bằng chứng cách này chạy được, không cần phần mềm lấy bình luận tự động.

## File ra

| File | Dùng để làm gì |
|---|---|
| `binh_luan_phan_loai.csv` | mỗi bình luận một dòng kèm nhãn, mã, size, số lượng máy đọc được |
| `chot_don_theo_khach.csv` | **phiếu chốt đơn**: mỗi khách × mã × món × size một dòng, có cột trống để nhân viên điền size chốt, mã KiotViet và kết quả |
| `nhu_cau_theo_ma_size.csv` | cầu theo mã × size: số chiếc đặt, số khách, số lượt hỏi còn / hỏi giá / hỏi size |
| `can_hoi_lai.csv` | khách hỏi giá, hỏi còn, hỏi size mà **không thấy đặt** — danh sách nhắn lại, có link trang cá nhân |
| `tom_tat.json` | số tổng hợp cho báo cáo Chủ tịch |

Nhãn bình luận: `niem-yet` · `dat` · `dat-thieu-ma` · `dat-thieu-size` · `hoi-gia` ·
`hoi-con` · `hoi-size` · `doi` · `huy` · `ship` · `ib` · `ngoai-pham-vi` (thuốc nhỏ mắt,
theo Luật cứng 12 của master prompt) · `khac`.

## Mã suy luận: đo được, nên đừng tin quá

Rất nhiều khách chỉ gõ size vì mã đang hiện trên màn hình (`sz 32`, `cả set 25kg`).
Công cụ gán mã **được shop niêm yết gần nhất trước đó** cho các dòng này và ghi rõ độ tin:

| Độ tin | Nghĩa |
|---|---|
| `chac` | bình luận ghi rõ cả mã và size |
| `thieu-size` | ghi rõ mã, không đọc được size |
| `suy-luan` | size rõ, mã lấy theo mốc niêm yết cách ≤ 120 giây |
| `suy-luan-yeu` | như trên nhưng cách > 120 giây — rất dễ sai |
| `khong-ro-ma` | không đọc được mã nào |

Mỗi lần chạy, công cụ **tự đo** quy tắc này ngay trên buổi live đang xử lý: lấy các bình
luận khách **có** ghi rõ mã, giả vờ không biết, rồi so mã suy luận với mã khách ghi.
Kết quả ghi ở `tom_tat.json` → `suy_luan_do_chinh_xac_phan_tram`.

Đo trên live 09/09: **84,3%** (trên 83 dòng kiểm được, cửa sổ 120 giây). Các cách khác đều
tệ hơn: lấy mốc từ mọi bình luận có mã còn 76%, bỏ giới hạn thời gian còn 71%.

Nghĩa là khoảng **1/6 dòng `suy-luan` gán sai mã**. Đừng đưa thẳng vào đơn: cột
"Size chốt" và "Kết quả" trong phiếu là để người xác nhận. Cách chữa gốc nằm ở buổi live,
không nằm ở công cụ: shop niêm yết mã rõ ràng từng lượt và nhắc khách luôn gõ mã trước size.

## Cân nặng, chiều cao: không tự quy đổi

Khách hay ghi `19kg`, `1m32`, `130`. Bảng quy đổi của shop **chưa được xác nhận**
(ISS-0007), nên công cụ giữ nguyên cách khách gọi và bật cờ `Cần quy đổi size`
(live 09/09: 112 dòng). Khi shop chốt bảng quy đổi, thêm một bước quy đổi ở đây —
không đoán trước.

## Quyền riêng tư

File ra **có tên khách và link trang cá nhân**. Không commit (xem `.gitignore`), không
dán vào trang web, không đưa lên artifact công khai. Dùng xong thì để trong thư mục
riêng của shop.
