# Kết nối KiotViet · quyền sổ · ghép mã live 17/9

Cập nhật 26/09/2026. Phiên trước để lại ba việc chờ; phiên này làm được hai, việc thứ ba vẫn chờ chủ shop.

## 1. Bảng trạng thái 5 việc

| # | Việc | Trạng thái | Đang chờ ai, chờ gì |
|---|---|---|---|
| 1 | Mạng ra ngoài | **Chặn** | Chủ shop mở Network access cho `id.kiotviet.vn`, `public.kiotapi.com`, `docs.google.com` |
| 2 | Khoá KiotViet | **Chưa có** | Chủ shop lưu `client_id` / `client_secret` / tên gian hàng vào API credentials của môi trường |
| 3 | Quyền 3 sổ | **Xong phần kiểm — cả 3 sổ còn mở công khai** | Chủ shop đổi quyền; đã soạn sẵn tin nhắn nhắc, chưa gửi |
| 4 | Bảng ghép mã | **Xong phần kiểm — 0/45 món đã làm** | Chủ shop ngồi ghép mã trên trang "Ghép mã KiotViet 17/9" |
| 5 | Đối soát live 17/9 | **Chưa chạy (đúng quy định)** | Chờ việc 2 và 4 xong |

## 2. Mạng và khoá

Thử lúc 26/09, cả ba địa chỉ đều bị chính sách mạng của môi trường từ chối ở bước CONNECT:

| Địa chỉ | Mã lỗi |
|---|---|
| `id.kiotviet.vn:443` | 403 — connect_rejected (policy denial) |
| `public.kiotapi.com:443` | 403 — connect_rejected (policy denial) |
| `docs.google.com:443` | 403 — connect_rejected (policy denial) |

Không tìm đường vòng. Kiểm tra biến môi trường: **không có** `KIOTVIET_CLIENT_ID`, `KIOTVIET_CLIENT_SECRET`, `KIOTVIET_RETAILER`, và không có biến nào chứa chữ "kiot". Nên bước lấy token và gọi thử `products?pageSize=1` chưa chạy được. Không khoá nào được in ra hay lưu lại ở đâu.

Có một đường đi vòng hợp lệ đã dùng: **connector Google Drive chạy phía máy chủ, không qua mạng của máy này**, nên vẫn đọc được quyền sổ và nội dung bảng giá. Đó là cách việc 3 và 4 hoàn thành được.

## 3. Quyền 3 sổ — cả ba còn mở công khai

Đọc quyền ngày 26/09:

| Sổ | Quyền | Chủ file |
|---|---|---|
| Live 17/9 | `anyone` · reader | dinhthuylinh18102003@gmail.com |
| LIVE 8-9/9 | `anyone` · reader | myheartisyours2598@gmail.com |
| CHECK GIÁ PAGE + LIVE TĐ 2026 | `anyone` · reader | saltvn2910@gmail.com |

Cả ba vẫn ở mức "bất kỳ ai có link đều xem được". Sổ Live 17/9 chứa tab ĐƠN OK với khoảng 204 tên khách, nên đây là chỗ rò dữ liệu khách hàng thật, không phải rủi ro lý thuyết.

Ba chủ file là ba người khác nhau — không ai trong số đó tự biết hai sổ kia cũng đang mở. Việc đổi quyền phải do từng chủ file làm.

### Nháp tin nhắn (chưa gửi)

> Chị ơi, sổ [tên sổ] đang để chế độ "bất kỳ ai có link đều xem được". Sổ có tên khách nên nhờ chị đổi giúp sang "Chỉ người được thêm" (Share → General access → Restricted), rồi thêm riêng những người cần xem. Em không tự đổi vì file là của chị.

## 4. Bảng ghép mã — 0/45 món

Collection `ghep` của trang "Ghép mã KiotViet 17/9" **rỗng: không có doc nào**. Theo quy ước "món nào chưa có doc là chưa làm" thì cả 45 món đều chưa làm.

Một lưu ý quan trọng: trang lưu lựa chọn vào máy người dùng trước, rồi mới đẩy lên kho chung. Nếu chủ shop đã bấm chọn mà lúc đó trang báo "Anh chỉ có quyền xem trang này", thì lựa chọn chỉ nằm trên máy đó và không ai đọc được. Nên "0 doc" có thể là *chưa làm*, cũng có thể là *đã làm nhưng chưa lưu lên được*. Cần chủ shop mở lại trang xem dòng trạng thái ghi gì.

### Kiểm được gì khi chưa có KiotViet

Sáu phân loại mà prompt yêu cầu (Khớp / Lệch giá / Lệch size / Không tìm thấy mã / Chưa làm / Cần hỏi) đều cần so với hàng thật trên KiotViet. Chưa nối được thì không món nào kết luận được "Khớp" hay "Lệch".

Thay vào đó bảng dưới xếp theo **mức sẵn sàng**, dựa trên bảng giá gốc đọc ngày 26/09:

- **Sẵn sàng xác nhận (9 món)** — bảng giá LIVE 17/9 ghi thẳng mã, cùng giá cùng dải size. Chỉ cần mở KiotViet đối chiếu một lần.
- **Cần hỏi (18 món)** — dính một trong các mâu thuẫn dưới, hoặc mã chỉ suy từ live 8-9/9 chứ không có trong bảng 17/9.
- **Chưa có mã trong bảng giá (18 món)** — bảng giá không ghi mã nào.

Tính theo số chiếc khách đặt (tổng 1.005 chiếc):

| Nhóm | Chiếc đặt | Tỷ lệ |
|---|---|---|
| Sẵn sàng xác nhận | 578 | 58% |
| Cần hỏi | 146 | 15% |
| Chưa có mã trong bảng giá | 281 | 28% |

| # | Mã live | Món | Mã KiotViet (bảng giá) | Kết quả kiểm | Đặt | Tồn sổ | Ghi chú |
|---|---|---|---|---|---|---|---|
| 1 | M01 | Quần da beo | `—` | Chưa có mã trong bảng giá | 150 | — | Món đặt nhiều nhất buổi (150 chiếc, khoảng 91,5 triệu) mà bảng giá chưa có mã KiotViet. |
| 2 | M11 | Tất ren trắng | `—` | Chưa có mã trong bảng giá | 36 | — | Bảng giá không ghi mã cho món này |
| 3 | M07 | Set pyjama hoa hồng | `—` | Chưa có mã trong bảng giá | 20 | 103 | Live 8-9/9 có “Set Pyjama hồng 590k / 790k” (M14) cùng giá và size, nhưng bảng giá cũng không ghi mã. |
| 4 | M02 | Áo (đi kèm quần M02) | `—` | Chưa có mã trong bảng giá | 14 | — | Khách đặt áo M02 nhưng sổ M02 chỉ có quần. Cần hỏi có áo M02 thật không. |
| 5 | M04 | Váy Tru nâu (váy hoa nâu) | `—` | Chưa có mã trong bảng giá | 14 | 183 | Bảng giá không ghi mã cho món này |
| 6 | M21 | Set áo gấu nâu + quần kẻ xanh | `—` | Chưa có mã trong bảng giá | 12 | 207 | Live 8-9/9 có “Set gấu nâu 490k / 590k” (M09) trùng giá và size, nhưng bảng giá cũng không ghi mã. Tồn sổ lớn (207). |
| 7 | M02 | Quần short vàng | `—` | Chưa có mã trong bảng giá | 10 | 16 | Bảng giá không ghi mã cho món này |
| 8 | — | Áo mèo chấm bi (không mã live) | `—` | Chưa có mã trong bảng giá | 10 | — | Bảng giá không ghi mã cho món này |
| 9 | M05 | Giày nâu | `—` | Chưa có mã trong bảng giá | 4 | 63 | Bảng giá không ghi mã cho món này |
| 10 | M16 | Chân váy set kẻ xanh | `—` | Chưa có mã trong bảng giá | 4 | — | Bảng giá không ghi mã cho món này |
| 11 | M09 | Túi xách nâu da lộn | `—` | Chưa có mã trong bảng giá | 3 | 6 | Bảng giá không ghi mã cho món này |
| 12 | M12 | Áo khoác kaki be | `—` | Chưa có mã trong bảng giá | 1 | 9 | Bảng giá không ghi mã cho món này |
| 13 | M18 | Áo khoác hồng có mũ | `—` | Chưa có mã trong bảng giá | 1 | — | Bảng giá không ghi mã cho món này |
| 14 | M25 | Váy hoa gấm đỏ | `—` | Chưa có mã trong bảng giá | 1 | 31 | Bảng giá không ghi mã cho món này |
| 15 | M28 | Chân váy kaki nâu | `—` | Chưa có mã trong bảng giá | 1 | — | Bảng giá không ghi mã cho món này |
| 16 | M11 | Áo ghi lê bông xanh | `—` | Chưa có mã trong bảng giá | 0 | — | Bảng giá không ghi mã cho món này |
| 17 | M22 | Set chip | `—` | Chưa có mã trong bảng giá | 0 | 24 | Bảng giá không ghi mã cho món này |
| 18 | M23 | Set chip | `—` | Chưa có mã trong bảng giá | 0 | — | Bảng giá không ghi mã cho món này |
| 19 | M14 | Áo xám chó tay kẻ đỏ | `T6K02TT019902; T6W02TT019905` | Cần hỏi | 31 | 68 | size S,M chồng lên T6K02TT019902 (cùng 690k) |
| 20 | M13 | Áo sơ mi ren trắng | `C6K01TT019904; C6K01TT019903` | Cần hỏi | 24 | 49 | áo sơ mi ren còn mã thứ hai C6K01TT019903 (8-9/9), cùng size cùng giá |
| 21 | M14 | Chân váy | `T6K01SD019908; T6W01SD019902` | Cần hỏi | 24 | — | dùng cho 6 chân váy: M06+M14 (17/9), M12+M13+M25+M29 (8-9/9) — cùng mô tả 4-6y→12-14y 690k, XS/S 790k; size S chồng lên T6K01SD019908 (cùng 790k) |
| 22 | M03 | Boot nâu tua rua | `T6K11FW019902` | Cần hỏi | 11 | 45 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 23 | M24 | Áo khoác nâu da lộn | `C6K02TT019902` | Cần hỏi | 10 | 47 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 24 | M06 | Chân váy nâu | `T6K01SD019908` | Cần hỏi | 9 | — | dùng cho 6 chân váy: M06+M14 (17/9), M12+M13+M25+M29 (8-9/9) — cùng mô tả 4-6y→12-14y 690k, XS/S 790k |
| 25 | M15 | Áo khoác cổ kẻ nâu | `C6K12TT019905` | Cần hỏi | 8 | 67 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 26 | M17 | Áo nâu | `C6K02TT019901` | Cần hỏi | 6 | 32 | dùng 2 giá: 520k/620k (M12 8-9/9) và 490k/590k (M04 8-9/9) |
| 27 | M17 | Quần jean xanh túi kẻ nâu | `C6K01PP019911` | Cần hỏi | 6 | — | Ứng viên độ khớp thấp, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 28 | M16 | Set kẻ xanh (áo) | `T6W01TT019909` | Cần hỏi | 4 | 19 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 29 | M20 | Quần jean xanh kèm yếm | `T6K03OS019901` | Cần hỏi | 4 | 12 | Ứng viên độ khớp thấp, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 30 | M28 | Áo nhung nâu | `C6K01TT019906; C6K02TT019901` | Cần hỏi | 4 | 48 | dùng 2 giá: 520k/620k (M12 8-9/9) và 490k/590k (M04 8-9/9) |
| 31 | M19 | Quần loe hồng | `C6K03PP019902` | Cần hỏi | 2 | 3 | dùng cho quần loe của cả M19 và M30 |
| 32 | M27 | Áo len đỏ tay bèo | `SP026129` | Cần hỏi | 1 | — | Ứng viên độ khớp thấp, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 33 | M29 | Váy công chúa ba lỗ | `C6K21DD019913; ICKDD010116084` | Cần hỏi | 1 | 55 | 2 mã ứng viên, phải nhìn hàng để chọn |
| 34 | M30 | Quần loe xám | `C6K03PP019902; ICKPP01012603` | Cần hỏi | 1 | 10 | dùng cho quần loe của cả M19 và M30 |
| 35 | M18 | Áo gió be | `T6K12TT019902` | Cần hỏi | 0 | 47 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 36 | M26 | Áo khoác jean xanh | `T6K12TT019901` | Cần hỏi | 0 | 8 | Ứng viên độ khớp trung bình, suy từ live 8-9/9 chứ không phải bảng 17/9 |
| 37 | M01 | Áo thun xám | `T6K02TT019910` | Sẵn sàng xác nhận | 145 | 160 | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 38 | M10 | Chân váy đen dài viền trắng | `C6K01SD019905` | Sẵn sàng xác nhận | 97 | — | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 39 | M10 | Áo len ghi lê trắng | `C6K09TT019901` | Sẵn sàng xác nhận | 81 | 83 | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 40 | M08 | Áo thun trắng mèo nâu | `T6K02TT019909` | Sẵn sàng xác nhận | 77 | 216 | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 41 | M10 | Áo giữ nhiệt trắng (áo trong) | `C6K07TT019905` | Sẵn sàng xác nhận | 76 | — | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 42 | M08 | Chân váy xám viền trắng | `T6K01SD019911` | Sẵn sàng xác nhận | 37 | — | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 43 | M06 | Áo ghi lê be | `T6K08TT019904` | Sẵn sàng xác nhận | 29 | 156 | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 44 | M06 | Áo sơ mi jean xanh | `T6K03TT019903` | Sẵn sàng xác nhận | 18 | — | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |
| 45 | M11 | Váy xám công sở | `T6K01DD019901` | Sẵn sàng xác nhận | 18 | 24 | Bảng giá 17/9 ghi thẳng mã, cùng giá cùng size |

## 5. Kết luận 5 mâu thuẫn của bảng giá

Đọc trực tiếp bảng "CHECK GIÁ PAGE + LIVE TĐ 2026" ngày 26/09 qua connector Drive. Mọi trích dẫn dưới là chữ trong bảng, không phải suy đoán.

### 5.1 `T6K01SD019908` dùng cho 6 chân váy — xác nhận

Sáu lần, hai buổi live, mô tả **giống hệt nhau từng chữ**: "4-6y → 12-14y giá 690k, XS/S giá 790k".

| Buổi | Mã live |
|---|---|
| LIVE 17/9 | M06 (chân váy nâu), M14 (chân váy) |
| LIVE 8-9/9 | M12, M13, M25, M29 |

> **ĐÍNH CHÍNH 27/09.** Kết luận đầu tiên của tôi ("mã dán tạm, không phải một mặt hàng") là **sai**. Sau khi đọc trực tiếp 28 tab của sổ Live 17/9, bằng chứng chỉ theo hướng ngược lại. Phần dưới là kết luận đã sửa.

**Kết luận đúng:** `T6K01SD019908` **là một mặt hàng thật** — chân váy nâu của M06 — và nó được bán lại trong nhiều lượt lên sóng khác nhau. Mã KiotViet không sai; cái sai là **sổ live đặt mã theo lượt lên sóng, không theo sản phẩm**.

**Bằng chứng quyết định:** tab M14 của sổ Live 17/9 **không có khối tồn nào cho chân váy** — nó chỉ có một khối "áo 590-690". Dòng cuối tab ghi thẳng: `MIX CÙNG CHÂN VÁY M06`. Nghĩa là 24 chiếc chân váy khách đặt dưới M14 vốn dĩ phải rút từ tồn của M06.

Sổ còn 7 dòng "MIX CÙNG" khác cùng kiểu: M02→M01, M08→M06, M13→M10, M16→M06, M19→M18, M26→M20, M28→M01.

**Hệ quả (đã tính lại):** tồn chân váy M06 là 47 chiếc trên 7 cột size. Đặt 33 chiếc (M06 9 + M14 24) → **không vượt tổng, còn 14 chiếc**. Nhưng phải kiểm từng size, vì hai mã live dùng hai dải size khác nhau. Cảnh báo "bán vượt kho" ở mức tổng là **không đúng**; rủi ro thật nằm ở từng ô size.

**Mức chắc chắn:** cao. Dựa trên ghi chú do chính người trực sổ viết, không phải suy luận từ hình thức dữ liệu.

### 5.2 `C6K02TT019901` hai giá — xác nhận

| Nơi ghi | Mô tả trong bảng giá |
|---|---|
| LIVE 8-9/9, khối M12 | Áo nâu 10-12y, 12-14y **520k**; XS, S **620k** |
| LIVE 8-9/9, khối M04 | Áo nâu 1-2y → 10-12y **490k**; XS, S **590k** |

Hai dải size **chồng nhau** ở 10-12y và ở XS/S. Nên một đơn size 10-12y dưới mã này không biết là 490k hay 520k.

Sát bên còn có `C6K02TT019902` = "áo nâu 390k / 490k" (M29, 8-9/9). Ba dòng "áo nâu", hai mã chỉ khác chữ số cuối.

**Với live 17/9:** M17 Áo nâu (sổ ghi 520k/620k) khớp đúng dòng M12; M28 Áo nhung nâu (490k/590k) khớp đúng dòng M04. Nhiều khả năng đây là **hai mặt hàng khác nhau bị gán chung một mã**, chứ không phải một dòng ghi nhầm.

### 5.3 Áo sơ mi ren hai mã — xác nhận

| Nơi ghi | Mã | Mô tả |
|---|---|---|
| LIVE 17/9, khối M13 | `C6K01TT019904` | Áo sơ mi 1-2y → 10-12y 690k; XS, S 750k |
| LIVE 8-9/9, khối M17 | `C6K01TT019903` | Áo sơ mi ren 1-2y → 10-12y 690k; XS, S 750k |

Trùng cả dải size lẫn hai mức giá, chỉ khác chữ số cuối (3 và 4).

**Kết luận:** gần như chắc chắn một trong hai là gõ nhầm — hai lô hàng khác nhau hiếm khi trùng khớp đến mức này. **Không đoán mã nào đúng**: cả hai đều có thể tồn tại trên KiotViet (một trong hai là áo khác). Phải tra.

### 5.4 Hai mã `T6W` dưới khối M14 — xác nhận, và tìm ra quy luật

Bảng giá LIVE 17/9, ngay dưới khối M14: "Áo: S ; M giá 690" → `T6W02TT019905`; "Chân váy: S ; M ; L giá 790" → `T6W01SD019902`.

**Quy luật T6W = dòng size người lớn.** Căn cứ từ bảng 8-9/9: `T6W08TT019903` "Áo ghi lê Freesize 890k", `T6W01SP019901` "Quần nhung nâu S, M, L 890k", `T6W01TT019909` "Áo 790". Mọi mã T6W chỉ mang size S/M/L/Freesize.

**Nhưng vấn đề thật không phải là chưa gắn món, mà là size chồng nhau:**

| Món M14 | Mã trẻ em | Size phủ | Mã người lớn | Size phủ | Trùng |
|---|---|---|---|---|---|
| Áo | `T6K02TT019902` | 4-6y → 10-12y 590k; **XS, S, M 690k** | `T6W02TT019905` | **S, M 690k** | S, M — cùng giá 690k |
| Chân váy | `T6K01SD019908` | 4-6y → 12-14y 690k; **XS, S 790k** | `T6W01SD019902` | **S, M, L 790k** | S — cùng giá 790k |

Một chiếc áo M14 size S bán ra có thể được ghi vào mã nào cũng "đúng". Tồn tách làm đôi, không mã nào phản ánh đúng số thật.

### 5.5 `C6K01TT0199014` thừa một số — xác nhận

LIVE 8-9/9, khối M23, "Áo trắng 1-2y → 10-12y 590k; XS, S 650k". Mã dài 14 ký tự, trong khi `C6K01TT019903`, `C6K01TT019904`, `C6K01TT019906` đều 13 ký tự.

Không ảnh hưởng tới 45 món của 17/9, nhưng bảng giá này còn dùng tiếp nên phải sửa. **Không đoán mã đúng** — phải tra KiotViet.

### 5.6 Một chỗ nữa, ngoài 5 mục prompt nêu

`C6K03PP019902` ("Quần loe 490k", M23 của 8-9/9) đang được **gợi ý** cho cả M19 Quần loe hồng lẫn M30 Quần loe xám của 17/9. Đây là lỗi của phần gợi ý tự động, **không phải** mâu thuẫn trong bảng giá — bảng giá chỉ ghi mã này một lần. Nhưng nếu chủ shop bấm nhận cả hai thì sẽ tạo ra đúng cái bẫy kho chung như mục 5.1.

## 6. Báo cáo

### 6.1 Tôi hiểu yêu cầu như thế nào

Nối KiotViet để có số bán thật, kiểm lại quyền 3 sổ, và kiểm từng mã trong bảng ghép — nhằm tới một đích duy nhất: **mỗi món bán trên live phải có đúng một mã KiotViet**, để tồn sổ và tồn thật nói cùng một thứ tiếng. Chưa có nó thì không đối soát được buổi live nào.

### 6.2 Dữ liệu đã có

- Quyền của cả 3 sổ, đọc trực tiếp ngày 26/09.
- Toàn bộ nội dung bảng giá "CHECK GIÁ PAGE + LIVE TĐ 2026": 6 tab, trong đó LIVE 17/9 và LIVE 8-9/9 là nguồn mã.
- 45 món của live 17/9 kèm tồn sổ, số chiếc đặt và 27 gợi ý mã, lấy từ trang "Ghép mã KiotViet 17/9".
- Collection `ghep`: rỗng.

### 6.3 Dữ liệu còn thiếu và giả định đang dùng

| Thiếu gì | Ảnh hưởng |
|---|---|
| Kết nối và khoá KiotViet | Không món nào kết luận được "Khớp" hay "Lệch". Toàn bộ phân loại trong bảng 45 món là **mức sẵn sàng**, không phải kết quả đối chiếu. |
| ~~Nội dung 28 tab mã của sổ Live 17/9~~ | **Đã đọc 27/09** — xem mục 7. Đối soát vẫn chờ KiotViet. |
| Ảnh sản phẩm | Không phân biệt được chân váy M06 và M14 có phải một mẫu không. |

Ba giả định tôi đang dùng, và phải được xác nhận:

1. **Bảng giá là bảng quy đổi mã trên thực tế.** Không ai gọi nó như vậy, nhưng cột "MÃ KIOT" là chỗ duy nhất nối mã live với KiotViet.
2. **`T6W` là dòng size người lớn.** Suy từ 5 lần xuất hiện, lần nào cũng chỉ có S/M/L/Freesize. Chưa ai xác nhận.
3. **Số tồn sổ và số chiếc đặt** lấy nguyên từ trang "Phòng duyệt live 17/09", phiên này chưa kiểm lại từ sổ gốc.

### 6.4 Phân tích vấn đề

**Biểu hiện:** 0/45 món được ghép; đối soát không chạy được.

**Nguyên nhân trực tiếp:** mạng bị chặn và chưa có khoá KiotViet.

**Nguyên nhân gốc — nằm ở chỗ khác hẳn.** Kể cả khi mở mạng và có khoá ngay hôm nay, **28% số chiếc khách đặt vẫn không ghép được**, vì bảng giá không có mã cho chúng. Nặng nhất:

> **M01 Quần da beo: 150 chiếc đặt — món nhiều nhất cả buổi, khoảng 91,5 triệu — và bảng giá để trống ô mã.**

Tôi đọc lại dòng gốc trong bảng giá LIVE 17/9 để chắc: khối M01 có hai dòng, dòng "Áo" có mã `T6K02TT019910`, dòng "Quần: 4-6y đến 12-14y giá 490 / S ; M giá 690" **kết thúc mà không có mã nào**. Trùng khớp với ghi chú của sổ live: "QUẦN VIẾT GIẤY".

Vậy gốc rễ là: **hệ thống mã hàng của shop có ba mức chất lượng khác nhau mà không ai phân biệt** —

| Mức | Số món | Đặc điểm |
|---|---|---|
| Có mã riêng, đúng | 9 | Bảng 17/9 ghi thẳng, khớp giá và size |
| Có mã nhưng dùng chung / trùng / chồng size | 18 | `T6K01SD019908`, `C6K02TT019901`, cặp T6K–T6W… |
| Không có mã | 18 | Trong đó món bán chạy nhất buổi |

Ba mức này trông giống nhau khi nhìn bảng giá — đều là một dòng có chữ. Chỉ khi đối chiếu mới lộ ra.

### 6.5 Những điểm đang làm đúng

- **Bảng giá có cột MÃ KIOT.** Shop đã có ý thức nối hai hệ thống. Không phải bắt đầu từ số không.
- **Quy tắc đặt mã có hệ thống**: `T6K` trẻ em, `T6W` người lớn, `C6K`/`ICK` theo dòng hàng, đuôi 6 số. Đây là tài sản — có quy tắc thì kiểm được bằng máy.
- **Trang ghép mã dựng sẵn 27/45 gợi ý kèm độ khớp và lý do**, và cắm cờ đúng 9 chỗ rủi ro. Người ghép không phải bắt đầu từ trang trắng.
- **Sổ live ghi chú trung thực** những chỗ mình thiếu ("QUẦN VIẾT GIẤY", "Cvay hết"). Ghi nhận cái mình không biết là thói quen tốt và hiếm.

### 6.6 Những điểm cần khắc phục

| Góc nhìn | Vấn đề |
|---|---|
| Khách hàng | 204 tên khách trong sổ Live 17/9 đang ai có link cũng xem được |
| Hàng hoá | 18/45 món không có mã; món 150 chiếc nằm trong đó |
| Tồn kho | `T6K01SD019908` gộp 6 chân váy; cặp T6K–T6W chồng size S/M ở M14 |
| Tài chính | `C6K02TT019901` hai giá chồng size → doanh thu ghi sai ở size 10-12y và XS/S |
| Vận hành | Mã hàng vẫn nằm trong trí nhớ người; bảng giá kiêm vai trò bảng quy đổi mà không ai bảo trì |
| Nhân sự | Ba sổ ba chủ khác nhau, không ai thấy toàn cảnh |

### 6.7 Giải pháp đề xuất

| # | Việc | Ai làm | Đo bằng gì | Ưu tiên |
|---|---|---|---|---|
| 1 | Đổi quyền 3 sổ sang "Chỉ người được thêm" | Ba chủ file | Đọc lại quyền, không còn dòng `anyone` | Cao |
| 2 | Cấp mã KiotViet cho M01 Quần da beo | Người nhập hàng | Bảng giá có mã; 150 chiếc truy được | Cao |
| 3 | Mở Network access + lưu khoá KiotViet | Chủ shop | `products?pageSize=1` trả 200 | Cao |
| 4 | Ngồi ghép 9 món "sẵn sàng" trước | Chủ shop | 9 doc trong `ghep` | Cao |
| 5 | Quyết `T6K01SD019908`: một mẫu hay sáu mẫu | Chủ shop + người nhập hàng | Mỗi chân váy một mã riêng | Cao |
| 6 | Tách hoặc gộp cặp T6K–T6W ở M14 | Người nhập hàng | Không size nào nằm trong hai mã | Trung bình |
| 7 | Sửa `C6K01TT0199014` và chọn đúng mã áo sơ mi ren | Người giữ bảng giá | Mọi mã đúng 13 ký tự và có thật trên KiotViet | Trung bình |
| 8 | Đặt bảng giá làm bảng quy đổi chính thức, có người chịu trách nhiệm | Chủ shop | Mỗi buổi live không còn ô mã trống | Dài hạn |

### 6.8 Kế hoạch

**7 ngày** — việc 1, 2, 3 ở trên. Ba việc này đều là việc của người, không ai làm thay được, và việc 1 là rủi ro dữ liệu khách đang chạy từng ngày.

**30 ngày** — ghép xong 45 món (bắt đầu từ 9 món sẵn sàng, rồi 18 món cần hỏi, cuối cùng 18 món chưa có mã). Chạy đối soát live 17/9. Áp quy tắc "không có mã KiotViet thì không lên live" cho buổi kế tiếp.

**90 ngày** — mỗi buổi live mới tự động kiểm: mã nào chưa có trong sổ mã hàng thì báo trước khi lên sóng. Nối số bán thật từ KiotViet vào màn hình "nhập thêm / giữ / dừng".

### 6.9 Rủi ro và phương án dự phòng

| Rủi ro | Dự phòng |
|---|---|
| Đổi quyền sổ làm gãy công cụ đang đọc sổ qua link công khai | Đổi quyền trước, sửa công cụ sau — dữ liệu khách quan trọng hơn. Connector Drive vẫn đọc được sổ đã khoá nếu tài khoản được chia sẻ. |
| Ghép mã sai còn tệ hơn không ghép | Món nào không chắc thì bấm "Cần hỏi", đừng bấm "Đã xác nhận". Một mã sai làm hỏng cả số tồn lẫn số bán. |
| KiotViet không quản lý tới từng size | Thì `T6K01SD019908` và cặp T6K–T6W không sửa được bằng ghép mã, phải sửa trong KiotViet trước. |
| Chủ shop đã ghép mà không lưu lên được | Mở lại trang, đọc dòng trạng thái ở góc. Nếu ghi "chỉ lưu trên máy này" thì phải cấp quyền ghi trước khi ngồi làm. |

### 6.10 Những điểm AI có thể đang đánh giá sai

1. **"0 doc" có thể không có nghĩa là chưa làm.** Trang lưu vào máy trước rồi mới đẩy lên chung. Nếu chủ shop chỉ có quyền xem, lựa chọn nằm lại trên máy và tôi không thấy. Tôi đang báo "chưa làm" dựa trên một kho rỗng, chứ không phải bằng chứng là chưa ai bấm.
2. **Tôi kết luận `T6K01SD019908` là mã dán tạm từ hình thức của dữ liệu, không từ hàng thật.** Nếu shop thật sự bán đúng một mẫu chân váy nâu suốt hai buổi và gọi nó theo mã live của từng set, thì mã ấy đúng và kết luận của tôi sai.
3. **Quy luật "T6W = size người lớn" chỉ dựa trên 5 lần xuất hiện.** Đủ để nêu giả thuyết, không đủ để chắc. Nếu sai thì phân tích mục 5.4 sai theo.
4. **Con số 281 chiếc / 28% phụ thuộc vào số chiếc đặt của trang "Phòng duyệt live 17/09"**, mà phiên này tôi chưa kiểm lại từ sổ gốc. Nếu số đó lệch thì mức nghiêm trọng tôi mô tả lệch theo.
5. **Tôi giả định bảng giá là bảng quy đổi.** Có thể shop còn một danh sách mã khác ở nơi tôi chưa thấy — nếu có thì phần "18 món không có mã" hẹp lại đáng kể.

### 6.11 Câu hỏi tiếp theo

1. **Quần da beo M01 — 150 chiếc, món nhiều nhất buổi — đã lên đơn KiotViet chưa, và dưới mã nào?** Nếu chưa có mã thật thì 150 chiếc này chưa từng vào hệ thống, và đó là việc gấp hơn mọi thứ khác trong bản này.
2. **`T6K01SD019908` là một chiếc chân váy hay sáu chiếc khác nhau?** Câu trả lời quyết định 33 chiếc đặt ngày 17/9 có đang trừ nhầm kho hay không, và quyết định cách sửa (tách mã hay giữ nguyên).
3. **Khi mở trang ghép mã, dòng trạng thái ở góc ghi gì?** Nó phân biệt "chưa ai làm" với "đã làm mà không lưu lên được" — hai tình huống cần hai cách xử lý khác hẳn nhau.

## 7. Đọc sổ Live 17/9 (27/09) — quy trình làm việc thật

Đọc toàn bộ 28 tab mã và tab ĐƠN OK qua connector Drive. **Chỉ đọc, không sửa gì.** Sổ vẫn đang được chỉnh — lần sửa gần nhất 27/09 lúc 08:29, tức 10 ngày sau buổi live.

Không có tên khách nào được chép vào tài liệu này.

### 7.1 Cấu trúc một tab mã

```
MÃ     | <mã live> | <ký hiệu người phụ trách>
GIÁ    | <người>
<ghi chú tự do>
<giá thấp>,<giá cao>
SL     | n1 | n2 | n3 | ...        ← tồn đầu buổi, mỗi số một cột size
<tên món> <giá> | <size 1> | <size 2> | ...
<tên khách> | <tên khách> | ...     ← mỗi cột một size, mỗi ô một người đặt
```

**Mỗi cột là một size. Mỗi ô có tên là một chiếc đã đặt.** Đếm số ô trong cột rồi so với dòng SL là ra còn hay hết. Không có công thức nào — đếm bằng mắt.

Một tab có thể chứa **nhiều khối món**: M10 có 3 khối (áo ghi lê, áo giữ nhiệt, chân váy), M06 có 3, M11 có 3.

### 7.2 Con số thật của buổi live

| | |
|---|---|
| Khối món có dòng SL | **42** trên 30 mã live |
| Tổng tồn đầu buổi | **2.490 chiếc** |

**File CSV mà quy trình B12 đang dùng chỉ có 28 dòng và 1.791 chiếc** — thiếu **699 chiếc, 28% hàng của buổi live**. Nguyên nhân: người chép tay chỉ lấy **khối món đầu tiên của mỗi tab**.

| Mã | Các khối trong sổ | Chép tay lấy | Bỏ sót |
|---|---|---|---|
| M01 | áo 160 · quần da beo 139 | 160 | **139** |
| M10 | ghi lê 83 · giữ nhiệt 56 · chân váy 112 | 83 | **168** |
| M08 | áo 216 · chân váy 129 | 216 | **129** |
| M11 | váy 24 · áo 6 · tất ren 114 | 24 | **120** |
| M06 | ghi lê 156 · sơ mi 31 · chân váy 47 | 156 | **78** |
| M16 | áo 19 · chân váy 19 | 19 | 19 |
| M28 | áo 48 · chân váy 18 | 48 | 18 |
| M17 | áo 32 · quần 7 | 32 | 7 |
| M18 | áo gió 47 · khoác hồng 1 | 47 | 1 |

Quần da beo M01 — món 150 chiếc đặt — **có tồn 139 chiếc ghi rõ trong sổ**, nhưng không có trong file chép tay. Mọi phân tích dựa trên file đó đều thiếu món này.

### 7.3 Mã live là lượt lên sóng, không phải sản phẩm

Sổ có 8 dòng ghi quan hệ chéo:

| Tab | Ghi chú trong sổ |
|---|---|
| M02 | MIX CÙNG ÁO M01 |
| M08 | LÊN LẠI MIX ÁO CÙNG CHÂN VÁY NÂU M06 |
| M13 | MIX CÙNG CHÂN VÁY M10 |
| M14 | MIX CÙNG CHÂN VÁY M06 |
| M16 | MIX CÙNG ÁO GHI LÊ M06 |
| M19 | Mix cùng áo hồng M18 |
| M26 | MIX CÙNG QUẦN M20 |
| M28 | MIX CÙNG QUẦN DA BEO M01 |

Đây là chìa khoá của cả bài toán ghép mã: **một sản phẩm xuất hiện trong nhiều set, mỗi set một mã live.** Bảng giá gán mã KiotViet theo **sản phẩm**; sổ live gán theo **lượt lên sóng**. Hai hệ đếm khác nhau, nên không bao giờ khớp 1–1.

Vì vậy quan hệ đúng là **nhiều mã live → một mã KiotViet**, chứ không phải một–một. Sổ mã hàng phải cho phép điều đó, và cảnh báo "hai món dùng chung một mã" chỉ nên bật khi hai món **không** có dòng MIX nối nhau.

### 7.4 Những chỗ dữ liệu tự mâu thuẫn

**Cột size nhiều hơn số tồn** — 2 chỗ:

| Món | Số tồn | Số cột size | Cột gộp |
|---|---|---|---|
| M01 áo | 7 | 8 | "110 1-2" và "2-4" chung một số |
| M08 áo | 8 | 9 | "120 6-8 (hoặc 4-6)" |

**Cột size mơ hồ** — M14 có cột ghi `160 S hoặc M`; M15 có cột `160 XS & S`. Hai size trong một ô tồn thì không biết hết size nào.

**Size thiếu trong dãy** — M03 không có 28, M05 không có 29, M28 chân váy nhảy từ 120 sang 140 (thiếu 130 8-10).

**Tồn ghi dạng `a+b`** — `6+2`, `27+1 đổi`, `5+1`, `7 (CÒN VỀ THÊM)`. Phần "+b" là hàng về thêm hoặc hàng đổi về, nhưng không có cột riêng nên máy không phân biệt được với tồn gốc.

**M16 áo và chân váy có dòng SL giống hệt nhau** (`1,1,2,3,8,4`). Có thể đúng, cũng có thể là chép đè. Cần kiểm.

### 7.5 Một ô chứa quá nhiều thứ

Ô tên khách đang gánh đồng thời: tên · số lượng (`x2`) · size thật khi khác cột · trạng thái tiền (`đợi ck`, `đợi cọc`, `ck`) · trạng thái chờ (`đợi rep`) · nguồn đơn (`page`) · khuyến mãi (`KM`) · thao tác (`đổi`, `đổi về`, `đổi sz`, `huỷ`, `lấy thêm`, `phụ`).

Không có cột riêng cho bất kỳ thứ nào. Hệ quả: muốn biết "bao nhiêu đơn đang đợi chuyển khoản" thì phải đọc tay từng ô của 42 khối món.

`phụ` xuất hiện rải rác — nhiều khả năng là khách đặt khi đã hết hàng, tức **danh sách chờ đang nằm lẫn trong sổ tồn** chứ không có chỗ riêng.

### 7.6 Tab ĐƠN OK

15 cột, chia theo chữ cái đầu của tên: `AB`, `C D Đ`, `M`, `L`, `P`, `Q`, `V`, `N`, `N 3-4chữ`, `T`, `T 3-4chữ`, `H`, `H 3-4 CHỮ`, `GKEFJI`, `SXWOURY`. Dòng đầu có 4 nhãn: ĐƠN GẤP, QUA LẤY, ĐƠN HỦY, KHÁCH HP.

Đây là **bảng tra tay "khách này đã lên đơn chưa"**. Ba chữ cái N, T, H bị tách đôi theo độ dài tên — tra nhầm cột là mất dấu khách. Và vì khớp bằng tên Facebook nên hai người trùng tên không phân biệt được; sổ tồn có những tên lặp lại nhiều lần ở nhiều cột mà không biết là một người mua nhiều hay nhiều người.

### 7.7 Rủi ro nghiêm trọng: sổ đang mở công khai

Sổ này để chế độ "bất kỳ ai có link đều xem được" (mục 3). Bên trong, ngoài tên khách, còn có ghi chú nội bộ nằm ngay cạnh tên:

- `thiếu 2 ng, giả vờ thất lạc`
- `con này cút, đơn VH cầm`
- `hiệp sĩ lợn huỷ`
- `chốt page thì nhận lố lên 2c đi, form rộng lắm mấy con này có 4 mấy cân k vừa đâu`

Câu đầu tiên mô tả một cách xử lý thiếu hàng. Nếu một khách hàng, một đối thủ hoặc một nhà báo mở link này, thiệt hại uy tín lớn hơn nhiều so với việc lộ danh sách tên. **Đây là lý do đổi quyền sổ phải làm trong hôm nay, không chờ gì cả.**
