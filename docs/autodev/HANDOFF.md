# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R18.

## Trạng thái
- **R18 (todo CLI không traceback, không treo, không ghi hỏng) đạt, đã merge** PR #62 (`f05759b`). 4 task, mỗi task 1 vòng. Supervisor tự chạy: verify lần 2 sạch (lần 1 đỏ 1 test site Chrome, họ H-21), smoke sạch; A1 24, A2 7 passed; ruff sạch; 3 file test 85 passed; `test_store_safety` 5 × 23; CLI thật 4 ca exit 2, file nguyên byte. 8 test roadmap chạy trên code `main` cũ: đỏ cả 8 (test khoá treo).
- Đóng H-35, H-36, H-37, H-38. H-34 thu hẹp còn kiểu `title`/`done`.
- `due-overdue/goal.json`: mọi mốc `done`. `lazy-landing/goal.json`: R19 đề xuất (PR #60), chưa có plan.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R18" (có kết quả thí nghiệm superpowers 8c).

## Việc mở
- **Cần người:** `/private/tmp/r18-base` là worktree tách rời (tại `2d3a076`) do developer dev-04 tạo ngoài repo; guard chặn xoá → `git worktree remove /private/tmp/r18-base`.
- H-34 (`title`/`done` không kiểm kiểu → `KeyError` traceback), H-41: chờ leader đưa vào mốc todo sau.
- R18 giả định đã chấp nhận: `TODO_LOCK_TIMEOUT` (giây, mặc định 5; docstring `cli.py` chưa ghi); id `0` hợp lệ; id quá dài (kể cả số 0 đầu) exit 2; file có hard link ghi tại chỗ (mất nguyên tử khi bị kill).
- Ghi chú không chặn R18: thông báo `ValueError` của Python lộ nguyên văn; `due` in nguyên chuỗi ngày dài; `os.access(W_OK)` vô tác dụng khi root; đường dẫn lỗi `load` (như người dùng gõ) khác `save` (`realpath`).
- Test site (Chrome probe `test_site_ly.py`) đỏ chập chờn cả ở verify lẫn CI (H-21); mỗi lần chạy lại xanh. Pages chờ cả bộ test nên có thể chặn deploy.
- Pytest toàn bộ ~130–200 giây (511 test), vượt timeout 120 giây mặc định của Bash.
- Từ R16, **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge PR đụng `site/`.
- Ghi chú cũ (không chặn): reviewer R16 (`check_reachable` lặp, `PATH` cố định, symlink trong `site/`); chờ font 800 ms; L2 chưa bắt `<svg><a xlink:href>`; vòng chờ `lazySite` hẹp.
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12, H-14, H-47, H-48.
- Số USD thật của R4, R6–R18: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R10, R11, R13–R18 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11`, `review-r16`; `/tmp/r14old.QM4a`, `/tmp/r14probe`, `/tmp/r15old.P0ib`, `/tmp/r15edge`, `/tmp/r17old.oZgK`, `/tmp/r16old.LcWL`, `/tmp/r16edge.n3VY`, `/tmp/r18old.t3l2` (bản sao kiểm tra của supervisor).

## Mốc kế tiếp
- **R19** (`lazy-landing`: công cụ đo và cổng deploy không lách được; H-43, H-44, H-40, H-45, H-27, H-46) đã trong `goal.json`, chưa có `plan/R19.md` → `/autodev:plan-next R19`, rồi `/autodev:run R19`.
