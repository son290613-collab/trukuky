"""Kéo toàn bộ các tab của Google Sheet công khai (quyền 'bất kỳ ai có link') thành JSON.

Chạy:
    python fetch_so_live.py --check <spreadsheet_id>          # chỉ kiểm tra mạng
    python fetch_so_live.py <spreadsheet_id> [...] -o out.json

Cần mạng tới docs.google.com và *.googleusercontent.com. Không cần đăng nhập.
Thứ tự thử cho mỗi tab: export CSV theo gid (giữ nguyên ô) → gviz CSV theo gid (headers=0).
File ra có dữ liệu khách — không commit, không chia sẻ công khai.
"""
import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"
BASE = "https://docs.google.com/spreadsheets/d/{id}"


def get(url, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read(), r.geturl()
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 ** (k + 1))
    raise last


def js_str(s):
    s = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: "\\u00" + m.group(1), s)
    try:
        return json.loads('"' + s + '"')
    except ValueError:
        return s


def list_sheets(sid):
    """Tên + gid của mọi tab, đọc từ trang htmlview."""
    raw, _ = get(BASE.format(id=sid) + "/htmlview")
    h = raw.decode("utf8", "replace")
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    title = title.group(1).replace(" - Google Sheets", "").replace(" - Google Trang tính", "").strip() if title else sid
    found = [(js_str(n), g) for n, g in re.findall(r'name:\s*"((?:[^"\\]|\\.)*)",\s*pageUrl:\s*"(?:[^"\\]|\\.)*",\s*gid:\s*"(\d+)"', h)]
    if not found:
        found = [(re.sub(r"<[^>]+>", "", n).strip(), g)
                 for g, n in re.findall(r'id="sheet-button-(\d+)"[^>]*>(.*?)</li>', h, re.S)]
    seen, out = set(), []
    for n, g in found:
        if g not in seen:
            seen.add(g)
            out.append({"name": n, "gid": g})
    return title, out


def fetch_tab(sid, gid):
    tries = [("export", BASE.format(id=sid) + f"/export?format=csv&gid={gid}"),
             ("gviz", BASE.format(id=sid) + f"/gviz/tq?tqx=out:csv&headers=0&gid={gid}")]
    errs = []
    for method, url in tries:
        try:
            raw, final = get(url)
            text = raw.decode("utf8", "replace")
            if text.lstrip().startswith("<"):
                errs.append(f"{method}: trả về HTML (có thể cần đăng nhập)")
                continue
            return method, list(csv.reader(io.StringIO(text)))
        except Exception as e:  # noqa: BLE001 — ghi lại lỗi từng cách, thử cách sau
            errs.append(f"{method}: {e}")
    raise RuntimeError("; ".join(errs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("-o", "--out", default="so_live_raw.json")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        for sid in a.ids:
            try:
                title, tabs = list_sheets(sid)
                print(f"OK  {sid}: '{title}', {len(tabs)} tab")
                if tabs:
                    m, rows = fetch_tab(sid, tabs[0]["gid"])
                    print(f"    tab đầu '{tabs[0]['name']}' qua {m}: {len(rows)} dòng")
            except Exception as e:  # noqa: BLE001
                print(f"LỖI {sid}: {e}")
        return
    result = {"fetched_at": time.strftime("%Y-%m-%d %H:%M:%S %z"), "spreadsheets": []}
    for sid in a.ids:
        title, tabs = list_sheets(sid)
        book = {"id": sid, "title": title, "sheets": []}
        for t in tabs:
            try:
                m, rows = fetch_tab(sid, t["gid"])
                book["sheets"].append({**t, "method": m, "rows": rows})
                print(f"{title} / {t['name']}: {len(rows)} dòng ({m})", file=sys.stderr)
            except Exception as e:  # noqa: BLE001
                book["sheets"].append({**t, "error": str(e), "rows": []})
                print(f"{title} / {t['name']}: LỖI {e}", file=sys.stderr)
        result["spreadsheets"].append(book)
    json.dump(result, open(a.out, "w", encoding="utf8"), ensure_ascii=False)
    n = sum(len(s["sheets"]) for s in result["spreadsheets"])
    bad = sum(1 for b in result["spreadsheets"] for s in b["sheets"] if s.get("error"))
    print(f"Xong: {n} tab, {bad} lỗi → {a.out}")


if __name__ == "__main__":
    main()
