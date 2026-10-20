# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-21 · Nguồn: duyệt R14 (supervisor) + audit R4–R10 (`docs/audits/2026-10-16.md`)

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

## Mục tiêu và tiêu chí
- `due-overdue`: 5/5 = **100%** (xong).
- `lazy-landing` (`docs/goals/lazy-landing/criteria.md`, bản 2): 17/17 = **100%** theo lệnh đo; audit 2026-10-16 ước thực tế ≈ 80%; R14 đóng 6 lỗ công cụ/luật, còn H-03..05, H-11, H-12, H-14, H-20 (R15 / leader). Nên `/autodev:audit` đo lại.

| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| L1 | `uv run pytest -q tests/test_site.py` | 0 failed, ≥ 6 | 11 passed, đạt |
| L2 | `uv run pytest -q tests/test_site_policy.py` | 0 failed, ≥ 6 | 52 passed, đạt |
| L3 | `uv run pytest -q` | 0 failed | 295 passed × 3 lần liền, đạt |
| L4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| L5 | smoke HTTP (`criteria.md`) | `200` hai dòng | đạt |
| D1 | `uv run pytest -q tests/test_tools.py` | 0 failed, ≥ 5, không skip | 21 passed; chập chờn 2/7 lần khi máy tải nặng (H-21) |
| D2 | `uv run pytest -q tests/test_design_doc.py` | 0 failed | 7 passed, đạt |
| D3 | `uv run pytest -q tests/test_site_visual.py` | 0 failed, ≥ 5 | đạt |
| D4 | `uv run python scripts/page_metrics.py --check-overflow` | exit 0 | exit 0, 4/4 tổ hợp không tràn, đạt |
| D5 | `uv run python scripts/contrast.py` | 0 cặp trượt, exit 0 | exit 0 (sáng + tối), đạt |
| D6 | `uv run pytest -q tests/test_site_motion.py` | 0 failed, ≥ 4 | 13 passed (có mạng), đạt |
| E4 | `uv run pytest -q tests/test_site_content.py` | 0 failed, ≥ 4 | 12 passed, đạt |
| E1 | `uv run pytest -q tests/test_site_seo.py` | 0 failed, ≥ 6 | 12 passed, đạt |
| E5 | `uv run pytest -q tests/test_site_i18n.py` | 0 failed, ≥ 4 | 14 passed, đạt |
| E2 | `uv run python scripts/lh_check.py` | perf ≥ 90, a11y/bp/seo ≥ 95, ≤ 300 KB | `/` trung vị 100×4, 173 KB; `/en/` 99/100/100/100, 166 KB; đạt (R14, sau bỏ `onload`) |
| D7 | `grep -q '^Leader duyệt: đạt' docs/design/lazy-landing.md` | exit 0 | đạt (leader, PR #38, 2026-10-20) |
| E3 | `uv run python scripts/smoke_pages.py` | 200, SHA khớp `main` | exit 0 @ `66bcab8`, đạt |

## Kiến trúc hiện nay
- `src/todo/`: CLI todo (`add --due`, `list`, `overdue`, `done`, `due`); luật ngày duy nhất ở `store.valid_due`.
- `site/`: landing "Quán cóc đầu ngõ" 6 phần (`hero`, `dich-vu`, `cach-lam`, `du-an` (3 dự án hư cấu, mỗi `article` có "(ví dụ)" + SVG), `hoi-dap` (4 `<details>`), `lien-he`). `style.css`: token 6 màu sáng ở `:root` (`--color-*`), Google Fonts (Baloo 2, Be Vietnam Pro) nạp trong HTML bằng `<link rel=preload as=style>` (không `onload`; `main.js` đổi `rel` sang `stylesheet`, R14) + `<noscript>` (R10, bỏ `@import`), menu bảng liền có chấm dẫn. Tối: `@media (prefers-color-scheme: dark)` chỉ gán lại token `:root` theo bảng "Tối" của doc, thêm `--color-chu-nut`, `--color-chu-tren-tra`. `:focus-visible` có `outline` cho link và nút. 8 SVG inline (`currentColor` / `var()`, nét 2,5): hero (ghế + ly), 3 biểu tượng gói, ghế trống ở liên hệ, 3 minh hoạ `#du-an` (`aria-hidden`).
- Chuyển động: GSAP 3.12.5 qua jsDelivr (SRI, `defer`) + `site/main.js`. Không có `gsap` thì không làm gì (không class `js`). Một timeline hero (`h1`, `.hero-hinh`, `gsap.from` + `clearProps`); nút `#luoi-nut` (`hidden` khi không JS, `aria-pressed`) dịch hai ghế và ly. `window.lazySite.shouldAnimate()` đọc `prefers-reduced-motion`; `false` thì không timeline, nút dùng `gsap.set`.
- `scripts/screenshot.py`: Chrome headless; 1280 trực tiếp, < 1000 qua iframe; tối bằng `--blink-settings`; ảnh ở `.autodev/shots/` (gitignore). R14: `shoot()` xoá ảnh cũ trước khi chụp; Chrome `returncode != 0`, không có tệp, timeout 60 giây (hằng số), DOM rỗng → `RuntimeError`; `main` in `Lỗi: ...`, exit 2 (cả `--url` không tới được); `--page` chỉ ghi chunk hash khi chụp xong. Dưới `--virtual-time-budget` rAF gần như không phát: hero chụp ra còn dở intro (đẩy `gsap.globalTimeline.time` như test, CDP thời gian thật, hoặc bản sao bỏ `<script>`).
- `scripts/page_metrics.py`: JSON mỗi dòng một tổ hợp (`width`, `mode`, `innerWidth`, `overflow`, `svg_by_section`, `h1`, `body_font`, `colors`); `colors` gộp theo bộ (màu, nền, cỡ, đậm), nền lấy theo cây cha. `--check-overflow` exit 1 khi tràn; exit 2 lỗi công cụ (Chrome, trang không có, danh sách rỗng); `--pages` nhận `/en/`, `/en`, `/en/index.html` (R14). `h1.font_family` là chuỗi khai báo, không chứng minh font đã tải (H-04).
- `scripts/contrast.py`: tỉ lệ WCAG 2.x trên `colors` của `page_metrics.py`; chữ lớn (≥ 24px, hoặc ≥ 18,66px đậm) 3:1, còn lại 4,5:1; mặc định 1280, cả hai chế độ (`--widths`, `--modes`, `--site`); exit 1 khi trượt, 2 khi lỗi công cụ (R14). Bỏ qua alpha chữ, không đo `:hover`/`:focus`.
- SEO (R9): `scripts/site_config.py` (`SITE_URL` = `https://silver-rp.github.io/autodev-sandbox/` từ R11); meta OG/Twitter, canonical, JSON-LD `ProfessionalService`, `robots.txt`, `sitemap.xml` ghi cứng URL (test kiểm khớp `SITE_URL`, không còn `example.github.io`).
- Triển khai (R11): `.github/workflows/pages.yml` (push `main` + `workflow_dispatch`; checkout@v4, configure-pages@v5, upload-pages-artifact@v3 `path: site`, deploy-pages@v4; `concurrency: pages`) thay `<meta name="version" content="dev">` ở hai trang bằng `github.sha` trước khi upload. `scripts/smoke_pages.py [--url] [--sha] [--retries 10] [--interval 30]`: `/` 200 + "Lười Code Studio" + version = `origin/main`, `/en/`, `/style.css`, `/og.png` 200. `screenshot.py --url` giữ đường con, không dùng `__frame__`, lỗi HTTP → exit khác 0. Mỗi merge vào `main` (kể cả PR hồ sơ) deploy lại. `og.svg` → `og.png` qua `screenshot.py --page /og.svg --size 1200x630`, PNG mang chunk `tEXt` `source-sha256` (`og_png_current`). `pytest` có `pythonpath` trong `pyproject.toml`.
- Song ngữ (R13): `site/en/index.html` (`lang="en"`, cùng id section tiếng Việt không dấu) dùng chung `../style.css`, `../main.js`; `hreflang` vi/en/x-default + canonical riêng mỗi trang, URL tuyệt đối; link `.doi-ngon-ngu` ở header (không JS); `#luoi-nut` lấy nhãn từ `data-on`/`data-off`; `sitemap.xml` hai URL. `contrast.py`, `page_metrics.py` có `--pages` (mặc định mọi trang có thật), `screenshot.py --pages` (ảnh `en-<w>-<mode>.png`).
- `scripts/lh_check.py` (R10): phục vụ `site/` cổng 0; `npx -y lighthouse@12` mobile, 3 lần `/` + 1 lần `/en/`, trung vị; exit 1 dưới ngưỡng E2; exit 2 lỗi công cụ: thiếu `npx`/Chrome, quá `--timeout` (mặc định 180 giây), JSON thiếu khoá/`null`/NaN, trang không có, không trang nào (R14). `--pages` thay `--only`.
- `tests/_policy.py` (R14): bắt `<base>`, URL `/\`, `\\`, mọi `on*`, `javascript:`, `object data`, `svg image`/`use`/`xlink:href`, `form action` ngoài, SRI rỗng; miễn trừ `canonical`/`alternate hreflang` chỉ khi `href` bắt đầu bằng `SITE_URL` và `rel` đúng một giá trị; quét cả `site/**/*.svg`. `check(html, css)` cho L2; `_pinned(src)`: mọi `@tag` phải là X.Y.Z, không có `@` thì cần `/X.Y.Z/`.

## Quy tắc → test bảo vệ
| Quy tắc | Test bảo vệ |
|---|---|
| Lỗi không ghi file; ngày sai thoát 2 | `tests/test_due.py`, `tests/test_valid_due_strict.py`, `tests/test_cli_overdue.py` |
| Quá hạn: biên, sắp, không phụ thuộc đồng hồ | `tests/test_overdue.py` |
| Ảnh 360 thật (PNG + `innerWidth`), tối thật | `tests/test_tools.py` |
| Tương phản AA trên trang thật, nền trong suốt theo cha, chữ lớn 3:1 | `tests/test_tools.py` (`test_contrast_*`), `tests/test_site_dark.py` |
| Luật tài nguyên L2 (kể cả `@latest/X.Y.Z`, 22 biến thể H-06/H-09, `.svg`, trang thật không `on*`) | `tests/test_site_policy.py` |
| Công cụ đo: 0 đạt, 1 trượt ngưỡng, 2 lỗi công cụ; ảnh cũ không mang hash mới; `--pages /en/` | `tests/test_screenshot_errors.py`, `tests/test_tools_errors.py` |
| Spec thiết kế đủ (D2) | `tests/test_design_doc.py` |
| Hex `:root` = bảng màu sáng đọc từ doc; không hex rời (trừ khối tối) | `tests/test_site_visual.py` |
| Khối tối chỉ gán lại `:root`, hex = bảng "Tối" của doc; SVG không hex cứng | `tests/test_site_dark.py` |
| Focus thấy được; SVG `aria-hidden` hoặc `role="img"` + `<title>`; heading không nhảy cấp; link và nút có tên | `tests/test_site_a11y.py` |
| SVG ≥ 3 phần tử vẽ, `<title>`/`aria-hidden`, `viewBox` | `tests/test_site_hero.py`, `tests/test_site_menu.py` |
| Nút `mailto:` bắt đầu bằng động từ; không `→`, không `uppercase`; FAQ ≥ 4 `<details>` có `summary`, CSS không ẩn `summary`; 3 dự án có "ví dụ" + SVG; cấm "khách hàng nói"/"đánh giá"/"testimonial" | `tests/test_site_content.py` |
| Không JS / CDN lỗi: mọi phần hiện; CSS không ẩn ngoài `.js`; SRI khớp; 1 timeline; giảm chuyển động bỏ timeline | `tests/test_site_motion.py` |
| Meta OG/Twitter, URL theo `SITE_URL`, `og.png` 1200×630 khớp hash `og.svg`, màu SVG thuộc token, favicon không `<text>`, JSON-LD | `tests/test_site_seo.py`, `tests/test_site_share.py` |
| Workflow Pages ghim 4 action, quyền đúng, `path: site`; hai trang có `meta version` giữ chỗ; smoke so SHA, thiếu `og.png` → exit 1; `screenshot.py --url` giữ đường con | `tests/test_pages_workflow.py`, `tests/test_smoke_pages.py`, `tests/test_screenshot_url.py` |
| Bản Anh: cùng id, 1 `<h1>`, không chữ Việt có dấu, tài nguyên chung 200; `hreflang` hai chiều tuyệt đối; link chuyển ngôn ngữ; sitemap 2 URL | `tests/test_site_i18n.py` |
| Đúng 1 nút `type="button"`, `hidden` khi không JS, `aria-pressed` đổi, `:focus-visible` có `outline` | `tests/test_site_button.py` |

## Lỗ hổng mở
| Mã | Mức | Mô tả | Mốc nhận |
|---|---|---|---|
| H-03 | vừa | Ở 360: dấu chấm dẫn menu bị ẩn (`.cham {display:none}`) và nút header bị ẩn, lệch wireframe 360 của doc; không test nào bắt | R15 |
| H-04 | thấp | Test font `<h1>` chỉ đọc `font-family` khai báo; cần `document.fonts.check` để chứng minh Baloo 2 đã tải | R15 |
| H-05 | thấp | `style.css` chưa có `@media (prefers-reduced-motion: reduce)` như quy ước plan R7 (giảm chuyển động hiện chỉ ở `main.js`) | R15 |
| H-11 | vừa | Test a11y, nội dung, hero, nút, SVG hex, SRI, og:image chỉ đọc bản Việt | R15 |
| H-12 | vừa | D4, D5, E2, L5 không trong verify/smoke/CI; `contrast.py` mặc định 1280, bỏ `::before` | người (config) |
| H-13 | vừa | `todo done <id không có>` vẫn ghi file, không báo lỗi | mốc todo |
| H-14 | vừa | Email `hello@example.com` giữ chỗ bị test khoá, không hiện thành chữ; `robots.txt` dưới `/autodev-sandbox/` crawler không đọc (URL `example.github.io` đã sửa ở R11) | leader |
| H-18 | thấp | `todo` store: ghi song song mất cập nhật; JSON hỏng traceback; symlink bị thay | mốc todo |
| H-19 | thấp | `due-overdue/goal.json` còn `planned`; `criteria.md` nền cũ | người |
| H-20 | thấp | Nút hero dịch ly nhưng đá, ống hút đứng yên | R15 |
| H-21 | thấp | `test_tools.py` (Chrome thật) chập chờn khi máy tải nặng: Chrome quá 60 giây (hằng số) → exit 2; supervisor thấy 2/7 lần ở load ~14,5 | R15 |

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

## Quyết định gần đây
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
