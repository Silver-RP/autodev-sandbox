# Tiêu chí: `due-overdue`

Dự án chưa có file tiêu chí (`paths.criteria_file` rỗng), nên bảng dưới là toàn bộ tiêu chí của mục tiêu này. Nền đo ngày 2026-10-15 trên `origin/main` (`3f4c465`).

| Mã | Định nghĩa | Lệnh đo | Nền | Ngưỡng | % đạt |
|---|---|---|---|---|---|
| A1 | Hạn chót: `add --due`; `due <id> <ngày>` đặt và đổi hạn; `list` hiện hạn; ngày sai (`2026-02-30`, `2026-13-40`, `mai`) thoát 2; `id` không có thoát 1; khi lỗi file không đổi (so từng byte); file JSON cũ không có `due` vẫn chạy được `list` và `due` | `uv run pytest -q tests/test_due.py` | file chưa có | 0 failed, ≥ 7 test | số hành vi có test xanh / 7 |
| A2 | Quá hạn: chỉ lấy việc chưa xong có `due` < hôm nay; bỏ việc có hạn đúng hôm nay, việc có hạn tương lai, việc đã xong, việc không có hạn; sắp từ cũ đến mới (dữ liệu tạo theo thứ tự ngược); rỗng thì không in gì và thoát 0; "hôm nay" cố định qua `TODO_TODAY` | `uv run pytest -q tests/test_overdue.py` | file chưa có | 0 failed, ≥ 6 test | số hành vi có test xanh / 6 |
| A3 | Không hồi quy | `uv run pytest -q` | 4 đạt, 0 failed | 0 failed | 100% hoặc 0% |
| A4 | Lint sạch | `uv run ruff check .` | sạch | 0 lỗi | 100% hoặc 0% |
| A5 | Smoke CLI thật (lệnh dưới) | xem dưới | chưa có | in đúng 1 dòng chứa `qua-han`, thoát 0 | 100% hoặc 0% |

Lệnh A5, chạy ở thư mục gốc dự án:

```sh
export TODO_FILE="$(mktemp -d)/t.json" TODO_TODAY=2026-10-15
uv run todo add qua-han --due 2026-10-14
uv run todo add hom-nay --due 2026-10-15
uv run todo add tuong-lai --due 2026-10-16
uv run todo add xong-roi --due 2026-10-01 && uv run todo done 4
uv run todo add khong-han
uv run todo overdue   # mong đợi: đúng 1 dòng, chứa "qua-han"
```

% đạt của mục tiêu = số chỉ số đạt ngưỡng / 5. Mục tiêu xong khi đạt 5/5.
