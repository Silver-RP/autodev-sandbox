# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R6.

## Trạng thái
- R6 (dựng trang "Quán cóc đầu ngõ") **đã merge** vào `main` (PR #22, merge commit `ecd64d0`). D2, D3 đạt; `lazy-landing` 8/17 ≈ 47%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R6 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên, quyết định).
- `goal.json` của `lazy-landing`: R6 `done`, `plan_file: plan/R6.md`.

## Việc mở
- H-03 (vừa, R8): ở 360 dấu chấm dẫn của menu bị ẩn và nút header bị ẩn; lệch wireframe 360 của `docs/design/lazy-landing.md`. Supervisor không duyệt đề xuất sửa doc; R8 khôi phục theo doc, kèm test.
- H-04 (thấp, R8): `test_h1_font_loaded_and_differs_from_body` chỉ đọc `font-family` khai báo; thêm `document.fonts.check` để chứng minh Baloo 2 đã tải.
- H-02 (thấp, R7): `_policy` bỏ qua `@latest` khi URL có `/X.Y.Z/`.
- Font Google vào qua `@import` trong `style.css` (giới hạn 1 stylesheet của `test_site.py`); R10 xem lại hiệu năng.
- Số USD thật của R4, R6: `/autodev:session-end` (`metrics.py --write`); supervisor R6 hiện là số tạm `~0,89`.

## Mốc kế tiếp
- R7 (chuyển động GSAP + H-02), rồi R8 (tối, truy cập, H-03, H-04), theo chuỗi trong `ROADMAP.md`: R7 R8 R12 R9 R13 R10; R11 chờ leader bật Pages.
