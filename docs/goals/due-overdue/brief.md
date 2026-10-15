# Mục tiêu: hạn chót và lọc việc quá hạn (`due-overdue`)

## Mục tiêu
Thêm hạn chót cho việc trong todo CLI và lệnh liệt kê việc quá hạn.

## Kết quả mong muốn (nguyên văn leader)
> thêm hạn chót cho việc và lệnh lọc việc quá hạn

## Cách hiểu đã chốt
- Hạn chót chỉ là ngày `YYYY-MM-DD` (kiểm bằng `date.fromisoformat`), lưu ở trường `due` trong `todo.json`. Việc không có `due` (kể cả file cũ) vẫn hợp lệ.
- Có hai cách đặt hạn:
  - lúc tạo: `todo add <tên> --due YYYY-MM-DD`;
  - đặt hoặc đổi sau: `todo due <id> YYYY-MM-DD`.
- Khi lỗi, CLI in ra stderr, không ghi file, và thoát:
  - mã 2 khi ngày sai;
  - mã 1 khi `id` không có.
- `todo list` có thêm cột hạn chót.
- `todo overdue`:
  - liệt kê việc chưa xong có `due` < hôm nay;
  - in cùng định dạng với `list`, sắp theo hạn từ cũ đến mới;
  - không có việc quá hạn thì không in gì, thoát 0.
- "Hôm nay" lấy từ biến môi trường `TODO_TODAY` nếu có (để test và smoke), không thì dùng `date.today()`.
- Không thêm thư viện ngoài.
- Trần chi phí: 10 USD cho cả mục tiêu, chia 2 mốc theo lát dọc (R1 hạn chót, R2 `overdue`).

## Nhật ký hỏi đáp
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Hạn chót nhập theo dạng nào? | 1: chỉ ngày `YYYY-MM-DD`, quá hạn khi ngày hạn < hôm nay |
| 2 | Có cần đặt hoặc đổi hạn cho việc đã tạo không? | 2: `add --due` và `todo due <id> <ngày>` |
| 3 | Ngày sai hoặc `id` không có thì làm gì? | 1: stderr, ngày sai thoát 2, `id` không có thoát 1, không ghi file |
| 4 | `todo overdue` in ra thế nào? | 1: định dạng như `list`, sắp theo hạn tăng dần, rỗng thì thoát 0 |
| 5 | Giới hạn chi phí? | 1: ≤ 10 USD, 1–2 mốc |
| 6 | Chọn hướng ROADMAP nào? | 1: hai mốc lát dọc R1 → R2 |
| 7 | Duyệt tiêu chí | 1: đồng ý |
| 8 | Duyệt danh sách mốc | 1: đồng ý |
| 9 | Duyệt pre-mortem | 1: đồng ý |
| 10 | Duyệt thứ tự cắt, phần không cắt, việc chỉ người làm | 1: đồng ý |

## Giả định còn lại
- Ước tính lấy theo số đo của repo plugin (`autodev/docs/PROGRESS.md`: R4, M3, R9h), vì `plan/PROGRESS.md` của sandbox chưa có mốc nào chạy. Chạy xong R1 thì đối chiếu lại.
- Biến môi trường `TODO_TODAY` là cách chèn "hôm nay" do planner chọn, theo cùng kiểu với `TODO_FILE`.
- `store.save` ghi đè trực tiếp nên kill giữa lúc ghi có thể làm hỏng file. Đây là nợ có sẵn, ngoài phạm vi; leader quyết sau.
- Không xử lý múi giờ: "hôm nay" là ngày theo giờ máy.
