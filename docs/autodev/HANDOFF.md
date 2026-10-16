# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R12.

## Trạng thái
- R12 (FAQ + 3 dự án ví dụ) **đã merge** vào `main` (PR #28, merge commit `b7e2529`). E4 đạt; `lazy-landing` 12/17 ≈ 71%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R12 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên, quyết định).
- `goal.json` của `lazy-landing`: R12 `done`, `plan_file: plan/R12.md`.

## Việc mở
- **Leader (D7):** duyệt bằng mắt (ảnh 360/1280, sáng/tối; trang thật, nay có thêm `#du-an`, `#hoi-dap`), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`.
- **H-03, H-04, H-05 chưa đóng:** chuyển R10. **Cần thêm task (b) vào `plan/R10.md` trước khi chạy R10** (PR plan riêng; PR hồ sơ chỉ được sửa `docs/**`).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
- Flaky Chrome trong `tests/test_tools.py`: R12 thêm `test_metrics_svg_h1_font_and_repeat` (đỏ một lần, chạy lại xanh). Nên tăng timeout hoặc thử lại trong test.
- `test_css_does_not_hide_summary` không bắt rule `summary` lồng trong `@media` (siết khi tiện).
- Ảnh `screenshot.py`: dưới `--virtual-time-budget` hero còn dở intro. Nên sửa trong `screenshot.py`.
- Hai nút `.nut` ở hero sát nhau (thêm gap). Font Google qua `@import`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6, R7, R8, R12: `/autodev:session-end` (`metrics.py --write`); supervisor R12 hiện là số tạm `~1,16`.
- Thư mục tạm `.autodev/tmp/r12open/` (bản sao site có `<details open>`, untracked) ở worktree supervisor: xoá khi tiện (supervisor không tự xoá).

## Mốc kế tiếp
- R9 (SEO và chia sẻ), theo chuỗi trong `ROADMAP.md`: R9 R13 R10; R11 chờ leader bật Pages.
