# Nhật ký auto-dev (supervisor)

## R1: Hạn chót — merged 2026-10-15 (PR #5, `63cc7b0`)

Kiểm trên nhánh `milestone/R1` (`11226c2`), supervisor tự chạy:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → "sạch" (**danh sách `smoke` rỗng**, không chạy lệnh nào). CI `test` pass 2 lần; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | exit 0, sạch |
| 2 | `tests/test_due.py` 0 failed, ≥ 7 test (A1) | `uv run pytest -q tests/test_due.py` | 24 passed |
| 3 | `pytest` 0 failed (A3), ruff sạch (A4) | `uv run pytest -q`; `uv run ruff check .` | 30 passed; All checks passed |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | 15–20 | 4 | B3 0,28 |
| USD (worker + supervisor) | ~4 | 0,71 (chưa gồm supervisor; script không cộng tạm `~`) | B3 0,18 |
| Số vòng review | 3–5 | 3 (+1 gọi lại reviewer do trả "placeholder") | trong khoảng |

Lệch > 2 lần (thấp hơn): ước tính lấy từ mốc plugin có Postgres/pytest chậm; ở đây pytest 0,1 giây và task rất nhỏ. Mốc sau nên ước tính ~5 phút, ~1 USD worker. Số USD thật sau `/autodev:session-end` (`metrics.py --write`).

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| File cũ thiếu `due` | `test_set_due_on_legacy_file`, `test_list_legacy_file_without_due` |
| Lỗi vẫn ghi file | `test_set_due_missing_id_keeps_bytes`, `test_cli_due_errors_keep_file`, `test_set_due_missing_file_not_created` |
| Ngày hợp lệ giả | `test_valid_due_bad` (`2026-02-30`, `2026-13-40`, `mai`, `2026-1-5`); **còn hở ở store**: H-01 |
| `--due` bị nuốt vào tên | `test_cli_add_due_not_swallowed` |

### Kiểm biên độc lập (CLI thật, `TODO_FILE` tạm)
- `add --due 2026-10-20` (không tên), `add x --due` (thiếu giá trị) → thoát 2, không tạo file. Đúng.
- `add x --due 2026-W01-1`, `due 1 2026-W01-1`, `due 2 2026-02-29` → thoát 2, file giữ nguyên hash. `due 2 2028-02-29` (năm nhuận) → thoát 0. Đúng.
- `store.valid_due("2026-W01-1")` và `valid_due("20261020  ")` → True: lỗ hổng H-01 (store), CLI chặn được.

## R2: Lọc việc quá hạn + H-01 — merged 2026-10-16 (PR #8, `0aa2992`)

Kiểm trên nhánh `milestone/R2` (`d0cdd15`), supervisor tự chạy:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `[smoke] ok A5 overdue`, "sạch". CI `test` pass 2 lần; main không có check bắt buộc (repo private, API protection 403).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | exit 0, sạch |
| 2 | `verify.py --smoke` sạch (A5) | `python3 .../scripts/verify.py --smoke`; chuỗi A5 bằng tay | `ok A5 overdue`; tay: đúng 1 dòng `qua-han` |
| 3 | `tests/test_overdue.py` 0 failed, ≥ 6 test (A2) | `uv run pytest -q tests/test_overdue.py` | 7 passed |
| 4 | pytest 0 failed (A3), ruff sạch (A4) | `uv run pytest -q`; `uv run ruff check .` | 52 passed; All checks passed |
| 5 | H-01: `valid_due` từ chối `2026-W01-1`, `"20261020  "`, `" 2026-10-20"` | `uv run pytest -q tests/test_valid_due_strict.py tests/test_due.py`; tái hiện với `store.py` của main cũ | 34 passed; code cũ trả `[True, True, False]` (lỗi tái hiện), code mới đều False |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~10–15 | 4 | B3 0,40 |
| USD (worker + supervisor) | ~3 | 0,72 + ~0,75 | B3 ~0,49 |
| Số vòng review | 3–4 | 3 | trong khoảng |

Lệch > 2 lần (phút, thấp hơn): task nhỏ, pytest 0,1 giây; ước tính lấy 8 phút R1 (cả phiên) thay vì 4 phút worker. Mốc cùng cỡ sau: ~5 phút, ~0,8 USD worker.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Đạt sẵn nhờ dựng dữ liệu | dữ liệu 5 loại trong `tests/test_overdue.py`, `tests/test_cli_overdue.py`; smoke A5 đòi đúng 1 dòng |
| 2. Sai biên `<=` | test `due == today`; supervisor chạy A5 với `TODO_TODAY=2026-10-15` → chỉ `qua-han` |
| 3. Phụ thuộc đồng hồ | mọi test đặt `TODO_TODAY`; supervisor: `TODO_TODAY=2026-10-17` → 3 dòng đúng thứ tự; bỏ biến (máy 2026-10-16) → 2 dòng, đúng |
| 4. Sắp đúng do may | test tạo hạn ngược `10-12, 10-10, 10-11` |
| 5. H-01 nửa vời | `_ok_date` đã xoá, CLI gọi `store.valid_due`; test CLI cũ (`2026-02-30`, `mai`) xanh |
| 6. `due` hỏng | test `"due": "abc"`; supervisor thêm `null`, `123` → bỏ qua, không lỗi |

### Kiểm biên độc lập (CLI thật, `TODO_FILE` tạm)
- `TODO_TODAY=` (rỗng) → stderr "TODO_TODAY không hợp lệ: ''", thoát 2. Đúng.
- File chưa có, không `TODO_TODAY` → không in, thoát 0. `overdue x` → thoát 2. Đúng.
- `due` là `"abc"`, `null`, `123` cùng hai việc cùng hạn `2026-01-01` → chỉ in hai việc hợp lệ, theo `id` 4, 5. Đúng.

### Ghi chú không chặn
- Test H-01 ở `tests/test_valid_due_strict.py`, test CLI ở `tests/test_cli_overdue.py` (file mới); plan ghi `tests/test_due.py`. Lệch tên file, không đổi hành vi: chấp nhận như điều chỉnh (a).
- Tham số `today` của `store.overdue` che hàm `store.today()`; docstring đầu `cli.py` một dòng dài.

## R4: Công cụ nhìn + luật tài nguyên mới — merged 2026-10-16 (PR #20, `34b1066`)

Kiểm trên nhánh `milestone/R4` (`f87f0b1`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → "sạch (không có lỗi mới so với baseline)", test_guard báo 1 thay đổi đã giải trình (`test_balanced_tags_no_script` → `test_balanced_tags`, đúng dev-04); `verify.py --smoke` → `ok A5 overdue`, "sạch". CI `test` pass 2 lần; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | exit 0, sạch |
| 2 | `tests/test_tools.py` 0 failed, ≥ 5 test, không skip (D1) | `uv run pytest -q -rs tests/test_tools.py` | 10 passed, 0 skipped (40 giây) |
| 3 | `tests/test_site_policy.py` 0 failed, ≥ 6 test (L2) | `uv run pytest -q -rs tests/test_site_policy.py` | 16 passed |
| 4 | `screenshot.py` ra 4 PNG đúng bề rộng | `uv run python scripts/screenshot.py`; `png_size` từng file | exit 0; `360-light/dark` (360, 800), `1280-light/dark` (1280, 800) |
| 5 | pytest 0 failed (L3), ruff sạch (L4), L5 in `200` hai dòng | `uv run pytest -q`; `uv run ruff check .`; lệnh L5 trong `criteria.md` | 95 passed; All checks passed; `200` `200` |

L1: `uv run pytest -q tests/test_site.py` → 11 passed.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~8–15 | 20 | B3 1,35 |
| USD (worker + supervisor) | ~1,8 | 1,06 + ~0,77 | B3 ~1,02 |
| Số vòng review | 4–6 | 4 (mỗi task 1 vòng) | trong khoảng |

Phút vượt cận trên do test Chrome (~40 giây mỗi lần chạy `test_tools.py`, verify chạy nhiều lần); không lệch quá 2 lần.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Ảnh 360 giả | `test_four_pngs_with_exact_widths` (header PNG) + `test_360_viewport_inside_iframe_is_360` (`innerWidth` = 360 trong iframe); supervisor: 4 ảnh thật đúng 360 / 1280 |
| 2. Tối không áp dụng | `test_dark_mode_applied_only_in_dark[360/1280]`; supervisor chạy lại 3 lần, xanh cả 3 |
| 3. Tràn bị `overflow-x:hidden` che | `test_metrics_overflow_caught_despite_overflow_hidden` (exit 1, có `div#wide`) |
| 4. Nới luật quá tay | 6 ca âm trong `tests/test_site_policy.py`; supervisor thử thêm (dưới) |

### Kiểm biên độc lập (`tests/_policy.check`, `page_metrics.py` trên `site/`)
- `<script type="module">` inline → vi phạm; `type="Application/LD+JSON"` → hợp lệ; `//evil.example` trong `<link>` → 2 vi phạm (không https, domain lạ); `@import "https://evil.example/x.css"` (không `url()`) → bắt; `fonts.googleapis.com.evil.example` → bắt; `<a href="HTTP://…">` → bắt. Đúng.
- **Hở nhỏ:** `src=".../gsap@latest/3.12.5/x.js"` có `integrity` + `crossorigin` → **không** vi phạm (regex ghim khớp `/3.12.5/` nên bỏ qua `@latest`). Ca giả tạo, không chặn; ghi H-02 cho R7 (mốc đầu dùng CDN).
- `page_metrics.py --check-overflow` trên `site/` → exit 0, 4 tổ hợp `overflow: []`, 0 SVG, `h1` 32px `system-ui` (khớp nền D3). Ảnh tối = sáng vì `site/` chưa có CSS tối (R8).

### Ghi chú không chặn
- Worker báo `test_dark_mode_applied_only_in_dark[1280]` đỏ một lần rồi xanh; supervisor không tái hiện (3/3 xanh). Theo dõi ở R6–R8.
- Luật L2 chưa kiểm `srcset`, `javascript:` (ngoài phạm vi plan).

<!-- metrics:start (tự sinh bởi .autodev/metrics.py, đừng sửa tay) -->
<!-- metrics:end -->
