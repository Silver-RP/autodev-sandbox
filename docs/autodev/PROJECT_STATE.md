# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-16 · Nguồn: duyệt mốc R2 (supervisor)

## Mốc
| Mốc | Trạng thái | Ghi chú |
|---|---|---|
| R1 | merged | PR #5; 3 task, mỗi task 1 vòng; 30 test pass |
| R2 | merged | PR #8 (`0aa2992`); 3 task, mỗi task 1 vòng; 52 test pass; đóng H-01 |

## Mục tiêu và tiêu chí
Mục tiêu `due-overdue` (`docs/goals/due-overdue/criteria.md`): 5/5 = **100%** (xong).
| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| A1 | `uv run pytest -q tests/test_due.py` | 0 failed, ≥ 7 test | 24 passed, đạt |
| A2 | `uv run pytest -q tests/test_overdue.py` | 0 failed, ≥ 6 test | 7 passed, đạt |
| A3 | `uv run pytest -q` | 0 failed | 52 passed, đạt |
| A4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| A5 | smoke `todo overdue` (`verify.py --smoke`) | đúng 1 dòng | 1 dòng `qua-han`, đạt |

## Kiến trúc hiện nay
- `src/todo/store.py`: JSON list trong một file; `add(path, title, due=None)`, `set_due`, `complete`, `valid_due` (regex `[0-9]{4}-[0-9]{2}-[0-9]{2}` + `date.fromisoformat`), `today()` (đọc `TODO_TODAY`, sai thì `ValueError`), `overdue(items, today)` (chưa xong, `due` hợp lệ `< today`, sắp theo `due`, `id`). Việc không hạn thì không có khoá `due`.
- `src/todo/cli.py`: `add <tên...> [--due]`, `list`, `overdue` (cùng định dạng `id\tx\tdue\ttitle`), `done <id>`, `due <id> <ngày>`; kiểm ngày chỉ qua `store.valid_due`.

## Quy tắc → test bảo vệ
| Quy tắc (CLAUDE.md / plan) | Test bảo vệ |
|---|---|
| Lỗi không ghi file (so từng byte) | `test_set_due_missing_id_keeps_bytes`, `test_cli_due_errors_keep_file`, `tests/test_valid_due_strict.py` |
| File cũ không có `due` vẫn chạy | `test_set_due_on_legacy_file`, `test_list_legacy_file_without_due` |
| Ngày sai thoát 2, id thiếu thoát 1 | `test_cli_add_bad_due`, `test_cli_due_errors_keep_file` |
| Một luật ngày duy nhất ở store (H-01) | `tests/test_valid_due_strict.py` |
| Quá hạn: biên `due == today`, sắp, dữ liệu hỏng, không phụ thuộc đồng hồ | `tests/test_overdue.py`, `tests/test_cli_overdue.py` |

## Lỗ hổng mở
Không có. (H-01 đóng ở R2, PR #8.)

## Nợ không chặn
- `store.save` không ghi nguyên tử (ngoài phạm vi R2, leader quyết).
- Tham số `today` của `store.overdue` che hàm `store.today()`; docstring đầu `cli.py` một dòng dài.

## Quyết định gần đây
- 2026-10-16: merge R2 (PR #8). Chấp nhận (a): test H-01/CLI đặt ở file mới thay vì `tests/test_due.py`. Mục tiêu `due-overdue` đạt 5/5.
- 2026-10-15: merge R1 (PR #5). Đề xuất (c) "siết `valid_due` trong store" → ghi H-01, làm đầu R2.
