# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R14.

## Trạng thái
- **R14 (cứng hoá công cụ đo và luật tài nguyên) đạt, đã merge** PR #44 (`66bcab8`). 4 task, mỗi task 1 vòng. Supervisor tự chạy: verify, smoke sạch; pytest 3 lần liền 295 passed; `lh_check.py` exit 0 (`/` 100×4, `/en/` perf 99); `page_metrics`/`contrast` (cả `--pages /en/`) exit 0; 52 test L2. Test H-xx mới chạy trên code `main` cũ: 48 failed (tái hiện đúng). Sau merge: workflow `pages` xanh, `smoke_pages.py` OK @ `66bcab8`.
- Đóng H-06, H-07, H-09, H-10, H-15, H-17; bỏ H-08 khỏi bảng (D7 đạt). `lazy-landing` 17/17 theo lệnh đo.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R14".

## Việc mở
- **R15 cần `/autodev:plan-next R15`** (đã có trong `goal.json`): H-03, H-04, H-05, H-11, H-20, cộng **H-21** mới: `test_tools.py` chập chờn khi máy tải nặng (Chrome quá 60 giây → exit 2; supervisor thấy 2/7 lần ở load ~14,5). Gợi ý: cho timeout Chrome đặt được qua env/cờ, hoặc test Chrome chạy tuần tự.
- Ghi chú reviewer R14 (không chặn): L2 chưa bắt `<svg><a xlink:href>` ngoài (supervisor xác nhận lọt); vòng chờ `lazySite` 10 × 50 ms hẹp; timeout Chrome 60 giây còn là hằng số.
- Từ R11, **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge bất kỳ PR nào đụng `site/`.
- Ghi chú reviewer R11 (không chặn): `smoke_pages.git_sha()` chưa có test, `except OSError` hơi rộng; `screenshot.py --url` với localhost gốc vẫn đi đường `data:` iframe; chưa thử "kill giữa deploy".
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12 (thêm D4, D5, E2, L5 vào smoke/CI), H-14 (email, `robots.txt` dưới đường con) cần leader.
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Nhỏ: `test_css_does_not_hide_summary` không bắt rule lồng `@media`; `screenshot.py` chụp hero còn dở intro; hai nút `.nut` ở hero sát nhau.
- Số USD thật của R4, R6–R14: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R13, R10, R11, R14 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): thư mục tạm untracked `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11` ở worktree supervisor; `/tmp/r14old.QM4a`, `/tmp/r14probe` (bản sao kiểm tra của supervisor R14).

## Mốc kế tiếp
- Nên chạy `/autodev:audit` trước (đo lại độ khớp thực tế `lazy-landing` sau R14), rồi `/autodev:plan-next R15`.
