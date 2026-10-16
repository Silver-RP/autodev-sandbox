# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R7.

## Trạng thái
- R7 (chuyển động GSAP + nút vui) **đã merge** vào `main` (PR #24, merge commit `1a66df0`). D6 đạt, đóng H-02; `lazy-landing` 9/17 ≈ 53%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R7 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên, quyết định).
- `goal.json` của `lazy-landing`: R7 `done`, `plan_file: plan/R7.md`.

## Việc mở
- H-03 (vừa, R8): ở 360 dấu chấm dẫn của menu bị ẩn và nút header bị ẩn; lệch wireframe 360 của `docs/design/lazy-landing.md`. R8 khôi phục theo doc, kèm test.
- H-04 (thấp, R8): `test_h1_font_loaded_and_differs_from_body` chỉ đọc `font-family` khai báo; thêm `document.fonts.check`.
- H-05 (thấp, R8): `style.css` chưa có `@media (prefers-reduced-motion: reduce)` (quy ước plan R7). Supervisor thấy sau khi merge; không chặn vì CSS chưa có chuyển động.
- Chụp ảnh R8+: dưới `--virtual-time-budget` intro hero còn dở (rAF không phát). Đẩy đồng hồ gsap như `test_site_motion.py` hoặc dùng CDP thời gian thật.
- Hai nút `.nut` ở hero sát nhau (thêm gap, R8/R9).
- Font Google qua `@import` trong `style.css`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6, R7: `/autodev:session-end` (`metrics.py --write`); supervisor R7 hiện là số tạm `~1,00`.

## Mốc kế tiếp
- R8 (tối, truy cập, H-03, H-04, H-05), theo chuỗi trong `ROADMAP.md`: R8 R12 R9 R13 R10; R11 chờ leader bật Pages.
