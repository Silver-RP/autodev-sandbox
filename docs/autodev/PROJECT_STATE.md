# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-16 · Nguồn: duyệt mốc R6 (supervisor)

## Mốc
| Mốc | Trạng thái | Ghi chú |
|---|---|---|
| R1 | merged | PR #5; 3 task, mỗi task 1 vòng; 30 test pass |
| R2 | merged | PR #8 (`0aa2992`); 3 task, mỗi task 1 vòng; 52 test pass; đóng H-01 |
| R3 | merged | PR #14; `site/` 4 phần, test cấu trúc, smoke HTTP; 69 test pass |
| R4 | merged | PR #20 (`34b1066`); 4 task, mỗi task 1 vòng; 95 test pass; D1, L2 đạt |
| R5 | cut | leader chọn trước hướng "Quán cóc đầu ngõ" |
| R6 | merged | PR #22 (`ecd64d0`); 5 task, 6 vòng review; 126 test pass; D2, D3 đạt |

## Mục tiêu và tiêu chí
- `due-overdue`: 5/5 = **100%** (xong).
- `lazy-landing` (`docs/goals/lazy-landing/criteria.md`, bản 2): 8/17 ≈ **47%**.

| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| L1 | `uv run pytest -q tests/test_site.py` | 0 failed, ≥ 6 | 11 passed, đạt |
| L2 | `uv run pytest -q tests/test_site_policy.py` | 0 failed, ≥ 6 | 16 passed, đạt |
| L3 | `uv run pytest -q` | 0 failed | 126 passed, đạt |
| L4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| L5 | smoke HTTP (`criteria.md`) | `200` hai dòng | đạt |
| D1 | `uv run pytest -q tests/test_tools.py` | 0 failed, ≥ 5, không skip | 10 passed, đạt |
| D2 | `uv run pytest -q tests/test_design_doc.py` | 0 failed | 7 passed, đạt |
| D3 | `uv run pytest -q tests/test_site_visual.py` | 0 failed, ≥ 5 | 8 passed, 0 skip, đạt |
| D4 | `uv run python scripts/page_metrics.py --check-overflow` | exit 0 | sáng exit 0 (360, 1280); tối thuộc R8 |
| D5–D7, E1–E5 | xem `criteria.md` | | chưa |

## Kiến trúc hiện nay
- `src/todo/`: CLI todo (`add --due`, `list`, `overdue`, `done`, `due`); luật ngày duy nhất ở `store.valid_due`.
- `site/`: landing "Quán cóc đầu ngõ" 4 phần (`hero`, `dich-vu`, `cach-lam`, `lien-he`). `style.css`: token 6 màu sáng ở `:root` (`--color-*`), `@import` Google Fonts (Baloo 2, Be Vietnam Pro), menu bảng liền có chấm dẫn, chưa có CSS tối. 5 SVG inline (`currentColor`, nét 2,5): hero (ghế + ly), 3 biểu tượng gói, ghế trống ở liên hệ.
- `scripts/screenshot.py`: Chrome headless; 1280 trực tiếp, < 1000 qua iframe; tối bằng `--blink-settings`; ảnh ở `.autodev/shots/` (gitignore).
- `scripts/page_metrics.py`: JSON mỗi tổ hợp (`innerWidth`, `overflow`, `svg_by_section`, `h1`, `body_font`, `colors`); `--check-overflow` exit 1 khi tràn. `h1.font_family` là chuỗi khai báo, không chứng minh font đã tải (H-04).
- `tests/_policy.py`: `check(html, css)` cho L2.

## Quy tắc → test bảo vệ
| Quy tắc | Test bảo vệ |
|---|---|
| Lỗi không ghi file; ngày sai thoát 2 | `tests/test_due.py`, `tests/test_valid_due_strict.py`, `tests/test_cli_overdue.py` |
| Quá hạn: biên, sắp, không phụ thuộc đồng hồ | `tests/test_overdue.py` |
| Ảnh 360 thật (PNG + `innerWidth`), tối thật | `tests/test_tools.py` |
| Luật tài nguyên L2 | `tests/test_site_policy.py` |
| Spec thiết kế đủ (D2) | `tests/test_design_doc.py` |
| Hex `:root` = bảng màu sáng đọc từ doc; không hex rời | `tests/test_site_visual.py` |
| SVG ≥ 3 phần tử vẽ, `<title>`/`aria-hidden`, `viewBox` | `tests/test_site_hero.py`, `tests/test_site_menu.py` |
| Nút `mailto:` bắt đầu bằng động từ; không `→`, không `uppercase` | `tests/test_site_content.py` |

## Lỗ hổng mở
| Mã | Mức | Mô tả | Mốc nhận |
|---|---|---|---|
| H-02 | thấp | `_policy` bỏ qua `@latest` khi URL cũng có đoạn `/X.Y.Z/` (vd `gsap@latest/3.12.5/x.js`) | R7 |
| H-03 | vừa | Ở 360: dấu chấm dẫn menu bị ẩn (`.cham {display:none}`) và nút header bị ẩn, lệch wireframe 360 của doc; không test nào bắt | R8 |
| H-04 | thấp | Test font `<h1>` chỉ đọc `font-family` khai báo; cần `document.fonts.check` để chứng minh Baloo 2 đã tải | R8 |

## Nợ không chặn
- Tham số `today` của `store.overdue` che `store.today()`.
- `test_dark_mode_applied_only_in_dark[1280]` từng đỏ một lần ở R4; R6 không tái hiện. Theo dõi.
- L2 chưa kiểm `srcset`, `javascript:`.
- Font Google qua `@import` trong CSS (tải muộn một nhịp); xem lại ở R10.
- `test_mobile_price_wraps_below_name` yếu (dùng `or`). SVG hero và ghế trống dùng `--color-muc-bang`: R8 đổi cho nền tối.

## Quyết định gần đây
- 2026-10-16: merge R6 (PR #22). Không duyệt đề xuất sửa doc để hợp thức việc ẩn nút header ở 360; ghi H-03, H-04 cho R8.
- 2026-10-16: merge R4 (PR #20). Ghi H-02 cho R7.
- 2026-10-16: merge R3 (PR #14); mục tiêu `lazy-landing` bản 2; R5 cắt.
- 2026-10-16: merge R2 (PR #8). `due-overdue` 5/5.
