# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R19.

## Trạng thái
- **R19 (công cụ đo và cổng deploy không lách được) đạt, đã merge** PR #65 (`805cbe0`). 4 task, 5 vòng (dev-02 2 vòng). Supervisor tự chạy: verify sạch (3 phút 20), smoke sạch; pytest 569 passed × 2; ruff sạch; D1 21 passed; D4, D5 exit 0; E3 sau merge: run `pages` 39562762336 (test → build `pages: read` → deploy) xanh, `smoke_pages.py` OK @ `805cbe0` (chạy lại lần hai cũng OK). 5 tệp test mới chạy trên code `main` cũ: 56 failed.
- Đóng H-27, H-40, H-43, H-44, H-45, H-46. Ghi H-50 (thấp, phần hở nhỏ supervisor tìm thấy).
- `due-overdue`, `lazy-landing` (`goal.json`): mọi mốc `done`; chưa có mốc nào chờ.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R19" (bảng tiêu chí, ước tính, pre-mortem, kiểm biên, thí nghiệm superpowers 8c).

## Việc mở
- **Cần người:** `/private/tmp/r18-base` vẫn là worktree tách rời (tại `2d3a076`, do developer R18 dev-04 tạo); guard chặn xoá → `git worktree remove /private/tmp/r18-base`.
- H-50: `smoke_pages --interval inf` traceback; `screenshot --pages " , "` không strip; `workflow_problems` lọt `write-all`/`shell: … || true`/`working-directory`; test TC 2 dev-03 yếu (supervisor đã bù bằng probe, chưa vào repo).
- H-34, H-41 (todo): chờ leader đưa vào mốc todo sau.
- R19 giả định đã chấp nhận: `build` giữ `pages: read`; `--retries 0` exit 2; SHA tính lại mỗi lần thử.
- Test site (Chrome) đỏ chập chờn khi tải nặng (H-21); Pages chờ cả bộ test nên có thể chặn deploy.
- Pytest toàn bộ ~200 giây (569 test), vượt timeout 120 giây mặc định của Bash.
- Mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages; chạy `smoke_pages.py` sau merge PR đụng `site/`.
- Ghi chú cũ (không chặn): R18 (`TODO_LOCK_TIMEOUT` chưa ghi docstring, `ValueError` lộ nguyên văn); reviewer R16 (`check_reachable` lặp, `PATH` cố định); chờ font 800 ms; L2 chưa bắt `<svg><a xlink:href>`.
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12, H-14, H-47, H-48.
- Số USD thật của R4, R6–R19: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R10, R11, R13–R19 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11`, `review-r16`; `/tmp/r14old.QM4a`, `/tmp/r14probe`, `/tmp/r15old.P0ib`, `/tmp/r15edge`, `/tmp/r17old.oZgK`, `/tmp/r16old.LcWL`, `/tmp/r16edge.n3VY`, `/tmp/r18old.t3l2`, `/tmp/r19old.cNRc`, `/tmp/r19probe`, `/tmp/r19edge.AGBV`, `/tmp/r19-*.txt`, `/tmp/r19-d4.err`.

## Mốc kế tiếp
- Chưa có mốc trong `goal.json`. Đề xuất: `/autodev:audit R18 R19` rồi `/autodev:propose-next` (ứng viên: mốc kiểm chứng H-21, H-31, H-39, H-42; mốc công cụ nhỏ H-49, H-50, H-30, H-32, H-33). H-34, H-41 chờ leader.
