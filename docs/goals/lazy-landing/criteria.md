# Tiêu chí: `lazy-landing` (bản 2)

Dự án chưa có file tiêu chí (`paths.criteria_file` rỗng), nên bảng dưới là toàn bộ tiêu chí. Nền đo ngày 2026-10-16 trên `origin/main` (`e00fa79`, sau R3).

**Thay đổi so với bản 1:**
- L1, L3, L4, L5 giữ nguyên.
- L2 cũ ("tối giản": không `<script>`, 0 tài nguyên ngoài, ≤ 30 KB, bắt buộc `system-ui` qua test R3) bị **thay** bằng L2 mới (luật tài nguyên có danh sách cho phép). Lý do: leader cho phép Google Fonts và JS qua CDN, và đổi yêu cầu từ "tối giản" sang "đẹp, có cá tính".
- Ngân sách dung lượng chuyển sang E2 (tổng tải ≤ 300 KB).
- Thêm D1–D7, E1–E5.

## Bảng chỉ số

| Mã | Định nghĩa | Lệnh đo | Nền | Ngưỡng |
|---|---|---|---|---|
| L1 | Cấu trúc trang (như bản 1) | `uv run pytest -q tests/test_site.py` | 11 passed | 0 failed, ≥ 6 test |
| L2 | Luật tài nguyên: domain ngoài chỉ thuộc `fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.jsdelivr.net`, `cdnjs.cloudflare.com`; script ngoài có `integrity` + `crossorigin` + phiên bản ghim (không `@latest`, không bỏ số phiên bản); script inline chỉ `type="application/ld+json"`; không có `http:`; quét HTML và CSS, không phân biệt hoa thường | `uv run pytest -q tests/test_site_policy.py` | chưa có | 0 failed, ≥ 6 test |
| L3 | Không hồi quy | `uv run pytest -q` | 69 passed | 0 failed |
| L4 | Lint sạch | `uv run ruff check .` | sạch | 0 lỗi |
| L5 | Smoke HTTP (lệnh ở cuối file) | xem dưới | đạt | in `200` hai dòng, exit 0 |
| D1 | Công cụ nhìn:<br>• `scripts/screenshot.py` ra 4 PNG (360 / 1280 × sáng / tối);<br>• bề rộng đọc từ header PNG đúng 360 / 1280;<br>• `innerWidth` trong iframe 360 = 360;<br>• chế độ tối: `matchMedia` = `true`;<br>• `scripts/page_metrics.py` in JSON;<br>• có ca âm: trang tràn ngang mẫu bị bắt | `uv run pytest -q tests/test_tools.py` | chưa có | 0 failed, ≥ 5 test |
| D2 | Spec thiết kế `docs/design/lazy-landing.md` (sửa 2026-10-16: leader chọn hướng trước khi chạy, R5 cắt):<br>• `Hướng đã chọn:` không rỗng;<br>• bảng màu sáng 6 hex + tối 6 hex;<br>• font Baloo 2 + Be Vietnam Pro;<br>• wireframe 360 và 1280;<br>• "Dấu hiệu AI đã tránh" đủ 5 dòng;<br>• không có `#F4F1EA` / `#D97757` | `uv run pytest -q tests/test_design_doc.py` (viết ở R6 dev-01) | spec đã viết, chưa có test | 0 failed |
| D3 | Phần nhìn, đo ở 1280:<br>• `#hero` có ≥ 1 SVG;<br>• `#dich-vu` có ≥ 3 SVG;<br>• mỗi SVG ≥ 3 phần tử vẽ và có `<title>`;<br>• font tính được của `<h1>` ≥ 40px và khác font thân bài, đúng font của hướng đã chọn;<br>• token màu khớp bảng màu của hướng đã chọn;<br>• có nút `mailto:` | `uv run pytest -q tests/test_site_visual.py` | 0 SVG, `<h1>` 32px | 0 failed, ≥ 5 test |
| D4 | Không tràn ngang: mọi phần tử có `scrollWidth ≤ innerWidth` ở 360 và 1280, sáng và tối | `uv run python scripts/page_metrics.py --check-overflow` | chưa đo | 4/4 không tràn, exit 0 |
| D5 | Tương phản WCAG AA trên màu tính được (`getComputedStyle`) của từng khối chữ, cả hai chế độ: chữ thường ≥ 4,5:1, chữ lớn ≥ 3:1 | `uv run python scripts/contrast.py` | chưa có | 0 cặp trượt, exit 0 |
| D6 | Chuyển động an toàn:<br>• có quy tắc `prefers-reduced-motion`, và khi giả lập `reduce` thì timeline không chạy;<br>• tắt JS hoặc CDN sai URL thì 4 phần vẫn hiện (không `opacity: 0` / `visibility: hidden`);<br>• SRI khớp sha384 của file trên CDN (skip khi không có mạng) | `uv run pytest -q tests/test_site_motion.py` | chưa có | 0 failed, ≥ 4 test |
| D7 | Leader duyệt bằng mắt (ảnh chụp và trang thật), sau R8 và sau R13 | `grep -q "^Leader duyệt: đạt" docs/design/lazy-landing.md` | "xấu quá" | exit 0 |
| E1 | SEO và chia sẻ:<br>• meta Open Graph và Twitter đủ;<br>• `og:image` là PNG 1200×630, > 5 KB;<br>• có favicon SVG, `robots.txt`, `sitemap.xml`;<br>• JSON-LD `json.loads` được, `@type` là `ProfessionalService` | `uv run pytest -q tests/test_site_seo.py` | chưa có | 0 failed, ≥ 6 test |
| E2 | Lighthouse mobile, trung vị 3 lần, đo `site/` qua HTTP; tổng tải ≤ 300 KB | `uv run python scripts/lh_check.py` (gọi `npx -y lighthouse@12`) | chưa đo | Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95 |
| E3 | Đã triển khai: URL Pages trả 200, chứa "Lười Code Studio" và `<meta name="version">` khớp SHA `main` | `curl -sf <URL Pages>` qua `scripts/smoke_pages.py` | chưa có | 200, khớp SHA |
| E4 | Nội dung mở rộng:<br>• FAQ ≥ 4 mục `<details>`;<br>• 3 dự án hư cấu, mỗi dự án có chữ "ví dụ";<br>• không có "khách hàng nói" / "đánh giá" | `uv run pytest -q tests/test_site_content.py` | chưa có | 0 failed, ≥ 4 test |
| E5 | Song ngữ:<br>• `site/en/index.html` `lang="en"`, cùng tập id phần như bản Việt;<br>• `hreflang` hai chiều;<br>• có nút chuyển ngôn ngữ;<br>• có trong `sitemap.xml` | `uv run pytest -q tests/test_site_i18n.py` | chưa có | 0 failed, ≥ 4 test |

**Lệnh L5** (chạy ở gốc dự án):

```sh
uv run python -c "import functools,http.server,threading,urllib.request as u; s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory='site')); threading.Thread(target=s.serve_forever,daemon=True).start(); [print(u.urlopen(f'http://127.0.0.1:{s.server_port}/{p}').status) for p in ('','style.css')]"
```

**% đạt** = số chỉ số đạt / 17 (L1–L5, D1–D7, E1–E5). Mục tiêu xong khi đạt 17/17. Mốc bị cắt thì chỉ số của mốc đó bị loại khỏi mẫu số, trừ chỉ số "không cắt" (xem `roadmap.md`).

Nền hiện tại: L1, L3, L4, L5 đạt → 4/17 ≈ 24%.

**Ghi chú môi trường:**
- Chrome 155 ở `/Applications/Google Chrome.app`, Node v22.
- Test cần Chrome hoặc mạng tự `skip` khi thiếu. CI chỉ chạy ruff + pytest, nên trên CI chúng có thể bị skip; cổng thật là `verify.py` local và reviewer.
