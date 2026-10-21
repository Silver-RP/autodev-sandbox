# Bàn giao

Cập nhật: 2026-10-21 · Leader đóng phiên (sau vòng tự chạy P14).

## Bước tiếp theo (cập nhật 2026-10-21)
- **Đã xong trong phiên (leader uỷ quyền toàn bộ):** vòng `--loop` 1: R17 → R16 → audit (13,75 USD, exit 0). Bật `experiments.superpowers` (#59). Vòng 2 `--propose 2 --auto-approve`: đề xuất R18, R19 (#60) → chạy, merge → audit `2026-10-21-4.md` → đề xuất R20, R21 (#68) → dừng exit 7 ngân sách (15,13 USD; trần 12). 0 can thiệp người. Số đo thật B1–B5 đã ghi (`metrics.py --write`).
- **Không có runner chạy, không PR mở.** `goal.json` còn `planned`: R20 (`due-overdue`, H-34/H-53/H-54, ước 2,5 USD), R21 (`lazy-landing`, H-52/H-51/H-55, ước 3,5 USD), cả hai `proposed: true`, chưa có plan.
- **Làm tiếp theo thứ tự:**
  1. **Chờ leader** trả lời bằng số: (1) chạy tiếp R20, R21 (~12 USD, đo thêm A/B superpowers); (2) tạo bot Telegram, gửi token + chat_id; (3) thử dự án thật thứ hai; (4) tạm dừng.
  2. Chạy: `cd ~/dev/autodev-sandbox && nohup ~/dev/autodev/scripts/autodev-run.sh --loop --max-usd 12 --propose 2 --auto-approve > .autodev/runs/nohup.out 2>&1 &`.
  3. Dọn (cần leader duyệt xoá): worktree `/private/tmp/r18-base`, nhánh `chore/autodev-plan-R14`, các thư mục `/tmp/r1*` liệt kê dưới.
- **Lịch sử ngắn:** 20/10 D7 đạt, Pages bật; 21/10 R11, R14, R15 (10,33 USD) rồi hai vòng tự chạy trên.

## Trạng thái
- **R19 (công cụ đo và cổng deploy không lách được) đạt, đã merge** PR #65 (`805cbe0`). 4 task, 5 vòng (dev-02 2 vòng). Supervisor tự chạy: verify sạch (3 phút 20), smoke sạch; pytest 569 passed × 2; ruff sạch; D1 21 passed; D4, D5 exit 0; E3 sau merge: run `pages` 39562762336 (test → build `pages: read` → deploy) xanh, `smoke_pages.py` OK @ `805cbe0` (chạy lại lần hai cũng OK). 5 tệp test mới chạy trên code `main` cũ: 56 failed.
- Đóng H-27, H-40, H-43, H-44, H-45, H-46. Ghi H-50 (thấp, phần hở nhỏ supervisor tìm thấy).
- `due-overdue`, `lazy-landing` (`goal.json`): R1–R19 `done` (R5 cắt); R20, R21 `planned` (supervisor đề xuất sau audit R18, R19).
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
- R20, R21 (`planned`, đề xuất #68 từ audit `2026-10-21-4.md`); runner `--loop` tự viết plan rồi chạy.
