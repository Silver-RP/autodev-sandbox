# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-16 · Nguồn: duyệt mốc R4 (supervisor)

## Mốc
| Mốc | Trạng thái | Ghi chú |
|---|---|---|
| R1 | merged | PR #5; 3 task, mỗi task 1 vòng; 30 test pass |
| R2 | merged | PR #8 (`0aa2992`); 3 task, mỗi task 1 vòng; 52 test pass; đóng H-01 |
| R3 | merged | PR #14; `site/` 4 phần, test cấu trúc, smoke HTTP; 69 test pass |
| R4 | merged | PR #20 (`34b1066`); 4 task, mỗi task 1 vòng; 95 test pass; D1, L2 đạt |
| R5 | cut | leader chọn trước hướng "Quán cóc đầu ngõ" |

## Mục tiêu và tiêu chí
- `due-overdue`: 5/5 = **100%** (xong).
- `lazy-landing` (`docs/goals/lazy-landing/criteria.md`, bản 2): 6/17 ≈ **35%**.

| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| L1 | `uv run pytest -q tests/test_site.py` | 0 failed, ≥ 6 | 11 passed, đạt |
| L2 | `uv run pytest -q tests/test_site_policy.py` | 0 failed, ≥ 6 | 16 passed, đạt |
| L3 | `uv run pytest -q` | 0 failed | 95 passed, đạt |
| L4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| L5 | smoke HTTP (`criteria.md`) | `200` hai dòng | đạt |
| D1 | `uv run pytest -q tests/test_tools.py` | 0 failed, ≥ 5, không skip | 10 passed, đạt |
| D4 | `uv run python scripts/page_metrics.py --check-overflow` | exit 0 | exit 0 trên `site/` hiện tại (chưa tính đạt: thuộc R8) |
| D2, D3, D5–D7, E1–E5 | xem `criteria.md` | | chưa |

## Kiến trúc hiện nay
- `src/todo/`: CLI todo (`add --due`, `list`, `overdue`, `done`, `due`); luật ngày duy nhất ở `store.valid_due`.
- `site/`: landing tĩnh 4 phần (`hero`, `dich-vu`, `cach-lam`, `lien-he`), `style.css` (`system-ui`, chưa có CSS tối, 0 SVG).
- `scripts/screenshot.py`: Chrome headless; 1280 chụp trực tiếp, < 1000 qua trang khung `/__frame__.html` (iframe); tối bằng `--blink-settings=preferredColorScheme=0`; `png_size`; ảnh ở `.autodev/shots/` (gitignore).
- `scripts/page_metrics.py`: JSON mỗi tổ hợp (`innerWidth`, `overflow`, `svg_by_section`, `h1`, `body_font`, `colors`); `--check-overflow` exit 1 khi tràn. Dùng lại `serve`/`page_url` của `screenshot.py`.
- `tests/_policy.py`: `check(html, css)` cho L2 (danh sách host cho phép, SRI, ghim phiên bản, script inline chỉ ld+json).

## Quy tắc → test bảo vệ
| Quy tắc | Test bảo vệ |
|---|---|
| Lỗi không ghi file; ngày sai thoát 2 | `tests/test_due.py`, `tests/test_valid_due_strict.py`, `tests/test_cli_overdue.py` |
| Quá hạn: biên, sắp, không phụ thuộc đồng hồ | `tests/test_overdue.py` |
| Ảnh 360 thật (PNG + `innerWidth`), tối thật | `tests/test_tools.py` |
| Tràn bị `overflow-x:hidden` che vẫn bắt | `test_metrics_overflow_caught_despite_overflow_hidden` |
| Luật tài nguyên L2 (6 ca âm, ca dương, quét đệ quy `site/`) | `tests/test_site_policy.py` |

## Lỗ hổng mở
| Mã | Mức | Mô tả | Mốc nhận |
|---|---|---|---|
| H-02 | thấp | `_policy` bỏ qua `@latest` khi URL cũng có đoạn `/X.Y.Z/` (vd `gsap@latest/3.12.5/x.js`) | R7 |

## Nợ không chặn
- Tham số `today` của `store.overdue` che `store.today()` (`store.save` nguyên tử đã xong ở PR #11).
- `test_dark_mode_applied_only_in_dark[1280]` từng đỏ một lần ở worker; supervisor 3/3 xanh. Theo dõi.
- L2 chưa kiểm `srcset`, `javascript:`.

## Quyết định gần đây
- 2026-10-16: merge R4 (PR #20). Chấp nhận đổi tên `test_balanced_tags_no_script` → `test_balanced_tags` (đúng dev-04). Ghi H-02 cho R7.
- 2026-10-16: merge R3 (PR #14); mục tiêu `lazy-landing` bản 2; R5 cắt.
- 2026-10-16: merge R2 (PR #8). `due-overdue` 5/5.
