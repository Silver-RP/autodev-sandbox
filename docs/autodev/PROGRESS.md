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

## R6: Dựng trang "Quán cóc đầu ngõ" — merged 2026-10-16 (PR #22, `ecd64d0`)

Kiểm trên nhánh `milestone/R6` (`9e29775`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → "sạch (không có lỗi mới so với baseline)", test_guard báo 1 thay đổi đã giải trình (`skipif` ở `tests/test_site_visual.py`, file mới, đúng dev-01.3); `verify.py --smoke` → `ok A5 overdue`, "sạch". CI `test` pass 2 lần; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | exit 0, sạch |
| 2 | 4 file test 0 failed; `test_site_visual.py` ≥ 5 (D3); `test_design_doc.py` xanh (D2); `test_site.py` không sửa (L1) | `uv run pytest -q -rs tests/test_design_doc.py tests/test_site_visual.py tests/test_site.py tests/test_site_policy.py`; `--collect-only tests/test_site_visual.py`; `git diff --stat 13a10f1 origin/milestone/R6 -- tests/test_site.py tests/test_site_policy.py` | 42 passed, 0 skipped; 8 test; diff rỗng |
| 3 | `page_metrics.py --check-overflow --modes light` exit 0 | lệnh đó | exit 0; 360 và 1280 `overflow: []`; SVG theo phần: hero 1, dich-vu 3, lien-he 1; `<h1>` 40px (360) / 64px (1280) "Baloo 2" |
| 4 | Reviewer nhìn 4 ảnh, ghi nhận xét | đọc `.autodev/reviews/dev-05-r2.json`; supervisor tự chụp `screenshot.py --height 3000` và xem 360-light, 1280-light | có nhận xét; ảnh: đúng bố cục doc (bảng hiệu gạch trà đá, hero 2 cột / 1 cột, menu bảng liền viền 3px, số trong tròn trà đá, ghế trống), dấu tiếng Việt đúng. Tối = sáng (R8) |
| 5 | L5 in `200` hai dòng | lệnh L5 trong `criteria.md` | `200` `200` |

L3: `uv run pytest -q` → 126 passed; L4: ruff "All checks passed!".

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 5 | 5 | 0 |
| Phút worker | ~20–35 | 44 | B3 1,25 |
| USD (worker + supervisor) | ~3,3 | 2,25 + ~0,89 | B3 ~0,95 |
| Số vòng review | 5–8 | 6 (dev-05 2 vòng) | trong khoảng |

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. SVG cho có | test SVG trong `tests/test_site_hero.py`, `tests/test_site_menu.py` (≥ 3 phần tử vẽ, `<title>`/`aria-hidden`, `viewBox`); supervisor xem ảnh: ghế, ly, nồi lẩu có hình rõ |
| 2. Lệch hướng | `test_root_hex_equal_light_palette_from_doc` (đọc doc), `test_no_loose_hex_outside_root`; supervisor: 6 hex `:root` đúng doc, 0 hex ngoài `:root`, 0 gradient/bóng. **Lệch wireframe 360 không test nào bắt:** H-03 |
| 3. Phá cấu trúc R3 | `test_site.py` 11 passed, diff rỗng |
| 4. Font không tải mà test xanh | **chưa chặn bằng test**: `test_h1_font_loaded_and_differs_from_body` đọc chuỗi `font-family` khai báo. Chỉ chặn bằng mắt (ảnh có chữ Baloo 2). H-04 |

### Kiểm biên độc lập
- CSS: `:root` có đúng 6 hex của doc; không hex ngoài `:root`; `white` (chữ trên nút đỏ) đúng doc dòng 23. Không `text-transform: uppercase`; "LƯỜI CODE STUDIO" viết hoa bằng nội dung, doc dòng 76 cho phép.
- 5 SVG: hero `role="img"` + `<title>`; 4 SVG trang trí `aria-hidden`; tất cả `stroke="currentColor"`, nét 2,5.
- Ảnh 360: **dấu chấm dẫn bị ẩn** (`.cham {display:none}` ≤ 40rem) trong khi doc (wireframe 360) ghi "dấu chấm dẫn co lại" và đó là điểm nhấn duy nhất; **nút header bị ẩn** ở 360 trong khi wireframe 360 có `[Gửi thư]`. Ghi H-03 (vừa), giao R8 (mốc 360/responsive).

### Quyết định
- Merge: 5/5 tiêu chí cấp mốc có bằng chứng tự chạy; lệch wireframe 360 là chi tiết responsive, không làm sai D2/D3/L1.
- Đề xuất (c) 1 của worker (sửa doc cho khớp việc ẩn nút header): **không duyệt**; doc là nguồn, R8 khôi phục theo doc (H-03).
- Đề xuất (c) 2 (`document.fonts.check`): duyệt hướng, ghi H-04 cho R8.

## R7: Chuyển động và tương tác — merged 2026-10-16 (PR #24, `1a66df0`)

Kiểm trên nhánh `milestone/R7` (`e59ee5d`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → "sạch (không có lỗi mới so với baseline)", test_guard báo 2 `pytest.skip` khi không có mạng ở `tests/test_site_motion.py`, đã giải trình (dc954cb); `verify.py --smoke` → `ok A5 overdue`, "sạch". CI `test` pass 2 lần; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch |
| 2 | motion + policy 0 failed; `test_site_motion.py` ≥ 4 (D6) | `uv run pytest -q -rs tests/test_site_motion.py tests/test_site_policy.py`; `grep -c "^def test_"` | 30 passed, 0 skipped (có mạng); 13 test |
| 3 | `test_site_visual.py`, `test_site.py` xanh; overflow sáng exit 0 | `uv run pytest -q tests/test_site_visual.py tests/test_site.py tests/test_site_button.py`; `page_metrics.py --check-overflow --modes light` | 27 passed; exit 0 |
| 4 | Ảnh trạng thái cuối timeline và ảnh tắt JS đủ nội dung | supervisor tự chụp 1280: Chrome headless qua CDP (Node, thời gian thật, chờ 3 s); bản sao tạm bỏ mọi `<script>` | timeline `progress()` = 1, `h1` và `.hero-hinh` opacity 1, transform `none`; ảnh cuối và ảnh không JS đủ 4 phần; không JS thì nút vui ẩn (không nút chết); sau khi bấm: `aria-pressed=true`, chữ "Đang lười giúp…", ghế xanh `translateX(16px)` |

L3: `uv run pytest -q` → 148 passed. H-02 đóng: ca `gsap@latest/3.12.5` trong `test_site_policy.py`; supervisor gọi `_policy._pinned` trực tiếp: `@latest/3.12.5` False, `@3.12` False, `@3.12.5` True, cdnjs `/3.12.5/` True.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~10–20 | 34 | B3 1,69 |
| USD (worker + supervisor) | ~2,3 | 1,38 + ~1,00 | B3 ~1,04 |
| Số vòng review | 3–5 | 3 | trong khoảng |

Phút lệch dưới 2 lần; nguyên nhân chính: Chrome headless không chạy `--blink-settings=scriptEnabled=false` và gần như không phát rAF, worker phải đổi cách test (iframe `sandbox`, đẩy đồng hồ gsap).

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. `gsap.from` làm ẩn sẵn, CDN lỗi thì trắng | `test_js_disabled_sections_visible` (iframe `sandbox` không `allow-scripts`, thay cờ blink không chạy), `test_broken_cdn_sections_visible`, `test_css_hides_nothing_outside_js_selector`; supervisor chụp ảnh không JS |
| 2. Rắc hiệu ứng | `test_single_timeline_and_no_section_loop`, `test_only_one_timeline_still`; supervisor đọc `main.js`: 1 timeline (2 bước hero), 1 tương tác |
| 3. Bỏ qua giảm chuyển động | `test_reduced_motion_no_timeline`, `test_click_reduced_motion_instant`; supervisor chạy `--force-prefers-reduced-motion`: `heroTimeline` = null, opacity 1. **CSS chưa có `@media (prefers-reduced-motion: reduce)`** như quy ước plan: H-05 |
| 4. SRI sai, script bị chặn âm thầm | `test_sri_hash_matches_cdn_file`, `test_with_cdn_gsap_present_and_sections_visible` (skip khi không mạng); supervisor thấy `window.gsap` có mặt |

### Kiểm biên độc lập
- Thời gian thật (CDP, không virtual-time): timeline chạy hết, hero về trạng thái gốc. Với `--virtual-time-budget` thì hero kẹt ở opacity ~0,8 / 0 (rAF không phát): lỗi môi trường headless, không phải trang; nhưng ảnh `screenshot.py` ở R8+ sẽ chụp hero dở dang nếu không đẩy đồng hồ gsap.
- Bấm nút 3 lần → `aria-pressed` true/false/true đúng; giảm chuyển động → ghế dịch tức thì (`gsap.set`).
- `_pinned` từ chối gói npm có scope (`/npm/@gsap/react@2.1.0/…`: tag `gsap` không phải X.Y.Z): chặt quá, không phải lỗ hổng; ghi nợ.

### Quyết định
- Merge: 4/4 tiêu chí cấp mốc có bằng chứng tự chạy; D6 đạt; đóng H-02. `lazy-landing` 9/17 ≈ 53%.
- H-05 (thấp, R8): thêm `@media (prefers-reduced-motion: reduce)` vào `style.css` và test. Supervisor phát hiện sau khi đã merge; không chặn vì CSS hiện không có chuyển động nào.
- Không có đề xuất (c).

## R8: Chế độ tối và truy cập — merged 2026-10-16 (PR #26, `8a5a9ba`)

Kiểm trên nhánh `milestone/R8` (`7e39a4e`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". Main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch |
| 2 | `contrast.py` exit 0 (D5) | `uv run python scripts/contrast.py`; thêm `--widths 360,1280` | "OK: mọi cặp màu đạt WCAG AA", exit 0 cả hai lệnh |
| 3 | `page_metrics.py --check-overflow` exit 0, 4 tổ hợp (D4) | `uv run python scripts/page_metrics.py --check-overflow` | exit 0; 4 dòng JSON (360/1280 × light/dark), `innerWidth` đúng, `overflow: []` cả 4 |
| 4 | `test_site_a11y.py` + `test_tools.py` 0 failed | `uv run pytest -q tests/test_site_a11y.py tests/test_tools.py` | 22 passed |
| 5 | D3, D6, L1, L2 xanh; nhìn 4 ảnh | `uv run pytest -q tests/test_site_visual.py tests/test_site_motion.py tests/test_site.py tests/test_site_policy.py tests/test_site_dark.py`; `scripts/screenshot.py` | 54 passed; supervisor xem 4 ảnh: tối là bảng riêng (nền xanh mực `#1B2A3A`, chữ `#E8EEF2`, nút san hô/xanh trời chữ tối), không phải "gần đen + accent axit"; tiếng Việt đúng dấu; không tràn. Ảnh 1280 có hero mờ do intro dở dưới `--virtual-time-budget` (đã biết); bản sao bỏ `<script>` chụp 1280 tối: ghế, ly, bàn rõ, đủ màu |

L3: `uv run pytest -q` → 165 passed (trong `verify.py`). D4, D5 đạt.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~15–25 | 43 | B3 1,73 |
| USD (worker + supervisor) | ~2,8 | 1,31 + ~1,09 | B3 ~0,86 |
| Số vòng review | 4–6 | 4 | trong khoảng |

Phút lệch dưới 2 lần; nguyên nhân: Chrome headless (mỗi lần đo 4 tổ hợp) và 1 lần verify bị chặn ở dev-02 (`pytest.skip` mới).

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Đo trên token chứ không trên trang thật | `contrast.py` lấy `getComputedStyle` qua `page_metrics.py` (HTTP); `test_contrast_low_contrast_page_fails`; supervisor bơm `--color-bui-duong: #3A4A5A` (tối) vào bản sao → bảng trượt `p.mo-ta`, `small` 1,60 < 4,5, exit 1 |
| 2. Nền trong suốt coi là trắng | `test_contrast_transparent_block_uses_ancestor_bg`; supervisor bơm `.mo-ta {background: transparent; color: #DDD}` (sáng) → trượt 1,24 trên nền `rgb(242,245,240)` của cha |
| 3. `outline: none` không thay thế | `test_khong_go_outline_neu_thieu_focus_visible`, `test_bo_kiem_outline_bat_loi`, `test_focus_visible_cho_link_va_nut`. Còn hở: regex lọt `outline:0px`, chưa gắn theo selector (reviewer ghi) |
| 4. Tối chỉ đổi nền, SVG vẫn đen | `test_svg_has_no_hardcoded_hex_paint`, `test_dark_hex_equals_doc_dark_palette`; supervisor xem ảnh tối 360 và 1280 (không JS) |

### Kiểm biên độc lập
- Lỗi chỉ ở chế độ tối (bản sao, đổi một token tối): `contrast.py` mặc định bắt được, exit 1, ở cả 360 và 1280 với `--widths`; `--modes light` vẫn exit 0 (đúng, lỗi chỉ ở tối).
- Chữ sáng trong khối trong suốt trên nền sáng: trượt đúng (xem pre-mortem 2).
- `page_metrics.py` gộp khối chữ theo bộ (màu, nền, cỡ, đậm): mọi tổ hợp khác nhau đều được đo, không chỉ phần tử đầu. Không đo trạng thái `:hover`/`:focus` (nợ).

### Quyết định
- Merge: 5/5 tiêu chí cấp mốc có bằng chứng tự chạy; D4, D5 đạt. `lazy-landing` 11/17 ≈ 65%.
- H-03, H-04, H-05 **chưa đóng**: plan R8 (duyệt ở PR #17, trước khi giao các H này cho R8) không có task cho chúng. Không chặn merge vì không thuộc tiêu chí plan. Chuyển mốc nhận sang R10 (mốc đó cũng xem lại font và CSS; R12 chạy ngay sau R8 nên không kịp thêm task). Plan R10 cần thêm task (b) cho ba H này trước khi chạy; PR hồ sơ chỉ được sửa `docs/autodev/**` nên supervisor không sửa plan ở đây (xem HANDOFF).
- Bài học: giao H-xx cho một mốc mà plan mốc đó đã duyệt thì phải thêm task vào plan ngay lúc giao, nếu không mốc sẽ chạy hết mà không đóng H nào.
- Không có đề xuất (c).

## R12: Mở rộng nội dung (FAQ, dự án ví dụ) — merged 2026-10-16 (PR #28, `b7e2529`)

Kiểm trên nhánh `milestone/R12` (`b49a0bc`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch |
| 2 | `test_site_content.py` 0 failed, ≥ 4 test (E4) | `uv run pytest -q tests/test_site_content.py` | 12 passed |
| 3 | `contrast.py`, `page_metrics.py --check-overflow` exit 0; `test_site_a11y.py`, `test_site.py` xanh | `uv run python scripts/contrast.py`; `uv run python scripts/page_metrics.py --check-overflow`; `uv run pytest -q tests/test_site_a11y.py tests/test_site.py` | "OK: mọi cặp màu đạt WCAG AA" exit 0; overflow exit 0; 17 passed |

L3: `uv run pytest -q` lần đầu 172 passed, 1 failed (`test_tools.py::test_metrics_svg_h1_font_and_repeat`, lỗi subprocess Chrome); chạy lại riêng → passed; `verify.py` (chạy trước đó) sạch. Ghi nợ flaky cùng họ `test_tools.py` (Chrome headless). L4: ruff sạch. E4 đạt.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~10–20 | 31 | B3 1,53 |
| USD (worker + supervisor) | ~2,3 | 0,99 + ~1,16 | B3 ~0,94 |
| Số vòng review | 3–5 | 3 | trong khoảng |

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Dự án hư cấu trông như thật | test `test_site_content.py` (chữ "ví dụ" mỗi `article`, từ cấm toàn trang); supervisor đọc 3 thẻ: tên đều có "(ví dụ)", `grep -ic "khách hàng nói\|đánh giá\|testimonial"` → 0 |
| 2. FAQ dài vỡ 360 / tụt tương phản | `contrast.py`, `--check-overflow` exit 0 với FAQ **đóng**; supervisor thêm bản sao `<details open>` (xem kiểm biên) |
| 3. `summary` bị ẩn | `test_css_does_not_hide_summary`; supervisor đọc `style.css`: 3 rule `display: none` (`button.nut[hidden]`, `header .nut`, `.cham` trong `@media`) không chạm `summary`/`details`; `summary:focus-visible` có `outline`. Còn hở: regex không bắt rule lồng trong `@media` (reviewer ghi) |

### Kiểm biên độc lập
- Mở cả 4 `<details>` (bản sao `.autodev/tmp/r12open/`, `<details open>`): `contrast.py --widths 360,1280` → exit 0; `page_metrics.py --check-overflow` → exit 0, 4/4 tổ hợp `overflow: []`. Câu trả lời FAQ (ẩn khi đóng) cũng đạt AA.
- Nội dung: FAQ trả lời thẳng giá, thời gian, sửa, tên miền ("Của bạn…"); thứ tự section `hero, dich-vu, cach-lam, du-an, hoi-dap, lien-he` đúng quy ước; heading `h2` → `h3` không nhảy cấp.

### Quyết định
- Merge: 3/3 tiêu chí cấp mốc có bằng chứng tự chạy; E4 đạt. `lazy-landing` 12/17 ≈ 71%.
- Chấp nhận (a) dev-01 nới 3 test cũ từ `== 4` section sang `>= 4` (thêm section là đúng phạm vi; số assert giữ nguyên).
- Không đóng H nào (R12 không nhận H). Không có đề xuất (c).

<!-- metrics:start (tự sinh bởi .autodev/metrics.py, đừng sửa tay) -->
<!-- metrics:end -->
