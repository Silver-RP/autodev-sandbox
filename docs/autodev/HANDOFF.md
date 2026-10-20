# Bàn giao

Cập nhật: 2026-10-20 · Supervisor (headless, `--review-only`) sau mốc R11.

## Trạng thái
- **R11 (GitHub Pages) đạt, đã merge** PR #40 (`099dfd9`). 3 task, mỗi task 1 vòng. Workflow `pages` chạy xanh (run 39428889863); supervisor tự chạy `uv run python scripts/smoke_pages.py` trên `https://silver-rp.github.io/autodev-sandbox/` → OK lần 1, SHA khớp `main`, exit 0 (E3). verify, smoke sạch; 229 test pass.
- D7 leader đã duyệt (PR #38). `lazy-landing` 17/17 = 100% theo lệnh đo (audit ước thực tế thấp hơn: còn H-07..H-12, H-14).
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R11".

## Việc mở
- **R14 (dọn lỗ hổng site) cần `/autodev:plan-next R14`**, và thêm R14 vào `docs/goals/lazy-landing/goal.json` khi viết plan. Ứng viên: H-03..H-06 (như bàn giao R10), H-07 (cao), H-09..H-12, H-14 (email giữ chỗ, `robots.txt` dưới đường con), H-15, H-17, H-20. Chọn theo mức, giữ mốc nhỏ.
- Từ R11, **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge bất kỳ PR nào đụng `site/`.
- Ghi chú reviewer R11 (không chặn): `smoke_pages.git_sha()` chưa có test, `except OSError` hơi rộng; `screenshot.py --url` với localhost gốc vẫn đi đường `data:` iframe; chưa thử "kill giữa deploy" (`workflow_dispatch` chạy lại).
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`).
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Flaky Chrome trong `tests/test_tools.py`, `test_site_motion.py`, `test_site_button.py` khi tải nặng.
- Nhỏ: `lh_check.py --runs 0` ném `StatisticsError`; `test_css_does_not_hide_summary` không bắt rule lồng `@media`; `screenshot.py` chụp hero còn dở intro; hai nút `.nut` ở hero sát nhau.
- Số USD thật của R4, R6–R13: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R13, R10, R11 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): thư mục tạm untracked `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11` (bản sao nhánh mốc) ở worktree supervisor.

## Mốc kế tiếp
- R14 (cần plan, chạy được ngay). Sau R14 nên chạy `/autodev:audit` để đo lại độ khớp thực tế của `lazy-landing`.
