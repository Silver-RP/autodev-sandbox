# Mục tiêu: landing page "vibe coder lười" (`lazy-landing`)

## Mục tiêu
Làm một landing page tĩnh, tối giản, giới thiệu dịch vụ làm website của một vibe coder lười biếng.

## Kết quả mong muốn (nguyên văn leader)
> Xây dựng website đơn giản, tối giản, 1 landing page về trang dịch vụ xây dựng trang web của 1 vibe coding lười biếng

## Cách hiểu đã chốt
- **Vị trí và cách kiểm:** trang nằm ở `site/index.html` + `site/style.css` trong repo sandbox. Kiểm bằng hai lệnh CI có sẵn (`uv run pytest -q`, `uv run ruff check .`); CI không đổi.
- **Công nghệ:** không framework, không bước build, không `<script>`, không tài nguyên ngoài (font, CDN, ảnh từ xa).
- **Nội dung:** tiếng Việt, giọng hài tự giễu. Bốn phần:
  - hero (`#hero`);
  - dịch vụ kèm giá đùa (`#dich-vu`);
  - cách làm (`#cach-lam`);
  - liên hệ bằng `mailto:` (`#lien-he`).
- **Thông tin giữ chỗ:** tên hư cấu "Lười Code Studio", email `hello@example.com`, giá dạng chữ đùa. Leader thay thông tin thật sau.
- **Giao diện:** một cột, chữ hệ thống, có chế độ tối, dùng tốt ở 360px, tổng `site/` ≤ 30 KB.
- **Phạm vi:** không triển khai lên host trong mục tiêu này.
- **Chi phí:** trần 5 USD, hai mốc lát dọc:
  - R3: trang dùng được;
  - R4: hoàn thiện tối giản.

## Nhật ký hỏi đáp
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Trang web đặt ở đâu? | 1: `site/` trong repo sandbox, kiểm bằng pytest + ruff |
| 2 | Ngôn ngữ của trang? | 1: tiếng Việt |
| 3 | Tên, email, giá lấy từ đâu? | 1: tên hư cấu, email giữ chỗ, giá chữ đùa; leader thay sau |
| 4 | Giới hạn chi phí? | 1: ≤ 5 USD |
| 5 | Hướng ROADMAP? | 1: hai mốc lát dọc R3 → R4 |
| 6 | Duyệt tiêu chí | 1: đồng ý |
| 7 | Duyệt danh sách mốc | 1: đồng ý |
| 8 | Duyệt pre-mortem | 1: đồng ý |
| 9 | Duyệt thứ tự cắt, phần không cắt, việc chỉ người làm | 1: đồng ý |

## Giả định còn lại
- Ước tính dựa trên R1 và R2 của sandbox: mỗi mốc 3 task, khoảng 0,7 USD worker. Viết HTML/CSS có thể tốn token hơn sửa CLI một chút; chạy xong R3 thì đối chiếu lại.
- Supervisor tính theo số đo sandbox (khoảng 0,75 USD), không theo mức "+2 USD" của thiết kế mục 6.5. R1, R2 đã lệch hơn 2 lần so với mức đó.
- Trang đẹp và hài hay không thì máy không đo được; leader duyệt bằng mắt.
- Đánh số mốc nối tiếp ROADMAP sandbox (R3, R4).
- Mục tiêu `due-overdue` đã đạt 5/5, nhưng `goal.json` của nó vẫn ghi mốc `planned`. Lệnh này không sửa file đó.
