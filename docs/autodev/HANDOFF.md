# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R9.

## Trạng thái
- **R9 (SEO và chia sẻ) chưa đạt, KHÔNG merge.** PR #30 vẫn mở trên `milestone/R9`. Runner dừng ở đây; cần người chạy lại.
  - Tiêu chí cấp mốc 1, 2 đỏ: `test_og_png_size_and_fresh` so `mtime`, đỏ sau mọi checkout/clone mới (`verify.py`: 1 lỗi mới). CI xanh chỉ do may.
  - `og.svg`/`og.png`/`favicon.svg` lệch "Quy ước chung" của plan: gradient chàm, Helvetica, dấu tích, câu về CLI todo; không token màu, không Baloo 2, không minh hoạ ghế/ly.
  - Phần đạt: meta OG/Twitter, canonical, `SITE_URL`, robots, sitemap, JSON-LD (test xanh); smoke sạch.
- Supervisor đã thêm task (b) `dev-05` (vẽ lại ảnh chia sẻ + favicon theo hướng "Quán cóc đầu ngõ") và `dev-06` (hash nguồn trong PNG thay `mtime`; `pythonpath` thay `sys.path.insert`) vào `plan/R9.md` **trên nhánh `milestone/R9`** (commit `90fd3f7`, đã push).
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R9.
- `lazy-landing` vẫn 12/17 ≈ 71% (E1 chưa đạt).

## Việc mở
- **Chạy lại R9:** `/autodev:run R9` (hoặc `/autodev:run-milestone R9` trong worktree `autodev-sandbox-autodev`). Worktree worker phải `git pull` nhánh `milestone/R9` trước (supervisor đã đẩy `90fd3f7` lên remote). Worker làm dev-05, dev-06 rồi supervisor duyệt lại.
- **Quyết định (c) đã tự quyết (cần leader biết):** bỏ tiêu chí "`og.png` mới hơn `og.svg`" (dev-02 TC1, pre-mortem 4), thay bằng chunk `tEXt` `source-sha256` khớp sha256 của `og.svg` (dev-06).
- **Leader (D7):** duyệt bằng mắt (ảnh 360/1280, sáng/tối; trang thật, có `#du-an`, `#hoi-dap`), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`.
- **H-03, H-04, H-05 chưa đóng:** chuyển R10. **Cần thêm task (b) vào `plan/R10.md` trước khi chạy R10** (PR plan riêng; PR hồ sơ chỉ được sửa `docs/**`).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
- Flaky Chrome trong `tests/test_tools.py`, `test_site_motion.py::test_js_disabled_sections_visible` (R9 đỏ một lần). Nên tăng timeout hoặc thử lại trong test.
- `test_css_does_not_hide_summary` không bắt rule `summary` lồng trong `@media` (siết khi tiện).
- Ảnh `screenshot.py`: dưới `--virtual-time-budget` hero còn dở intro. Nên sửa trong `screenshot.py`.
- Hai nút `.nut` ở hero sát nhau (thêm gap). Font Google qua `@import`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6–R9, R12: `/autodev:session-end` (`metrics.py --write`); supervisor R9 hiện là số tạm `~1,14`.
- Thư mục tạm `.autodev/tmp/r12open/` (untracked) ở worktree supervisor: xoá khi tiện (supervisor không tự xoá).

## Mốc kế tiếp
- R9 (chạy lại với dev-05, dev-06), rồi theo chuỗi `ROADMAP.md`: R13 R10; R11 chờ leader bật Pages. R13 phụ thuộc R9 nên chưa chạy được.
