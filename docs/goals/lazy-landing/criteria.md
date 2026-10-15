# Tiêu chí: `lazy-landing`

Dự án chưa có file tiêu chí (`paths.criteria_file` rỗng), nên bảng dưới là toàn bộ tiêu chí của mục tiêu này. Nền đo ngày 2026-10-16 trên `origin/main` (`2ea6f24`).

| Mã | Định nghĩa | Lệnh đo | Nền | Ngưỡng | % đạt |
|---|---|---|---|---|---|
| L1 | Cấu trúc `site/index.html`, kiểm bằng `html.parser`:<br>• `<html lang="vi">`, `meta charset`, `meta viewport`, `<title>`, `meta description`;<br>• đúng một `<h1>`;<br>• 4 thẻ `section` thật với id `hero`, `dich-vu`, `cach-lam`, `lien-he`, mỗi phần ≥ 20 ký tự chữ, không có `lorem` / `TODO` / `placeholder`;<br>• có link `mailto:`;<br>• có chữ "Lười Code Studio";<br>• trỏ `style.css` và file đó tồn tại;<br>• thẻ mở và đóng của `section` / `main` / `header` / `footer` khớp nhau | `uv run pytest -q tests/test_site.py` | file chưa có | 0 failed, ≥ 6 test | số hành vi có test xanh / 6 |
| L2 | Tối giản và truy cập:<br>• `@media (prefers-color-scheme: dark)` gán lại biến màu nền và màu chữ, khác bản sáng;<br>• khung nội dung dùng `max-width`, không có `width` / `min-width` > 360px;<br>• 0 tài nguyên ngoài: `src` / `href` / CSS `url()` / `@import` không chứa `http:`, `https:`, `//`; được dùng đường dẫn tương đối, `#…`, `mailto:`;<br>• mọi `<img>` có `alt`;<br>• heading không nhảy cấp;<br>• tổng mọi file trong `site/` ≤ 30 KB;<br>• không có `<script>` | `uv run pytest -q tests/test_site_polish.py` | file chưa có | 0 failed, ≥ 6 test | số hành vi có test xanh / 6 |
| L3 | Không hồi quy | `uv run pytest -q` | 52 passed | 0 failed | 100% hoặc 0% |
| L4 | Lint sạch | `uv run ruff check .` | sạch | 0 lỗi | 100% hoặc 0% |
| L5 | Smoke HTTP thật (lệnh dưới) | xem dưới | chưa có | in `200` hai dòng, exit 0 | 100% hoặc 0% |

Lệnh L5, chạy ở thư mục gốc dự án. Lệnh đã chạy thử trên file giả ngày 2026-10-16 và in `200` hai dòng.

```sh
uv run python -c "import functools,http.server,threading,urllib.request as u; s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='site')); threading.Thread(target=s.serve_forever,daemon=True).start(); [print(u.urlopen(f'http://127.0.0.1:{s.server_port}/{p}').status) for p in ('','style.css')]"
```

% đạt của mục tiêu = số chỉ số đạt ngưỡng / 5. Mục tiêu xong khi đạt 5/5 **và** leader đã duyệt bằng mắt (xem "việc chỉ người làm" trong `roadmap.md`).
