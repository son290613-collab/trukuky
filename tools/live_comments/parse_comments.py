"""Tổng hợp bình luận một buổi live thành phiếu chốt đơn.

Chạy:
    python parse_comments.py <binh_luan.csv> <thu_muc_ra>
    python parse_comments.py --selftest

Vào: file CSV xuất từ sổ bình luận live (xem README, mục "Cách lấy bình luận").
Cột bắt buộc (nhận cả tên tiếng Việt lẫn tiếng Anh, không phân biệt dấu/hoa thường):
    Phút trong video · Người bình luận · Nội dung bình luận
Cột tuỳ chọn: Trang cá nhân · Có ghi mã? · Là shop niêm yết?

Ra (trong <thu_muc_ra>):
    binh_luan_phan_loai.csv   mỗi bình luận một dòng, kèm phân loại và thứ đọc được
    chot_don_theo_khach.csv   mỗi khách × mã × món × size một dòng, cột trống để nhân viên xác nhận
    nhu_cau_theo_ma_size.csv  cầu theo mã và size: đặt, hỏi còn, hỏi giá
    can_hoi_lai.csv           khách hỏi mà chưa thấy đặt, và dòng đặt thiếu size
    tom_tat.json              số tổng hợp để đưa lên báo cáo

Nguyên tắc: công cụ KHÔNG đoán thay người.
- Bình luận ghi rõ mã + size  -> do_tin = "chac".
- Bình luận chỉ có size, mã lấy theo mã được nhắc gần nhất trước đó -> "suy-luan" (phải người xác nhận).
- Cân nặng và chiều cao KHÔNG tự quy ra size (bảng quy đổi của shop chưa được xác nhận):
  ghi nguyên văn và gắn cờ "can-quy-doi".
File ra có tên khách: không commit, không chia sẻ link công khai.
"""
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

# ---------- chuẩn hoá chữ ----------

def bo_dau(s):
    """Bỏ dấu, hạ chữ thường: dùng để so tên cột và dò từ khoá."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower().strip()


COT = {
    "phut": ["phut trong video", "phut", "thoi gian", "time", "minute"],
    "nguoi": ["nguoi binh luan", "khach", "ten khach", "commenter", "author", "name"],
    "trang": ["trang ca nhan", "link", "profile", "profile url"],
    "noidung": ["noi dung binh luan", "noi dung", "binh luan", "comment", "message", "text"],
    "coma": ["co ghi ma?", "co ghi ma", "ma"],
    "niemyet": ["la shop niem yet?", "la shop niem yet", "shop niem yet", "niem yet"],
}


def do_cot(fieldnames):
    """Ghép tên cột thật của file với các khoá bên trong."""
    tim = {}
    for khoa, ten in COT.items():
        for f in fieldnames or []:
            if bo_dau(f) in ten:
                tim[khoa] = f
                break
    thieu = [k for k in ("phut", "nguoi", "noidung") if k not in tim]
    if thieu:
        raise SystemExit(
            "Thiếu cột bắt buộc: %s. Cột đang có: %s"
            % (", ".join(thieu), ", ".join(fieldnames or []))
        )
    return tim


def giay(s):
    """'03:21' hoặc '1:03:21' -> số giây. Không đọc được thì None."""
    s = (s or "").strip()
    if not re.fullmatch(r"\d{1,2}(:\d{1,2}){1,2}", s):
        return None
    p = [int(x) for x in s.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return p[0] * 3600 + p[1] * 60 + p[2]


def mmss(g):
    if g is None:
        return ""
    return "%02d:%02d:%02d" % (g // 3600, g % 3600 // 60, g % 60)


# ---------- từ khoá ----------

TU_GIA = ("gia", "bao nhieu", "bn ", " bn", "bnhieu", "nhieu tien", "xin gia", "giá")
TU_CON = ("con khong", "con ko", "con k", "con size", "con ko a", "het chua", "con hang")
TU_HOI_SIZE = ("size gi", "size nao", "sz gi", "lay size gi", "mac size", "vua k", "vua ko", "co vua")
TU_DAT = ("lay", "chot", "dat", "order", "mua", "minh lay", "e lay", "cho e", "cho minh", "co e")
TU_IB = ("ib", "inbox", "nhan tin", "nhan rieng", "zalo")
TU_NGOAI = ("thuoc nho mat", "nho mat", "thuoc mat")
TU_DOI = ("doi size", "doi sang", "doi lai", "cho e doi", "đổi")
TU_HUY = ("huy don", "khong lay nua", "thoi khong lay", "bo don")
TU_SHIP = ("ship", "dia chi", "gui hang", "cod", "chuyen khoan", "coc")

MON = [
    ("set", ("ca set", "nguyen set", "set ", " set", "sét", "bo ", "3 mon", "2 mon")),
    ("áo khoác", ("ao khoac", "khoac", "ao bo", "ao jean", "jean")),
    ("áo", ("ao ",)),
    ("quần", ("quan ", "quan loe", "quan chip", "chan vay")),
    ("váy", ("vay ", "dam", "đầm")),
    ("boot/giày", ("boot", "bot ", "giay", "sandal", "sneaker")),
    ("phụ kiện", ("vong co", "vong tay", "tui", "mu ", "non ", "kep", "chun toc",
                  "cot toc", "cai toc", "bang do", "tat ", "hop chun", "hop ")),
    ("đồ ngủ", ("do ngu", "set ngu", "bo ngu", "pijama", "pyjama")),
]

# cỡ chữ của mẹ
CO_CHU = r"(?:XXL|XL|XS|S|M|L)"

# Dòng chỉ có size được gán mã nhắc gần nhất trong vòng bao nhiêu giây.
GIOI_HAN_SUY_LUAN = 120


def co_mon(t):
    """Đoán tên món trong câu; trả về danh sách (có thể rỗng)."""
    ra = []
    for ten, keys in MON:
        if any(k in t for k in keys):
            ra.append(ten)
    return ra


# ---------- đọc mã và size ----------

RE_MA = re.compile(r"(?<![\dA-Za-z])[Mm]\s?(\d{1,2})(?![\d])")
RE_MA_CHU = re.compile(r"(?i)\bm[ãa]\s*(\d{1,2})\b")


def doc_ma(goc):
    """Các mã live Mxx trong câu, theo thứ tự xuất hiện, không trùng.

    Bỏ qua trường hợp '1m32' (chiều cao) và 'sz M' (cỡ chữ) vì đã chặn bằng
    điều kiện trước/sau của biểu thức.
    """
    ra = []
    for m in list(RE_MA.finditer(goc)) + list(RE_MA_CHU.finditer(goc)):
        so = int(m.group(1))
        if 1 <= so <= 60:
            ma = "M%02d" % so
            if ma not in ra:
                ra.append(ma)
    return ra


RE_KG = re.compile(r"(?i)(\d{1,3})(?:[.,](\d))?\s*(kg|ki\b|kilo|can\b|cân)")
RE_CM = re.compile(r"(?i)(\d{2,3})\s*cm\b")
RE_M_CM = re.compile(r"(?i)\b1\s?m\s?(\d{2})\b")
RE_TUOI = re.compile(r"(?i)\b(\d{1,2})\s*[-–/]\s*(\d{1,2})\s*(?:y|t|tuoi|tuổi)?\b")
RE_TUOI_DON = re.compile(r"(?i)\b(\d{1,2})\s*(?:y\b|tuoi|tuổi)")
RE_CHIEU_CAO = re.compile(r"(?i)(?<![\d,.])(9\d|1[0-5]\d)(?![\d,.])\s*(?:cm)?")
RE_GIAY = re.compile(r"(?i)\b(2[5-9]|3\d|40)\b")
RE_CO_CHU = re.compile(r"(?i)(?:^|[\s(|/+,-]|(?<=\d))(?:sz|size|cỡ|co)?\s*(XXL|XL|XS|S|L)(?=$|[\s)|/+.,-])")
RE_CO_M = re.compile(r"(?i)(?:sz|size|cỡ)\s*M(?=$|[\s)|/+.,-])")
RE_SL = re.compile(r"(?i)\b(?:x\s?(\d)|(\d)\s*(?:cai|chiec|bo|set|đôi|doi)\b)")


def doc_size(goc, t, co_giay, co_me):
    """Trả về (danh sách size đọc được, cờ cần quy đổi, ghi chú).

    Mỗi size là chuỗi để nguyên cách khách gọi: '6-8y', '130cm', '19kg', 'M'.
    """
    sizes, can_quy, chu_thich = [], False, []

    for m in RE_KG.finditer(goc):
        so = m.group(1) + ("," + m.group(2) if m.group(2) else "")
        sizes.append(so + "kg")
        can_quy = True
    for m in RE_M_CM.finditer(goc):
        sizes.append("1m" + m.group(1))
        can_quy = True
    for m in RE_CM.finditer(goc):
        sizes.append(m.group(1) + "cm")
        can_quy = True

    for m in RE_TUOI.finditer(goc):
        a, b = int(m.group(1)), int(m.group(2))
        if 0 < a < b <= 16:                      # 6-8, 8/10, 10-12
            sizes.append("%d-%dy" % (a, b))
    for m in RE_TUOI_DON.finditer(goc):
        sizes.append(m.group(1) + "y")

    if co_giay and not sizes:
        for m in RE_GIAY.finditer(goc):
            sizes.append("sz" + m.group(1))

    for m in RE_CO_CHU.finditer(goc):
        sizes.append(m.group(1).upper())
    if RE_CO_M.search(goc) or (co_me and re.search(r"(?i)\bM\b", goc) and not RE_MA.search(goc)):
        sizes.append("M")

    if not sizes:
        for m in RE_CHIEU_CAO.finditer(goc):     # '130' trần, '110' trần
            sizes.append(m.group(1) + "cm")
            can_quy = True
            chu_thich.append("số trần, đoán là chiều cao")

    # bỏ trùng, giữ thứ tự
    gon = []
    for s in sizes:
        if s not in gon:
            gon.append(s)
    return gon, can_quy, "; ".join(chu_thich)


def doc_sl(goc):
    m = RE_SL.search(goc)
    if not m:
        return 1
    so = m.group(1) or m.group(2)
    try:
        n = int(so)
    except (TypeError, ValueError):
        return 1
    return n if 1 <= n <= 9 else 1


# ---------- phân loại ----------

def phan_loai(t, ma, sizes, mons=(), sl=1):
    """Nhãn ý định của bình luận. Một bình luận chỉ nhận một nhãn chính."""
    if any(k in t for k in TU_NGOAI):
        return "ngoai-pham-vi"
    if any(k in t for k in TU_HUY):
        return "huy"
    if any(k in t for k in TU_DOI):
        return "doi"
    if any(k in t for k in TU_HOI_SIZE):
        return "hoi-size"
    if any(k in t for k in TU_GIA):
        return "hoi-gia"
    if any(k in t for k in TU_CON):
        return "hoi-con"
    co_dat = any(k in t for k in TU_DAT)
    if co_dat and (ma or sizes):
        return "dat"
    if ma and sizes:
        return "dat"                   # kiểu 'M21 33', 'M22 sz 4-6'
    if sizes and not ma:
        return "dat-thieu-ma"
    if ma and not sizes:
        return "dat-thieu-size"
    if any(k in t for k in TU_SHIP):
        return "ship"
    if any(k in t for k in TU_IB):
        return "ib"
    if mons and (sl > 1 or re.match(r"\s*\d", t)):
        return "dat-thieu-size"      # có món và số lượng nhưng máy không đọc được size
    return "khac"


# ---------- xử lý một file ----------

def xu_ly(duong_vao, thu_muc_ra, ten_shop=None):
    with open(duong_vao, newline="", encoding="utf-8-sig") as f:
        doc = csv.DictReader(f)
        cot = do_cot(doc.fieldnames)
        dong = list(doc)

    # --- lượt đọc 1: tách mã và tên món, chưa đọc size ---
    ds = []
    for i, r in enumerate(dong, 1):
        goc = (r.get(cot["noidung"]) or "").strip()
        nguoi = (r.get(cot["nguoi"]) or "").strip()
        g = giay(r.get(cot["phut"]))
        t = bo_dau(goc)
        la_shop = False
        if "niemyet" in cot:
            la_shop = bo_dau(r.get(cot["niemyet"]) or "") in ("x", "co", "yes", "true", "1")
        if ten_shop and bo_dau(nguoi) == bo_dau(ten_shop):
            la_shop = True
        ds.append({
            "stt": i, "giay": g, "nguoi": nguoi,
            "trang": (r.get(cot.get("trang", "")) or "").strip() if "trang" in cot else "",
            "goc": goc, "t": t, "la_shop": la_shop,
            "ma": doc_ma(goc), "mon": co_mon(t),
        })

    # --- mốc thời gian của từng mã: dùng để gán mã cho dòng chỉ có size ---
    moc_shop = sorted((d["giay"], d["ma"][0]) for d in ds
                      if d["la_shop"] and d["ma"] and d["giay"] is not None)
    moc_tatca = sorted((d["giay"], d["ma"][0]) for d in ds if d["ma"] and d["giay"] is not None)
    moc = moc_shop if len(moc_shop) >= 5 else moc_tatca
    nguon_moc = "shop niêm yết" if moc is moc_shop else "mọi bình luận có mã"

    def ma_gan_nhat(g):
        if g is None:
            return None, None
        chon = None
        for mg, ma in moc:
            if mg <= g:
                chon = (mg, ma)
            else:
                break
        if not chon:
            return None, None
        return chon[1], g - chon[0]

    for d in ds:
        d["ma_suy_luan"], d["cach_giay"] = (None, None)
        if not d["ma"]:
            ma, cach = ma_gan_nhat(d["giay"])
            if ma is not None and cach is not None:
                d["ma_suy_luan"], d["cach_giay"] = ma, cach

    # --- tự đo quy tắc suy luận: với bình luận khách CÓ ghi rõ mã, mốc gần nhất
    # có trùng mã khách ghi không? Tỷ lệ này là độ tin của các dòng "suy-luan". ---
    trung = lech = 0
    for d in ds:
        if d["la_shop"] or not d["ma"] or d["giay"] is None:
            continue
        ma, cach = ma_gan_nhat(d["giay"])
        if ma is None or cach > GIOI_HAN_SUY_LUAN:
            continue
        if ma == d["ma"][0]:
            trung += 1
        else:
            lech += 1
    do_chinh_xac = round(trung / (trung + lech) * 100, 1) if (trung + lech) else None

    # --- món của từng mã: lời niêm yết của shop nặng hơn lời khách ---
    mon_cua_ma = defaultdict(Counter)
    for d in ds:
        for ma in d["ma"]:
            for mon in d["mon"]:
                mon_cua_ma[ma][mon] += 5 if d["la_shop"] else 1
    mon_chinh = {ma: c.most_common(1)[0][0] for ma, c in mon_cua_ma.items()}

    # --- lượt đọc 2: đọc size (biết mã bán giày hay không) rồi phân loại ---
    for d in ds:
        ma_hieu_luc = d["ma"][0] if d["ma"] else d["ma_suy_luan"]
        mon_ma = mon_chinh.get(ma_hieu_luc or "", "")
        co_giay = ("boot/giày" in d["mon"]) or mon_ma == "boot/giày"
        co_me = ("me" in d["t"] or "mẹ" in d["goc"] or "size" in d["t"] or "sz" in d["t"])
        sizes, can_quy, chu = doc_size(d["goc"], d["t"], co_giay=co_giay, co_me=co_me)
        d.update({
            "size": sizes, "can_quy": can_quy, "chu": chu, "sl": doc_sl(d["goc"]),
            "nhan": "niem-yet" if d["la_shop"] else phan_loai(d["t"], d["ma"], sizes, d["mon"], doc_sl(d["goc"])),
        })
        if d["nhan"] not in ("dat", "dat-thieu-ma", "dat-thieu-size", "hoi-con",
                             "hoi-size", "hoi-gia", "doi", "huy"):
            d["ma_suy_luan"], d["cach_giay"] = None, None   # chỉ suy luận khi có ích

    # --- dòng đặt: mỗi khách × mã × món × size ---
    don = defaultdict(lambda: {"sl": 0, "stt": [], "giay": None, "goc": [], "do_tin": "chac",
                               "can_quy": False, "chu": set()})
    for d in ds:
        if d["nhan"] not in ("dat", "dat-thieu-ma", "dat-thieu-size"):
            continue
        ma = d["ma"][0] if d["ma"] else d["ma_suy_luan"]
        if d["ma"]:
            do_tin = "chac"
        elif ma and d["cach_giay"] is not None and d["cach_giay"] <= GIOI_HAN_SUY_LUAN:
            do_tin = "suy-luan"
        elif ma:
            do_tin = "suy-luan-yeu"
        else:
            do_tin = "khong-ro-ma"
        if not d["size"]:
            do_tin = "thieu-size" if do_tin == "chac" else do_tin
        mon = d["mon"][0] if d["mon"] else ""
        for size in (d["size"] or [""]):
            k = (d["nguoi"], ma or "", mon, size)
            o = don[k]
            o["sl"] += d["sl"]
            o["stt"].append(d["stt"])
            o["goc"].append(d["goc"])
            o["can_quy"] = o["can_quy"] or d["can_quy"]
            if d["chu"]:
                o["chu"].add(d["chu"])
            if o["giay"] is None or (d["giay"] is not None and d["giay"] < o["giay"]):
                o["giay"] = d["giay"]
            muc = {"chac": 0, "suy-luan": 1, "thieu-size": 1, "suy-luan-yeu": 2,
                   "khong-ro-ma": 3}
            if muc.get(do_tin, 3) > muc.get(o["do_tin"], 0):
                o["do_tin"] = do_tin

    os.makedirs(thu_muc_ra, exist_ok=True)

    def ghi(ten, cols, rows):
        with open(os.path.join(thu_muc_ra, ten), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)

    ghi("binh_luan_phan_loai.csv",
        ["STT", "Thời điểm", "Người bình luận", "Nội dung", "Nhãn", "Mã ghi rõ",
         "Mã suy luận", "Cách mã (giây)", "Món", "Size đọc được", "SL", "Cần quy đổi", "Ghi chú"],
        [[d["stt"], mmss(d["giay"]), d["nguoi"], d["goc"], d["nhan"], " ".join(d["ma"]),
          d["ma_suy_luan"] or "", d["cach_giay"] if d["cach_giay"] is not None else "",
          " ".join(d["mon"]), " ".join(d["size"]), d["sl"],
          "x" if d["can_quy"] else "", d["chu"]] for d in ds])

    don_rows = []
    for (nguoi, ma, mon, size), o in sorted(don.items(), key=lambda kv: (kv[1]["giay"] or 0, kv[0][0])):
        don_rows.append([mmss(o["giay"]), nguoi, ma, mon, size, o["sl"], o["do_tin"],
                         "x" if o["can_quy"] else "", " ".join(str(s) for s in o["stt"]),
                         " || ".join(o["goc"])[:500], "; ".join(sorted(o["chu"])), "", "", ""])
    ghi("chot_don_theo_khach.csv",
        ["Thời điểm", "Người bình luận", "Mã", "Món", "Size khách gọi", "SL", "Độ tin",
         "Cần quy đổi size", "STT bình luận", "Nguyên văn", "Ghi chú máy",
         "Size chốt (nhân viên điền)", "Có trong KiotViet? (điền)", "Kết quả (điền)"],
        don_rows)

    CHUA_RO = "(chưa rõ mã)"
    cau = defaultdict(Counter)
    for (nguoi, ma, mon, size), o in don.items():
        cau[(ma or CHUA_RO, size)]["dat"] += o["sl"]
        cau[(ma or CHUA_RO, size)]["khach"] += 1
    for d in ds:
        if d["nhan"] not in ("hoi-con", "hoi-gia", "hoi-size"):
            continue
        ma = (d["ma"][0] if d["ma"] else d["ma_suy_luan"]) or CHUA_RO
        for size in (d["size"] or [""]):
            cau[(ma, size)][d["nhan"]] += 1
    ghi("nhu_cau_theo_ma_size.csv",
        ["Mã", "Size khách gọi", "Số chiếc đặt", "Số khách đặt", "Hỏi còn", "Hỏi giá", "Hỏi size"],
        [[ma, size, c["dat"], c["khach"], c["hoi-con"], c["hoi-gia"], c["hoi-size"]]
         for (ma, size), c in sorted(cau.items(),
                                     key=lambda kv: (kv[0][0] == CHUA_RO, -kv[1]["dat"], kv[0]))])

    nguoi_dat = {k[0] for k in don}
    hoi_rows = []
    for d in ds:
        if d["nhan"] in ("hoi-gia", "hoi-con", "hoi-size") and d["nguoi"] not in nguoi_dat:
            hoi_rows.append([mmss(d["giay"]), d["nguoi"], d["nhan"],
                             d["ma"][0] if d["ma"] else (d["ma_suy_luan"] or ""),
                             "chac" if d["ma"] else ("suy-luan" if d["ma_suy_luan"] else ""),
                             " ".join(d["size"]), d["goc"], d["trang"], "", ""])
    ghi("can_hoi_lai.csv",
        ["Thời điểm", "Người bình luận", "Hỏi gì", "Mã", "Độ tin mã", "Size nói tới",
         "Nguyên văn", "Trang cá nhân", "Đã nhắn lại? (điền)", "Kết quả (điền)"],
        hoi_rows)

    dem_nhan = Counter(d["nhan"] for d in ds)
    tom = {
        "file_vao": os.path.basename(duong_vao),
        "so_binh_luan": len(ds),
        "so_nguoi_binh_luan": len({d["nguoi"] for d in ds if d["nguoi"]}),
        "theo_nhan": dict(sorted(dem_nhan.items(), key=lambda kv: -kv[1])),
        "so_dong_dat": len(don_rows),
        "so_chiec_dat": sum(r[5] for r in don_rows),
        "so_khach_dat": len(nguoi_dat),
        "do_tin": dict(Counter(r[6] for r in don_rows)),
        "dong_can_quy_doi_size": sum(1 for r in don_rows if r[7] == "x"),
        "so_ma_duoc_nhac": len({m for d in ds for m in d["ma"]}),
        "moc_ma_lay_tu": nguon_moc,
        "so_moc_ma": len(moc),
        "suy_luan_do_chinh_xac_phan_tram": do_chinh_xac,
        "suy_luan_do_tren_bao_nhieu_dong": trung + lech,
        "suy_luan_cua_so_giay": GIOI_HAN_SUY_LUAN,
        "khach_hoi_ma_khong_thay_dat": len({r[1] for r in hoi_rows}),
        "khong_doc_duoc_thoi_diem": sum(1 for d in ds if d["giay"] is None),
    }
    with open(os.path.join(thu_muc_ra, "tom_tat.json"), "w", encoding="utf-8") as f:
        json.dump(tom, f, ensure_ascii=False, indent=1)
    return tom


# ---------- tự kiểm ----------

MAU = [
    ("00:10", "Shop Trukuky", "Mã M21 boot nâu, size 29 đến 36, giá 290", "", "x"),
    ("00:20", "Khách A", "M21 33", "", ""),
    ("00:25", "Khách B", "M21 boot 36 e có đặt rồi nha", "", ""),
    ("00:30", "Khách C", "sz 32", "", ""),
    ("00:40", "Khách D", "Bô bao nhiêu em", "", ""),
    ("01:00", "Shop Trukuky", "M22 set mẹ và bé", "", "x"),
    ("01:05", "Khách E", "M22 sz 4-6", "", ""),
    ("01:10", "Khách F", "cả set bé 19kg lấy size gì b nhi", "", ""),
    ("01:20", "Khách G", "Set M10 mẹ và bé còn k ạ", "", ""),
    ("01:30", "Khách H", "Chị lấy áo mickey size S cho mẹ", "", ""),
    ("01:40", "Khách A", "M21 lấy thêm x2", "", ""),
    ("01:50", "Khách I", "ca set 1m32 nang 25,5ki con k c", "", ""),
]


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    vao = os.path.join(d, "mau.csv")
    with open(vao, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Phút trong video", "Người bình luận", "Trang cá nhân",
                    "Nội dung bình luận", "Có ghi mã?", "Là shop niêm yết?"])
        for r in MAU:
            w.writerow([r[0], r[1], "", r[2], r[3], r[4]])
    tom = xu_ly(vao, os.path.join(d, "ra"), ten_shop="Shop Trukuky")

    loi = []

    def kiem(ten, duoc, mong):
        if duoc != mong:
            loi.append("%s: được %r, mong %r" % (ten, duoc, mong))

    kiem("số bình luận", tom["so_binh_luan"], len(MAU))
    kiem("niêm yết", tom["theo_nhan"].get("niem-yet"), 2)
    kiem("hỏi giá", tom["theo_nhan"].get("hoi-gia"), 1)

    with open(os.path.join(d, "ra", "binh_luan_phan_loai.csv"), encoding="utf-8-sig") as f:
        bl = {int(r["STT"]): r for r in csv.DictReader(f)}
    kiem("M21 33 -> mã", bl[2]["Mã ghi rõ"], "M21")
    kiem("M21 33 -> size", bl[2]["Size đọc được"], "sz33")
    kiem("'sz 32' nhận mã suy luận M21", bl[4]["Mã suy luận"], "M21")
    kiem("'bé 19kg' cần quy đổi", bl[8]["Cần quy đổi"], "x")
    kiem("'bé 19kg lấy size gì' là câu hỏi", bl[8]["Nhãn"], "hoi-size")
    kiem("'M22 sz 4-6' size", bl[7]["Size đọc được"], "4-6y")
    kiem("'size S cho mẹ' size", bl[10]["Size đọc được"], "S")
    kiem("'1m32 nang 25,5ki' đọc cả hai", bl[12]["Size đọc được"], "25,5kg 1m32")
    kiem("'Set M10 ... còn k' là hỏi còn", bl[9]["Nhãn"], "hoi-con")
    kiem("'Set M10' đọc đúng mã", bl[9]["Mã ghi rõ"], "M10")
    kiem("x2 ra số lượng 2", bl[11]["SL"], "2")

    with open(os.path.join(d, "ra", "chot_don_theo_khach.csv"), encoding="utf-8-sig") as f:
        don = list(csv.DictReader(f))
    kiem("Khách C chỉ có size -> suy-luan",
         [r["Độ tin"] for r in don if r["Người bình luận"] == "Khách C"], ["suy-luan"])
    kiem("Khách A gộp 2 lần đặt cùng mã",
         sorted((r["Mã"], r["Size khách gọi"], r["SL"]) for r in don if r["Người bình luận"] == "Khách A"),
         [("M21", "", "2"), ("M21", "sz33", "1")])

    if loi:
        print("TỰ KIỂM: TRƯỢT")
        for l in loi:
            print(" -", l)
        return 1
    print("TỰ KIỂM: ĐẠT (%d phép kiểm)" % 13)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ten_shop = sys.argv[3] if len(sys.argv) > 3 else None
    t = xu_ly(sys.argv[1], sys.argv[2], ten_shop=ten_shop)
    print(json.dumps(t, ensure_ascii=False, indent=1))
