# Bàn giao

Cập nhật: 2026-10-15 · Supervisor (headless, `--review-only`) sau mốc R1.

## Trạng thái
- R1 (Hạn chót) **đã merge** vào `main` (PR #5, merge commit `63cc7b0`). Mục tiêu `due-overdue`: 3/5 chỉ số đạt (A1, A3, A4) = 60%.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục R1 (bảng tiêu chí, ước tính ↔ thực tế, kiểm biên).

## Việc mở
- **H-01 (vừa):** `store.valid_due` nhận ISO tuần (`2026-W01-1`) và chuỗi có khoảng trắng cuối (`"20261020  "`), trái mô tả dev-01 ("ngày `YYYY-MM-DD` có thật"). CLI chặn được (`_ok_date`), nhưng R2 so sánh hạn trong store. Đề nghị đưa vào R2 làm task đầu (siết `valid_due` + test).
- Reviewer trả chuỗi "placeholder" thay vì JSON một lần ở dev-03 (lỗi quy trình plugin, cần xem bên repo plugin).
- `.autodev/config.json` có `smoke: []`: `verify.py --smoke` xanh nhưng không chạy gì. R2 nên thêm lệnh A5 vào `smoke` (người dùng/leader sửa config; developer không được sửa).
- Docstring đầu `cli.py` một dòng dài (không chặn).

## Mốc kế tiếp
- R2 (Lọc việc quá hạn): cần `plan/R2.md` trên `origin/main` trước khi chạy. Phụ thuộc R1: đã xong.
