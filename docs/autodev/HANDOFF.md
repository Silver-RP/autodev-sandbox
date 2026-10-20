# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R15.

## Trạng thái
- **R15 (hoàn thiện site) đạt, đã merge** PR #48 (`63cd730`). 4 task, mỗi task 1 vòng. Supervisor tự chạy: verify, smoke sạch; pytest 3 lần liền 374 passed; `page_metrics --check-overflow`, `contrast.py` exit 0; `lh_check.py` exit 0 (`/` 100×4, `/en/` 100×4); visual 8, motion 24, i18n 14 passed; font `document.fonts` vi/en PASSED (không skip). Test mới chạy trên `site/` cũ: 13 failed (tái hiện H-03, H-05, H-20). Sau merge: `smoke_pages.py` OK (lần 2) @ `63cd730`.
- Đóng H-03, H-04, H-05, H-11, H-20. `lazy-landing` 17/17 theo lệnh đo; mọi mốc trong `goal.json` đã `done`.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R15".

## Việc mở
- **Lộ trình hết mốc.** Leader quyết mốc kế: (1) mốc công cụ: H-21 (timeout Chrome hằng số, chập chờn khi tải nặng), H-23, H-24, H-25, H-27..H-33; (2) mốc todo: H-13, H-18, H-26; (3) H-22 hero thiếu laptop/người ngủ gật/hơi nước/ngáp: làm hay ghi "lệch đã chấp nhận". Cần `/autodev:autodev-goal` hoặc thêm mốc vào ROADMAP rồi `/autodev:plan-next`.
- Ghi chú reviewer R15 (không chặn): chờ font cố định 800 ms trong `MEASURE_JS`; `test_cup_reduced_motion_block_instant` có assert `json.dumps(d)` vô nghĩa; test `scrollWidth` 360 chỉ chạy sáng (supervisor đo tối 360 và 320: không tràn).
- R15 (a) đã chấp nhận: `screenshot.frame_html` chép `#out` bằng polling 100 ms (ngoài phạm vi plan).
- Từ R11, **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge bất kỳ PR nào đụng `site/`.
- Ghi chú cũ (không chặn): L2 chưa bắt `<svg><a xlink:href>` ngoài; vòng chờ `lazySite` 10 × 50 ms hẹp; `smoke_pages.git_sha()` chưa có test; `screenshot.py --url` localhost gốc vẫn đi `data:` iframe.
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12 (thêm D4, D5, E2, L5 vào smoke/CI), H-14 (email, `robots.txt` dưới đường con) cần leader.
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Nhỏ: `test_css_does_not_hide_summary` không bắt rule lồng `@media`; `screenshot.py` chụp hero còn dở intro; hai nút `.nut` ở hero sát nhau.
- Số USD thật của R4, R6–R15: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R10, R11, R13, R14, R15 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): thư mục tạm untracked `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11` ở worktree supervisor; `/tmp/r14old.QM4a`, `/tmp/r14probe`, `/tmp/r15old.P0ib`, `/tmp/r15edge` (bản sao kiểm tra của supervisor).

## Mốc kế tiếp
- Chưa có. Leader chọn hướng (mốc công cụ / mốc todo / H-22), có thể chạy `/autodev:audit` trước để đo lại độ khớp thực tế sau R15.
