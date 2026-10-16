# Bàn giao

Cập nhật: 2026-10-16 · Supervisor (headless, `--review-only`) sau mốc R13.

## Trạng thái
- **R13 (song ngữ Việt/Anh) đạt, đã merge** PR #33 (`68112ec`). 3 task, mỗi task 1 vòng. E5 đạt (`test_site_i18n.py` 14 passed); `contrast.py`, `page_metrics.py --check-overflow` exit 0 cho `/` và `/en/`; verify, smoke sạch.
- Hồ sơ duyệt: `docs/autodev/PROGRESS.md` mục "R13".
- `lazy-landing` 14/17 ≈ 82%. Còn D7, E2, E3.

## Việc mở
- **Leader (D7):** duyệt bằng mắt cả bản Việt và bản Anh (`/` và `/en/`, ảnh 360/1280, sáng/tối; `site/og.png`), ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md`. Nhận xét reviewer về bản Anh: giọng đùa giữ tốt; vài câu FAQ dài; "Alley Corner Cafe", "Ink Stroke" sát nghĩa đen; ở 360 link "Tiếng Việt" rớt dòng dưới logo (bản Việt cùng dòng).
- **H-03, H-04, H-05, H-06 chưa đóng:** chuyển R10. **Cần thêm task (b) vào `plan/R10.md` trước khi chạy R10** (PR plan riêng; PR hồ sơ chỉ được sửa `docs/**`).
  - H-03 (vừa): ở 360 chấm dẫn menu và nút header bị ẩn; khôi phục theo wireframe 360 của doc, kèm test.
  - H-04 (thấp): test font `<h1>` thêm `document.fonts.check`.
  - H-05 (thấp): `@media (prefers-reduced-motion: reduce)` trong `style.css`.
  - H-06 (thấp): `tests/_policy.py` chỉ miễn trừ `rel=alternate hreflang` khi `href` bắt đầu bằng `SITE_URL`, kèm test (hiện `https://evil.com/x.css` lọt).
- Bản Anh chưa có JSON-LD; `og:image` bản Anh dùng chung `og.png` chữ Việt (plan R13 không yêu cầu; cân nhắc khi tiện).
- R11 đổi `SITE_URL`: phải sửa cả meta, `hreflang`, canonical của **cả hai trang**, `robots.txt`, `sitemap.xml`, JSON-LD (ghi cứng; test sẽ đỏ nếu quên).
- Flaky Chrome trong `tests/test_tools.py`, `test_site_motion.py`, `test_site_button.py` (R13 dev-02 gặp 2 lần khi tải nặng). Nên tăng timeout hoặc thử lại trong test.
- `test_css_does_not_hide_summary` không bắt rule `summary` lồng trong `@media` (siết khi tiện).
- Ảnh `screenshot.py`: dưới `--virtual-time-budget` hero còn dở intro. Nên sửa trong `screenshot.py`.
- Hai nút `.nut` ở hero sát nhau (thêm gap). Font Google qua `@import`; R10 xem lại hiệu năng.
- Số USD thật của R4, R6–R9, R12, R13: `/autodev:session-end` (`metrics.py --write`); supervisor R9 lần 2, R13 hiện là số tạm.
- Thư mục tạm untracked ở worktree supervisor: `.autodev/tmp/r12open/`, `.autodev/tmp/r9clone2/`. Xoá khi tiện (supervisor không tự xoá).

## Mốc kế tiếp
- Theo chuỗi `ROADMAP.md`: R10 (thêm task H-03..06 trước, phụ thuộc R7, R8, R13 đều xong) → R11 (chờ leader bật Pages).
