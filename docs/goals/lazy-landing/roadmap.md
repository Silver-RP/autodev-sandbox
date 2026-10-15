# ROADMAP: `lazy-landing`

Hướng đã chọn: hai mốc theo lát dọc. R3 xong là có trang xem được; R4 hoàn thiện tối giản. Trần chi phí: 5 USD.

**Nguồn ước tính:** số đo thật của sandbox trong `docs/autodev/PROGRESS.md`.

| Mốc | Task | Phút worker | USD |
|---|---|---|---|
| R1 | 3 | 4 | 0,71 worker |
| R2 | 3 | 4 | 0,72 worker + ~0,75 supervisor |

Ghi chú của supervisor sau R2: "mốc cùng cỡ sau: ~5 phút, ~0,8 USD worker". Mỗi mốc ước tính 0,8 worker + 0,8 supervisor = 1,6 USD. Giờ máy ước tính 0,2 (khoảng 5 phút worker cộng supervisor, làm tròn lên).

Lệch khỏi luật mục 6.5:
- Supervisor tính theo số đo sandbox, không theo mức "+2 USD": mức đó đo trên mốc có Postgres của dự án khác, và R1, R2 đã lệch hơn 2 lần so với nó.
- Không áp "≥ 25 phút/task": không có Postgres.
- Không cộng tiền audit.

## R3: Trang dùng được
- **Mục tiêu:** có `site/index.html` + `site/style.css` xem được, đủ 4 phần với nội dung thật.
- **Phạm vi** (task dự kiến; P11 chốt trong `plan/R3.md`):
  1. `site/index.html`:
     - `lang="vi"`, meta (charset, viewport, description), `<title>`;
     - `header` / `main` / `footer`;
     - 4 `section` (`hero`, `dich-vu`, `cach-lam`, `lien-he`), giọng "lười" tự giễu;
     - tên "Lười Code Studio", `mailto:hello@example.com`, giá dạng chữ đùa.
  2. `site/style.css`: một cột, `max-width`, chữ hệ thống, khoảng trắng rộng.
  3. `tests/test_site.py` cho L1 (dùng `html.parser` của thư viện chuẩn).
  - Không có H-xx hay mã T: không có lỗ hổng mở hay danh sách task.
- **Chỉ số đẩy lên:** L1, L5; giữ L3, L4.
- **Ước tính:** 1,6 USD, 0,2 giờ máy (nguồn ở trên).
- **Xong khi:** `uv run pytest -q tests/test_site.py` 0 failed với ≥ 6 test; lệnh L5 in `200` hai dòng; `uv run pytest -q` và `uv run ruff check .` sạch.
- **Phụ thuộc:** không.
- **Pre-mortem** (chỉ thêm file tĩnh, không có trạng thái bền nên không có rủi ro "kill ở giữa"):
  1. *Đạt nhờ dựng dữ liệu:* tìm `id="hero"` bằng `in` thì chuỗi trong comment hay `<div>` cũng qua. Chặn bằng `html.parser` đếm thẻ `section` thật, mỗi phần ≥ 20 ký tự chữ.
  2. *Nội dung giữ chỗ:* đủ khung nhưng chữ là "Lorem ipsum". Chặn bằng test cấm `lorem` / `TODO` / `placeholder`.
  3. *Link CSS gãy:* test chỉ đọc HTML nên vẫn xanh. Chặn bằng test file CSS được trỏ tới phải tồn tại, và smoke L5 tải `/style.css`.
  4. *HTML hỏng:* thẻ không đóng làm sai bố cục. Chặn bằng test đếm thẻ mở và đóng của `section` / `main` / `header` / `footer`.

## R4: Hoàn thiện tối giản
- **Mục tiêu:** có chế độ tối, dùng được ở 360px, nhẹ, không phụ thuộc bên ngoài, đạt các kiểm truy cập cơ bản.
- **Phạm vi:**
  1. Biến màu CSS ở `:root`, `@media (prefers-color-scheme: dark)` gán lại; bỏ `width` cố định > 360px; `img { max-width: 100% }` nếu trang có ảnh.
  2. Dọn tài nguyên ngoài, thêm `alt`, sửa thứ tự heading, giữ tổng `site/` ≤ 30 KB, không có `<script>`.
  3. `tests/test_site_polish.py` cho L2.
- **Chỉ số đẩy lên:** L2; giữ L3, L4 (L1, L5 không được tụt).
- **Ước tính:** 1,6 USD, 0,2 giờ máy (nguồn ở trên).
- **Xong khi:** `uv run pytest -q tests/test_site_polish.py` 0 failed với ≥ 6 test; `uv run pytest -q`, `uv run ruff check .` sạch; lệnh L5 vẫn in `200` hai dòng.
- **Phụ thuộc:** R3.
- **Pre-mortem:**
  1. *Chế độ tối trên giấy:* khối `@media` rỗng hoặc không đổi nền. Chặn bằng test đòi gán lại cả biến nền lẫn biến chữ, giá trị khác bản sáng.
  2. *Đạt 360px nhờ quy tắc kiểm hẹp:* `min-width: 800px` hoặc ảnh không co làm tràn ngang. Chặn bằng test cấm `width` / `min-width` > 360px và đòi `img { max-width: 100% }` khi có ảnh; leader kiểm thật trên điện thoại.
  3. *Đạt ngân sách nhờ đo thiếu:* chỉ cộng `index.html`. Chặn bằng test cộng mọi file trong `site/`.
  4. *Tài nguyên ngoài gián tiếp:* `@import url(https://…)` hoặc Google Fonts trong CSS. Chặn bằng test quét cả CSS tìm `http:`, `https:`, `//`.

## Tổng
| Mốc | Phụ thuộc | Chỉ số | USD | Giờ máy |
|---|---|---|---|---|
| R3 | – | L1, L5 (L3, L4) | 1,6 | 0,2 |
| R4 | R3 | L2 (L3, L4) | 1,6 | 0,2 |
| **Tổng** | | | **3,2** | **0,4** |

## Thứ tự cắt
1. Cắt R4 trước; R3 đứng riêng vẫn là trang xem được.
2. Trong R4: cắt ngân sách 30 KB trước, sau đó đến kiểm thứ tự heading. Giữ chế độ tối và luật 0 tài nguyên ngoài.

## Không cắt
- R3: đủ 4 phần với nội dung thật, `lang="vi"`, `meta viewport`, link CSS đúng (L1, L5).
- R4: luật 0 tài nguyên ngoài, không có `<script>`.
- Cả hai mốc: L3 (không hồi quy) và L4 (lint).

## Việc chỉ người làm
- Leader mở `site/index.html` ở chế độ sáng, chế độ tối và trên điện thoại (hoặc khung 360px) để duyệt giao diện và giọng văn trước khi đặt mục tiêu `done`.
- Leader thay tên, email và giá giữ chỗ bằng thông tin thật khi cần.
- Nếu muốn `verify.py --smoke` tự chạy L5, leader thêm lệnh L5 vào mục `smoke` của `.autodev/config.json` (developer không được sửa file này).

## Kế hoạch cũ được thay
Không có. `docs/goals/due-overdue/` đã xong (5/5) và giữ nguyên. Không có `plan/*.md` nào chưa chạy (R1, R2 đã merge). Mốc mới đánh số nối tiếp `docs/autodev/ROADMAP.md`.
