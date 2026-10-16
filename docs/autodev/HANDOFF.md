# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R8.

## Trạng thái
- R8 (chế độ tối + truy cập) **đã merge** vào `main` (PR #26, merge commit `8a5a9ba`). D4, D5 đạt; `lazy-landing` 11/17 ≈ 65%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R8 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên, quyết định).
- `goal.json` của `lazy-landing`: R8 `done`, `plan_file: plan/R8.md`.

## Việc mở
- **Leader (D7):** duyệt bằng mắt sau R8 (ảnh 360/1280, sáng/tối; trang thật), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`.
- **H-03, H-04, H-05 chưa đóng:** plan R8 (duyệt ở PR #17) không có task cho chúng; chuyển sang R10. **Cần thêm task (b) vào `plan/R10.md` trước khi chạy R10** (PR plan riêng; PR hồ sơ chỉ được sửa `docs/**` nên supervisor không sửa ở đây).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
- Ảnh `screenshot.py`: dưới `--virtual-time-budget` hero còn dở intro (1280 tối gần như mất SVG). Kiểm bằng bản sao bỏ `<script>` hoặc đẩy đồng hồ gsap. Nên sửa trong `screenshot.py`.
- Hai nút `.nut` ở hero sát nhau (thêm gap).
- Font Google qua `@import` trong `style.css`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6, R7, R8: `/autodev:session-end` (`metrics.py --write`); supervisor R8 hiện là số tạm `~1,09`.

## Mốc kế tiếp
- R12 (nội dung: FAQ, 3 dự án ví dụ), theo chuỗi trong `ROADMAP.md`: R12 R9 R13 R10; R11 chờ leader bật Pages.
