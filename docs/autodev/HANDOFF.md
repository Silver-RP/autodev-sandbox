# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R9 lần 2.

## Trạng thái
- **R9 (SEO và chia sẻ) đạt, đã merge** PR #30 (`91c071a`) sau (b) dev-05 (ảnh chia sẻ + favicon theo "Quán cóc đầu ngõ") và dev-06 (hash nguồn `source-sha256` thay `mtime`). E1 đạt; 189 test pass; verify, smoke sạch.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R9 lần 2".
- `lazy-landing` 13/17 ≈ 76%.

## Việc mở
- **Quyết định (c) đã tự quyết (leader cần biết):** bỏ tiêu chí "`og.png` mới hơn `og.svg`" (dev-02 TC1, pre-mortem 4), thay bằng chunk `tEXt` `source-sha256` khớp sha256 của `og.svg` (dev-06). Đã hiện thực, có test.
- **Leader (D7):** duyệt bằng mắt (ảnh 360/1280, sáng/tối; trang thật, có `#du-an`, `#hoi-dap`; thêm `site/og.png`), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`.
- **H-03, H-04, H-05 chưa đóng:** chuyển R10. **Cần thêm task (b) vào `plan/R10.md` trước khi chạy R10** (PR plan riêng; PR hồ sơ chỉ được sửa `docs/**`).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
- R11 đổi `SITE_URL`: phải sửa cả meta, `robots.txt`, `sitemap.xml`, JSON-LD trong HTML (ghi cứng; test sẽ đỏ nếu quên).
- Flaky Chrome trong `tests/test_tools.py`, `test_site_motion.py::test_js_disabled_sections_visible`. Nên tăng timeout hoặc thử lại trong test.
- `test_css_does_not_hide_summary` không bắt rule `summary` lồng trong `@media` (siết khi tiện).
- Ảnh `screenshot.py`: dưới `--virtual-time-budget` hero còn dở intro. Nên sửa trong `screenshot.py`.
- Hai nút `.nut` ở hero sát nhau (thêm gap). Font Google qua `@import`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6–R9, R12: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2 hiện là số tạm.
- Thư mục tạm untracked ở worktree supervisor: `.autodev/tmp/r12open/`, `.autodev/tmp/r9clone2/` (clone kiểm R9). Xoá khi tiện (supervisor không tự xoá).

## Mốc kế tiếp
- Theo chuỗi `ROADMAP.md`: R13 (song ngữ, phụ thuộc R12, R9 đều xong) → R10 (thêm task H-03..05 trước) → R11 (chờ leader bật Pages).
