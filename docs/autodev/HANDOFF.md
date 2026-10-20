# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R17.

## Trạng thái
- **R17 (cứng hoá todo CLI) đạt, đã merge** PR #52 (`3a18132`). 3 task, mỗi task 1 vòng. Supervisor tự chạy: verify, smoke sạch; pytest 412 passed; `test_store_safety.py` 5 lần liền 6 passed; CLI thật `done ²`/`add ""`/`done 9`/`list` file hỏng → exit 2/2/1/2, không Traceback. Test mới chạy trên code `main` cũ: 34 failed (tái hiện H-26, H-13, H-18; test song song `20 == 40`).
- Đóng H-13, H-18, H-26. Mở H-34 (thấp): `load` chưa kiểm `title`/`done`; lỗi OS (thư mục không có) vẫn traceback.
- Mọi mốc trong `due-overdue/goal.json` đã `done`. Còn `lazy-landing` R16 (`planned`, chưa có `plan/R16.md`).
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R17".

## Việc mở
- **R16 (công cụ đo, deploy)** trong `lazy-landing/goal.json`: cần `/autodev:plan-next R16` rồi chạy.
- H-34: đề xuất (c) của R17 chờ leader: `cli.main` bắt `OSError` → stderr một dòng, exit 2; `load` kiểm `title` là `str`, `done` là `bool`.
- R17 giả định đã chấp nhận: khoá `flock` trên thư mục chứa đích (hai file todo cùng thư mục chờ nhau); tiêu đề không gộp/cắt khoảng trắng thường; `\r\n` thành một khoảng trắng.
- Pytest toàn bộ ~165–210 giây (412 test), vượt timeout 120 giây mặc định của Bash; làm phút worker R17 gấp 3 ước tính.
- Leader quyết H-22 (hero thiếu laptop/người ngủ gật/hơi nước/ngáp: làm hay ghi "lệch đã chấp nhận").
- Ghi chú reviewer R15 (không chặn): chờ font cố định 800 ms trong `MEASURE_JS`; `test_cup_reduced_motion_block_instant` có assert `json.dumps(d)` vô nghĩa; test `scrollWidth` 360 chỉ chạy sáng.
- Từ R11, **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge bất kỳ PR nào đụng `site/`.
- Ghi chú cũ (không chặn): L2 chưa bắt `<svg><a xlink:href>` ngoài; vòng chờ `lazySite` 10 × 50 ms hẹp; `smoke_pages.git_sha()` chưa có test; `screenshot.py --url` localhost gốc vẫn đi `data:` iframe.
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12 (thêm D4, D5, E2, L5 vào smoke/CI), H-14 (email, `robots.txt` dưới đường con) cần leader.
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Số USD thật của R4, R6–R17: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R10, R11, R13, R14, R15, R17 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11`; `/tmp/r14old.QM4a`, `/tmp/r14probe`, `/tmp/r15old.P0ib`, `/tmp/r15edge`, `/tmp/r17old.oZgK` (bản sao kiểm tra của supervisor).

## Mốc kế tiếp
- R16 (`lazy-landing`, công cụ đo và deploy chặt; phạm vi ở `docs/goals/lazy-landing/roadmap.md`): `/autodev:plan-next R16`.
