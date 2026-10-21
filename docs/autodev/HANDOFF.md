# Bàn giao

Cập nhật: 2026-10-21 · Supervisor (headless, `--review-only`) sau mốc R16.

## Trạng thái
- **R16 (công cụ đo và deploy chặt) đạt, đã merge** PR #56 (`ff8c12f`). 4 task, mỗi task 1 vòng. Supervisor tự chạy: verify, smoke sạch; pytest 467 passed × 2; D4, D1 (21), D2 (10), E2 (100×4), D5, ruff đạt; sau merge workflow `pages` test → build → deploy xanh, `smoke_pages.py` OK @ `ff8c12f`. Test mới chạy trên code `main` cũ: 42 failed.
- Đóng H-22 (spec hero sửa theo trang đã duyệt, mục "Phần spec cũ bị bỏ"), H-23, H-24, H-25, H-28, H-29. H-27 còn phần kiểm `main.js`/`robots.txt`/`sitemap.xml`, version `/en/`; H-40 còn phần `smoke_pages`.
- Mọi mốc trong `due-overdue/goal.json` và `lazy-landing/goal.json` đã `done`.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R16".

## Việc mở
- **Không còn mốc lập sẵn.** Đề xuất (audit 2026-10-21-2, plan R16 "Đề xuất chờ duyệt"): mốc công cụ tiếp (H-21, H-27 phần còn lại, H-30, H-32, H-33, H-40 `smoke_pages --url`/`--interval`/`--retries` âm), R18 todo (H-34..H-38, H-41), R19 kiểm chứng (H-31, H-39, H-42). Leader lập goal/roadmap (`/autodev:autodev-goal`) rồi `/autodev:plan-next`.
- R16 giả định đã chấp nhận: phần tử `overflow-x` khác `visible` có `scrollWidth > clientWidth` là khung cuộn hợp lệ (không tính tràn); thêm `pyyaml` nhóm `dev`; test bước "Ghi phiên bản" dùng shim `sed -i ''` trên macOS.
- Ghi chú reviewer R16 (không chặn): `check_reachable` gọi lặp mỗi width × mode; test version-step cố định `PATH=/usr/bin:/bin`; chưa probe symlink trong `site/` trỏ ra ngoài.
- H-34: đề xuất (c) của R17 chờ leader: `cli.main` bắt `OSError` → exit 2; `load` kiểm `title` là `str`, `done` là `bool`.
- Pytest toàn bộ ~175 giây (467 test), vượt timeout 120 giây mặc định của Bash.
- Từ R16, workflow `pages` chạy ruff + pytest trước deploy; **mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại Pages**; chạy `smoke_pages.py` sau merge PR đụng `site/`.
- Ghi chú cũ (không chặn): chờ font 800 ms trong `MEASURE_JS`; L2 chưa bắt `<svg><a xlink:href>` ngoài; vòng chờ `lazySite` 10 × 50 ms hẹp; `screenshot.py --url` localhost gốc vẫn đi `data:` iframe.
- Leader: thay tên, email, giá giữ chỗ bằng thông tin thật (human_only trong `goal.json`); H-12 (thêm D4, D5, E2, L5 vào smoke/CI), H-14 (email, `robots.txt` dưới đường con).
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Số USD thật của R4, R6–R17: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R10, R11, R13–R17 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10`, `review-r11`, `review-r16`; `/tmp/r14old.QM4a`, `/tmp/r14probe`, `/tmp/r15old.P0ib`, `/tmp/r15edge`, `/tmp/r17old.oZgK`, `/tmp/r16old.LcWL`, `/tmp/r16edge.n3VY` (bản sao kiểm tra của supervisor).

## Mốc kế tiếp
- Chưa có. Leader chọn trong đề xuất ở "Việc mở" (mốc công cụ tiếp / R18 todo / R19 kiểm chứng), lập goal + roadmap, rồi `/autodev:plan-next <mốc>`.
