# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R4.

## Trạng thái
- R4 (Công cụ nhìn + luật tài nguyên mới) **đã merge** vào `main` (PR #20, merge commit `34b1066`). D1 và L2 đạt; `lazy-landing` 6/17 ≈ 35%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R4 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên).
- `goal.json` của `lazy-landing`: R4 `done`, `plan_file: plan/R4.md`.

## Việc mở
- H-02 (thấp): `tests/_policy.py` bỏ qua `@latest` khi URL cũng có `/X.Y.Z/`. Giao R7 (mốc đầu dùng GSAP qua CDN).
- Theo dõi `test_dark_mode_applied_only_in_dark[1280]` (worker thấy đỏ 1 lần; supervisor 3/3 xanh).
- Số USD thật của R4: `/autodev:session-end` (`metrics.py --write`); hiện supervisor là số tạm `~0,77`.

## Mốc kế tiếp
- R6 (dựng trang theo spec "Quán cóc đầu ngõ"), theo chuỗi trong `ROADMAP.md`: R6 R7 R8 R12 R9 R13 R10; R11 chờ leader bật Pages.
