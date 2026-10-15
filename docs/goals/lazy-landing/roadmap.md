# ROADMAP: `lazy-landing` (bản 2)

Hướng: lõi R4–R8 (đẹp, có cá tính, tự nhìn được) rồi mở rộng R12 → R9 → R13 → R10 → R11. Không có trần chi phí.

## Nguồn ước tính
Số đo sandbox trong `docs/autodev/PROGRESS.md`:

| Mốc | Task | Phút | USD |
|---|---|---|---|
| R1 | 3 | 4 (worker) | 0,71 worker |
| R2 | 3 | 4 (worker) | 0,72 worker + ~0,75 supervisor |
| R3 | 3 | ~5 (cả mốc) | chưa đo |

Công thức: **USD = số task × 0,25 × hệ số + 0,75 supervisor**.
- Hệ số ×2 cho mốc chụp và đọc ảnh, ×1,5 cho mốc song ngữ. Đây là giả định, chưa có số đo; đối chiếu sau R5 và sửa ước tính các mốc sau nếu lệch quá 2 lần.
- Giờ máy: khoảng 5 phút mỗi 3 task × hệ số, cộng thời gian Chrome / Lighthouse, làm tròn lên 0,1 giờ.
- So với luật mục 6.5: supervisor tính theo số đo sandbox (khoảng 0,75 USD), không theo mức "+2 USD" (vì R1, R2 đã lệch hơn 2 lần so với mức đó); không có Postgres; không cộng tiền audit.

## R3: Landing page dùng được (đã xong)
- **Trạng thái:** merged 2026-10-16, PR #14 (`e00fa79`). Plan: `plan/R3.md`. Đạt L1, L3, L4, L5.
- **Thay đổi ở bản 2:** test `test_css_content` (bắt buộc `system-ui`, cấm `//`) sẽ được R4 sửa theo luật L2 mới.

## R4: Công cụ nhìn và dọn luật cũ
- **Mục tiêu:** agent và reviewer chụp và đo được trang thật; luật tài nguyên khớp quyết định mới.
- **Phạm vi:**
  1. `scripts/screenshot.py`:
     - chụp bằng Chrome headless: 1280px trực tiếp, 360px qua trang khung `<iframe width=360>`;
     - chế độ tối bằng `--blink-settings=preferredColorScheme=0`;
     - ghi PNG vào thư mục chỉ định (mặc định `.autodev/shots/`, thêm vào `.gitignore`).
  2. `scripts/page_metrics.py`:
     - nạp trang qua `--dump-dom` với script đo chèn tạm (không sửa `site/`);
     - in JSON: `innerWidth`, phần tử tràn, số SVG theo section, font và cỡ `<h1>`, màu tính được;
     - cờ `--check-overflow` trả exit ≠ 0 khi tràn.
  3. `tests/test_tools.py`:
     - kiểm bề rộng PNG, `innerWidth` = 360 trong iframe, `matchMedia` tối = `true`;
     - ca âm: trang tràn ngang mẫu (kể cả có `overflow-x: hidden` trên `body`);
     - skip khi không có Chrome.
  4. `tests/test_site_policy.py` thay luật cũ:
     - danh sách domain cho phép, SRI + `crossorigin` + phiên bản ghim, script inline chỉ JSON-LD, không phân biệt hoa thường;
     - sửa `test_css_content` của R3 (bỏ `system-ui`, cho `//` của domain được phép).
- **Chỉ số đẩy lên:** D1, L2; giữ L1, L3–L5.
- **Ước tính:** 4 task × 0,25 + 0,75 = **1,8 USD**, **0,2 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_tools.py tests/test_site_policy.py` 0 failed (≥ 5 và ≥ 6 test); `uv run python scripts/screenshot.py` ra 4 PNG đúng bề rộng; `verify.py` sạch.
- **Phụ thuộc:** R3.
- **Pre-mortem:**
  1. *Ảnh 360 giả* (Chrome headless không xuống dưới 500px, đã đo): test đọc header PNG **và** `innerWidth` trong iframe = 360.
  2. *Chế độ tối không áp dụng*: test trang mẫu `matchMedia('(prefers-color-scheme: dark)')` = `true`.
  3. *Kiểm tràn đạt sẵn* nhờ `overflow-x: hidden`: đo `scrollWidth` của mọi phần tử; ca âm có `overflow-x: hidden`.
  4. *Nới luật quá tay*: script inline lạ phải bị trượt (ca âm); `@latest` hoặc thiếu `integrity` phải bị trượt.

## R5: Ba hướng thiết kế (dừng chờ leader)
- **Mục tiêu:** leader có 3 hướng khác hẳn nhau để chọn, mỗi hướng có bản phác và ảnh thật.
- **Phạm vi:**
  1. `docs/design/lazy-landing.md` theo quy trình `frontend-design`:
     - chủ đề, người xem, việc chính của trang;
     - mỗi hướng: tên, 4–6 màu hex có tên, kiểu chữ (Google Fonts), wireframe ASCII cho 360 và 1280, căn lề, nguyên tắc, "điểm nhấn duy nhất", mục "dấu hiệu AI đã tránh" (đủ 5 nhóm của skill);
     - dòng `Hướng đã chọn:` để trống.
  2. `site/_sketch/<hướng>.html` × 3: bản phác hero và một phần dịch vụ, mỗi bản ≥ 1 SVG tự vẽ.
  3. Ảnh 360 và 1280 của từng bản phác (qua `screenshot.py`), nhúng link trong doc.
  4. `tests/test_design_doc.py`: đủ mục mỗi hướng; 3 hướng khác nhau về font và wireframe; bản phác tồn tại và có SVG.
- **Chỉ số đẩy lên:** D2 (phần máy đo); phần "leader chọn" là việc chỉ người làm.
- **Ước tính:** 4 × 0,25 × 2 + 0,75 = **2,8 USD**, **0,3 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_design_doc.py` 0 failed; báo cáo mốc kết thúc bằng câu hỏi chọn hướng (đánh số 1–3) cho leader.
- **Phụ thuộc:** R4.
- **Pre-mortem:**
  1. *Ba hướng chỉ là một hướng đổi màu*: test so font và wireframe; reviewer nhìn 3 ảnh cạnh nhau.
  2. *Rơi vào dấu hiệu AI* (nền kem `#F4F1EA` + accent `#D97757`, thẻ SaaS, nhãn VIẾT HOA, `→`): reviewer so mã màu và đọc mục "đã tránh"; test cấm hai mã màu đó.
  3. *Bản phác chỉ là chữ*: mỗi bản phác ≥ 1 SVG; reviewer nhìn ảnh.

## R6: Dựng trang theo hướng đã chọn
- **Mục tiêu:** `site/index.html` + `style.css` mang hướng đã chọn, có đồ hoạ, vẫn giữ cấu trúc R3.
- **Phạm vi:**
  1. Token màu và chữ ở `:root` khớp hướng đã chọn; Google Fonts (`preconnect`, `display=swap`, có font dự phòng).
  2. Bố cục và nội dung viết lại theo phần "viết trong thiết kế" của skill (giọng chủ động, cụ thể, không chữ đệm); giữ 4 id của R3.
  3. Hero có minh hoạ SVG inline tự vẽ (ví dụ võng, ly cà phê, laptop "tự code"), dùng `currentColor` hoặc biến màu.
  4. SVG cho 3 gói và 3 bước ("cách làm" là chuỗi thật nên được đánh số); nút hành động `mailto:`.
  5. `tests/test_site_visual.py` (D3) và ảnh chụp 4 cỡ sau mỗi task cho reviewer.
- **Chỉ số đẩy lên:** D3; giữ L1 (không cắt).
- **Ước tính:** 5 × 0,25 × 2 + 0,75 = **3,3 USD**, **0,4 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_site_visual.py tests/test_site.py tests/test_site_policy.py` 0 failed; reviewer đã xem 4 ảnh.
- **Phụ thuộc:** R5 **và** dòng `Hướng đã chọn:` đã được leader điền.
- **Pre-mortem:**
  1. *SVG cho có*: mỗi SVG ≥ 3 phần tử vẽ và có `<title>`; reviewer nhìn ảnh.
  2. *Lệch hướng đã chọn*: test so token màu và font với hướng trong doc.
  3. *Phá cấu trúc R3*: L1 phải xanh.
  4. *Font Google không tải mà test vẫn xanh*: kiểm font tính được của `<h1>` trên trang thật (`page_metrics.py`); skip khi không có mạng, reviewer ghi lại.

## R7: Chuyển động và tương tác
- **Mục tiêu:** một khoảnh khắc chuyển động lúc tải trang và một tương tác vui, không làm hỏng trang khi thiếu JS.
- **Phạm vi:**
  1. GSAP qua `cdn.jsdelivr.net` hoặc `cdnjs`, ghim phiên bản, `integrity` + `crossorigin`, `defer`.
  2. Một timeline lúc tải trang (hero và minh hoạ); một tương tác, ví dụ nút "Để tôi lười giúp bạn" làm minh hoạ phản ứng. Không rắc hiệu ứng ở mọi section.
  3. `prefers-reduced-motion: reduce` thì bỏ timeline. Trạng thái ẩn ban đầu chỉ do JS đặt (class `js` trên `<html>`), không đặt sẵn trong CSS.
  4. `tests/test_site_motion.py` (D6).
- **Chỉ số đẩy lên:** D6.
- **Ước tính:** 3 × 0,25 × 2 + 0,75 = **2,3 USD**, **0,3 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_site_motion.py tests/test_site_policy.py` 0 failed.
- **Phụ thuộc:** R6.
- **Pre-mortem:**
  1. *Kiểu `gsap.from` làm nội dung ẩn sẵn*, CDN lỗi thì trang trắng: test tắt JS và test CDN sai URL, 4 phần vẫn hiện.
  2. *Rắc hiệu ứng*: reviewer đếm timeline và tương tác (tối đa 1 + 1).
  3. *Bỏ qua giảm chuyển động*: test giả lập `reduce`.
  4. *SRI sai hash nên script bị chặn âm thầm*: test tính sha384 của file trên CDN (skip khi không có mạng).

## R8: Chế độ tối và truy cập
- **Mục tiêu:** chế độ tối được thiết kế riêng; đạt tương phản AA, focus, bàn phím; không tràn ở 360.
- **Phạm vi:**
  1. Bảng màu tối riêng (không chỉ đảo màu); SVG đổi màu theo chế độ.
  2. `scripts/contrast.py` (D5) đo màu tính được của từng khối chữ, cả hai chế độ.
  3. `:focus-visible` rõ ràng; điều hướng bằng bàn phím tới nút liên hệ và tương tác R7; SVG trang trí `aria-hidden`, SVG mang nghĩa có `<title>`; heading không nhảy cấp.
  4. Sửa mọi chỗ tràn ở 360 và 1280 (D4).
- **Chỉ số đẩy lên:** D4, D5.
- **Ước tính:** 4 × 0,25 × 2 + 0,75 = **2,8 USD**, **0,3 giờ**.
- **Xong khi:** `uv run python scripts/contrast.py` và `uv run python scripts/page_metrics.py --check-overflow` exit 0; `verify.py` sạch. Sau mốc, **leader duyệt D7 lần 1**.
- **Phụ thuộc:** R6 (chạy sau R7 để đo cả phần tử tương tác).
- **Pre-mortem:**
  1. *Tương phản đo trên token chứ không trên trang thật*: `contrast.py` dùng `getComputedStyle` trên trang thật.
  2. *`outline: none` không có thay thế*: test bắt.
  3. *Tối chỉ đổi nền, SVG vẫn đen*: SVG dùng `currentColor` hoặc biến; reviewer nhìn ảnh tối.

## R12: Mở rộng nội dung
- **Mục tiêu:** trang đủ ý cho người xem thật: hỏi đáp và ví dụ việc đã làm.
- **Phạm vi:**
  1. FAQ ≥ 4 câu bằng `<details>`, giọng đúng thương hiệu.
  2. Mục "dự án đã lười xong": 3 dự án hư cấu, mỗi dự án ghi "ví dụ", có minh hoạ SVG nhỏ.
  3. `tests/test_site_content.py` (E4); chạy lại D4 và D5.
- **Chỉ số đẩy lên:** E4.
- **Ước tính:** 3 × 0,25 × 2 + 0,75 = **2,3 USD**, **0,2 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_site_content.py` 0 failed; D4 và D5 vẫn exit 0.
- **Phụ thuộc:** R6 (chạy sau R8).
- **Pre-mortem:**
  1. *Dự án hư cấu trông như thật*: test đòi chữ "ví dụ", cấm "khách hàng nói" / "đánh giá".
  2. *FAQ dài làm vỡ 360px*: D4 chạy lại.

## R9: SEO và chia sẻ
- **Mục tiêu:** chia sẻ link có ảnh đẹp; máy tìm kiếm hiểu trang.
- **Phạm vi:**
  1. Meta Open Graph và Twitter, `canonical`.
  2. `site/og.png` 1200×630 dựng từ một SVG riêng rồi chụp bằng `screenshot.py`.
  3. Favicon SVG, `robots.txt`, `sitemap.xml` (URL gốc lấy từ một hằng duy nhất để R11 thay).
  4. JSON-LD `ProfessionalService`; `tests/test_site_seo.py` (E1).
- **Chỉ số đẩy lên:** E1.
- **Ước tính:** 4 × 0,25 + 0,75 = **1,8 USD**, **0,2 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_site_seo.py` 0 failed.
- **Phụ thuộc:** R6, R12.
- **Pre-mortem:**
  1. *`og:image` sai cỡ hoặc trống*: test đọc header PNG đúng 1200×630, file > 5 KB; reviewer nhìn ảnh.
  2. *JSON-LD sai cú pháp*: `json.loads`, kiểm `@context` và `@type`.
  3. *URL tuyệt đối trỏ domain chưa có*: một hằng duy nhất; R11 thay và test lại.

## R13: Song ngữ Việt/Anh
- **Mục tiêu:** bản tiếng Anh tương đương, chuyển qua lại được.
- **Phạm vi:**
  1. `site/en/index.html` dùng chung `style.css` và SVG; nội dung dịch có chủ đích, giữ giọng đùa.
  2. `hreflang` hai chiều, `x-default`, thêm vào `sitemap.xml`; meta OG tiếng Anh.
  3. Nút chuyển ngôn ngữ (link thường, không cần JS); `tests/test_site_i18n.py` (E5).
- **Chỉ số đẩy lên:** E5.
- **Ước tính:** 3 × 0,25 × 1,5 + 0,75 ≈ **1,9 USD**, **0,3 giờ**.
- **Xong khi:** `uv run pytest -q tests/test_site_i18n.py` 0 failed; D4, D5 chạy cho cả `/en/`. Sau mốc, **leader duyệt D7 lần 2**.
- **Phụ thuộc:** R12, R9.
- **Pre-mortem:**
  1. *Bản Anh thiếu phần*: test so tập id hai bản.
  2. *`hreflang` một chiều*: test kiểm cả hai chiều.
  3. *Dịch máy cẩu thả*: leader xem ở D7.

## R10: Hiệu năng
- **Mục tiêu:** điểm Lighthouse cao trên mobile mà không bỏ thiết kế.
- **Phạm vi:**
  1. `scripts/lh_check.py`: phục vụ `site/` qua HTTP, chạy `npx -y lighthouse@12` chế độ mobile 3 lần, lấy trung vị, so ngưỡng, tính tổng tải.
  2. Tối ưu: `preconnect`, `font-display: swap`, cắt bớt trọng lượng font, `defer` JS, nén SVG.
  3. Sửa đến khi đạt E2.
- **Chỉ số đẩy lên:** E2.
- **Ước tính:** 3 × 0,25 + 0,75 = **1,5 USD**, **0,3 giờ** (Lighthouse chạy chậm).
- **Xong khi:** `uv run python scripts/lh_check.py` exit 0 (Performance ≥ 90, Accessibility / Best Practices / SEO ≥ 95, tổng tải ≤ 300 KB).
- **Phụ thuộc:** R7, R8, R13.
- **Pre-mortem:**
  1. *Đạt nhờ đo trang rút gọn hoặc đo ở desktop*: đo đúng `site/` qua HTTP, mobile, trung vị 3 lần.
  2. *Bỏ font hoặc chuyển động để lấy điểm*: D3, D6 phải vẫn xanh.

## R11: Triển khai GitHub Pages
- **Mục tiêu:** trang có URL thật, tự cập nhật khi merge `main`.
- **Phạm vi:**
  1. `.github/workflows/pages.yml` deploy `site/` khi push `main`; ghi `<meta name="version" content="<SHA>">` lúc build.
  2. `scripts/smoke_pages.py` (E3); thay hằng URL gốc ở R9 bằng URL thật.
- **Chỉ số đẩy lên:** E3.
- **Ước tính:** 2 × 0,25 + 0,75 = **1,3 USD**, **0,2 giờ**.
- **Xong khi:** `uv run python scripts/smoke_pages.py` exit 0 (200, có tên, SHA khớp).
- **Phụ thuộc:** R10 **và** leader đã bật Pages.
- **Pre-mortem:**
  1. *Deploy bản cũ hoặc dính cache*: smoke so SHA trong meta với `main`.
  2. *Repo private chưa bật Pages*: mốc BLOCKED, không giả đạt.
  3. *Kill giữa deploy*: Pages deploy nguyên khối theo artifact; chạy lại workflow là đủ, smoke xác nhận.

## Tổng
| Thứ tự chạy | Mốc | Phụ thuộc | Chỉ số | USD | Giờ máy |
|---|---|---|---|---|---|
| – | R3 (xong) | – | L1, L5 | – | – |
| 1 | R4 | R3 | D1, L2 | 1,8 | 0,2 |
| 2 | R5 | R4 | D2 | 2,8 | 0,3 |
| 3 | R6 | R5 + leader chọn | D3 | 3,3 | 0,4 |
| 4 | R7 | R6 | D6 | 2,3 | 0,3 |
| 5 | R8 | R6 | D4, D5 (+ D7 lần 1) | 2,8 | 0,3 |
| 6 | R12 | R6 | E4 | 2,3 | 0,2 |
| 7 | R9 | R6, R12 | E1 | 1,8 | 0,2 |
| 8 | R13 | R12, R9 | E5 (+ D7 lần 2) | 1,9 | 0,3 |
| 9 | R10 | R7, R8, R13 | E2 | 1,5 | 0,3 |
| 10 | R11 | R10 + leader bật Pages | E3 | 1,3 | 0,2 |
| | **Tổng (R4–R13)** | | | **21,8** | **2,7** |

## Thứ tự cắt
1. R11 Triển khai
2. R13 Song ngữ
3. R10 Hiệu năng (giữ phần tối ưu đã làm)
4. R9 SEO và chia sẻ
5. R12 Mở rộng nội dung
6. R7 Chuyển động (trang vẫn đẹp khi tĩnh)

## Không cắt
- R4, R5, R6, R8 (lõi "đẹp, có cá tính, không chỉ chữ", chế độ tối, truy cập) và D7 (leader duyệt bằng mắt).
- Ở mọi mốc: L1, L3, L4, L5; luật tài nguyên L2 (danh sách cho phép, SRI); nội dung đủ khi tắt JS.

## Việc chỉ người làm
- Sau R5: chọn hướng thiết kế, điền `Hướng đã chọn:` trong `docs/design/lazy-landing.md`.
- Sau R8 và sau R13: duyệt bằng mắt (D7); ghi `Leader duyệt: đạt` hoặc ý sửa.
- Trước R11: bật GitHub Pages (repo private cần gói trả phí, hoặc đổi sang public) và cho biết URL.
- Thay tên, email, giá giữ chỗ khi cần.
- Tuỳ chọn: thêm `screenshot.py` và lệnh L5 vào `smoke` của `.autodev/config.json`.

## Kế hoạch cũ được thay
- **R4 cũ** "Hoàn thiện tối giản" (chỉ số L2 cũ: không `<script>`, 0 tài nguyên ngoài, ≤ 30 KB, bắt buộc `system-ui`) bị **thay** bằng R4–R8 ở trên. Lý do: leader xem R3 và thấy "xấu quá, chỉ có text"; đổi yêu cầu sang đẹp, có cá tính, cho phép Google Fonts và JS qua CDN.
- Phần còn hợp lệ của R4 cũ được chuyển sang mốc mới:
  - chế độ tối và 360px → R8;
  - `alt` / heading → R8;
  - quét tài nguyên ngoài không phân biệt hoa thường → L2 ở R4 (ghi chú reviewer R3).
- R3 và các chỉ số L1, L3, L4, L5 giữ nguyên.
