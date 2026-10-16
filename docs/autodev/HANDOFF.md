# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R10.

## Trạng thái
- **R10 (hiệu năng) đạt, đã merge** PR #35 (`576fd3d`). 3 task, 4 vòng (dev-02 REWORK 1 lần). E2 đạt: supervisor tự chạy `lh_check.py`, `/` trung vị 100/100/100/100 (perf 99, 100, 100), 173 KB; `/en/` 100×4, 165 KB. verify, smoke sạch; 210 test pass.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R10".
- `lazy-landing` 15/17 ≈ 88%. Còn D7 (leader), E3 (R11).

## Việc mở
- **Quyết định (c) của supervisor:** plan R10 không có task cho H-03..H-06 (chưa ai thêm task (b) như bàn giao trước yêu cầu). Không chặn R10 vì tiêu chí R10 đủ. H-03..H-06 chuyển sang **R14 (mới): dọn lỗ hổng site**, phụ thuộc R10, không cần Pages. **Cần `/autodev:plan-next R14`** (và thêm R14 vào `docs/goals/lazy-landing/goal.json` khi viết plan).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
  - H-06 (thấp): `tests/_policy.py` chỉ miễn trừ `rel=alternate hreflang` khi `href` bắt đầu bằng `SITE_URL`, kèm test (hiện `https://evil.com/x.css` lọt).
- **Leader (D7):** duyệt bằng mắt cả bản Việt và bản Anh (`/` và `/en/`, ảnh 360/1280, sáng/tối; `site/og.png`), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`. Từ R10 font nạp bằng `preload` + `onload`: có thể thấy FOUT thoáng.
- **Leader (R11):** bật GitHub Pages và cho biết URL.
- R11 đổi `SITE_URL`: phải sửa cả meta, `hreflang`, canonical của **cả hai trang**, `robots.txt`, `sitemap.xml`, JSON-LD (ghi cứng; test sẽ đỏ nếu quên).
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt.
- Flaky Chrome trong `tests/test_tools.py`, `test_site_motion.py`, `test_site_button.py` khi tải nặng. Nên tăng timeout hoặc thử lại trong test.
- Nhỏ: `lh_check.py --runs 0` ném `StatisticsError`; `test_css_does_not_hide_summary` không bắt rule lồng `@media`; `screenshot.py` chụp hero còn dở intro; hai nút `.nut` ở hero sát nhau.
- Số USD thật của R4, R6–R10, R12, R13: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R13, R10 hiện là số tạm.
- Dọn khi tiện (supervisor không tự xoá): thư mục tạm untracked `.autodev/tmp/` ở worktree supervisor; nhánh local `review-r10` (bản sao `milestone/R10`) ở worktree supervisor.

## Mốc kế tiếp
- R14 (cần plan, chạy được ngay) → R11 (chờ leader bật Pages).
