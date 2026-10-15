# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R2.

## Trạng thái
- R2 (Lọc việc quá hạn + H-01) **đã merge** vào `main` (PR #8, merge commit `0aa2992`). Mục tiêu `due-overdue`: 5/5 chỉ số đạt = **100%**, mục tiêu xong.
- H-01 đã đóng (test tái hiện: đỏ trên code cũ, xanh trên code mới).
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R2 (bảng tiêu chí, ước tính ↔ thực tế, pre-mortem, kiểm biên).

## Việc mở
- Không có lỗ hổng mở. Nợ không chặn: `store.save` chưa ghi nguyên tử; tham số `today` che `store.today()`; docstring `cli.py` dài.
- Reviewer trả "placeholder" thay vì JSON ở R1 dev-03 (lỗi quy trình plugin, xem bên repo plugin); R2 không gặp lại.
- Ước tính phút/USD cao hơn thực tế > 2 lần hai mốc liền: mốc cùng cỡ sau nên ước tính ~5 phút, ~0,8 USD worker.
- Số USD thật của R2: chạy `/autodev:session-end` (`metrics.py --write`).

## Mốc kế tiếp
- Chưa có. Mục tiêu `due-overdue` xong; leader chọn mục tiêu mới (`/autodev:autodev-goal`) hoặc quyết nợ `store.save`.
