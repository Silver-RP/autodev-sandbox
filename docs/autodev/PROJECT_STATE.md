# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-21 · Nguồn: audit sau R16 (`docs/audits/2026-10-21-3.md`) + duyệt R15, R17, R16, R18, R19 (supervisor)

## Mốc
| Mốc | Trạng thái | Ghi chú |
|---|---|---|
| R1 | merged | PR #5; 3 task, mỗi task 1 vòng; 30 test pass |
| R2 | merged | PR #8 (`0aa2992`); 3 task, mỗi task 1 vòng; 52 test pass; đóng H-01 |
| R3 | merged | PR #14; `site/` 4 phần, test cấu trúc, smoke HTTP; 69 test pass |
| R4 | merged | PR #20 (`34b1066`); 4 task, mỗi task 1 vòng; 95 test pass; D1, L2 đạt |
| R5 | cut | leader chọn trước hướng "Quán cóc đầu ngõ" |
| R6 | merged | PR #22 (`ecd64d0`); 5 task, 6 vòng review; 126 test pass; D2, D3 đạt |
| R7 | merged | PR #24 (`1a66df0`); 3 task, mỗi task 1 vòng; 148 test pass; D6 đạt; đóng H-02 |
| R8 | merged | PR #26 (`8a5a9ba`); 4 task, mỗi task 1 vòng; 165 test pass; D4, D5 đạt; H-03..05 không có task, chuyển R10 |
| R12 | merged | PR #28 (`b7e2529`); 3 task, mỗi task 1 vòng; 173 test pass; E4 đạt |
| R9 | merged | PR #30 (`91c071a`); 4 task + (b) dev-05, dev-06; 7 vòng; 189 test pass; E1 đạt |
| R13 | merged | PR #33 (`68112ec`); 3 task, mỗi task 1 vòng; 204 test pass; E5 đạt; ghi H-06 cho R10 |
| R10 | merged | PR #35 (`576fd3d`); 3 task, 4 vòng; 210 test pass; E2 đạt; H-03..06 không có task, chuyển R14 |
| R11 | merged | PR #40 (`099dfd9`); 3 task, mỗi task 1 vòng; 229 test pass; E3 đạt trên URL thật; đóng H-16 |
| R14 | merged | PR #44 (`66bcab8`); 4 task, mỗi task 1 vòng; 295 test pass; đóng H-06, H-07, H-09, H-10, H-15, H-17; ghi H-21 |
| R15 | merged | PR #48 (`63cd730`); 4 task, mỗi task 1 vòng; 374 test pass; D3, D4, D6, E5 giữ; đóng H-03, H-04, H-05, H-11, H-20 |
| R17 | merged | PR #52 (`3a18132`); 3 task, mỗi task 1 vòng; 412 test pass; A1–A4 giữ; đóng H-13, H-18, H-26; ghi H-34 |
| R16 | merged | PR #56 (`ff8c12f`); 4 task, mỗi task 1 vòng; 467 test pass × 2; D1, D2, D4, E2, E3 giữ; đóng H-22..H-25, H-28, H-29; H-27 một phần |
| R18 | merged | PR #62 (`f05759b`); 4 task, mỗi task 1 vòng; 511 test; A1–A4 giữ; đóng H-35..H-38; H-34 thu hẹp |
| R19 | merged | PR #65 (`805cbe0`); 4 task, 5 vòng; 569 test pass × 2; D1, D4, D5, E3 giữ; đóng H-27, H-40, H-43..H-46; ghi H-50 |

## Mục tiêu và tiêu chí
- `due-overdue`: 5/5 = **100%** theo lệnh đo; sau R18 còn hở H-34 (kiểu `title`/`done`), H-41.
- `lazy-landing` (`docs/goals/lazy-landing/criteria.md`, bản 2): 17/17 = **100%** theo lệnh đo; audit sau R16 ước thực tế ≈ 78–82% (đẹp ~73%, kỹ thuật ~88%, phát hành ~70%).
| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| L1 | `uv run pytest -q tests/test_site.py` | 0 failed, ≥ 6 | 11 passed, đạt |
| L2 | `uv run pytest -q tests/test_site_policy.py` | 0 failed, ≥ 6 | 52 passed, đạt |
| L3 | `uv run pytest -q` | 0 failed | 569 passed × 2, 0 failed (R19; test site chập chờn H-21), đạt |
| L4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| L5 | smoke HTTP (`criteria.md`) | `200` hai dòng | đạt |
| D1 | `uv run pytest -q tests/test_tools.py` | 0 failed, ≥ 5, không skip | 21 passed; chập chờn 2/7 lần khi máy tải nặng (H-21) |
| D2 | `uv run pytest -q tests/test_design_doc.py` | 0 failed | 10 passed (R16: mục "Phần spec cũ bị bỏ"), đạt |
| D3 | `uv run pytest -q tests/test_site_visual.py` | 0 failed, ≥ 5 | 8 passed; font tải thật qua `document.fonts` `/` + `/en/` (`test_site_fonts.py`, R15), đạt |
| D4 | `uv run python scripts/page_metrics.py --check-overflow` | exit 0 | exit 0 với phép đo có `scrollWidth` (R16), `/` + `/en/`, đạt |
| D5 | `uv run python scripts/contrast.py` | 0 cặp trượt, exit 0 | exit 0 (sáng + tối), đạt |
| D6 | `uv run pytest -q tests/test_site_motion.py` | 0 failed, ≥ 4 | 24 passed (có mạng); CSS có khối reduced-motion (R15), đạt |
| E4 | `uv run pytest -q tests/test_site_content.py` | 0 failed, ≥ 4 | 12 passed, đạt |
| E1 | `uv run pytest -q tests/test_site_seo.py` | 0 failed, ≥ 6 | 12 passed, đạt |
| E5 | `uv run pytest -q tests/test_site_i18n.py` | 0 failed, ≥ 4 | 14 passed, đạt |
| E2 | `uv run python scripts/lh_check.py` | perf ≥ 90, a11y/bp/seo ≥ 95, ≤ 300 KB | `/` trung vị 100×4, 174 KB; `/en/` 100×4, 166 KB; đạt (R16) |
| D7 | `grep -q '^Leader duyệt: đạt' docs/design/lazy-landing.md` | exit 0 | đạt (leader, PR #38, 2026-10-20) |
| E3 | `uv run python scripts/smoke_pages.py` | 200, SHA khớp `main` | exit 0 @ `805cbe0` (R19: kiểm cả `en/` version, `main.js`, `robots.txt`, `sitemap.xml`), đạt |

## Kiến trúc hiện nay
- `src/todo/`: CLI todo (`add --due`, `list`, `overdue`, `done`, `due`); luật ngày duy nhất ở `store.valid_due`. R17: `store.load` ném `StoreError` (JSON, cấu trúc, `id`), `cli.main` bắt → exit 2; `store.clean_title`; `store.lock(path)` = `flock` trên thư mục chứa đích thật; `save` ghi vào `realpath`.
- `site/`: landing "Quán cóc đầu ngõ" 6 phần (`hero`, `dich-vu`, `cach-lam`, `du-an` (3 dự án hư cấu, mỗi `article` có "(ví dụ)" + SVG), `hoi-dap` (4 `<details>`), `lien-he`). `style.css`: token 6 màu sáng ở `:root` (`--color-*`), Google Fonts (Baloo 2, Be Vietnam Pro) nạp trong HTML bằng `<link rel=preload as=style>` (không `onload`; `main.js` đổi `rel` sang `stylesheet`, R14) + `<noscript>` (R10, bỏ `@import`), menu bảng liền có chấm dẫn. Tối: `@media (prefers-color-scheme: dark)` chỉ gán lại token `:root` theo bảng "Tối" của doc, thêm `--color-chu-nut`, `--color-chu-tren-tra`. `:focus-visible` có `outline` cho link và nút. 8 SVG inline (`currentColor` / `var()`, nét 2,5): hero (ghế + ly), 3 biểu tượng gói, ghế trống ở liên hệ, 3 minh hoạ `#du-an` (`aria-hidden`).
- Chuyển động: GSAP 3.12.5 qua jsDelivr (SRI, `defer`) + `site/main.js`. Không có `gsap` thì không làm gì (không class `js`). Một timeline hero (`h1`, `.hero-hinh`, `gsap.from` + `clearProps`); nút `#luoi-nut` (`hidden` khi không JS, `aria-pressed`) dịch hai ghế và ly. `window.lazySite.shouldAnimate()` đọc `prefers-reduced-motion`; `false` thì không timeline, nút dùng `gsap.set`.
- `scripts/screenshot.py`: Chrome headless; 1280 trực tiếp, < 1000 qua iframe; tối bằng `--blink-settings`; ảnh ở `.autodev/shots/` (gitignore). R14: `shoot()` xoá ảnh cũ trước khi chụp; Chrome `returncode != 0`, không có tệp, timeout 60 giây (hằng số), DOM rỗng → `RuntimeError`; `main` in `Lỗi: ...`, exit 2 (cả `--url` không tới được); `--page` chỉ ghi chunk hash khi chụp xong. R16: mọi lần chụp (`--site`/`--url`, `--pages`/`--page`) gọi `check_reachable` trước, khác 200 → exit 2, xoá PNG cũ; `--page --url` không ghi `source-sha256`; `--widths`/`--height`/`--out` tệp/`..` → usage exit 2. Dưới `--virtual-time-budget` rAF gần như không phát: hero chụp ra còn dở intro (đẩy `gsap.globalTimeline.time` như test, CDP thời gian thật, hoặc bản sao bỏ `<script>`).
- `scripts/page_metrics.py`: JSON mỗi dòng một tổ hợp (`width`, `mode`, `innerWidth`, `overflow`, `svg_by_section`, `h1`, `body_font`, `colors`); `colors` gộp theo bộ (màu, nền, cỡ, đậm), nền lấy theo cây cha. `--check-overflow` exit 1 khi tràn; exit 2 lỗi công cụ (Chrome, trang không có, danh sách rỗng); `--pages` nhận `/en/`, `/en`, `/en/index.html` (R14). R15: `MEASURE_JS` ghi `#out` sau `document.fonts.ready` + 800 ms; `screenshot.frame_html` chép `#out` bằng polling 100 ms. R16: tràn = `html.scrollWidth > clientWidth`, hoặc `rect.right > innerWidth + 1`, hoặc phần tử `overflow-x: visible` có `scrollWidth > clientWidth + 1` (khung `auto/scroll/hidden/clip` không tính); `parse_widths` (số nguyên dương) chung cho `contrast`; `--pages` `..` → exit 2.
- `scripts/contrast.py`: tỉ lệ WCAG 2.x trên `colors` của `page_metrics.py`; chữ lớn (≥ 24px, hoặc ≥ 18,66px đậm) 3:1, còn lại 4,5:1; mặc định 1280, cả hai chế độ (`--widths`, `--modes`, `--site`); exit 1 khi trượt, 2 khi lỗi công cụ (R14); đọc `color(srgb r g b)`, màu khác không đọc được → exit 2 (R16). Bỏ qua alpha chữ, không đo `:hover`/`:focus`.
- SEO (R9): `scripts/site_config.py` (`SITE_URL` = `https://silver-rp.github.io/autodev-sandbox/` từ R11); meta OG/Twitter, canonical, JSON-LD `ProfessionalService`, `robots.txt`, `sitemap.xml` ghi cứng URL (test kiểm khớp `SITE_URL`, không còn `example.github.io`).
- Triển khai (R11): `.github/workflows/pages.yml` (push `main` + `workflow_dispatch`; R16: job `test` (ruff + pytest) → `build` (`needs: test`) → `deploy`; checkout@v4, configure-pages@v5, upload-pages-artifact@v3 `path: site`, deploy-pages@v4; `concurrency: pages`) thay `<meta name="version" content="dev">` ở hai trang bằng `github.sha` trước khi upload. R19: `permissions` cấp workflow chỉ `contents: read`; `build` `pages: read`, `deploy` `pages: write` + `id-token: write`; mọi job có `timeout-minutes`. `scripts/smoke_pages.py [--url] [--sha] [--retries 10] [--interval 30]`: `/` 200 + "Lười Code Studio", `/` và `/en/` version = SHA `main` của remote **tính lại mỗi lần thử** (`git fetch origin +refs/heads/main:refs/remotes/origin/main`, timeout 60 giây, `GIT_TERMINAL_PROMPT=0`; lỗi git exit 2; `--sha` thì không gọi git); `style.css`, `og.png`, `main.js`, `robots.txt`, `sitemap.xml` 200; URL không http/https, `--interval` < 0, `--retries` ≤ 0 → exit 2; `HTTPException` tính lần thử lỗi (R19). `screenshot`/`page_metrics`/`contrast` bắt `(RuntimeError, OSError, ValueError)` → exit 2 (R19). `screenshot.py --url` giữ đường con, không dùng `__frame__`, lỗi HTTP → exit khác 0. Mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại. `og.svg` → `og.png` qua `screenshot.py --page /og.svg --size 1200x630`, PNG mang chunk `tEXt` `source-sha256` (`og_png_current`). `pytest` có `pythonpath` trong `pyproject.toml`.
- Song ngữ (R13): `site/en/index.html` (`lang="en"`, cùng id section tiếng Việt không dấu) dùng chung `../style.css`, `../main.js`; `hreflang` vi/en/x-default + canonical riêng mỗi trang, URL tuyệt đối; link `.doi-ngon-ngu` ở header (không JS); `#luoi-nut` lấy nhãn từ `data-on`/`data-off`; `sitemap.xml` hai URL. `contrast.py`, `page_metrics.py` có `--pages` (mặc định mọi trang có thật), `screenshot.py --pages` (ảnh `en-<w>-<mode>.png`).
- `scripts/lh_check.py` (R10): phục vụ `site/` cổng 0; `npx -y lighthouse@12` mobile, 3 lần `/` + 1 lần `/en/`, trung vị; exit 1 dưới ngưỡng E2; exit 2 lỗi công cụ: thiếu `npx`/Chrome, quá `--timeout` (mặc định 180 giây), JSON thiếu khoá/`null`/NaN, trang không có, không trang nào (R14); `--site` không phải thư mục/thiếu `index.html` (R16, trước khi gọi Lighthouse). `--pages` thay `--only`.
- `tests/_policy.py` (R14): bắt `<base>`, URL `/\`, `\\`, mọi `on*`, `javascript:`, `object data`, `svg image`/`use`/`xlink:href`, `form action` ngoài, SRI rỗng; miễn trừ `canonical`/`alternate hreflang` chỉ khi `href` bắt đầu bằng `SITE_URL` và `rel` đúng một giá trị; quét cả `site/**/*.svg`. `check(html, css)` cho L2; `_pinned(src)`: mọi `@tag` phải là X.Y.Z, không có `@` thì cần `/X.Y.Z/`.

## Quy tắc → test bảo vệ
| Quy tắc | Test bảo vệ |
|---|---|
| Lỗi không ghi file; ngày sai thoát 2 | `tests/test_due.py`, `tests/test_valid_due_strict.py`, `tests/test_cli_overdue.py` |
| `todo`: id chỉ chữ số ASCII; tiêu đề rỗng exit 2, tab/xuống dòng thành khoảng trắng; `done` id không có exit 1 không ghi; JSON hỏng/sai `id` exit 2; ghi qua symlink; khoá `flock` | `tests/test_cli_errors.py`, `tests/test_store_safety.py` |
| Quá hạn: biên, sắp, không phụ thuộc đồng hồ | `tests/test_overdue.py` |
| Ảnh 360 thật (PNG + `innerWidth`), tối thật | `tests/test_tools.py` |
| Tương phản AA trên trang thật, nền trong suốt theo cha, chữ lớn 3:1 | `tests/test_tools.py` (`test_contrast_*`), `tests/test_site_dark.py` |
| Luật tài nguyên L2 (kể cả `@latest/X.Y.Z`, 22 biến thể H-06/H-09, `.svg`, trang thật không `on*`) | `tests/test_site_policy.py` |
| Công cụ đo: 0 đạt, 1 trượt ngưỡng, 2 lỗi công cụ/tham số; ảnh cũ không mang hash mới; `--pages /en/`; 404 không chụp; tràn `scrollWidth`; `lh_check` thiếu `index.html`; `smoke_pages` fetch, lỗi git exit 2; lỗi môi trường/tham số exit 2 không traceback, SHA mỗi lần thử, git timeout (R19) | `tests/test_screenshot_errors.py`, `tests/test_tools_errors.py`, `tests/test_screenshot_http.py`, `tests/test_overflow_scrollwidth.py`, `tests/test_tools_git_site.py`, `tests/test_tools_env_errors.py`, `tests/test_smoke_pages_args.py` |
| Spec thiết kế đủ (D2); hero không còn hứa laptop/ngủ gật/hơi nước/ngáp ngoài "Phần spec cũ bị bỏ" | `tests/test_design_doc.py` |
| Hex `:root` = bảng màu sáng đọc từ doc; không hex rời (trừ khối tối) | `tests/test_site_visual.py` |
| Khối tối chỉ gán lại `:root`, hex = bảng "Tối" của doc; SVG không hex cứng | `tests/test_site_dark.py` |
| Focus thấy được; SVG `aria-hidden` hoặc `role="img"` + `<title>`; heading không nhảy cấp; link và nút có tên | `tests/test_site_a11y.py` |
| SVG ≥ 3 phần tử vẽ, `<title>`/`aria-hidden`, `viewBox` | `tests/test_site_hero.py`, `tests/test_site_menu.py` |
| Nút `mailto:` bắt đầu bằng động từ; không `→`, không `uppercase`; FAQ ≥ 4 `<details>` có `summary`, CSS không ẩn `summary`; 3 dự án có "ví dụ" + SVG; cấm "khách hàng nói"/"đánh giá"/"testimonial" | `tests/test_site_content.py` |
| Không JS / CDN lỗi: mọi phần hiện; CSS không ẩn ngoài `.js`; SRI khớp; 1 timeline; giảm chuyển động bỏ timeline | `tests/test_site_motion.py` |
| Meta OG/Twitter, URL theo `SITE_URL`, `og.png` 1200×630 khớp hash `og.svg`, màu SVG thuộc token, favicon không `<text>`, JSON-LD | `tests/test_site_seo.py`, `tests/test_site_share.py` |
| Workflow Pages (đọc YAML): job `test` → `build` → `deploy`, bước test đúng nguyên lệnh, không `continue-on-error`/`if:`, quyền theo job, `timeout-minutes` (R19), ghim 4 action, `path: site`, lệnh "Ghi phiên bản" chạy thật; hai trang có `meta version` giữ chỗ; smoke so SHA, thiếu `og.png` → exit 1; `screenshot.py --url` giữ đường con | `tests/test_pages_workflow.py`, `tests/test_smoke_pages.py`, `tests/test_screenshot_url.py` |
| Bản Anh: cùng id, 1 `<h1>`, không chữ Việt có dấu, tài nguyên chung 200; `hreflang` hai chiều tuyệt đối; link chuyển ngôn ngữ; sitemap 2 URL | `tests/test_site_i18n.py` |
| Đúng 1 nút `type="button"`, `hidden` khi không JS, `aria-pressed` đổi, `:focus-visible` có `outline` | `tests/test_site_button.py` |

## Lỗ hổng mở
| Mã | Mức | Mô tả | Mốc nhận |
|---|---|---|---|
| H-12 | vừa | D4, D5, E2, L5 không trong verify/smoke/CI; `contrast.py` mặc định 1280, bỏ `::before` | người (config) |
| H-14 | vừa | Email `hello@example.com` giữ chỗ bị test khoá, không hiện thành chữ; `robots.txt` dưới `/autodev-sandbox/` crawler không đọc (URL `example.github.io` đã sửa ở R11) | leader |
| H-19 | thấp | `lazy-landing/criteria.md` còn nền "4/17", "L3 nền 69"; `ROADMAP.md` còn "R3–R13", "Trước R11" cũ (`goal.json` đã sửa) | người |
| H-21 | vừa | Cả bộ test chập chờn khi tải nặng (Chrome quá 60 giây → exit 2; audit R16: 1 failed, tải 27); Pages nay chờ cả bộ nên chặn deploy | mốc kiểm chứng |
| H-30 | thấp | L2 còn lọt `input type=image`, `video poster`, `srcset`, `meta refresh`, `iframe srcdoc`, `integrity=""`, `image-set()` | mốc công cụ |
| H-31 | thấp | Đạt trên giấy: probe hero tự đẩy timeline, chờ `lazySite` 10×50 ms ảo, D6/D3 xanh bằng skip khi offline | mốc công cụ |
| H-32 | thấp | `contrast.py`: `font-size:0`, nền gradient, `colors` rỗng đạt im lặng; `lh_check` `round()` banker trượt oan biên 95 | mốc công cụ |
| H-33 | thấp | Hết giờ chỉ giết tiến trình trực tiếp (`npx→node→Chrome` mồ côi); `OSError` khi dọn hồ sơ; chưa xác nhận, có thể góp H-21 | mốc công cụ |
| H-34 | thấp | `todo`: `load` chưa kiểm `title` (str), `done` (bool): `[{"id":1,"title":"a"}]` → `list` traceback `KeyError` (phần lỗi OS đóng gián tiếp ở R18: `OSError` → exit 2) | mốc todo (leader duyệt) |
| H-39 | vừa | Đóng H-04/05/11/20 yếu: 23 test skip offline (verify không đếm), H-11 mới 6/8 tệp (seo, share, visual, menu còn chỉ `index.html`), probe 360 đo trước font, ca âm rỗng, `test_site_ly.py:217` tautology | mốc kiểm chứng |
| H-41 | thấp | `todo list` cột `due` rỗng vỡ shell `read`; title/due từ file không làm sạch; README thiếu hợp đồng CLI | mốc todo (leader duyệt) |
| H-42 | thấp | `#luoi-nut`: ghế đỏ không test; nhãn vi cứng trong `main.js` | mốc kiểm chứng |
| H-47 | thấp | H-22 đóng bằng sửa spec: chưa hỏi lại leader về hero; dòng `Leader duyệt` không test | leader |
| H-48 | thấp | Bản Anh không JSON-LD, `og:image` chữ Việt, không test | leader |
| H-49 | thấp | `page_metrics` mặc định thu hẹp im lặng khi thiếu `en/`; `scrollWidth` báo oan off-canvas; `check_reachable` nhận mọi 2xx | mốc công cụ |
| H-50 | thấp | `smoke_pages --interval inf`/`1e12` → `OverflowError` traceback; `screenshot --pages " , "` không strip (chụp trang tên rỗng); `workflow_problems` lọt `permissions: write-all`, `shell: … \|\| true`, `working-directory`; test TC 2 dev-03 R19 xanh cả trên code cũ | mốc công cụ |

## Nợ không chặn
- Tham số `today` của `store.overdue` che `store.today()`.
- `test_dark_mode_applied_only_in_dark[1280]` từng đỏ một lần ở R4; `test_tools.py::test_four_pngs_with_exact_widths` timeout một lần ở R7. Không tái hiện. Theo dõi.
- L2 chưa kiểm `srcset`, `javascript:`. `_pinned` từ chối gói npm có scope (`@scope/pkg@X.Y.Z`): chặt quá.
- `test_mobile_price_wraps_below_name` yếu (dùng `or`).
- R7: test timeline thiếu assert trạng thái đầu; test CDN online nên `assert` thay `skip`; hai nút `.nut` ở hero sát nhau (thêm gap).
- R9: `og.svg` đứng riêng cần `@import` font (chỉ `og.png` chắc đúng font); `png_add_text` không atomic; vài test còn `sys.path.insert`; chưa có test bảo vệ miễn trừ canonical.
- R12: `test_metrics_svg_h1_font_and_repeat` (Chrome) đỏ một lần khi supervisor chạy cả bộ, chạy lại xanh; regex `test_css_does_not_hide_summary` không bắt rule lồng trong `@media`; test dự án dựa vào thẻ `article`.
- R8: kiểm `outline` lọt `outline:0px` và chưa gắn theo selector; `contrast.py` ném ValueError với màu tên (`red`), bỏ qua alpha chữ.
- R10: điểm Lighthouse phụ thuộc mạng ngoài (Google Fonts, jsDelivr).
- R14: L2 chưa bắt `<svg><a xlink:href>` ngoài (link điều hướng); vòng chờ `lazySite` trong probe chỉ 10 × 50 ms (biên hẹp).
- R13: bản Anh chưa có JSON-LD, `og:image` dùng chung `og.png` chữ Việt; test chữ Việt chỉ bắt chữ có dấu; ở 360 link "Tiếng Việt" rớt dòng dưới logo.

- R15: chờ font cố định 800 ms trong `MEASURE_JS` (có thể chập chờn khi mạng chậm); `test_cup_reduced_motion_block_instant` có assert `json.dumps(d)` vô nghĩa; test `scrollWidth` 360 chỉ chạy sáng.

## Quyết định gần đây
- 2026-10-21: merge R19 (PR #65). 7/7 tiêu chí tự chạy đạt (569 passed × 2; verify, smoke sạch; Pages test → build (`pages: read`) → deploy xanh, `smoke_pages` OK @ `805cbe0`, kiểm cả `en/`, `main.js`, `robots.txt`, `sitemap.xml`); test mới đỏ 56 ca trên code cũ. Đóng H-27, H-40, H-43, H-44, H-45, H-46. (c) phần hở nhỏ gộp H-50 (thấp) thay vì chặn.
- 2026-10-21: merge R18 (PR #62). 8/8 tiêu chí tự chạy đạt (verify lần 2 sạch, lần 1 đỏ 1 test site H-21; `test_store_safety` 5 × 23 passed; CLI thật 4 ca exit 2, file nguyên byte); 8 test roadmap đỏ trên code cũ (test khoá treo). Đóng H-35..H-38; H-34 thu hẹp còn kiểu `title`/`done`.
- 2026-10-21: audit R16 (`docs/audits/2026-10-21-3.md`): 7 lỗ mới H-43..H-49 (4 vừa, 3 thấp); H-22..H-25, H-28 xác nhận đóng (92 test tự chạy xanh); H-29 mở lại một phần (H-43, H-44); H-40, H-21 nâng vừa. Thực tế lazy-landing ~78–82%, due-overdue ~95%. Đề xuất R18 todo, R19 kiểm chứng (+H-21, H-46), R20 công cụ; leader: H-47, H-48.
- 2026-10-21: merge R16 (PR #56). 8/8 tiêu chí tự chạy đạt (467 passed × 2; Pages test → build → deploy xanh, `smoke_pages` OK @ `ff8c12f`); test mới đỏ 42 ca trên code cũ. Đóng H-22 (spec theo trang đã duyệt), H-23, H-24, H-25, H-28, H-29. (c) H-27 chỉ đóng phần fetch/lỗi git, phần kiểm thêm tài nguyên giữ mở; H-40 thu hẹp còn `smoke_pages`.
- 2026-10-21: audit R15, R17 (`docs/audits/2026-10-21-2.md`): 8 lỗ mới H-35..H-42 (5 vừa, 3 thấp), 0 đóng; xác nhận H-13, H-18, H-26, H-03 đóng thật; H-04, H-05, H-11, H-20 đóng một phần (H-39). Đề xuất: R16 công cụ (H-23..25, 27..30, 32, 33, 40), R18 todo (H-34..38, 41), R19 kiểm chứng (H-39, H-31, H-42); leader/người: H-22, H-14, H-12.
- 2026-10-21: merge R17 (PR #52). 7/7 tiêu chí tự chạy đạt (412 passed; song song 5 lần xanh; CLI thật exit 2/2/1/2, không traceback); test mới đỏ 34 ca trên code cũ. Đóng H-13, H-18, H-26. (c) ghi H-34 (`title`/`done`, lỗi OS) thay vì chặn: ngoài phạm vi roadmap R17.
- 2026-10-21: merge R15 (PR #48). 8/8 tiêu chí tự chạy đạt (374 passed × 3); test mới đỏ 13 ca trên `site/` cũ. Đóng H-03, H-04, H-05, H-11, H-20. (a) chấp nhận sửa `screenshot.frame_html` (polling `#out`). H-21, H-23..25, H-29, H-32, H-33 chuyển "mốc công cụ" (plan R15 để ngoài phạm vi); H-22 → leader.
- 2026-10-21: audit R1–R14 (`docs/audits/2026-10-21.md`): 12 lỗ mới H-22..H-33 (7 vừa, 5 thấp), 0 đóng; 6 lỗ R14 đóng nhưng còn phần hở (H-23, H-25, H-29, H-30, H-31). Đề xuất: R15 thêm dev công cụ (H-23..25, 29, 32, 33); mốc todo nhỏ (H-13, H-18, H-26); leader quyết H-22, H-14; người đưa D4/D5/L5 vào `smoke` (H-12).
- 2026-10-21: merge R14 (PR #44). 7 tiêu chí tự chạy đạt; `test_tools.py` chập chờn khi tải nặng → H-21 (R15), không chặn vì không hồi quy. Đóng H-06, H-07, H-09, H-10, H-15, H-17; bỏ H-08 khỏi bảng (D7 đạt). (c) chấp nhận `--pages` thay `--only`, `onload` font chuyển sang `main.js`.
- 2026-10-20: merge R11 (PR #40). Workflow `pages` xanh; `smoke_pages.py` trên URL thật exit 0 (E3); đóng H-16; H-14 còn email + `robots.txt`. D7 leader duyệt (PR #38) → `lazy-landing` 17/17.
- 2026-10-16: audit R4–R10 (`docs/audits/2026-10-16.md`): 14 lỗ mới H-07..H-20 (2 cao), 0 đóng; độ khớp thực tế ≈ 80% (đẹp đúng hướng ~65%, kỹ thuật ~85%, phát hành ~60%); đề xuất leader duyệt D7 trước R14/R11.
- 2026-10-16: merge R10 (PR #35). E2 đạt; (c) H-03..06 chuyển sang mốc mới R14 (cần `/autodev:plan-next R14`).
- 2026-10-16: merge R13 (PR #33). E5 đạt; ghi H-06 cho R10.
- 2026-10-16: merge R9 lần 2 (PR #30) sau dev-05, dev-06. E1 đạt; ảnh chia sẻ, favicon đúng hướng.
- 2026-10-16: không merge R9 lần 1 (PR #30). Tiêu chí 1, 2 đỏ (test `mtime`); `og.svg`/favicon lệch "Quy ước chung". (b) dev-05, dev-06; (c) bỏ tiêu chí `mtime`, thay hash nguồn trong PNG.
- 2026-10-16: merge R12 (PR #28). E4 đạt; chấp nhận (a) nới test số section `== 4` → `>= 4`.
- 2026-10-16: merge R8 (PR #26). D4, D5 đạt; H-03..05 không có task trong plan R8, chuyển R10 (plan R10 cần thêm task).
- 2026-10-16: merge R7 (PR #24). D6 đạt, đóng H-02; ghi H-05 cho R8.
- 2026-10-16: merge R6 (PR #22). Không duyệt đề xuất sửa doc để hợp thức việc ẩn nút header ở 360; ghi H-03, H-04 cho R8.
- 2026-10-16: merge R4 (PR #20). Ghi H-02 cho R7.
- 2026-10-16: merge R3 (PR #14); mục tiêu `lazy-landing` bản 2; R5 cắt.
