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

## R4
- dev-01 DONE (1 vòng, commit c77b877): `scripts/screenshot.py` (360 qua iframe, 1280 trực tiếp, sáng/tối), `png_size`, 7 test Chrome thật không skip. 76 test pass. Ghi chú reviewer (không chặn): `site/` chưa có CSS dark nên 360-dark = 360-light; ảnh 360 không hiện cuộn ngang của iframe (dev-02 đo tràn).
- dev-02 DONE (1 vòng, commit 28f51b6): `scripts/page_metrics.py` (tràn đo theo `getBoundingClientRect().right` nên bắt được `overflow-x:hidden`; svg theo section; h1/body font; màu). `site/` hiện: không tràn ở 4 tổ hợp, svg toàn 0, h1 32px system-ui, màu sáng = tối. Ghi chú reviewer (không chặn): `test_dark_mode_applied_only_in_dark[1280]` (dev-01) đỏ một lần trong verify rồi xanh khi chạy lại (nghi chập chờn, cần theo dõi); `--widths` không kiểm số.
- dev-03 DONE (1 vòng, commit cae7cab): `tests/_policy.py` (`check(html, css)`) và `tests/test_site_policy.py` (16 test, 6 ca âm, ca dương). 95 test pass. Ghi chú reviewer (không chặn): `srcset` và `javascript:` chưa kiểm.
- dev-04 DONE (1 vòng, commit a3b18ec): dọn `test_css_content` (bỏ `system-ui`, bỏ cấm tài nguyên) và đổi `test_balanced_tags_no_script` thành `test_balanced_tags` (bỏ `scripts == 0`). verify lần đầu bị test_guard chặn vì đổi tên; developer thêm `allow-test-change` có giải trình, reviewer xác nhận. 11 test trong `test_site.py`; đột biến `evil.example` làm `test_site_policy` đỏ.

## R6
- dev-01 DONE (1 vòng, commit ad06983): `tests/test_design_doc.py` (7 test, D2), `tests/test_site_visual.py` (8 test), token `:root` khớp bảng sáng của doc, Google Fonts (preconnect ở HTML, URL font trong `@import` đầu `style.css` vì `test_site.py` giới hạn 1 stylesheet), khung bố cục. 110 test pass. Ghi chú reviewer (không chặn): `allow-test-change` ở ad06983 chính đáng (`skipif` ở file mới); `@import` làm font tải muộn một nhịp; mailto header lấn nhẹ dev-02.
- dev-02 DONE (1 vòng, commit c298790): viết lại chữ 4 phần ("Menu hôm nay", "Gọi món thế nào", "Ghé quán"), nút `mailto:` "Gửi thư cho tôi" ở hero và liên hệ, `tests/test_site_content.py` (4 test). 114 test pass. Ghi chú reviewer (không chặn): parser mailto phân biệt hoa thường; class `nut` chưa có CSS.

## Đề xuất chờ duyệt
