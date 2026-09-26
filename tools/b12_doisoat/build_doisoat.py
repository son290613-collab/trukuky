"""Dựng file đối soát buổi live (B12) — bình luận ↔ sổ live ↔ ĐƠN OK.

Chạy:
    python build_doisoat.py <phieu_binh_luan.json> <don_ok.csv> <so_ton.csv> <file_ra.xlsx>

- phieu_binh_luan.json : khối dữ liệu của trang "Chốt đơn live" (custs, lines, matrix, stats)
- don_ok.csv           : tab "ĐƠN OK" của sổ live, xuất CSV (hàng 1 = chú giải màu, hàng 2 = nhóm chữ cái)
- so_ton.csv           : bảng tồn chép từ các tab M của sổ live (xem so_ton_live20260917.csv)

Mọi con số tổng hợp trong file ra là công thức; chỉ dữ liệu gốc và tham số là giá trị nhập.
File ra có tên khách (tên Facebook) — không đưa vào kho mã, không chia sẻ link công khai.
"""
import csv
import difflib
import json
import re
import sys
import unicodedata
from collections import Counter

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SRC_JSON, SRC_DONOK, SRC_TON, OUT = sys.argv[1:5]

# ---------- kiểu dáng ----------
F = "Arial"
f_base = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_head = Font(name=F, size=10, bold=True, color="FFFFFF")
f_title = Font(name=F, size=14, bold=True, color="1F4E3C")
f_h2 = Font(name=F, size=11, bold=True, color="1F4E3C")
f_input = Font(name=F, size=10, color="0000FF")
f_link = Font(name=F, size=10, color="008000")
f_note = Font(name=F, size=9, italic=True, color="555555")
fill_head = PatternFill("solid", fgColor="2F6B54")
fill_calc = PatternFill("solid", fgColor="E3EFE7")
fill_input = PatternFill("solid", fgColor="FFF6CC")
fill_total = PatternFill("solid", fgColor="D9D9D9")
fill_red = PatternFill("solid", fgColor="F8D7DA")
fill_amber = PatternFill("solid", fgColor="FCE8C3")
fill_green = PatternFill("solid", fgColor="D8EFDD")
fill_grey = PatternFill("solid", fgColor="ECECEC")
thin = Side(style="thin", color="BFBFBF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top")
MONEY = "#,##0"
PCT = "0%"
TIME = "[h]:mm:ss"


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.replace("đ", "d").replace("Đ", "D").lower())


def tsec(t):
    if not t:
        return None
    h, m, s = (int(x) for x in t.split(":"))
    return (h * 3600 + m * 60 + s) / 86400


def header(ws, row, cols, widths=None):
    for j, name in enumerate(cols, 1):
        c = ws.cell(row=row, column=j, value=name)
        c.font, c.fill, c.alignment, c.border = f_head, fill_head, Alignment(wrap_text=True, vertical="center"), box
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[row].height = 30


def style_body(ws, r1, r2, c1, c2, calc_cols=(), input_cols=(), fmt=None):
    fmt = fmt or {}
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = f_input if c in input_cols else f_base
            cell.border = box
            if c in calc_cols:
                cell.fill = fill_calc
            if c in input_cols:
                cell.fill = fill_input
            if c in fmt:
                cell.number_format = fmt[c]


# ---------- đọc nguồn ----------
D = json.load(open(SRC_JSON, encoding="utf8"))
CUST = {c["id"]: c for c in D["custs"]}
LINES = sorted(D["lines"], key=lambda x: x["o"])
GROUP = ["Đã rõ", "Kiểm kho", "Hỏi lại khách", "Có thể đã huỷ"]
TON = list(csv.DictReader(open(SRC_TON, encoding="utf8")))
raw = list(csv.reader(open(SRC_DONOK, encoding="utf8")))
legend, buckets = raw[0], raw[1]
DONOK = []
for r in raw[2:]:
    for j, v in enumerate(r):
        v = v.strip()
        if v:
            DONOK.append((buckets[j], v))

cust_names = sorted({c["n"] for c in D["custs"]})
fold_map = {}
for n in cust_names:
    fold_map.setdefault(fold(n), n)
MARKERS = re.compile(r"\s+(gấp|gap|x\d+)$", re.I)


def clean_ok(name):
    """Bỏ đuôi ghi chú ('gấp', 'x2') để so tên; không sửa tên gốc."""
    c = MARKERS.sub("", name).strip()
    note = "bỏ đuôi ghi chú" if c != name else ""
    if c not in cust_names and fold(c) in fold_map:
        c, note = fold_map[fold(c)], (note + "; " if note else "") + "khác dấu/viết hoa"
    return c, note


def near(name, pool):
    m = difflib.get_close_matches(fold(name), [fold(p) for p in pool], n=1, cutoff=0.82)
    if not m:
        return ""
    for p in pool:
        if fold(p) == m[0]:
            return p if p != name else ""
    return ""


DONOK_ROWS = [(b, n, *clean_ok(n)) for b, n in DONOK]
ok_clean = {c for _, _, c, _ in DONOK_ROWS}

wb = Workbook()

# ======================= GOC-SO-TON =======================
so = wb.active
so.title = "GOC-SO-TON"
cols = ["Mã M", "Món (tên chuẩn)", "Cột trong sổ", "Size khách gọi 1", "Size khách gọi 2", "Giá (VNĐ)",
        "SL ghi trong sổ", "SL phần chính", "SL phần '+'", "Tồn dùng tính", "Mã KiotViet", "Ghi chú sổ",
        "Khoá 1", "Khoá 2", "Khoá mã|món"]
header(so, 1, cols, [7, 20, 18, 9, 9, 11, 18, 9, 9, 10, 16, 48, 22, 22, 18])
for i, t in enumerate(TON, start=2):
    vals = [t["ma_m"], t["mon"], t["cot_so"], t["size_1"], t["size_2"] or None, int(t["gia"]), t["sl_goc"],
            int(t["sl_a"]), int(t["sl_b"]), f"=H{i}+I{i}*'TOM-TAT'!$C$5", t["ma_kiot"] or None, t["ghi_chu_so"] or None,
            f'=A{i}&"|"&B{i}&"|"&D{i}', f'=IF(E{i}="","",A{i}&"|"&B{i}&"|"&E{i})', f'=A{i}&"|"&B{i}']
    for j, v in enumerate(vals, 1):
        so.cell(row=i, column=j, value=v)
N_SO = len(TON) + 1
style_body(so, 2, N_SO, 1, 15, calc_cols=(10, 13, 14, 15), input_cols=range(1, 13), fmt={6: MONEY})
for r in range(2, N_SO + 1):
    so.cell(row=r, column=10).font = f_base
so.freeze_panes = "C2"
so.auto_filter.ref = f"A1:O{N_SO}"
so["J1"].comment = Comment("= phần chính + phần '+' × tham số 'TOM-TAT'!C5 (1 = tính cả phần '+'). "
                           "Chưa rõ '+N' trong sổ là hàng đổi về, hàng kho khác hay hàng về thêm.", "NV4-B12")
SO_R = "$2:$400"


def so_col(c):
    return f"'GOC-SO-TON'!${c}$2:${c}$400"


# ======================= QUY-DOI-MA =======================
qd = wb.create_sheet("QUY-DOI-MA")
header(qd, 1, ["Mã trong bình luận", "Món trong bình luận", "Quy về mã sổ", "Quy về món sổ", "Lý do", "Độ chắc", "Khoá"],
       [12, 22, 12, 18, 70, 22, 22])
QD = [("M15", "Áo mèo", "M08", "Áo mèo",
       "Tab M15 của sổ là áo khoác cổ kẻ nâu; bản cũ tự ghi 'cùng mẫu áo mèo M08, cùng giá' → tồn nằm ở tab M08.",
       "Cao — cần 1 người xem lại bình luận 3:15:57"),
      ("M13", "Chân váy đen", "M10", "Chân váy",
       "Sổ và bảng giá 17/9 chỉ có áo sơ mi ren cho M13; giá 590/690 trùng chân váy M10 (C6K01SD019905). "
       "Nếu đúng, cầu chân váy M10 phải cộng thêm các dòng này.",
       "Trung bình — HỎI Quản lý")]
for i, row in enumerate(QD, start=2):
    for j, v in enumerate(row, 1):
        qd.cell(row=i, column=j, value=v)
    qd.cell(row=i, column=7, value=f'=A{i}&"|"&B{i}')
style_body(qd, 2, 12, 1, 7, calc_cols=(7,), input_cols=range(1, 7))
for r in range(2, 13):
    qd.cell(row=r, column=7).font = f_base
    for c in (5, 6):
        qd.cell(row=r, column=c).alignment = wrap
qd["A14"] = "Thêm dòng khi phát hiện bình luận ghi sai mã. Cột 'Khoá' tự tính; để trống dòng chưa dùng."
qd["A14"].font = f_note

# ======================= GOC-DON-OK =======================
ok = wb.create_sheet("GOC-DON-OK")
header(ok, 1, ["Nhóm chữ cái (hàng 2 của tab)", "Tên ghi trong sổ (gốc)", "Tên dùng để so", "Làm sạch",
               "Có trong bình luận?", "Tên gần giống trong bình luận (gợi ý)"], [14, 26, 26, 22, 14, 30])
for i, (b, n, c, note) in enumerate(DONOK_ROWS, start=2):
    ok.cell(row=i, column=1, value=b)
    ok.cell(row=i, column=2, value=n)
    ok.cell(row=i, column=3, value=c)
    ok.cell(row=i, column=4, value=note or None)
    ok.cell(row=i, column=5, value=f"=IF(COUNTIF('GOC-BINH-LUAN'!$D$2:$D$3000,C{i})>0,\"CÓ\",\"KHÔNG\")")
    ok.cell(row=i, column=6, value=(near(c, cust_names) if c not in cust_names else "") or None)
N_OK = len(DONOK_ROWS) + 1
style_body(ok, 2, N_OK, 1, 6, calc_cols=(5,), input_cols=(1, 2))
ok.freeze_panes = "B2"
ok.auto_filter.ref = f"A1:F{N_OK}"
ok["H1"] = "Chú giải màu ở hàng 1 của tab ĐƠN OK:"
ok["H1"].font = f_bold
for k, v in enumerate([x for x in legend if x], start=2):
    ok.cell(row=k, column=8, value=v)
ok.cell(row=7, column=8, value="Màu ô không đọc được qua xuất CSV → chưa biết tên nào là ĐƠN HỦY / ĐƠN GẤP / QUA LẤY / KHÁCH HP.").font = f_note
ok.column_dimensions["H"].width = 60

# ======================= GOC-BINH-LUAN =======================
bl = wb.create_sheet("GOC-BINH-LUAN")
cols = ["Thứ tự BL", "Giờ video", "Mã KH", "Tên Facebook", "Mã (BL)", "Món (BL)", "Size", "SL", "Đơn giá BL (VNĐ)",
        "Nhóm (bản cũ)", "Ghi chú bản cũ", "Bình luận gốc", "ID bình luận",
        "Mã sổ", "Món sổ", "Vị trí dòng tồn", "Tồn sổ", "Cộng dồn theo giờ", "Giá sổ (VNĐ)",
        "Thành tiền BL (VNĐ)", "Kết luận tồn", "Kiểm giá", "Trong ĐƠN OK?", "Việc cần làm"]
header(bl, 1, cols, [7, 9, 7, 20, 7, 16, 8, 5, 11, 12, 26, 40, 18, 7, 14, 7, 7, 8, 11, 12, 20, 8, 9, 30])
for i, l in enumerate(LINES, start=2):
    c = CUST.get(l["c"], {})
    note = " · ".join(x for x in [l["st"] if l["st"] != "Rõ ràng" else "", l["no"]] if x)
    vals = [l["o"], tsec(l["t"]), l["c"], c.get("n"), l["m"], l["i"], l["s"], l["q"], l["p"], GROUP[l["g"]],
            note or None, l["tx"], l["fb"]]
    for j, v in enumerate(vals, 1):
        bl.cell(row=i, column=j, value=v)
    bl.cell(row=i, column=13).number_format = "@"
    r = i
    bl.cell(row=r, column=14, value=f"=IFERROR(INDEX('QUY-DOI-MA'!$C$2:$C$50,MATCH(E{r}&\"|\"&F{r},'QUY-DOI-MA'!$G$2:$G$50,0)),E{r})")
    bl.cell(row=r, column=15, value=f"=IFERROR(INDEX('QUY-DOI-MA'!$D$2:$D$50,MATCH(E{r}&\"|\"&F{r},'QUY-DOI-MA'!$G$2:$G$50,0)),F{r})")
    bl.cell(row=r, column=16, value=f"=IFERROR(MATCH(SUBSTITUTE(N{r}&\"|\"&O{r}&\"|\"&G{r},\"?\",\"#\"),{so_col('M')},0),IFERROR(MATCH(SUBSTITUTE(N{r}&\"|\"&O{r}&\"|\"&G{r},\"?\",\"#\"),{so_col('N')},0),\"\"))")
    bl.cell(row=r, column=17, value=f"=IF(P{r}=\"\",\"\",INDEX({so_col('J')},P{r}))")
    bl.cell(row=r, column=18, value=f"=IF(OR(P{r}=\"\",J{r}=\"Có thể đã huỷ\"),\"\",SUMIFS($H$2:$H$3000,$P$2:$P$3000,P{r},$A$2:$A$3000,\"<=\"&A{r},$J$2:$J$3000,\"<>Có thể đã huỷ\"))")
    bl.cell(row=r, column=19, value=f"=IF(P{r}=\"\",\"\",INDEX({so_col('F')},P{r}))")
    bl.cell(row=r, column=20, value=f"=IF(I{r}=\"\",\"\",H{r}*I{r})")
    bl.cell(row=r, column=21, value=(f"=IF(J{r}=\"Có thể đã huỷ\",\"HUỶ\",IF(P{r}<>\"\",IF(R{r}<=Q{r},\"TRONG TỒN\",\"VƯỢT TỒN\"),IF(LEFT(G{r},1)=\"?\",\"THIẾU SIZE\","
                                     f"IF(COUNTIF({so_col('O')},SUBSTITUTE(N{r}&\"|\"&O{r},\"?\",\"#\"))>0,\"SIZE KHÔNG CÓ TRONG SỔ\","
                                     f"IF(COUNTIF({so_col('A')},SUBSTITUTE(N{r},\"?\",\"#\"))>0,\"MÓN CHƯA CÓ TRONG SỔ\",\"MÃ KHÔNG CÓ TRONG SỔ\")))))"))
    bl.cell(row=r, column=22, value=f"=IF(OR(S{r}=\"\",I{r}=\"\"),\"\",IF(S{r}=I{r},\"KHỚP\",\"LỆCH\"))")
    bl.cell(row=r, column=23, value=f"=IF(COUNTIF('GOC-DON-OK'!$C$2:$C$500,D{r})>0,\"CÓ\",\"CHƯA\")")
    bl.cell(row=r, column=24, value=(f"=IF(U{r}=\"HUỶ\",\"—\",IF(U{r}=\"TRONG TỒN\",IF(J{r}=\"Hỏi lại khách\",\"Hỏi lại size/món rồi chốt\",\"Có hàng: chốt được\"),"
                                     f"IF(U{r}=\"VƯỢT TỒN\",\"Hết size: mời đổi size / đặt chờ\",IF(U{r}=\"THIẾU SIZE\",\"Hỏi size rồi tra tồn\",IF(U{r}=\"SIZE KHÔNG CÓ TRONG SỔ\",\"Báo không có size, gợi ý size gần\","
                                     f"IF(U{r}=\"MÓN CHƯA CÓ TRONG SỔ\",\"Tra sổ giấy / KiotViet\",\"Xác định mã hàng\"))))))"))
N_BL = len(LINES) + 1
style_body(bl, 2, N_BL, 1, 24, calc_cols=range(14, 25), input_cols=range(1, 14),
           fmt={2: TIME, 9: MONEY, 19: MONEY, 20: MONEY})
for r in range(2, N_BL + 1):
    bl.cell(row=r, column=12).alignment = Alignment(vertical="top", wrap_text=False)
bl.freeze_panes = "E2"
bl.auto_filter.ref = f"A1:X{N_BL}"
bl["R1"].comment = Comment("Cộng dồn SL của cùng dòng tồn, theo thứ tự bình luận (sớm trước). "
                           "Giả định: shop xếp hàng theo giờ bình luận (B12 §4.4). Kiểm mẫu 23 tên đầu tab M10: 14/23 trùng nhóm đặt sớm nhất → dùng như ước lượng.", "NV4-B12")
bl["U1"].comment = Comment("TRONG TỒN: cộng dồn ≤ tồn sổ · VƯỢT TỒN: đặt sau khi size đã đủ người · "
                           "THIẾU SIZE: khách chưa nói size · SIZE KHÔNG CÓ: mã-món có trong sổ nhưng size này không có · MÓN CHƯA CÓ: sổ không ghi món này "
                           "(vd quần M01 'viết giấy') · MÃ KHÔNG CÓ: mã '?' hoặc hàng không có tab.", "NV4-B12")

for rng, fill in ((f'U2:U{N_BL}', None),):
    pass
bl.conditional_formatting.add(f"U2:U{N_BL}", FormulaRule(formula=[f'U2="VƯỢT TỒN"'], fill=fill_red))
bl.conditional_formatting.add(f"U2:U{N_BL}", FormulaRule(formula=[f'U2="TRONG TỒN"'], fill=fill_green))
bl.conditional_formatting.add(f"V2:V{N_BL}", FormulaRule(formula=[f'V2="LỆCH"'], fill=fill_red))


def blc(c):
    return f"'GOC-BINH-LUAN'!${c}$2:${c}$3000"


# ======================= TON-SIZE =======================
ts = wb.create_sheet("TON-SIZE")
cols = ["Mã M", "Món", "Cột trong sổ", "Giá (VNĐ)", "Tồn sổ", "Cầu từ bình luận", "Cầu chắc (Đã rõ + Kiểm kho)",
        "Còn lại (tồn − cầu)", "Bán được (ước)", "% bán", "Tình trạng", "Vượt? (1/0)", "0 đơn? (1/0)", "Mã KiotViet"]
header(ts, 1, cols, [7, 20, 18, 11, 8, 10, 12, 11, 10, 8, 14, 8, 8, 16])
for r in range(2, N_SO + 1):
    ts.cell(row=r, column=1, value=f"='GOC-SO-TON'!A{r}")
    ts.cell(row=r, column=2, value=f"='GOC-SO-TON'!B{r}")
    ts.cell(row=r, column=3, value=f"='GOC-SO-TON'!C{r}")
    ts.cell(row=r, column=4, value=f"='GOC-SO-TON'!F{r}")
    ts.cell(row=r, column=5, value=f"='GOC-SO-TON'!J{r}")
    ts.cell(row=r, column=6, value=f"=SUMIFS({blc('H')},{blc('P')},ROW()-1,{blc('J')},\"<>Có thể đã huỷ\")")
    ts.cell(row=r, column=7, value=f"=SUMIFS({blc('H')},{blc('P')},ROW()-1,{blc('J')},\"Đã rõ\")+SUMIFS({blc('H')},{blc('P')},ROW()-1,{blc('J')},\"Kiểm kho\")")
    ts.cell(row=r, column=8, value=f"=E{r}-F{r}")
    ts.cell(row=r, column=9, value=f"=MIN(E{r},F{r})")
    ts.cell(row=r, column=10, value=f"=IF(E{r}=0,\"\",I{r}/E{r})")
    ts.cell(row=r, column=11, value=f"=IF(F{r}>E{r},\"VƯỢT \"&(F{r}-E{r}),IF(F{r}=0,\"0 ĐƠN\",IF(I{r}/E{r}>=0.8,\"SẮP HẾT\",\"CÒN \"&(E{r}-F{r}))))")
    ts.cell(row=r, column=12, value=f"=IF(F{r}>E{r},1,0)")
    ts.cell(row=r, column=13, value=f"=IF(F{r}=0,1,0)")
    ts.cell(row=r, column=14, value=f"='GOC-SO-TON'!K{r}&\"\"")
for c in range(1, 6):
    for r in range(2, N_SO + 1):
        ts.cell(row=r, column=c).font = f_link
style_body(ts, 2, N_SO, 1, 14, calc_cols=range(6, 14), fmt={4: MONEY, 10: PCT})
for c in range(1, 6):
    for r in range(2, N_SO + 1):
        ts.cell(row=r, column=c).font = f_link
tr = N_SO + 1
ts.cell(row=tr, column=1, value="TỔNG (theo bộ lọc)")
for c, L in ((5, "E"), (6, "F"), (7, "G"), (9, "I"), (12, "L"), (13, "M")):
    ts.cell(row=tr, column=c, value=f"=SUBTOTAL(9,{L}2:{L}{N_SO})")
ts.cell(row=tr, column=10, value=f"=IF(E{tr}=0,\"\",I{tr}/E{tr})")
for c in range(1, 15):
    ts.cell(row=tr, column=c).fill, ts.cell(row=tr, column=c).font, ts.cell(row=tr, column=c).border = fill_total, f_bold, box
ts.cell(row=tr, column=10).number_format = PCT
ts.freeze_panes = "D2"
ts.auto_filter.ref = f"A1:N{N_SO}"
ts.conditional_formatting.add(f"K2:K{N_SO}", FormulaRule(formula=['LEFT(K2,4)="VƯỢT"'], fill=fill_red))
ts.conditional_formatting.add(f"K2:K{N_SO}", FormulaRule(formula=['K2="SẮP HẾT"'], fill=fill_amber))
ts.conditional_formatting.add(f"K2:K{N_SO}", FormulaRule(formula=['K2="0 ĐƠN"'], fill=fill_grey))


def tsc(c):
    return f"'TON-SIZE'!${c}$2:${c}${N_SO}"


# ======================= KHACH =======================
kh = wb.create_sheet("KHACH")
cols = ["Mã KH", "Tên Facebook", "Nguồn", "Giờ BL đầu", "Dòng đặt", "Tiền trong tồn (VNĐ)", "Tiền vượt tồn (VNĐ)",
        "Tiền chưa kiểm được (VNĐ)", "Dòng cần hỏi lại", "Trong ĐƠN OK?", "Tên trùng?", "Tên gần giống ở nguồn kia (gợi ý)",
        "Trạng thái", "Việc cần làm", "Ưu tiên", "Kết quả liên hệ", "Mã đơn KiotViet", "Người xử lý", "Ghi chú"]
header(kh, 1, cols, [8, 22, 13, 9, 7, 12, 12, 12, 8, 9, 10, 22, 30, 44, 7, 20, 14, 12, 24])

STATUS = [("CHƯA LÊN ĐƠN – CÓ HÀNG", "Tra KiotViet theo tên → không có: xem inbox → ghi SÓT (xử lý ngay) hoặc HUỶ (ghi lý do)", 1),
          ("ĐÃ LÊN ĐƠN – CÓ DÒNG VƯỢT TỒN", "Mở đơn KiotViet: size ở dòng vượt tồn có thật được giao không? Nếu có → size đó đã bán quá sổ", 1),
          ("CÓ ĐƠN – KHÔNG CÓ TRONG BÌNH LUẬN", "Đơn qua inbox/người dẫn đọc tên: đối chiếu KiotViet, ghi nguồn đơn", 2),
          ("CHƯA LÊN ĐƠN – CHƯA KIỂM ĐƯỢC TỒN", "Hỏi size (nếu thiếu) · tra sổ giấy quần M01 / KiotViet cho món sổ không ghi · rồi xử như ưu tiên 1", 2),
          ("CHƯA LÊN ĐƠN – HẾT SIZE", "Xác nhận đã báo hết cho khách; ghi HẾT HÀNG – ĐÃ BÁO", 3),
          ("ĐÃ LÊN ĐƠN", "Đối chiếu tiền KiotViet với cột F + H", 3),
          ("KHÔNG CÓ DÒNG ĐẶT", "—", 4)]

# thứ tự dòng: tính trạng thái giống công thức để sắp xếp
res = {}
cum = Counter()
key2row = {}
for i, t in enumerate(TON):
    for s in (t["size_1"], t["size_2"]):
        if s:
            key2row[(t["ma_m"], t["mon"], s)] = i
stock = [int(t["sl_a"]) + int(t["sl_b"]) for t in TON]
remap = {(a, b): (c, d) for a, b, c, d, *_ in QD}
agg = Counter()
for l in LINES:
    if l["g"] == 3:
        continue
    m, it = remap.get((l["m"], l["i"]), (l["m"], l["i"]))
    k = key2row.get((m, it, l["s"]))
    v = (l["p"] or 0) * l["q"]
    a = agg.setdefault(l["c"], Counter())
    a["n"] += 1
    if k is None:
        a["unk"] += v
        a["unk_n"] += 1
    else:
        cum[k] += l["q"]
        tag = "in" if cum[k] <= stock[k] else "over"
        a[tag] += v
        a[tag + "_n"] += 1


def status_py(cid, name, src):
    if src == "ok":
        return 2, 0
    a = agg.get(cid, Counter())
    if a["n"] == 0:
        return 4, 0
    if name in ok_clean:
        return (1 if a["over_n"] > 0 else 3), -(a["in"] + a["unk"])
    if a["in_n"] > 0:
        return 1, -a["in"]
    if a["unk_n"] > 0:
        return 2, -a["unk"]
    return 3, -a["over"]


rows = [(c["id"], c["n"], "Bình luận", tsec(c["f"])) for c in D["custs"]]
okonly = sorted({c for _, _, c, _ in DONOK_ROWS if c not in cust_names})
rows += [(f"OK-{k:03d}", n, "Chỉ có ở ĐƠN OK", None) for k, n in enumerate(okonly, 1)]
rows.sort(key=lambda x: (*status_py(x[0], x[1], "ok" if x[2] != "Bình luận" else "bl"), x[1]))

ST0 = 3
for i, (cid, name, src, first) in enumerate(rows, start=2):
    r = i
    kh.cell(row=r, column=1, value=cid)
    kh.cell(row=r, column=2, value=name)
    kh.cell(row=r, column=3, value=src)
    kh.cell(row=r, column=4, value=first)
    kh.cell(row=r, column=5, value=f"=COUNTIFS({blc('C')},A{r},{blc('J')},\"<>Có thể đã huỷ\")")
    kh.cell(row=r, column=6, value=f"=SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"TRONG TỒN\")")
    kh.cell(row=r, column=7, value=f"=SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"VƯỢT TỒN\")")
    kh.cell(row=r, column=8, value=(f"=SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"MÓN CHƯA CÓ TRONG SỔ\")"
                                    f"+SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"SIZE KHÔNG CÓ TRONG SỔ\")"
                                    f"+SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"MÃ KHÔNG CÓ TRONG SỔ\")"
                                    f"+SUMIFS({blc('T')},{blc('C')},A{r},{blc('U')},\"THIẾU SIZE\")"))
    kh.cell(row=r, column=9, value=f"=COUNTIFS({blc('C')},A{r},{blc('J')},\"Hỏi lại khách\")")
    kh.cell(row=r, column=10, value=f"=IF(COUNTIF('GOC-DON-OK'!$C$2:$C$500,B{r})>0,\"CÓ\",\"CHƯA\")")
    kh.cell(row=r, column=11, value=f"=IF(COUNTIF($B$2:$B$1000,B{r})>1,\"TRÙNG TÊN\",\"\")")
    if src == "Bình luận" and name not in ok_clean:
        kh.cell(row=r, column=12, value=near(name, sorted(ok_clean)) or None)
    elif src != "Bình luận":
        kh.cell(row=r, column=12, value=near(name, cust_names) or None)
    n_in = f"COUNTIFS({blc('C')},A{r},{blc('U')},\"TRONG TỒN\")"
    n_over = f"COUNTIFS({blc('C')},A{r},{blc('U')},\"VƯỢT TỒN\")"
    kh.cell(row=r, column=13, value=(f"=IF(C{r}=\"Chỉ có ở ĐƠN OK\",\"CÓ ĐƠN – KHÔNG CÓ TRONG BÌNH LUẬN\",IF(E{r}=0,\"KHÔNG CÓ DÒNG ĐẶT\","
                                     f"IF(J{r}=\"CÓ\",IF({n_over}>0,\"ĐÃ LÊN ĐƠN – CÓ DÒNG VƯỢT TỒN\",\"ĐÃ LÊN ĐƠN\"),"
                                     f"IF({n_in}>0,\"CHƯA LÊN ĐƠN – CÓ HÀNG\",IF(E{r}-{n_over}>0,\"CHƯA LÊN ĐƠN – CHƯA KIỂM ĐƯỢC TỒN\",\"CHƯA LÊN ĐƠN – HẾT SIZE\")))))"))
    kh.cell(row=r, column=14, value=f"=IFERROR(INDEX($W${ST0}:$W${ST0+6},MATCH(M{r},$V${ST0}:$V${ST0+6},0)),\"\")")
    kh.cell(row=r, column=15, value=f"=IFERROR(INDEX($X${ST0}:$X${ST0+6},MATCH(M{r},$V${ST0}:$V${ST0+6},0)),\"\")")
N_KH = len(rows) + 1
style_body(kh, 2, N_KH, 1, 19, calc_cols=range(5, 16), input_cols=(16, 17, 18, 19), fmt={4: TIME, 6: MONEY, 7: MONEY, 8: MONEY})
for r in range(2, N_KH + 1):
    kh.cell(row=r, column=17).number_format = "@"
kh.freeze_panes = "C2"
kh.auto_filter.ref = f"A1:S{N_KH}"
dv = DataValidation(type="list", formula1='"ĐÃ CHỐT,SÓT – ĐÃ XỬ LÝ,KHÁCH HUỶ,KHÔNG PHẢN HỒI – HUỶ,HẾT HÀNG – ĐÃ BÁO,TRÙNG TÊN – KHÁC NGƯỜI"', allow_blank=True)
kh.add_data_validation(dv)
dv.add(f"P2:P{N_KH}")
kh.conditional_formatting.add(f"M2:M{N_KH}", FormulaRule(formula=['O2=1'], fill=fill_red))
kh.conditional_formatting.add(f"M2:M{N_KH}", FormulaRule(formula=['O2=2'], fill=fill_amber))
kh.conditional_formatting.add(f"M2:M{N_KH}", FormulaRule(formula=['M2="ĐÃ LÊN ĐƠN"'], fill=fill_green))
kh["V1"] = "Bảng việc (sửa được)"
kh["V1"].font = f_h2
for j, h in enumerate(["Trạng thái", "Việc cần làm", "Ưu tiên"], start=22):
    c = kh.cell(row=2, column=j, value=h)
    c.font, c.fill, c.border = f_head, fill_head, box
for k, (s, v, p) in enumerate(STATUS):
    for j, x in enumerate((s, v, p), start=22):
        c = kh.cell(row=ST0 + k, column=j, value=x)
        c.font, c.fill, c.border, c.alignment = f_input, fill_input, box, wrap
kh.column_dimensions["V"].width = 30
kh.column_dimensions["W"].width = 50
kh.column_dimensions["X"].width = 7
kh["J1"].comment = Comment("So tên Facebook với cột 'Tên dùng để so' của GOC-DON-OK (khớp đúng chữ). "
                           "Tên TRÙNG (nhiều tài khoản cùng tên) có thể khớp nhầm người — kiểm bằng KiotViet.", "NV4-B12")


def khc(c):
    return f"KHACH!${c}$2:${c}$1000"


# ======================= MAU-MA =======================
mm = wb.create_sheet("MAU-MA")
mm["A1"] = "Quyết định mẫu mã — buổi live 17/09/2026 (cầu bình luận ↔ tồn sổ)"
mm["A1"].font = f_title
mm["A2"] = ("Đọc: '% bán' = số đặt nằm trong tồn ÷ tồn sổ. 'Hoạt động lúc lên' = số dòng đặt của CẢ buổi trong 30 phút sau khi lên mã "
            "(đo độ đông người xem). Mã lên lúc vắng khách thì % bán thấp chưa nói lên mẫu xấu.")
mm["A2"].font = f_note
cols = ["Mã", "Món", "Giờ lên live", "Hoạt động lúc lên (dòng/30')", "Tồn sổ", "Cầu bình luận", "Bán được (ước)", "% bán",
        "Số size vượt", "Số size 0 đơn", "Khách xin size không có", "Giá trị đặt BL (VNĐ)", "Đề xuất", "Nhận xét NV4 (26/09, tĩnh)"]
HR = 4
header(mm, HR, cols, [7, 22, 9, 11, 8, 9, 9, 8, 8, 8, 10, 13, 30, 60])
at = {}
for r in D["matrix"]:
    if r["at"] and (r["m"], r["i"]) not in at:
        at[(r["m"], r["i"])] = tsec(r["at"])
items = []
seen = set()
for t in TON:
    k = (t["ma_m"], t["mon"])
    if k not in seen:
        seen.add(k)
        items.append(k)
dem = Counter()
for l in LINES:
    if l["g"] != 3:
        dem[remap.get((l["m"], l["i"]), (l["m"], l["i"]))] += l["q"]
extra = [k for k, v in dem.most_common() if k not in seen and k[0] not in ("?",) and k[1] != "?"]
NOTES = {
    ("M01", "Áo"): "Size S (170) vượt 30/22 — cầu size mẹ S mạnh nhất buổi; người dẫn báo hết áo mẹ ≈0:27. Size M, 12-14 khách xin nhưng không có.",
    ("M10", "Áo ghi lê"): "Bán 92% tồn trong ~20 phút; vượt ở 4-6 và 1-2. Mẫu mạnh nhất buổi. Áo giữ nhiệt + chân váy cùng set chưa có số tồn trong sổ.",
    ("M11", "Váy"): "Tồn mỏng (24), vượt ở 4-6. Nếu nhập lại: dồn size 4-6, 6-8.",
    ("M04", "Váy hoa nâu"): "Tồn lớn nhất (183), bán ước 8% dù lên lúc đông (0:29). Tín hiệu mẫu/giá chưa hợp — không nhập thêm; thử phối set / đổi cách quay trước khi tính sale.",
    ("M21", "Set gấu nâu"): "Tồn 207, bán 6% nhưng lên lúc 4:08 (vắng). Chưa đủ căn cứ kết luận — đưa lên đầu buổi sau.",
    ("M29", "Váy"): "Khách xin 'váy công chúa' từ sớm (3 khách, 10 lần) nhưng mã lên lúc 4:58 — gần hết buổi. Lên sớm buổi sau.",
    ("M08", "Áo mèo"): "Bán đều mọi size (35%); không vượt. Giữ, không cần nhập thêm ngay.",
    ("M06", "Áo ghi lê"): "Vượt ở size M (tồn 1). Size XS tồn 50 — dư nhiều.",
    ("M14", "Áo xám"): "Vượt ở M (tồn 1); cột 160 sổ ghi 'S hoặc M' — cần tách size trong sổ.",
    ("M02", "Quần vàng"): "6-8y: 8 người đặt / tồn 3 (tính cả phần '+').",
    ("M05", "Giày nâu"): "Tồn 63, bán 4 đôi (6%) dù lên lúc 0:36 — tín hiệu yếu.",
}
r0 = HR + 1
all_items = items + extra
for n, (m, it) in enumerate(all_items):
    r = r0 + n
    mm.cell(row=r, column=1, value=m)
    mm.cell(row=r, column=2, value=it)
    mm.cell(row=r, column=3, value=at.get((m, it)))
    mm.cell(row=r, column=4, value=f"=IF(C{r}=\"\",\"\",COUNTIFS({blc('B')},\">=\"&C{r},{blc('B')},\"<\"&(C{r}+1/48)))")
    mm.cell(row=r, column=5, value=f"=IF(COUNTIFS({tsc('A')},A{r},{tsc('B')},B{r})=0,\"\",SUMIFS({tsc('E')},{tsc('A')},A{r},{tsc('B')},B{r}))")
    mm.cell(row=r, column=6, value=f"=SUMIFS({blc('H')},{blc('N')},A{r},{blc('O')},B{r},{blc('J')},\"<>Có thể đã huỷ\")")
    mm.cell(row=r, column=7, value=f"=IF(E{r}=\"\",\"\",SUMIFS({tsc('I')},{tsc('A')},A{r},{tsc('B')},B{r}))")
    mm.cell(row=r, column=8, value=f"=IF(OR(E{r}=\"\",E{r}=0),\"\",G{r}/E{r})")
    mm.cell(row=r, column=9, value=f"=IF(E{r}=\"\",\"\",SUMIFS({tsc('L')},{tsc('A')},A{r},{tsc('B')},B{r}))")
    mm.cell(row=r, column=10, value=f"=IF(E{r}=\"\",\"\",SUMIFS({tsc('M')},{tsc('A')},A{r},{tsc('B')},B{r}))")
    mm.cell(row=r, column=11, value=f"=SUMIFS({blc('H')},{blc('N')},A{r},{blc('O')},B{r},{blc('U')},\"SIZE KHÔNG CÓ TRONG SỔ\")")
    mm.cell(row=r, column=12, value=f"=SUMIFS({blc('T')},{blc('N')},A{r},{blc('O')},B{r},{blc('J')},\"<>Có thể đã huỷ\")")
    mm.cell(row=r, column=13, value=(f"=IF(E{r}=\"\",\"CẦN SỐ TỒN (sổ chưa ghi)\",IF(I{r}>0,IF(H{r}>='TOM-TAT'!$C$6,\"NHẬP THÊM – đúng size vượt\",\"BỔ SUNG riêng size vượt\"),"
                                     f"IF(H{r}>='TOM-TAT'!$C$6,\"GIỮ – bán tiếp\",IF(AND(D{r}<>\"\",D{r}<'TOM-TAT'!$C$9),\"CHƯA KẾT LUẬN – lên lại đầu buổi\","
                                     f"IF(AND(H{r}<'TOM-TAT'!$C$7,E{r}>='TOM-TAT'!$C$8),\"KHÔNG NHẬP THÊM – đổi cách bán\",\"THEO DÕI\")))))"))
    mm.cell(row=r, column=14, value=NOTES.get((m, it)))
    if NOTES.get((m, it)):
        mm.row_dimensions[r].height = 40
rN = r0 + len(all_items) - 1
style_body(mm, r0, rN, 1, 14, calc_cols=range(4, 14), input_cols=(1, 2, 3), fmt={3: TIME, 8: PCT, 12: MONEY})
for r in range(r0, rN + 1):
    mm.cell(row=r, column=14).alignment = wrap
    mm.cell(row=r, column=14).font = f_base
mm.freeze_panes = mm.cell(row=r0, column=3)
mm.auto_filter.ref = f"A{HR}:N{rN}"
mm.conditional_formatting.add(f"M{r0}:M{rN}", FormulaRule(formula=[f'LEFT(M{r0},4)="NHẬP"'], fill=fill_green))
mm.conditional_formatting.add(f"M{r0}:M{rN}", FormulaRule(formula=[f'LEFT(M{r0},3)="BỔ "'], fill=fill_green))
mm.conditional_formatting.add(f"M{r0}:M{rN}", FormulaRule(formula=[f'LEFT(M{r0},5)="KHÔNG"'], fill=fill_red))
mm.conditional_formatting.add(f"M{r0}:M{rN}", FormulaRule(formula=[f'LEFT(M{r0},4)="CHƯA"'], fill=fill_amber))
mm.conditional_formatting.add(f"M{r0}:M{rN}", FormulaRule(formula=[f'LEFT(M{r0},3)="CẦN"'], fill=fill_grey))
mm["C4"].comment = Comment("Giờ bình luận niêm yết đầu tiên của mã (bản cũ đọc từ bình luận shop).", "NV4-B12")

# cầu chưa có mã + nhịp buổi live
u0 = rN + 3
mm.cell(row=u0, column=1, value="Khách xin nhưng shop chưa lên mã (đếm từ bình luận, bản cũ)").font = f_h2
header(mm, u0 + 1, ["", "Món khách xin", "Số khách", "Số lần nhắc", "Ví dụ"], None)
mm.cell(row=u0 + 1, column=1).fill = PatternFill(None)
for k, u in enumerate(D["stats"]["unlisted"]):
    r = u0 + 2 + k
    mm.cell(row=r, column=2, value=u["item"])
    mm.cell(row=r, column=3, value=u["customers"])
    mm.cell(row=r, column=4, value=u["mentions"])
    mm.cell(row=r, column=5, value=" | ".join(u["examples"]))
    for c in range(2, 6):
        mm.cell(row=r, column=c).font, mm.cell(row=r, column=c).border = f_input, box
t0 = u0 + 3 + len(D["stats"]["unlisted"])
mm.cell(row=t0, column=1, value="Nhịp buổi live — bình luận của khách mỗi 15 phút (bản cũ)").font = f_h2
header(mm, t0 + 1, ["", "Từ phút", "Bình luận khách"], None)
mm.cell(row=t0 + 1, column=1).fill = PatternFill(None)
for k, v in enumerate(D["stats"]["timeline"]):
    r = t0 + 2 + k
    mm.cell(row=r, column=2, value=k * 15 / 1440).number_format = "h:mm"
    mm.cell(row=r, column=3, value=v)
    for c in (2, 3):
        mm.cell(row=r, column=c).font, mm.cell(row=r, column=c).border = f_input, box

# ======================= LOI-BAN-CU =======================
lo = wb.create_sheet("LOI-BAN-CU")
lo["A1"] = "Bản cũ ('Chốt đơn live 17/09') sai hoặc thiếu gì — đối chiếu với sổ 'Live 17/9' và bảng 'CHECK GIÁ … / LIVE 17/9'"
lo["A1"].font = f_title
header(lo, 3, ["#", "Chỗ sai / thiếu", "Bằng chứng", "Hậu quả nếu giữ nguyên", "Đã sửa trong file này", "Còn cần"],
       [4, 38, 48, 38, 36, 30])
LOI = [
    ("Chấm 'Kiểm kho' bằng phỏng đoán (120 dòng), không có số tồn",
     "Sổ có số lượng (SL) từng size cho 28 mã-món",
     "Nhắn khách 'đang kiểm hàng' cho cả người chắc chắn có hàng",
     "Mỗi dòng có Tồn sổ + Cộng dồn → TRONG / VƯỢT TỒN (GOC-BINH-LUAN cột Q–U)", "—"),
    ("Không biết sổ đơn live 17/9 đã tồn tại; ghi 'chưa có sổ chốt đơn'",
     "Sổ 'Live 17/9' tạo 17/09 10:23, có tab ĐƠN OK (204 tên) và 29 tab mã",
     "377 khách bình luận không được đánh dấu ai đã lên đơn",
     "Cột 'Trong ĐƠN OK?' cho từng dòng và từng khách", "Màu ô trong ĐƠN OK (đơn huỷ/gấp/qua lấy) chưa đọc được"),
    ("M13 'Chân váy đen' (11 dòng) là món không có trong M13",
     "Tab M13 = 'áo sơmi ren trắng'; bảng giá LIVE 17/9 M13 chỉ có áo sơ mi C6K01TT019904",
     "Cầu chân váy M10 bị tách đôi → đếm thiếu nguy cơ vượt tồn",
     "QUY-DOI-MA quy về M10 Chân váy (có thể sửa)", "Quản lý xác nhận"),
    ("M15 'Áo mèo' (2 dòng) — M15 là áo khoác cổ kẻ nâu",
     "Tab M15; bản cũ tự ghi 'cùng mẫu áo mèo M08'",
     "Trừ nhầm tồn áo khoác", "QUY-DOI-MA quy về M08 Áo mèo", "—"),
    ("M06 'Chân váy nâu' và M14 'Chân váy' tính như 2 hàng khác nhau",
     "Bảng giá LIVE 17/9: cả hai cùng mã KiotViet T6K01SD019908",
     "33 chiếc đặt trên 1 kho chung — không ai thấy vượt",
     "Ghi trong MAU-MA (cả hai 'CẦN SỐ TỒN')", "Số tồn T6K01SD019908 từ KiotViet"),
    ("Món không có thật: M16 'Áo nâu', M26 'Quần 590'; M28 'Quần' đúng ra là chân váy kaki",
     "Tab M16 = set kẻ xanh (chỉ áo); M26 = áo khoác jean; M28 = áo nhung + chân váy kaki",
     "Tin nhắn gửi khách gọi sai tên món", "Ghi nhận; không có dòng đặt nào cho M16 áo nâu / M26 quần", "Sửa tên M28 trong mẫu tin"),
    ("Size không tồn tại vẫn niêm là 'có': Boot M03 size 28, Giày M05 size 29, Chân váy M10 size 1-2y",
     "Sổ M03 không có cột 28; M05 không có 29; bảng giá M10 chân váy 'từ 2-4y'",
     "Nhận đơn size không có", "Dòng đặt size không có → 'SIZE KHÔNG CÓ TRONG SỔ'", "—"),
    ("Quy đổi chiều cao → size dùng một bảng chung (140cm = 10-12y…)",
     "Mỗi mã một thang: M01 140 = 8-10, 160 = XS; M10 90 = 1-2, 150 = XS; M08 120 = '6-8 (hoặc 4-6)'",
     "254 dòng 'AI gợi ý size' có thể lệch 1 bậc với mã có thang riêng", "Chưa tự sửa size gợi ý (vẫn nhóm 'Hỏi lại khách')",
     "Bảng size theo từng mã (B2)"),
    ("Tính 150 quần M01 (91,5 triệu) như đơn chắc",
     "Tab M01: '* QUẦN VIẾT GIẤY' — quần không có trong sổ",
     "Không đối chiếu được phần tiền lớn nhất buổi", "Quần M01 → 'MÓN CHƯA CÓ TRONG SỔ'", "Ảnh/chép sổ giấy quần M01"),
    ("Áo mèo chấm bi (10 cái, không mã) không có chỗ trong sổ",
     "Sổ không có tab nào cho áo chấm bi",
     "10 đơn dễ rơi", "Nhóm 'MÃ KHÔNG CÓ TRONG SỔ'", "Hỏi ai giữ danh sách áo chấm bi"),
    ("Trang dài, 4 tab, không có cột 'kết quả' để ghi lại",
     "—", "Không đo được đã xử lý bao nhiêu", "KHACH có 4 cột nhập (kết quả, mã KiotViet, người, ghi chú)", "—"),
    ("Giá: KHÔNG sai", "0 dòng lệch giữa giá bản cũ và giá sổ trên các mã-món sổ có ghi", "—", "Cột 'Kiểm giá' giữ để kiểm các buổi sau", "—"),
]
for k, row in enumerate(LOI, start=1):
    r = 3 + k
    lo.cell(row=r, column=1, value=k)
    for j, v in enumerate(row, start=2):
        lo.cell(row=r, column=j, value=v)
style_body(lo, 4, 3 + len(LOI), 1, 6)
for r in range(4, 4 + len(LOI)):
    lo.row_dimensions[r].height = 54
    for c in range(1, 7):
        lo.cell(row=r, column=c).alignment = wrap
lo.freeze_panes = "B4"

# ======================= TOM-TAT =======================
tt = wb.create_sheet("TOM-TAT", 0)
tt.column_dimensions["A"].width = 3
tt.column_dimensions["B"].width = 58
tt.column_dimensions["C"].width = 16
tt.column_dimensions["D"].width = 16
tt.column_dimensions["E"].width = 60
tt["B1"] = "Đối soát live 17/09/2026 — tóm tắt 1 trang"
tt["B1"].font = f_title
tt["B3"] = "THAM SỐ (ô vàng, sửa được)"
tt["B3"].font = f_h2
PARAMS = [("Mã buổi", "LIVE-20260917", "Theo 02 §3"),
          ("Tính phần '+N' của sổ vào tồn? (1 = có, 0 = không)", 1, "Sổ ghi '6+2', '30+1'… — chưa rõ nghĩa, xem câu hỏi Q1"),
          ("Ngưỡng bán tốt (% tồn)", 0.6, "≥ ngưỡng → GIỮ / NHẬP THÊM"),
          ("Ngưỡng bán chậm (% tồn)", 0.2, "< ngưỡng và tồn lớn → KHÔNG NHẬP THÊM"),
          ("Tồn lớn (chiếc)", 30, ""),
          ("Hoạt động thấp (dòng đặt / 30 phút)", 50, "Giờ đầu buổi ≈ 300 dòng/30'; sau 3:15 < 40")]
for k, (lab, v, note) in enumerate(PARAMS):
    r = 4 + k
    tt.cell(row=r, column=2, value=lab).font = f_base
    c = tt.cell(row=r, column=3, value=v)
    c.font, c.fill, c.border = f_input, fill_input, box
    tt.cell(row=r, column=5, value=note or None).font = f_note
tt["C6"].number_format = PCT
tt["C7"].number_format = PCT

tt["B11"] = "SỐ LIỆU CHÍNH (tự tính)"
tt["B11"].font = f_h2
header_cells = ["Chỉ số", "Số", "Tiền (VNĐ)", "Đọc thế nào"]
for j, h in enumerate(header_cells, start=2):
    c = tt.cell(row=12, column=j, value=h)
    c.font, c.fill, c.border = f_head, fill_head, box
KPI = [
    ("Bình luận đọc được / Facebook báo", f"=\"{D['stats']['comments']:,} / {D['stats']['fb_total']:,}\"".replace(",", "."), None,
     "Thiếu 3%; đơn qua inbox và người dẫn đọc tên không có ở đây"),
    ("Dòng đặt từ bình luận (không tính dòng huỷ)", f"=COUNTA({blc('J')})-COUNTIF({blc('J')},\"Có thể đã huỷ\")",
     f"=SUMIFS({blc('T')},{blc('J')},\"<>Có thể đã huỷ\")", "Giá trị đặt, chưa phải doanh thu"),
    ("  → trong tồn sổ", f"=COUNTIF({blc('U')},\"TRONG TỒN\")", f"=SUMIFS({blc('T')},{blc('U')},\"TRONG TỒN\")", "Có hàng theo thứ tự bình luận"),
    ("  → vượt tồn sổ", f"=COUNTIF({blc('U')},\"VƯỢT TỒN\")", f"=SUMIFS({blc('T')},{blc('U')},\"VƯỢT TỒN\")", "Đặt sau khi size đã đủ người"),
    ("  → chưa kiểm được (sổ không ghi món / size / mã, hoặc thiếu size)", f"=COUNTA({blc('U')})-COUNTIF({blc('U')},\"TRONG TỒN\")-COUNTIF({blc('U')},\"VƯỢT TỒN\")-COUNTIF({blc('U')},\"HUỶ\")",
     f"=SUMIFS({blc('T')},{blc('J')},\"<>Có thể đã huỷ\")-D15-D16",
     "Chủ yếu quần M01 (ghi giấy), chân váy + áo giữ nhiệt M10"),
    ("Dòng 'Kiểm kho' của bản cũ nay đã có kết luận", f"=COUNTIFS({blc('J')},\"Kiểm kho\",{blc('U')},\"TRONG TỒN\")+COUNTIFS({blc('J')},\"Kiểm kho\",{blc('U')},\"VƯỢT TỒN\")",
     None, "Còn lại là món sổ không ghi"),
    ("Size-ô bị đặt vượt tồn", f"=SUM({tsc('L')})", None, "Xem TON-SIZE, lọc 'VƯỢT'"),
    ("Giá lệch giữa bản cũ và sổ", f"=COUNTIF({blc('V')},\"LỆCH\")", None, "0 = giá bản cũ đúng với sổ"),
    ("Khách có dòng đặt (bình luận)", f"=COUNTIFS({khc('C')},\"Bình luận\",{khc('E')},\">0\")", None, ""),
    ("Tên trong ĐƠN OK (sau làm sạch, không trùng)", f"=SUMPRODUCT(('GOC-DON-OK'!$C$2:$C$500<>\"\")/COUNTIF('GOC-DON-OK'!$C$2:$C$500,'GOC-DON-OK'!$C$2:$C$500&\"\"))",
     None, "204 dòng gốc; màu ô (đơn huỷ…) chưa đọc được"),
    ("  → khớp tên với khách bình luận", f"=COUNTIFS({khc('C')},\"Bình luận\",{khc('J')},\"CÓ\")", None, "Khớp đúng chữ; tên trùng cần KiotViet xác nhận"),
    ("  → chỉ có ở ĐƠN OK (không thấy bình luận)", f"=COUNTIF({khc('C')},\"Chỉ có ở ĐƠN OK\")", None, "Đơn qua inbox / đọc tên / viết khác tên"),
    ("Khách bình luận có hàng nhưng CHƯA thấy ở ĐƠN OK", f"=COUNTIF({khc('M')},\"CHƯA LÊN ĐƠN – CÓ HÀNG\")",
     f"=SUMIFS({khc('F')},{khc('M')},\"CHƯA LÊN ĐƠN – CÓ HÀNG\")", "Vùng dò đơn sót / đơn huỷ — ưu tiên 1"),
    ("Khách đã lên đơn nhưng có dòng vượt tồn", f"=COUNTIF({khc('M')},\"ĐÃ LÊN ĐƠN – CÓ DÒNG VƯỢT TỒN\")",
     f"=SUMIFS({khc('G')},{khc('M')},\"ĐÃ LÊN ĐƠN – CÓ DÒNG VƯỢT TỒN\")", "Kiểm KiotViet: size đó có thật được giao?"),
]
for k, (lab, n, money, note) in enumerate(KPI):
    r = 13 + k
    tt.cell(row=r, column=2, value=lab)
    tt.cell(row=r, column=3, value=n)
    tt.cell(row=r, column=4, value=money)
    tt.cell(row=r, column=5, value=note or None)
    for c in range(2, 6):
        cell = tt.cell(row=r, column=c)
        cell.border = box
        cell.font = f_base if c != 5 else f_note
    tt.cell(row=r, column=3).fill = fill_calc
    tt.cell(row=r, column=4).fill = fill_calc
    tt.cell(row=r, column=3).number_format = MONEY
    tt.cell(row=r, column=4).number_format = MONEY
tt["C13"].fill = PatternFill(None)
tt["C13"].font = f_input

a0 = 13 + len(KPI) + 1
tt.cell(row=a0, column=2, value="VIỆC LÀM NGAY (theo thứ tự)").font = f_h2
ACT = [
    (f"=\"1. Dò \"&C25&\" khách có hàng nhưng chưa ở ĐƠN OK (\"&SUBSTITUTE(TEXT(D25,\"#,##0\"),\",\",\".\")&\"đ): KHACH, lọc Ưu tiên = 1\"",
     "B5 + người trực inbox · hạn 28/09"),
    (f"=\"2. Mở KiotViet \"&C26&\" khách đã lên đơn mà có dòng vượt tồn — xem size đó có bị bán quá sổ\"", "B10 + B16 · 28/09"),
    ("3. Chép sổ giấy quần M01 + số tồn chân váy/áo giữ nhiệt M10, chân váy M08/M14 vào GOC-SO-TON → file tự tính lại",
     "Người ghi sổ live · 29/09"),
    ("4. Xác nhận 2 dòng ở QUY-DOI-MA và nghĩa '+N' (tham số C5)", "Quản lý · 27/09"),
    ("5. Buổi sau: đưa M21, M29 lên đầu buổi; không nhập thêm M04, M05; nhập đúng size vượt (M01 S, M10 1-2/4-6, M11 4-6)",
     "B7 + B15 · trước live kế tiếp"),
]
for k, (txt, owner) in enumerate(ACT):
    r = a0 + 1 + k
    tt.cell(row=r, column=2, value=txt).font = f_base
    tt.cell(row=r, column=5, value=owner).font = f_note
    tt.cell(row=r, column=2).alignment = wrap
    tt.row_dimensions[r].height = 28
tt.freeze_panes = "A3"

# ======================= DOC-TRUOC =======================
dt = wb.create_sheet("DOC-TRUOC", 0)
dt.column_dimensions["A"].width = 16
dt.column_dimensions["B"].width = 26
dt.column_dimensions["C"].width = 90
fname = OUT.split("/")[-1]
A = [
    f"Tên file: {fname}",
    "Mục đích: trả lời 'buổi live 17/09 còn ai chưa lên đơn, size nào bán quá sổ, mẫu nào nên nhập thêm / dừng?'",
    "Nguồn: (1) phiếu bình luận của bản 'Chốt đơn live 17/09' — 2.028/2.096 bình luận; (2) sổ 'Live 17/9' (Google Sheet): tab ĐƠN OK + dòng SL/giá của 29 tab mã; (3) 'CHECK GIÁ PAGE + LIVE TĐ 2026' tab LIVE 17/9: mã KiotViet",
    "Khoảng thời gian: buổi live 2026-09-17 12:03 → ≈17:07 (bình luận muộn tới 2026-09-20)",
    "Trích xuất lúc: 2026-09-26 (sổ sửa lần cuối 2026-09-25 17:07; bảng giá 2026-09-25 10:31)",
    "Người lập: NV4-B12 (agent)",
    "Đơn vị tiền tệ: VNĐ",
    "BẢN SAO phân tích — nguồn chân lý vẫn là sổ 'Live 17/9' và KiotViet. Hai Google Sheet gốc KHÔNG bị sửa. Có tên Facebook khách: không chia sẻ link công khai.",
    "Giải thích sheet và cột: bảng dưới",
]
for k, v in enumerate(A, start=1):
    c = dt.cell(row=k, column=1, value=v)
    c.font = f_bold if k in (1, 8) else f_base
header(dt, 11, ["Sheet", "Dùng để", "Cột chính · kiểu"])
SHEETS = [
    ("TOM-TAT", "1 trang: tham số, số chính, 5 việc", "Ô vàng = tham số sửa được; ô xanh nhạt = công thức"),
    ("KHACH", "Mỗi khách 1 dòng + việc cần làm", "Trạng thái/Việc/Ưu tiên tự tính · P–S là ô nhập (kết quả, mã đơn KiotViet — dạng chữ)"),
    ("TON-SIZE", "Mỗi size của mỗi mã 1 dòng: tồn ↔ cầu", "Tình trạng: VƯỢT n / SẮP HẾT / CÒN n / 0 ĐƠN · dòng tổng dùng SUBTOTAL"),
    ("MAU-MA", "Quyết định mẫu: nhập thêm / giữ / dừng", "% bán = bán được ÷ tồn · Hoạt động lúc lên = độ đông người xem"),
    ("LOI-BAN-CU", "Bản cũ sai gì, đã sửa gì", "12 dòng"),
    ("GOC-BINH-LUAN", "1.020 dòng đặt từ bình luận (gốc A–M) + cột tính N–X", "Giờ = [h]:mm:ss · tiền = số · ID bình luận = chữ"),
    ("GOC-SO-TON", "Tồn + giá chép từ 29 tab mã của sổ", "Mỗi cột size của sổ 1 dòng; cột sổ gộp 2 size (vd M01 110 = 1-2 và 2-4) có 2 'size khách gọi'"),
    ("GOC-DON-OK", "204 tên trong tab ĐƠN OK", "Cột C = tên đã bỏ đuôi 'gấp'/'x2' để so; tên gốc giữ ở cột B"),
    ("QUY-DOI-MA", "Sửa mã/món bình luận ghi sai", "Thêm dòng → toàn file tính lại"),
]
for k, row in enumerate(SHEETS, start=12):
    for j, v in enumerate(row, start=1):
        c = dt.cell(row=k, column=j, value=v)
        c.font, c.border, c.alignment = f_base, box, wrap
g0 = 12 + len(SHEETS) + 1
dt.cell(row=g0, column=1, value="Giới hạn — đọc trước khi dùng số").font = f_h2
LIM = [
    "Chưa đọc được danh sách tên khách trong 29 tab mã của sổ (Drive chặn xuất file > 10 MB, chỉ trả 10 dòng đầu mỗi tab) → 'trong/vượt tồn' từng khách xếp theo giờ bình luận. Kiểm mẫu 23 tên đầu tab M10 (áo ghi lê): 18/23 có dòng đặt cùng size trong bình luận, chỉ 14/23 thuộc nhóm đặt sớm nhất → kết luận từng khách là ước lượng; TỔNG vượt theo size đáng tin hơn.",
    f"=\"2. Sổ chỉ ghi SL cho món chính của mỗi tab: \"&COUNTIF({blc('U')},\"MÓN CHƯA CÓ TRONG SỔ\")&\" dòng (≈\"&ROUND(SUMIFS({blc('T')},{blc('U')},\"MÓN CHƯA CÓ TRONG SỔ\")/1000000,0)&\" triệu) thuộc món sổ không ghi — lớn nhất là quần M01 (sổ ghi 'QUẦN VIẾT GIẤY').\"",
    "ĐƠN OK so bằng tên Facebook đúng chữ; 14 tên hiển thị thuộc ≥ 2 tài khoản khác nhau — cột 'Tên trùng?' đánh dấu. Màu ô (đơn huỷ/gấp/qua lấy/khách HP) chưa đọc được.",
    "Bình luận chỉ thấy khoảng 2/3 giá trị đơn thật (số của B10 trên buổi 8-9/9) — 'Cầu' ở đây là cận dưới.",
    "Chưa mở KiotViet: mọi kết luận 'sót/huỷ' phải qua bước tra KiotViet ở cột 'Việc cần làm'.",
]
for k, v in enumerate(LIM, start=1):
    c = dt.cell(row=g0 + k, column=1, value=v if v.startswith("=") else f"{k}. {v}")
    c.font = f_base
q0 = g0 + len(LIM) + 2
dt.cell(row=q0, column=1, value="Câu hỏi cần Quản lý trả lời (đổi kết quả tính)").font = f_h2
QS = [
    "Q1. Số '+N' trong sổ (vd '6+2', '30+1', '10 + 1 … đổi về') là gì: hàng khách đổi về, hàng ở kho khác, hay hàng sắp về? → tham số TOM-TAT!C5.",
    "Q2. M13 'chân váy đen' có phải chân váy M10 (C6K01SD019905) không? → QUY-DOI-MA dòng 3.",
    "Q3. Quần M01 'viết giấy' — ai giữ tờ giấy? Chép vào GOC-SO-TON là file tự tính lại 150 dòng quần.",
    "Q4. Màu ô trong tab ĐƠN OK: tên nào là ĐƠN HỦY? (hoặc cho 1 cột chữ thay màu).",
    "Q5. Cho B12 tài khoản KiotViet chỉ xem để tự đối chiếu 'CHƯA LÊN ĐƠN' được không?",
]
for k, v in enumerate(QS, start=1):
    dt.cell(row=q0 + k, column=1, value=v).font = f_base
dt.freeze_panes = "A10"

# thứ tự sheet
order = ["DOC-TRUOC", "TOM-TAT", "KHACH", "TON-SIZE", "MAU-MA", "LOI-BAN-CU", "GOC-BINH-LUAN", "GOC-SO-TON", "GOC-DON-OK", "QUY-DOI-MA"]
wb._sheets = [wb[n] for n in order]
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 100
wb["DOC-TRUOC"].sheet_properties.tabColor = "2F6B54"
wb["TOM-TAT"].sheet_properties.tabColor = "2F6B54"
for n in ("KHACH", "TON-SIZE", "MAU-MA"):
    wb[n].sheet_properties.tabColor = "A75A16"
for n in ("GOC-BINH-LUAN", "GOC-SO-TON", "GOC-DON-OK", "QUY-DOI-MA"):
    wb[n].sheet_properties.tabColor = "808080"
wb.active = 1
wb.save(OUT)
print("saved", OUT, "rows BL", N_BL - 1, "SO", N_SO - 1, "OK", N_OK - 1, "KH", N_KH - 1, "MAU", len(all_items))
