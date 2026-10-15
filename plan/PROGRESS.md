# Nhật ký mốc

## R1
- dev-01 DONE (1 vòng, commit 43af2ca): store.valid_due, add(due), set_due; việc mới không hạn thì không ghi khoá `due`. Ghi chú reviewer (không chặn): `valid_due("2026-W01-1")` trả True (ISO tuần); dev-02 nên thêm kiểm dạng `YYYY-MM-DD` ở CLI.
- dev-02 DONE (1 vòng, commit 6ea15b4): `add --due`, `todo due`; CLI từ chối ISO tuần. Ghi chú: docstring đầu cli.py thành một dòng dài (không chặn).
- dev-03 DONE (1 vòng, commit 2aabcba): `list` hiện cột hạn. Lần review đầu trả "placeholder" (không phải JSON), gọi lại reviewer được PASS.

## R2
- dev-01 DONE (1 vòng, commit 0e97636): siết `store.valid_due` (H-01), CLI bỏ `_ok_date`. 40 test pass.
- dev-02 DONE (1 vòng, commit 8bcc4e5): `store.today` (TODO_TODAY) và `store.overdue`. 47 test pass. Ghi chú reviewer (không chặn): tham số `today` che tên hàm `today()`.
- dev-03 DONE (1 vòng, commit b3bc04a): lệnh `todo overdue`, `_line` dùng chung với `list`; smoke A5 ok. 52 test pass.

## R3
- dev-01 DONE (1 vòng, commit ad0e85e): `site/index.html` (4 section, tiếng Việt) và `tests/test_site.py` (8 test, có ca âm). 63 test pass. Ghi chú reviewer (không chặn): kiểm `lorem/todo/placeholder` quét cả nguồn thô, chặt hơn plan.
- dev-02 DONE (1 vòng, commit 2a71b92): `site/style.css` (`:root`, `max-width: 40rem`, `system-ui`), link từ `index.html`, 3 test. 66 test pass. Developer không chạy test đỏ trước; reviewer thử 11 đột biến, test đỏ đúng chỗ. Ghi chú (không chặn): kiểm `http:` phân biệt hoa thường (R4 nên quét không phân biệt); `href="../site/style.css"` vẫn qua.
- dev-03 DONE (1 vòng, commit 5328535): `tests/test_site_http.py` (3 test, `ThreadingHTTPServer` thật, 200 / `text/css` / 404, tắt server trong fixture). L5 in `200` hai dòng. Test xanh ngay lần đầu; reviewer thử 4 đột biến, đều đỏ. Ghi chú (không chặn): nên assert `Content-Type text/html` cho `/`.

## Đề xuất chờ duyệt
