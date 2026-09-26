"""Đọc các tab mã (M01, M02…) của sổ live thành bảng phẳng.

Cấu trúc một khối trong tab (một tab có thể có nhiều khối, mỗi khối một món):

    MÃ   | …  | M10 | (chữ ký người phụ trách)
    GIÁ  | …
    (dòng giá, ô gộp: 690 ở cột size bé, 790 ở cột size mẹ)
    SL   | 3 | 5 | 6 | …                 ← số lượng từng cột size; có thể "6+2", "7 (CÒN VỀ THÊM)"
    <nhãn khối> | 90 1-2 | 100 2-4 | …    ← vd "áo ghi lê 690-790"; ô cột = tag cm + tuổi
    tên khách dưới từng cột size, theo thứ tự ghi; có thể có cột số thứ tự 1, 2, 3…

Kết quả: một dòng cho mỗi ô size (TON) và một dòng cho mỗi tên khách (TEN).
"""
import re
import unicodedata

AGE = re.compile(r"(?<![\d-])(\d{1,2})\s*-\s*(\d{1,2})(?![\d-])")
ADULT = re.compile(r"(?<![A-Za-z])(XS|S|M|L|XL)(?![A-Za-z])")
TAG = re.compile(r"^\s*(\d{2,3})\b")
NUM = re.compile(r"\d+")


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.replace("đ", "d").replace("Đ", "D").lower())


def cell(rows, r, c):
    return rows[r][c].strip() if r < len(rows) and c < len(rows[r]) and rows[r][c] else ""


def parse_sl(raw):
    """'6+2' → (6, 2); '7 ( CÒN VỀ THÊM)' → (7, 0); '10 + 1 … đổi về' → (10, 1)."""
    nums = [int(x) for x in NUM.findall(raw or "")]
    if not nums:
        return None, None
    return nums[0], (nums[1] if "+" in raw and len(nums) > 1 else 0)


def _sizes(text):
    out = [f"{a}-{b}y" for a, b in AGE.findall(text)]
    out += ADULT.findall(text.upper())
    return list(dict.fromkeys(out))


def sizes_split(label):
    """Nhãn cột → (size chính, size phụ).
    '110 1-2, 2-4' → (['1-2y','2-4y'], []) · '160 XS & S' → (['XS','S'], [])
    '120 6-8 (hoặc 4-6)' → (['6-8y'], ['4-6y']) · '160 S hoặc M' → (['S'], ['M']) · '26' → (['26'], [])"""
    m = re.search(r"\(?\s*hoặc\b(.*)$", label, re.I)
    main, alt = (label[: m.start()], m.group(1)) if m else (label, "")
    pri, sec = _sizes(main), [x for x in _sizes(alt) if x not in _sizes(main)]
    if not pri and not sec:
        g = re.fullmatch(r"\s*(\d{2})\s*", label)  # cỡ giày 26…37
        if g:
            pri = [g.group(1)]
    return pri, sec


def sizes_of(label):
    pri, sec = sizes_split(label)
    return pri + sec


def price_tiers(text):
    """'áo 390-490' → [390000, 490000]; 'boot 890' → [890000]; 'túi 1590' → [1590000]."""
    vals = [int(x) for x in NUM.findall(text or "") if 100 <= int(x) <= 5000]
    return [v * 1000 for v in vals]


def clean_name(raw):
    """Tách tên khách khỏi ghi chú trong ô: số lượng 'x2', size gợi ý, 'đổi …', 'gấp'."""
    s = " ".join(raw.split())
    note = []
    q = 1
    m = re.search(r"\bx\s*(\d+)\b", s, re.I)
    if m:
        q = int(m.group(1))
        s = (s[: m.start()] + s[m.end():]).strip()
    m = re.search(r"\bđổi\b.*$", s, re.I)
    if m:
        note.append(m.group(0).strip())
        s = s[: m.start()].strip()
    m = re.search(r"\b(gấp|gap)\b", s, re.I)
    if m:
        note.append("gấp")
        s = (s[: m.start()] + s[m.end():]).strip()
    size_hint = ""
    m = re.search(r"\s(\d{1,2}\s*-\s*\d{1,2}|XS|S|M|L|\d{3})$", s)
    if m:
        size_hint = m.group(1).replace(" ", "")
        s = s[: m.start()].strip()
    s = s.strip(" -–,.;:()")
    return s, q, size_hint, "; ".join(note)


def is_stop(rows, r):
    a = fold(cell(rows, r, 0))
    return a in ("ma", "gia", "sl")


def parse_tab(name, rows):
    code_m = re.match(r"\s*(M\d+)", name, re.I)
    code = code_m.group(1).upper() if code_m else name.strip()
    width = max((len(x) for x in rows), default=0)
    ton, ten = [], []
    sl_rows = [r for r in range(len(rows)) if fold(cell(rows, r, 0)) == "sl"]
    for bi, r in enumerate(sl_rows):
        lab_r = r + 1
        block_label = cell(rows, lab_r, 0)
        cols = [c for c in range(1, width) if cell(rows, lab_r, c)]
        if not cols:  # khối một cỡ (túi…): lấy cột có SL
            cols = [c for c in range(1, width) if cell(rows, r, c)]
        # dòng giá: gần nhất phía trên có số trong vùng cột khối; ô gộp → điền tiếp sang phải
        prices = {}
        for pr in range(r - 1, max(-1, r - 5), -1):
            vals = {c: cell(rows, pr, c) for c in range(1, width)}
            if any(re.fullmatch(r"\d{3,4}", v) for c, v in vals.items() if c in cols or c <= max(cols, default=0)):
                cur = None
                for c in range(1, (max(cols) if cols else 0) + 1):
                    v = vals.get(c, "")
                    if re.fullmatch(r"\d{3,4}", v):
                        cur = int(v) * 1000
                    if c in cols and cur:
                        prices[c] = cur
                break
        tiers = price_tiers(block_label)
        end = sl_rows[bi + 1] if bi + 1 < len(sl_rows) else len(rows)
        for c in cols:
            label = cell(rows, lab_r, c) or "Freesize"
            a, b = parse_sl(cell(rows, r, c))
            price = prices.get(c) or (tiers[0] if len(tiers) == 1 else None)
            ton.append({"tab": name, "ma": code, "khoi": bi + 1, "nhan_khoi": block_label, "cot": c,
                        "nhan_cot": label, "sizes": sizes_split(label)[0] or (["Freesize"] if label == "Freesize" else []),
                        "sizes_phu": sizes_split(label)[1],
                        "sl_goc": cell(rows, r, c), "sl_a": a, "sl_b": b, "gia": price})
            rank = 0
            for rr in range(lab_r + 1, end):
                if is_stop(rows, rr):
                    break
                v = cell(rows, rr, c)
                if not v or re.fullmatch(r"\d{1,3}", v):
                    continue
                rank += 1
                nm, q, hint, note = clean_name(v)
                ten.append({"tab": name, "ma": code, "khoi": bi + 1, "nhan_khoi": block_label, "cot": c,
                            "nhan_cot": label, "thu_tu": rank, "o_goc": v, "ten": nm, "sl": q,
                            "size_ghi_them": hint, "ghi_chu": note, "dong": rr + 1})
    return ton, ten


def parse_book(book):
    ton, ten, skipped = [], [], []
    for sh in book["sheets"]:
        if re.match(r"\s*M\d+", sh["name"], re.I) and sh.get("rows"):
            a, b = parse_tab(sh["name"], sh["rows"])
            ton += a
            ten += b
        else:
            skipped.append(sh["name"])
    return ton, ten, skipped
