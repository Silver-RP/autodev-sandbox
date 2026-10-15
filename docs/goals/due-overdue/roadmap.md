# ROADMAP: `due-overdue`

Hướng đã chọn: hai mốc theo lát dọc. R1 xong là đặt được hạn và dùng được ngay; R2 thêm lọc quá hạn. Trần chi phí: 10 USD.

**Nguồn ước tính.** Sandbox chưa có số đo (`plan/PROGRESS.md` trống). Số đo lấy từ `/Users/ishopjapan/dev/autodev/docs/PROGRESS.md`, mốc cỡ nhỏ:

| Mốc | Task | Thời gian | Chi phí |
|---|---|---|---|
| R4 | 4 | 19 phút | 2,29 USD (worker 2,00) |
| M3 | 3 | 12,3 phút | 1,72 USD |
| R9h | 2 | 20 phút | worker 1,15 USD |

Áp luật mục 6.5:
- USD = worker + 2 USD supervisor.
- Không áp "≥ 25 phút/task": luật này dành cho task có pytest + Postgres, còn pytest ở đây chạy 0,1 giây.
- Không cộng tiền audit.

## R1: Hạn chót
- **Mục tiêu:** việc có hạn chót tùy chọn; đặt được lúc tạo và đổi được sau.
- **Phạm vi** (task dự kiến; P11 chốt trong `plan/R1.md`):
  1. `store`: trường `due` (chuỗi ISO), kiểm ngày bằng `date.fromisoformat`, đọc được việc cũ không có `due`.
  2. `todo add <tên> --due YYYY-MM-DD`.
  3. `todo due <id> YYYY-MM-DD`: ngày sai thoát 2, `id` không có thoát 1, cả hai in stderr và không ghi file.
  4. `todo list` có cột hạn; cập nhật docstring cách dùng của `cli.py`.
  - Không có H-xx hay mã T (dự án chưa có audit hay danh sách task).
- **Chỉ số đẩy lên:** A1; giữ A3, A4.
- **Ước tính:** 4 USD (worker ~2 theo R4 + 2 supervisor), 0,5 giờ máy (R4: 4 task, 19 phút, làm tròn lên).
- **Xong khi:** `uv run pytest -q tests/test_due.py` 0 failed với ≥ 7 test; `uv run pytest -q` và `uv run ruff check .` sạch.
- **Phụ thuộc:** không.
- **Pre-mortem:**
  1. *Đạt nhờ dựng dữ liệu:* test chỉ dùng việc mới tạo, nên không phát hiện file cũ thiếu `due` gây `KeyError`. Chặn bằng test A1 dùng JSON viết tay không có `due`.
  2. *Lỗi vẫn ghi file:* ghi trước rồi mới kiểm. Chặn bằng test so file trước và sau lệnh lỗi (giống hệt từng byte).
  3. *Kill ở giữa thì sao?* `save` ghi đè trực tiếp, ngắt giữa lúc ghi có thể làm hỏng JSON. Đây là nợ có sẵn, ngoài phạm vi, ghi ở "việc chỉ người làm"; không chặn bằng tiêu chí.
  4. *Ngày hợp lệ giả:* `2026-02-30` lọt qua nếu chỉ kiểm bằng regex. Chặn bằng `date.fromisoformat` và test A1 cho `2026-02-30`, `2026-13-40`.

## R2: Lọc việc quá hạn
- **Mục tiêu:** `todo overdue` liệt kê việc chưa xong đã quá hạn.
- **Phạm vi:**
  1. `store.overdue(items, today)`: lọc `not done and due and due < today`, sắp theo `due` tăng dần; đọc "hôm nay" từ `TODO_TODAY`, mặc định `date.today()`.
  2. Lệnh `todo overdue`: in cùng định dạng với `list`, rỗng thì không in gì và thoát 0.
  3. Smoke A5 (chuỗi lệnh trong `criteria.md`), ghi vào plan để reviewer chạy lại.
- **Chỉ số đẩy lên:** A2, A5; giữ A3, A4.
- **Ước tính:** 4 USD (worker ~1,7 theo M3 + 2 supervisor), 0,4 giờ máy (M3, R9h: 12–20 phút, làm tròn lên).
- **Xong khi:** `uv run pytest -q tests/test_overdue.py` 0 failed với ≥ 6 test; lệnh A5 in đúng 1 dòng; `uv run pytest -q` và `uv run ruff check .` sạch.
- **Phụ thuộc:** R1.
- **Pre-mortem:**
  1. *Đạt sẵn nhờ dựng dữ liệu:* test chỉ có việc quá hạn, nên lệnh in tất cả cũng xanh. Chặn bằng dữ liệu trộn đủ 5 loại (quá hạn, hạn hôm nay, hạn tương lai, đã xong, không hạn) trong A2 và A5; A5 đòi đúng 1 dòng.
  2. *Sai biên:* `<=` thay vì `<` làm việc có hạn hôm nay bị tính là quá hạn. Chặn bằng test riêng cho `due == today`.
  3. *Phụ thuộc đồng hồ máy:* test dùng `date.today()`. Chặn bằng `TODO_TODAY` cố định trong mọi test; reviewer chạy lại với ngày giả khác.
  4. *Sắp xếp đúng do may:* dữ liệu tạo sẵn theo thứ tự hạn tăng dần. Chặn bằng test tạo theo thứ tự hạn ngược.

## Tổng
| Mốc | Phụ thuộc | Chỉ số | USD | Giờ máy |
|---|---|---|---|---|
| R1 | – | A1 (A3, A4) | 4 | 0,5 |
| R2 | R1 | A2, A5 (A3, A4) | 4 | 0,4 |
| **Tổng** | | | **8** | **0,9** |

## Thứ tự cắt
1. Cắt R2 trước; R1 đứng riêng vẫn có giá trị.
2. Trong R2, cắt smoke A5 trước, giữ A2.

## Không cắt
- R1: đọc được file cũ không có `due`; không ghi file khi lỗi.
- R2: biên `due == today` không tính là quá hạn.
- Cả hai mốc: A3 (không hồi quy) và A4 (lint).

## Việc chỉ người làm
- Leader thử tay `todo add … --due`, `todo due`, `todo overdue` trên `todo.json` thật trước khi đặt mục tiêu `done`.
- Leader quyết có làm ghi nguyên tử cho `store.save` (nợ kill-giữa-chừng) ở mục tiêu khác hay không.

## Kế hoạch cũ được thay
Không có. Repo chưa có `docs/autodev/ROADMAP.md`, chưa có `plan/*.md` nào, và chưa có audit.
