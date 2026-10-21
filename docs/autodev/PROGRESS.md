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

## R9: SEO và chia sẻ — **chưa đạt, không merge** 2026-10-16 (PR #30 mở)

Kiểm trên nhánh `milestone/R9` (`17f1ecb`), supervisor tự chạy (chế độ B, `--review-only`):
`verify.py` → **"[test] 1 lỗi mới so với baseline: `tests/test_site_seo.py::test_og_png_size_and_fresh`"**; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (thứ tự ghi file trên runner may mắn).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | **chưa đạt**: 1 lỗi mới (`test_og_png_size_and_fresh`) |
| 2 | `test_site_seo.py` 0 failed, ≥ 6 test (E1) | `uv run pytest -q tests/test_site_seo.py` | **chưa đạt**: 1 failed, 9 passed |
| 3 | `test_site_policy.py`, `test_site.py`, `test_site_a11y.py` xanh | `uv run pytest -q tests/test_site_policy.py tests/test_site.py tests/test_site_a11y.py` | 34 passed, đạt |

Nguyên nhân 1–2: test so `mtime` (`og.png` ≥ `og.svg`). Sau checkout, `stat` hai file cùng giây; 3/3 lần `git clone` mới: `og.svg` mới hơn `og.png` ~0,24 ms → đỏ. Worker xanh chỉ vì ảnh vừa chụp trên máy nó.

Ngoài tiêu chí số, "Quy ước chung" (ảnh chia sẻ, favicon) **chưa đạt** (supervisor nhìn `site/og.png`, đọc `og.svg`, `favicon.svg`): gradient chàm `#1e1b4b → #4338ca`, `Helvetica`, biểu tượng dấu tích, câu "Việc cần làm, gọn trong một dòng lệnh." (giới thiệu CLI todo, không phải studio); không màu token, không Baloo 2, không minh hoạ ghế/ly. Favicon là chữ "L" trên `#1f2937`, không lấy từ hero. Reviewer dev-02 "nhìn `og.png`" mà không đối chiếu hướng thiết kế.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 (+2 task (b)) | +2 |
| Phút worker | ~10–20 | 41 | B3 2,04 |
| USD (worker + supervisor) | ~1,8 | 1,45 + ~1,14 | B3 ~1,44 |
| Số vòng review | 4–6 | 5 | trong khoảng |

Phút lệch > 2 lần: phiên worker bị ngắt sau dev-01 và chạy tiếp (11:08 → 12:55), dev-02 chụp Chrome, dev-04 thêm vòng 2.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. `og:image` sai cỡ/trống | `png_size` = (1200, 630), 320 KB; chặn được cỡ, **không** chặn sai nội dung (xem trên) |
| 2. JSON-LD sai cú pháp | `test_jsonld_professional_service` (`json.loads`, `@context`, `@type`, `url`, `email`), xanh |
| 3. URL tuyệt đối lệch | `test_absolute_urls_start_with_site_url`, `test_robots_and_sitemap_use_site_url`, JSON-LD `url` = `SITE_URL`; xanh |
| 4. `og.png` cũ so với `og.svg` | test `mtime`: **chính nó hỏng** sau checkout; thay bằng hash nguồn (dev-06) |

### Kiểm biên độc lập
- Clone mới 3 lần (`git clone --no-local -b milestone/R9`): `og.png` mtime < `og.svg` cả 3 → test đỏ.
- Miễn trừ canonical trong `tests/_policy.py`: `check('<link rel="stylesheet canonical" href="https://evil.com/x.css">')` → bị chặn (đúng); `rel=" Canonical "` + domain lạ → miễn (chấp nhận được: canonical không tải tài nguyên).
- `test_site_seo.py` chạy riêng: không lỗi import (vá `sys.path` của dev-04 có tác dụng).

### Quyết định
- **Không merge PR #30.** Tiêu chí cấp mốc 1, 2 chưa đạt; ảnh chia sẻ, favicon lệch "Quy ước chung".
- (b) thêm `dev-05` (vẽ lại `og.svg`/`favicon.svg` theo token, Baloo 2, minh hoạ hero; chụp lại `og.png`) và `dev-06` (bỏ `mtime`, chunk `tEXt` `source-sha256`; `pythonpath` thay `sys.path.insert`) vào `plan/R9.md` trên nhánh `milestone/R9` (`90fd3f7`).
- (c) tự quyết: chấp nhận đề xuất của worker, bỏ tiêu chí "`og.png` mới hơn `og.svg`" (dev-02 TC1, pre-mortem 4); thay bằng kiểm hash nguồn (dev-06).
- Chấp nhận (a) dev-01 miễn trừ hẹp `rel="canonical"` trong `_policy.py`.

## R9 lần 2 — **đạt, merged** 2026-10-16 (PR #30, `91c071a`)

Worker làm (b) dev-05, dev-06 (mỗi task 1 vòng). Supervisor kiểm trên `milestone/R9` (`7a28b7e`), chế độ B `--review-only`:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch"; `uv run pytest -q` → 189 passed; ruff sạch. CI PR: 2 job `test` pass (main không có check bắt buộc).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` (worktree supervisor; clone mới + `touch site/og.svg`: test SEO vẫn xanh) | sạch, đạt |
| 2 | `test_site_seo.py` 0 failed, ≥ 6 (E1) | `uv run pytest -q tests/test_site_seo.py` | 12 passed, đạt |
| 3 | `test_site_policy.py`, `test_site.py`, `test_site_a11y.py` xanh | `uv run pytest -q tests/test_site_policy.py tests/test_site.py tests/test_site_a11y.py` | 34 passed, đạt |

"Quy ước chung" (ảnh, favicon): supervisor nhìn `site/og.png`: nền `#F2F5F0`, tên "Lười Code Studio" font Baloo 2, câu chào = `<h1>` hero, hai ghế xanh/đỏ + ly trà đá; hex trong `og.svg`, `favicon.svg` đều thuộc 6 token sáng của `style.css`; không còn Helvetica, "dòng lệnh", `#4338ca`. Favicon là ly trà đá (không `<text>`). Đạt.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 6 (4 + 2 task (b)) | +2 |
| Phút worker | ~10–20 | 64 (2 lượt) | B3 3,19 |
| USD (worker + supervisor) | ~1,8 | 3,44 + ~1 (phiên này, tạm) | B3 ~1,91+ |
| Số vòng review | 4–6 | 7 | +1 |

Lệch > 2 lần (phút): lượt 1 ảnh chia sẻ sai hướng và test `mtime` hỏng → phải chạy lượt 2 cho dev-05, dev-06; dev-02/05 chụp Chrome.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. `og:image` sai cỡ/trống | `png_size` (1200, 630), > 5 KB; nội dung: test màu token, Baloo 2, câu chào từ hero (`test_site_share.py`) + supervisor nhìn ảnh |
| 2. JSON-LD sai cú pháp | `test_jsonld_professional_service`, xanh |
| 3. URL tuyệt đối lệch | `test_absolute_urls_start_with_site_url`, `test_robots_and_sitemap_use_site_url`, xanh |
| 4. `og.png` cũ so với `og.svg` | chunk `source-sha256` (`test_og_png_size_and_matches_source`, `test_og_png_stale_when_svg_changes`, `test_png_without_text_chunk_is_stale`) |

### Kiểm biên độc lập
- `git clone --no-local -b milestone/R9` mới: `test_site_seo.py` + `test_site_share.py` 16 passed (lượt 1 đỏ 3/3 clone).
- `touch site/og.svg` trong clone: 12 passed (không còn phụ thuộc `mtime`).
- Thêm 1 byte vào `og.svg`: `test_og_png_size_and_matches_source` đỏ (đúng lúc); khôi phục thì xanh.

### Quyết định
- **Merge PR #30** (merge commit, giữ nhánh). E1 đạt → `lazy-landing` 13/17 ≈ 76%.
- Non-blocking (worker tự ghi, chuyển nợ): `og.svg` đứng riêng cần `@import` font; `png_add_text` không atomic; vài test còn `sys.path.insert`; chưa có test bảo vệ miễn trừ canonical.

## R13: Song ngữ Việt/Anh — **đạt, merged** 2026-10-16 (PR #33, `68112ec`)

Worker làm dev-01..03 (mỗi task 1 vòng, không REWORK). Supervisor kiểm trên `origin/milestone/R13` (`f405290`), chế độ B `--review-only`:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch, đạt |
| 2 | `test_site_i18n.py` 0 failed, ≥ 4 (E5) | `uv run pytest -q tests/test_site_i18n.py` | 14 passed, đạt |
| 3 | `contrast.py`, `page_metrics.py --check-overflow` exit 0 cho `/` và `/en/` | `scripts/contrast.py --pages <p>`, `scripts/page_metrics.py --pages <p> --check-overflow`, `p` = `/index.html`, `/en/index.html` | 4 lệnh exit 0; "mọi cặp màu đạt WCAG AA"; `overflow: []` mọi tổ hợp, đạt |
| 4 | `test_site_seo.py`, `test_site_policy.py` xanh (policy quét `site/en/`) | `uv run pytest -q tests/test_site_seo.py tests/test_site_policy.py`; `test_site_policy.py:17` dùng `SITE.rglob("*")` | 29 passed; có quét `site/en/`, đạt |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~10–20 | 36 | B3 1,81 |
| USD (worker + supervisor) | ~1,9 | 1,40 + ~1,26 (supervisor, tạm) | B3 ~1,40 |
| Số vòng review | 3–5 | 3 | 0 |

Không lệch quá 2 lần.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Bản Anh thiếu phần / còn chữ Việt | `test_en_sections_match_vi`, `test_en_has_no_vietnamese_visible_text`, `test_en_main_js_labels_not_vietnamese` (chỉ bắt chữ có dấu; supervisor grep thêm từ Việt không dấu thường gặp: 0) |
| 2. `hreflang` một chiều / URL tương đối | `test_hreflang_both_pages_absolute_and_correct` (hai trang, `x-default`, URL từ `SITE_URL`) |
| 3. Tài nguyên gãy ở `/en/` | `test_en_page_and_relative_assets_served`, `test_switch_links_resolve_to_the_other_page`; supervisor `curl` mọi `src`/`href` tương đối của `/en/`: 200 |
| 4. Dịch cẩu thả | reviewer đọc và nhận xét (báo cáo mốc); còn chờ leader duyệt D7 |

### Kiểm biên độc lập
- `python3 -m http.server -d site` + `curl`: `/en/`, `/en/index.html`, `../style.css`, `../main.js`, `../favicon.svg`, `../` đều 200.
- `_policy.check('<link rel="alternate" hreflang="en" href="https://evil.com/x.css">', '')` → `[]` (lọt); `rel="alternate stylesheet"` vẫn bị bắt. Ghi H-06 (thấp).
- Bản Anh không có JSON-LD (bản Việt có), `og:image` dùng chung `og.png` chữ Việt. Plan không yêu cầu; ghi nợ.

### Quyết định
- **Merge PR #33** (merge commit, giữ nhánh). E5 đạt → `lazy-landing` 14/17 ≈ 82%.
- Thay đổi ngoài mô tả task, chấp nhận: `main.js` đọc `data-on`/`data-off`; `.doi-ngon-ngu` trong `style.css`; `screenshot.py --pages`.

## R10: Hiệu năng — **đạt, merged** 2026-10-16 (PR #35, `576fd3d`)

Worker làm dev-01..03 (dev-02 REWORK 1 lần: thiếu `<noscript>` font khi tắt JS; tổng 4 vòng review). Supervisor kiểm trên `origin/milestone/R10` (`68b509b`), chế độ B `--review-only`:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch, đạt |
| 2 | `lh_check.py` exit 0 (E2) | `uv run python scripts/lh_check.py` (57 giây) | `/` perf 99/100/100, trung vị 100/100/100/100, 172928 B; `/en/` 100/100/100/100, 165107 B; "OK: đạt ngưỡng E2", exit 0, đạt |
| 3 | `test_site_visual/motion/seo/i18n` xanh | `uv run pytest -q tests/test_site_visual.py tests/test_site_motion.py tests/test_site_seo.py tests/test_site_i18n.py` | 47 passed, đạt |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~15–25 | 42 | B3 1,67 |
| USD (worker + supervisor) | ~1,5 | 1,24 + ~1,26 (supervisor, tạm) | B3 ~1,67 |
| Số vòng review | 3–5 | 4 | 0 |

Không lệch quá 2 lần.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Đo trang rút gọn / desktop | `test_lh_build_command` (`--form-factor=mobile`, URL); `main` phục vụ `site/` thật qua `http.server`; supervisor tự chạy, byte 172928 khớp trang thật |
| 2. Bỏ font / chuyển động | `test_site_visual.py`, `test_site_motion.py` xanh; diff `site/` chỉ chuyển `@import` font sang `<link rel=preload>` + `<noscript>`, không xoá font, `main.js`, section; `test_font_noscript_fallback` |
| 3. Điểm dao động | trung vị 3 lần; báo cáo và supervisor ghi đủ 3 giá trị (99–100) |
| 4. `/en/` tụt | `lh_check.py` đo `/en/` mặc định; 100/100/100/100 |

### Kiểm biên độc lập
- Không có `npx` (`PATH=/usr/bin:/bin`): "Lỗi: không có npx (cài Node.js)", exit 2. Đúng quy ước.
- `lh_check.py --runs 0`: traceback `StatisticsError` thay vì lỗi gọn. Nợ thấp, không chặn.
- Điểm phụ thuộc mạng ngoài (Google Fonts, jsDelivr); đo ở mạng chậm có thể khác.

### Quyết định
- **Merge PR #35** (merge commit, giữ nhánh). E2 đạt → `lazy-landing` 15/17 ≈ 88%.
- Chấp nhận (a): `stylesheet_hrefs` bỏ qua `<link>` trong `<noscript>`; fixture Lighthouse dựng inline trong `tests/test_tools.py`.
- (c) tự quyết: plan R10 không có task cho H-03..H-06 (việc "thêm task (b) trước R10" chưa làm). Không chặn R10 vì tiêu chí R10 đủ; H-03..H-06 chuyển sang **R14 (mới): dọn lỗ hổng site**, phụ thuộc R10, không cần Pages nên chạy được trước R11. Cần `/autodev:plan-next R14`.

## R11: Triển khai GitHub Pages — **đạt, merged** 2026-10-20 (PR #40, `099dfd9`)

Worker làm dev-01..03, mỗi task 1 vòng (3 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R11` (`ffdc755`), chế độ B `--review-only`:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc). 229 test.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | sạch, đạt |
| 2 | Sau merge: `smoke_pages.py` exit 0 (E3) | merge → `gh run watch 39428889863` (workflow `pages`, `success`, headSha `099dfd9`) → `uv run python scripts/smoke_pages.py` | "OK (lần 1): https://silver-rp.github.io/autodev-sandbox/ @ 099dfd9bcf04…", exit 0, đạt. `/en/` cũng có `meta version` = `099dfd9…`; `sitemap.xml` 200 |
| 3 | `test_site_seo.py`, `test_site_i18n.py` xanh với `SITE_URL` mới | `uv run pytest -q tests/test_site_seo.py tests/test_site_i18n.py tests/test_pages_workflow.py tests/test_smoke_pages.py tests/test_screenshot_url.py` | 45 passed, đạt; `grep -rn example.github.io site/ scripts/` rỗng |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~15–25 | 33 | B3 1,31 |
| USD (worker + supervisor) | ~1,6 | 1,04 + ~1,26 (supervisor, tạm) | B3 ~1,43 |
| Số vòng review | 3–4 | 3 | 0 |

Không lệch quá 2 lần. Chờ deploy (đo lần đầu): workflow `pages` ≈ 1 phút, smoke đạt ngay lần 1.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Deploy bản cũ / cache | `smoke_pages.py` so `meta[name=version]` với `origin/main`; `test_smoke_pages.py` (`--sha khac` → exit 1); supervisor thử cục bộ `--sha abc` → exit 1 |
| 2. Repo private chưa bật Pages | leader đổi public, bật Pages (`build_type: workflow`); `gh api .../pages` xác nhận; env `github-pages` chỉ cho `main` |
| 3. Kill giữa deploy | có `workflow_dispatch`, deploy nguyên khối theo artifact; chưa thử thật |
| 4. URL còn `example.github.io` | test dev-01 quét `site/`; grep của supervisor rỗng |

### Kiểm biên độc lập
- `smoke_pages.py` với server cục bộ dưới đường con `/autodev-sandbox` (không `/` cuối): `--sha dev` exit 0; `--sha abc --retries 2 --interval 0` exit 1; host chết (`127.0.0.1:1`) exit 1 gọn (HTTP 0); URL thật trước merge: 404, exit 1. Đúng.
- `screenshot.py --url https://silver-rp.github.io/autodev-sandbox/ --widths 360 --modes light`: exit 0, ảnh 360 đủ font, CSS (giữ đường con); `--url .../khong-co/` → exit 1. H-16 đóng (`tests/test_screenshot_url.py` xanh).
- Hai trang không có `href`/`src` gốc tuyệt đối `/…` (grep), nên tài nguyên chạy được dưới `/autodev-sandbox/`.

### Quyết định
- **Merge PR #40** (merge commit, giữ nhánh). E3 đạt; D7 leader đã duyệt (PR #38) → `lazy-landing` 17/17 = 100% theo lệnh đo.
- Đóng H-16. H-14 đóng một phần (URL `example.github.io`); còn email giữ chỗ và `robots.txt` dưới đường con (crawler không đọc) → R14 hoặc leader.
- Không có (c).

## R14: Cứng hoá công cụ đo và luật tài nguyên — **đạt, merged** 2026-10-21 (PR #44, `66bcab8`)

Worker làm dev-01..04, mỗi task 1 vòng (4 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R14` (`65be9fc`), chế độ B `--review-only`:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc). `plan/R14.md` trên nhánh chỉ đổi trạng thái task. Sau merge: workflow `pages` run 39446462879 xanh, `smoke_pages.py` → "OK (lần 1) … @ 66bcab8…", exit 0.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | verify + smoke sạch | `verify.py`, `verify.py --smoke` | sạch cả hai, đạt |
| 2 | (L3) pytest 3 lần liền | `uv run pytest -q` × 3 | 295 / 295 / 295 passed, đạt |
| 3 | (E2) `lh_check.py` exit 0 | `uv run python scripts/lh_check.py` | `/` trung vị 100×4, 173667 B; `/en/` 99/100/100/100, 165845 B; exit 0, đạt |
| 4 | (D1) `test_tools.py` | `uv run pytest -q tests/test_tools.py` × 7 | 5 lần 21 passed; **2 lần 1 failed** (`test_contrast_large_text_uses_3_to_1`, `Lỗi: Chrome quá thời gian (60 giây)` → exit 2) khi máy load ~14,5. Đạt có điều kiện, xem Quyết định |
| 5 | (L2) `test_site_policy.py` | `uv run pytest -q tests/test_site_policy.py` | 52 passed, đạt |
| 6 | D4, D5, `--pages /en/` | `page_metrics.py --check-overflow`, `contrast.py`, cả hai `--pages /en/` | exit 0 × 4, đạt |
| 7 | ruff | `uv run ruff check .` | "All checks passed!", đạt |

H-xx tái hiện: chép `test_screenshot_errors.py`, `test_tools_errors.py`, `test_site_policy.py` của nhánh sang bản `origin/main` cũ (`git archive`) → 48 failed (H-07: 8 test `screenshot`; H-10/H-15: 13 ca `lh_check`/`page_metrics`/`contrast`; H-09/H-06: 22 biến thể + quét `.svg` + `on*` trang thật). H-17: `test_probe_reports_missing_lazysite` (assert thông điệp "lazySite").

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~40–60 | 41 | B3 1,00 |
| USD (worker + supervisor) | ~2,9 | 1,35 + ~1,27 (supervisor, tạm) | B3 ~0,90 |
| Số vòng review | 4–6 | 4 | 0 |

Không lệch quá 2 lần.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Siết `on*` làm E2 tụt | `onload` font chuyển sang `main.js`, `<noscript>` giữ; `lh_check.py` supervisor chạy: perf 100 / 99 |
| 2. Timeout ngắn làm E2 đỏ giả | mặc định 180 giây; `test_lh_timeout_exit_2_and_default_timeout` |
| 3. PNG cũ mang hash mới (H-07) | `test_shoot_loi_xoa_png_cu`, `test_page_loi_khong_de_png_cu_mang_hash_moi` (đỏ trên main) |
| 4. Lỗi công cụ trông như đạt/trượt | `test_lh_null_score_exit_2`, `test_lh_non_finite_weight_exit_2`, `test_lh_empty_plan_exit_2_no_ok`, `test_measure_runtime_error_exit_2` |
| 5. `--pages /en/` là thư mục | `test_normalize_pages`, `test_real_en_page_and_missing_page`; supervisor chạy thật exit 0 |
| 6. Miễn trừ hreflang/canonical thành cửa sau | `test_h09_h06_negative_variants`; supervisor thử `rel="CANONICAL"` và `SITE_URL` bỏ `/` + `.evil.com` → bị bắt |
| 7. Ca âm chỉ một biến thể | 22 biến thể tham số hoá; supervisor thử `<img/onload>`, `onload = `, `java\tscript:` → bị bắt |
| 8. Hết chập chờn trên giấy | pytest 3 lần xanh; nhưng `test_tools.py` vẫn chập chờn khi máy tải nặng (H-21) |

### Kiểm biên độc lập
- Luật L2: `<svg><a xlink:href="https://evil.com">` **lọt** (link điều hướng, ngoài danh sách plan; reviewer cũng ghi). `canonical` đúng `SITE_URL` không bị bắt (đúng).
- `lh_check.py --pages ../` và `contrast.py --pages ../../etc/hosts` → "Lỗi: trang không có trong …/site", exit 2 (không thoát ra ngoài `site/`).

### Quyết định
- **Merge PR #44** (merge commit, giữ nhánh). Cả 7 tiêu chí có bằng chứng tự chạy; tiêu chí 4 chập chờn 2/7 lần do Chrome 60 giây khi máy tải nặng (load ~14,5, nhiều phiên song song). Không phải hồi quy: test dùng trang tổng hợp, không đụng `main.js`; trước R14 cùng lỗi ra traceback, giờ ra `Lỗi: … (exit 2)` đúng thiết kế. Ghi **H-21** (thấp, R15).
- Đóng H-06, H-07, H-09, H-10, H-15, H-17. Đóng luôn H-08 trong bảng (leader duyệt D7, plan R14 ghi "không làm").
- (c) tự quyết: chấp nhận hai đề xuất trong plan (`--pages` thay `--only`; `onload` font chuyển sang `main.js`), và (a) worker đổi `screenshot.py --url` không tới được từ exit 1 sang 2.

## R15: Hoàn thiện site — **đạt, merged** 2026-10-21 (PR #48, `63cd730`)

Worker làm dev-01..04, mỗi task 1 vòng (4 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R15` (`fb446d6`), chế độ B `--review-only`, load ~6–10:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc). Sau merge: `smoke_pages.py` → lần 1 version cũ (đang deploy), "OK (lần 2) … @ 63cd730…", exit 0.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | verify + smoke sạch | `verify.py`, `verify.py --smoke` | sạch cả hai, đạt |
| 2 | (L3) pytest 3 lần liền | `uv run pytest -q` × 3 | 374 / 374 / 374 passed, đạt |
| 3 | (D4) overflow | `uv run python scripts/page_metrics.py --check-overflow` | exit 0, đạt |
| 4 | (D3) `test_site_visual.py` ≥ 5; test font `document.fonts` hai trang | `uv run pytest -q tests/test_site_visual.py`; `uv run pytest -rA tests/test_site_fonts.py` | 8 passed; `test_fonts_loaded_through_document_fonts[vi]`, `[en]` PASSED (không skip), ca âm bỏ link font `[vi]`, `[en]` PASSED; đạt |
| 5 | (D6) `test_site_motion.py` ≥ 4 | `uv run pytest -q tests/test_site_motion.py` | 24 passed, đạt |
| 6 | (E5) `test_site_i18n.py` ≥ 4 | `uv run pytest -q tests/test_site_i18n.py` | 14 passed, đạt |
| 7 | D5, E2 không tụt | `contrast.py`; `lh_check.py` | contrast exit 0; `/` trung vị 100×4 (một lần perf 99), 174071 B; `/en/` 100×4, 166359 B; "OK: đạt ngưỡng E2", exit 0; đạt |
| 8 | ruff | `uv run ruff check .` | "All checks passed!", đạt |

H-xx tái hiện: chép nhánh sang `/tmp/r15old.P0ib`, thay `site/` bằng bản `origin/main` cũ (`git archive`), chạy `test_site_mobile.py`, `test_site_fonts.py`, `test_site_ly.py` → **13 failed** / 20 passed: H-03 (4 test 360 chấm dẫn + nút header, vi/en), H-05 (`test_reduced_motion_block_in_real_css`), H-20 (8 test `test_site_ly.py`). H-04: test font tải thật xanh trên site cũ (site cũ vốn tải font; lỗ là test chỉ đọc khai báo), bị chặn bằng ca âm `test_negative_no_font_links_is_caught[vi|en]` và `test_font_problems_flags_empty_and_check_only`. H-11: `--collect-only` có id `en` ở cả 6 tệp trong Mô tả dev-04 (a11y 3, button 4, content 7, dark 1, hero 3, motion 8); tổng 295 → 374 test.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~40–60 | 85 | B3 1,42 |
| USD (worker + supervisor) | ~2,8 | 2,53 + ~1,28 (supervisor, tạm) | B3 ~1,36 |
| Số vòng review | 4–6 | 4 | 0 |

Không lệch quá 2 lần. Phút cao hơn R14 vì mọi task có test Chrome mới tham số hoá vi/en.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Hiện lại chấm dẫn/nút gây tràn 360 | `test_360_header_button_visible_in_viewport[vi|en]`, `test_360_no_horizontal_scroll[vi|en]`; `page_metrics --check-overflow` exit 0 |
| 2. D4 xanh dù `nowrap` tràn (H-24) | `test_360_no_horizontal_scroll` đo `scrollWidth <= 360`; supervisor đo thêm tối 360 và 320 |
| 3. Chấm dẫn rộng 0 / mất nét | `check_cham` (≥ 16 px, `dotted`, cùng hàng giá); ca âm `test_negative_hidden_leader_is_caught` |
| 4. `fonts.check` true giả | `test_font_problems_flags_empty_and_check_only`, ca âm bỏ link font |
| 5. Đo trước khi font tải | `MEASURE_JS` chờ `document.fonts.ready` + 800 ms (reviewer: 800 ms cố định có thể chập chờn khi mạng chậm) |
| 6. Khối reduced-motion vô hiệu | ca âm comment, lồng `min-width`, thiếu `transition-duration`, sai selector/thiếu `!important` |
| 7. Chỉ thân ly dịch | `test_cup_moves_as_one_block`, ca âm `test_cup_negative_only_ly_path_moves` (đỏ trên main) |
| 8. Gom `<g>` đổi màu tô | `test_cup_group_keeps_fills[vi|en]`; contrast exit 0 |
| 9. Tham số hoá làm yếu test | 295 → 374; id `en` ở mọi tệp; reviewer dev-04 đối chiếu diff |
| 10. Bản Anh phải nới assert | giá trị theo trang trong bảng tham số (reviewer dev-04) |

### Kiểm biên độc lập
- Probe của `test_site_mobile.py` chạy ở tối 360 và sáng 320 (`/tmp/r15edge/edge.py`): `/` 360 tối `scrollWidth` 360, nút 24–194 px (xuống dòng dưới bảng hiệu), chấm dẫn hẹp nhất 20,7 px; `/en/` 360 tối nút 220–336, chấm 25,2 px; 320 cả hai trang `scrollWidth` 320, nút phải 296. Không tràn.
- Test font chạy thật (có mạng), không skip.
- Trên nhánh hồ sơ (chỉ sửa tài liệu), `verify.py` lần đầu đỏ `test_tools.py::test_dark_mode_applied_only_in_dark[360]`; chạy lại 3 lần: 2 passed mỗi lần; `verify.py` lần sau sạch. Chập chờn Chrome kiểu H-21 (load ~7), không phải hồi quy R15.

### Quyết định
- **Merge PR #48** (merge commit, giữ nhánh). 8/8 tiêu chí có bằng chứng tự chạy. Đóng H-03, H-04, H-05, H-11, H-20.
- (a) chấp nhận: `scripts/screenshot.py` `frame_html` chép `#out` bằng polling (ngoài phạm vi plan, cần vì `MEASURE_JS` ghi sau `fonts.ready`; test Chrome cũ xanh); test mới ở tệp mới `test_site_fonts.py`, `test_site_ly.py`; TC4 dev-03 bằng test mới thay vì mở rộng test cũ.
- Điều chỉnh: H-21, H-23, H-24, H-25, H-29, H-32, H-33 ghi "R15" nhưng plan R15 để ngoài phạm vi → chuyển "mốc công cụ" (leader lập); H-22 → leader.
- Ghi chú reviewer (không chặn): `scrollWidth` chỉ đo sáng (supervisor đo tối: đạt); chờ 800 ms cố định; `test_cup_reduced_motion_block_instant` có assert `json.dumps(d)` vô nghĩa.

## R17: Cứng hoá todo CLI — **đạt, merged** 2026-10-21 (PR #52, `3a18132`)

Worker làm dev-01..03, mỗi task 1 vòng (3 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R17` (`0adb956`), chế độ B `--review-only`: `verify.py` → "sạch (không có lỗi mới so với baseline)" (2 phút 49); `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | verify + smoke sạch | `verify.py`, `verify.py --smoke` | sạch cả hai, đạt |
| 2 | (A1) `test_due.py` ≥ 7 | `uv run pytest -q tests/test_due.py` | 24 passed, đạt |
| 3 | (A2) `test_overdue.py` ≥ 6 | `uv run pytest -q tests/test_overdue.py` | 7 passed, đạt |
| 4 | (A3) cả bộ | `uv run pytest -q` | 412 passed, 0 failed, đạt |
| 5 | (A4) ruff | `uv run ruff check .` | "All checks passed!", đạt |
| 6 | test mới + 5 lần song song | `uv run pytest -q tests/test_cli_errors.py tests/test_store_safety.py`; vòng 5 lần `test_store_safety.py` | 38 passed; 6/6/6/6/6 passed, exit 0; đạt |
| 7 | CLI thật, mã 2, 2, 1, 2 | `TODO_FILE=$(mktemp -d)/t.json`: `todo done ²`, `todo add ""`, `todo done 9`, `todo list` trên `{hỏng` | exit 2 (usage), 2 (`tiêu đề không được rỗng`), 1 (`không có việc id 9`), 2 (`<path>: JSON hỏng (…, dòng 1 cột 2)`); 0 dòng `Traceback`; đạt |

H-xx tái hiện: `git archive origin/main` (trước merge) sang `/tmp/r17old.oZgK`, chép `tests/test_cli_errors.py`, `tests/test_store_safety.py` vào, chạy → **34 failed** / 4 passed. Trong đó `test_add_through_symlink_keeps_link` (`assert link.is_symlink()` False), test hai tiến trình `assert 20 == 40` (mất việc thật, không chỉ `AttributeError`). Đóng H-13, H-18, H-26.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | ~10–20 | 60 | B3 3,02 |
| USD (worker + supervisor) | ~2,1 | 1,20 + ~1,33 (supervisor, tạm) | B3 ~1,20 |
| Số vòng review | 3–5 | 3 | 0 |

Phút lệch quá 2 lần: ước tính lấy R1/R2 (4 phút, 30–52 test) nhưng nay `pytest -q` cả bộ 412 test (có Chrome của site) mất ~165–210 giây, chạy ở mỗi verify/hook/reviewer. Mốc todo sau nên ước theo thời gian cả bộ test, không theo R1/R2.

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Test song song tình cờ xanh | `Barrier` + 2×20 `add`; đỏ trên code cũ (`20 == 40`); test khoá tất định `LOCK_NB` gặp `BlockingIOError`; supervisor thêm 3 tiến trình CLI thật × 10 `add` qua symlink → 30 việc, id `1..30` |
| 2. `os.replace` phá symlink | `test_add_through_symlink_keeps_link`, `test_cli_done_and_due_through_symlink` (đỏ trên cũ) |
| 3. Khoá trên inode bị thay | `lock_path` = thư mục chứa đích (`realpath`); TC 3–4 |
| 4. File `.lock` để lại rác | `test_atomic_save.py` không đổi, xanh; thư mục đích sau CLI chỉ có `t.json` |
| 5. `isdigit()` nhận `²`, `١` | `re.fullmatch(r"[0-9]+")`; test `done`/`due` với `²`, `١`, `１` |
| 6. Tiêu đề chỉ khoảng trắng | test `""`, `"   "`, `"\t\n"`, `"" --due`; supervisor `add --due 2026-10-20 "   "` → exit 2 |
| 7. Thiếu ký tự xuống dòng | `_BREAKS` có `\x1c-\x1e`, `\x85`, U+2028, U+2029 (supervisor xem byte); test `splitlines()` + 4 cột |
| 8. `done` id không có vẫn ghi | `complete` chỉ `save` khi `found`; test byte + `st_mtime_ns` |
| 9. JSON hỏng chỉ bắt ở `list` | `cli.main` bắt `StoreError` cho mọi lệnh; test tham số 5 lệnh; `add` không ghi đè file hỏng |
| 10. Kiểm cấu trúc lỏng | `{}`, `[1]`, thiếu `id`, `id` chuỗi/`bool`, `\xff\xfe` → exit 2. Còn hở: `title`/`done` (H-34) |
| 11. Hỏng file cũ không `due` | A1 `test_set_due_on_legacy_file`, `test_list_legacy_file_without_due` xanh |

### Kiểm biên độc lập
- `done 01` → exit 0 (id 1, chấp nhận: chữ số ASCII); `done 1` lặp lại → exit 0 lần 2 (không đổi hành vi cũ); `due 99999999999999999999 2026-10-20` → exit 1 `không có việc id …`, không traceback.
- `[{"id":1,"title":"a"}]` (thiếu `done`) → `todo list` **Traceback** `KeyError` exit 1; `add x` trên file đó vẫn ghi. Ngoài phạm vi roadmap R17 ("JSON hỏng hoặc phần tử thiếu `id`"), reviewer dev-02 đã nêu → ghi H-34.
- `TODO_FILE` trong thư mục không có: `add x` Traceback (`FileNotFoundError` từ `lock`) — plan để ngoài phạm vi → H-34.
- 3 tiến trình CLI thật song song × 10 `add` qua symlink: 30 việc, id đúng `1..30`, link còn, thư mục đích chỉ `t.json`.

### Quyết định
- **Merge PR #52** (merge commit, giữ nhánh). 7/7 tiêu chí có bằng chứng tự chạy. Đóng H-13, H-18, H-26; `due-overdue` R17 `done`.
- (c) tự quyết: ghi H-34 (thấp) thay vì chặn merge: `load` chưa kiểm `title`/`done`; lỗi OS traceback. Lý do: roadmap R17 và tiêu chí mốc chỉ đòi `id`; mục tiêu "không bao giờ traceback" của roadmap còn hở hai ý này, cần leader đưa vào mốc todo sau.
- Giả định plan đã chấp nhận: `flock` trên thư mục; không gộp/cắt khoảng trắng.

## R16: Công cụ đo và deploy chặt — **đạt, merged** 2026-10-21 (PR #56, `ff8c12f`)

Worker làm dev-01..04, mỗi task 1 vòng (4 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R16` (`fbbf217`), chế độ B `--review-only`: `verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: 2 job `test` pass (main không có check bắt buộc). Tệp đổi khớp phạm vi plan (5 script, `pages.yml`, spec, test, `pyproject.toml`/`uv.lock`); `site/` không đổi.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | verify + smoke sạch | `verify.py`, `verify.py --smoke` | sạch cả hai, đạt |
| 2 | (L3) cả bộ 2 lần liền | `verify.py` (pytest lần 1) rồi `uv run pytest -q` | lần 1 sạch; lần 2 467 passed (175 giây), 0 failed; đạt |
| 3 | (D4) overflow có `scrollWidth`, `/` + `/en/` | `uv run python scripts/page_metrics.py --check-overflow` | exit 0, đạt |
| 4 | (D1) `test_tools.py` ≥ 5 | `uv run pytest -q tests/test_tools.py` | 21 passed, đạt |
| 5 | (D2) spec + D7 | `uv run pytest -q tests/test_design_doc.py`; `grep -q '^Leader duyệt: đạt'` | 10 passed; grep exit 0; `Hướng đã chọn: 2 — Quán cóc đầu ngõ`; đạt |
| 6 | (E2) Lighthouse | `uv run python scripts/lh_check.py` | `/` trung vị 100×4, 173 763 B; `/en/` 100×4, 165 939 B; "OK: đạt ngưỡng E2"; đạt |
| 7 | (E3) sau merge | trước merge `pytest -q tests/test_smoke_pages.py tests/test_pages_workflow.py`; sau merge run `pages` 39528831394 rồi `uv run python scripts/smoke_pages.py` | 20 passed; job `test` → `build` → `deploy` đều success; "OK (lần 1): https://silver-rp.github.io/autodev-sandbox/ @ ff8c12f…"; đạt |
| 8 | (D5) contrast; ruff | `uv run python scripts/contrast.py`; `uv run ruff check .` | exit 0; "All checks passed!"; đạt |

H-xx tái hiện: `git archive origin/main` (trước merge) sang `/tmp/r16old.LcWL`, chép 5 tệp test mới/đổi + `pyproject.toml`/`uv.lock`, chạy → **42 failed** / 25 passed: H-24 `test_nowrap_text_in_clipped_box_is_overflow`; H-29 `test_bad_params_exit2` (12 ca), `test_normalize_pages_dir_without_slash`, `test_contrast_*`; H-28 `test_workflow_test_job_and_needs_chain`, ca âm, `test_jobs_exist[test]`; H-23 `test_site_pages_404_*`, `test_page_404_*` (site + url), `test_page_url_khong_ghi_source_sha`, `test_loi_tham_so_exit_2` (8 ca); H-25 `test_lh_missing_index_exit2`, `test_lh_site_not_exists`, `test_lh_site_is_file`; H-27 `test_git_sha_fetches_first`, `test_main_not_a_repo_exit2`, `test_main_no_git_binary`; H-22 3 test `test_design_doc.py`. Đóng H-22, H-23, H-24, H-25, H-28, H-29; H-27 đóng phần fetch/lỗi git (phần còn lại giữ mở); H-40 phần `screenshot`.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~60–90 | 90 | B3 1,00 |
| USD (worker + supervisor) | ~3,2 | 2,16 + ~1,34 (supervisor, tạm) | B3 ~1,09 |
| Số vòng review | 4–6 | 4 | 0 |

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. `scrollWidth` làm D4 đỏ thật | D4 exit 0 trên `site/` thật, không phải sửa `style.css` |
| 2. Báo tràn oan khung cuộn | `test_scroll_container_is_not_overflow` (`pre overflow-x:auto`) |
| 3. Pages chờ test làm deploy hỏng | `test_workflow_test_job_and_needs_chain`, `test_workflow_permissions_triggers_concurrency`; run thật sau merge: test/build/deploy success |
| 4. Test workflow chỉ regex | `test_version_step_writes_sha_once_per_page`, `..._fails_on_two_placeholders`, `..._missing_placeholder_fails` (chạy thật `sed`, shim `-i ''` trên macOS) |
| 5. Kiểm HTTP chỉ ở `--url` | `test_site_pages_404_exit_2_khong_png`, `test_page_404_exit_2_khong_tao_file[site/url]` (đỏ trên cũ) |
| 6. Hash `og.svg` lên ảnh URL ngoài | `test_page_url_khong_ghi_source_sha` (đỏ trên cũ), `test_page_site_ghi_source_sha` |
| 7. `smoke_pages` so `origin/main` cũ | `test_git_sha_fetches_first` (repo bare đi trước, đỏ trên cũ) |
| 8. Lỗi git/tham số traceback exit 1 | `test_bad_params_exit2`, `test_loi_tham_so_exit_2`, `test_main_not_a_repo_exit2`, `test_main_no_git_binary`, `test_lh_site_*` |
| 9. Sửa spec làm D2 đỏ / mất D7 | 7 test D2 cũ giữ, xanh; grep D7 exit 0 |
| 10. Spec còn hứa laptop/ngáp chỗ khác | `test_old_items_gone_outside_dropped_section` |

### Kiểm biên độc lập
- `smoke_pages.py --url http://127.0.0.1:9` trong thư mục không phải repo → `Lỗi: git fetch origin main lỗi (128): fatal: not a git repository…` exit 2.
- `lh_check.py --site <tệp thường>` → `Lỗi: --site không phải thư mục` exit 2; `screenshot.py --widths ","` → usage, exit 2; `page_metrics.py --widths 360,abc` → `Lỗi: --widths không hợp lệ: 'abc'` exit 2.
- `normalize_pages`: `/en` → `/en/index.html`; `/en/../../etc/passwd`, `..`, `/x/..` → "thoát khỏi site"; `/en/%2e%2e/index.html` → "không có trong site".
- `contrast.parse_color`: `color(srgb 1 0 0)` → (255,0,0); có alpha `/ 0.5` → (128,128,128); `color(display-p3 …)` → `ValueError` → `main` exit 2.

### Quyết định
- **Merge PR #56** (merge commit, giữ nhánh). 8/8 tiêu chí có bằng chứng tự chạy (E3 sau merge). `lazy-landing` R16 `done`.
- (c) tự quyết: H-27 chỉ đóng phần roadmap R16 (fetch trước, lỗi git exit 2); phần `main.js`/`robots.txt`/`sitemap.xml`, version `/en/` giữ mở (thu hẹp mô tả). H-40 thu hẹp còn phần `smoke_pages`.
- Chấp nhận (a): `test_pages_workflow.py` viết lại theo YAML (2 test cũ giữ); shim `sed` trên macOS thay `skip`. Giả định `overflow-x` khác `visible` = khung cuộn hợp lệ.
- Ghi chú reviewer (không chặn): `check_reachable` gọi lặp mỗi tổ hợp width × mode; test version-step cố định `PATH=/usr/bin:/bin`; chưa probe symlink trong `site/` trỏ ra ngoài.

## R18: Todo CLI không traceback, không treo, không ghi hỏng — **đạt, merged** 2026-10-21 (PR #62, `f05759b`)

Worker làm dev-01..04, mỗi task 1 vòng (4 vòng, không FAIL). Supervisor kiểm trên `origin/milestone/R18` (`819e758`), chế độ B `--review-only`. `verify.py` lần 1 → "1 lỗi mới so với baseline: `tests/test_site_ly.py::test_cup_moves_as_one_block[vi]`" (Chrome probe; `site/` và test site không đổi trong PR; `test_site_ly.py` chạy riêng 3 lần → 11 passed); lần 2 → "sạch". `verify.py --smoke` → `ok A5 overdue`, "sạch". CI PR: job `push` đỏ `test_site_ly.py::test_cup_negative_only_ly_path_moves[en]` ("probe không chạy", 1 failed / 510 passed), chạy lại → pass; job `pull_request` pass. Main không có check bắt buộc. Tệp đổi khớp phạm vi (`cli.py`, `store.py`, 3 file test, plan chỉ đổi trạng thái).

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | verify + smoke sạch | `verify.py` (2 lần), `verify.py --smoke` | lần 1 đỏ 1 test site (H-21), lần 2 sạch; smoke sạch; đạt |
| 2 | (A1) `test_due.py` ≥ 7 | `uv run pytest -q tests/test_due.py` | 24 passed, đạt |
| 3 | (A2) `test_overdue.py` ≥ 6 | `uv run pytest -q tests/test_overdue.py` | 7 passed, đạt |
| 4 | (A3) cả bộ 0 failed | `verify.py` lần 2 (pytest cả bộ, baseline rỗng); CI chạy lại | sạch; CI 511 test, 2 job pass; đạt |
| 5 | (A4) ruff | `uv run ruff check .` | "All checks passed!", đạt |
| 6 | 3 file test + 8 tên | `uv run pytest -q tests/test_cli_errors.py tests/test_store_safety.py tests/test_atomic_save.py`; `--collect-only` | 85 passed; đủ 8 tên (27 ca tham số); 8 đỏ trên code cũ (dưới); đạt |
| 7 | 5 lần liền; khoá < 2 giây | vòng 5 lần `tests/test_store_safety.py`; `::test_lock_timeout_exit_2 --durations=1` | 23 passed × 5, exit 0; ca chậm nhất 0,37 giây; đạt |
| 8 | CLI thật 4 ca | `TODO_FILE=$(mktemp -d)/t.json`: `done <5000 chữ số 1>`; `list` id −1; `add x` file 0444; `list` trên `[`×100000 | exit 2/2/2/2; 0 `Traceback`; stdout rỗng; `shasum` + `stat` (mtime, inode, mode) trước/sau giống; stderr: `id không hợp lệ (quá dài): 5000 chữ số`, `…: phần tử 1 có "id" âm (-1)`, `…: file không ghi được (chỉ đọc), không ghi đè`, `…: JSON lồng quá sâu`; đạt |

H-xx tái hiện: `git archive origin/main` (trước merge) sang `/tmp/r18old.t3l2`, chép 3 file test mới vào, chạy từng test roadmap: `test_done_huge_id_exit_2` 2 failed, `test_deeply_nested_json_exit_2` 4 failed, `test_load_rejects_negative_id` 5 failed, `test_load_rejects_duplicate_id` 5 failed, `test_lock_timeout_exit_2` **treo** (giết sau 60 giây), `test_self_symlink_exit_2` 6 failed, `test_readonly_file_not_overwritten` 1 failed, `test_hardlink_preserved` 1 failed. Đóng H-35, H-36, H-37, H-38.

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 4 | 4 | 0 |
| Phút worker | ~70–90 | 91 | ~1,0–1,3 (B3 1,01) |
| USD (worker + supervisor) | ~3,1 | 2,40 + ~1,38 (supervisor, tạm) | B3 ~1,22 |
| Số vòng review | 4–6 | 4 | 0 |

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| 1. Test khoá chập chờn/chậm | `Event` báo đã giữ khoá, `TODO_LOCK_TIMEOUT=0.3`; 5 × 23 passed; 0,37 giây |
| 2. Hard link làm mất nguyên tử | ghi tại chỗ chỉ khi `st_nlink > 1`; `test_failed_save_keeps_old_file_and_leaves_no_temp`, `test_two_processes_add_in_parallel` xanh |
| 3. Bắt ngoại lệ quá rộng | `grep -nE 'except (Exception\|BaseException)' src/todo/cli.py` không ra dòng (exit 1); H-34 `[{"id":1,"title":"a"}]` vẫn traceback như cũ (supervisor chạy) |
| 4. Id dài chỉ chặn ở `done` | `test_done_huge_id_exit_2` tham số `done`/`due` |
| 5. Số khổng lồ trong file | test id 1+5000 số 0 và 4300 chữ số 9 (`add` không ghi, không file tạm) |
| 6. argv không UTF-8 chỉ trong tiến trình | test `subprocess` argv bytes cho `add`, `due` |
| 7. Id âm/trùng chỉ chặn một lệnh | `test_load_rejects_*` tham số 5 lệnh |
| 8. Timeout khoá ném lỗi thô | `test_lock_timeout_exit_2` (exit 2, stderr "đang bị khoá") |
| 9. `TODO_LOCK_TIMEOUT` sai | test `abc`, `-1`, `0`, `nan`, `inf`; supervisor `-0` → exit 2 |
| 10. `os.access` rồi vẫn `os.replace` | `test_readonly_file_not_overwritten` (nội dung, mode, inode); CLI thật ca 0444 |
| 11. Symlink vòng coi như chưa có | `test_self_symlink_exit_2` (tự trỏ, `a → b → a`) |
| 12. Dọn tmp che lỗi gốc | test monkeypatch `os.replace`/`os.unlink` ("gốc" trong thông báo) |

### Kiểm biên độc lập
- `TODO_FILE` là thư mục: `list`, `add x` → exit 2 `…: không đọc được (Is a directory)`, không traceback.
- Symlink → file có hard link: `add y` exit 0, link giữ, `st_nlink` 2, link cứng thấy việc mới, không file tạm.
- `done 000…1` (5000 ký tự, số 0 đầu) → exit 2 "quá dài" (không phải exit 1); chấp nhận theo giả định plan (cú pháp).
- `TODO_LOCK_TIMEOUT=" 1e-9"` → `add` exit 0 (không ai giữ khoá); `-0` → exit 2; id `1e400` trong file → exit 2 "không phải số nguyên".
- Thông báo lỗi `load` dùng đường dẫn người dùng (`/var/…`), `save` dùng `realpath` (`/private/var/…`): không nhất quán, không chặn.

### Thí nghiệm superpowers (8c)
`superpowers:requesting-code-review` gọi trên diff `2d3a076..819e758`; supervisor tự review theo mẫu `code-reviewer.md` (headless, không mở subagent). Kết luận: sẵn sàng merge. Không Critical/Important. Minor: `_write_in_place` cắt rồi ghi (kill giữa chừng còn file rỗng; đánh đổi plan đã chấp nhận); `os.access(W_OK)` vô tác dụng khi root, TOCTOU; thông báo "id quá dài" lặp ở `done`/`due`; đường dẫn lỗi `load`/`save` khác nhau. Gác lại (ngoài phạm vi): H-34 (`title`/`done`), H-41. So R17 (không thí nghiệm): không thêm phát hiện chặn; thêm 1 ca biên (đường dẫn khác nhau).

### Quyết định
- **Merge PR #62** (merge commit, giữ nhánh). 8/8 tiêu chí có bằng chứng tự chạy. `due-overdue` R18 `done`.
- (c) tự quyết: H-34 thu hẹp còn phần kiểu `title`/`done` (phần lỗi OS đã exit 2 nhờ dev-04, supervisor thử `TODO_FILE` là thư mục); lỗi đỏ 1 test site trong verify lần 1 và CI `push` không chặn (không đụng `site/`, chạy lại xanh, họ H-21).
- Giả định plan chấp nhận: `TODO_LOCK_TIMEOUT` mặc định 5 giây (docstring `cli.py` chưa ghi, nợ nhỏ); id `0` hợp lệ; id quá dài exit 2; ghi tại chỗ khi có hard link.
- Việc cần người: `/private/tmp/r18-base` (worktree tách rời do developer dev-04 tạo, ngoài repo) cần `git worktree remove`.

<!-- metrics:start (tự sinh bởi .autodev/metrics.py, đừng sửa tay) -->
<!-- metrics:end -->
