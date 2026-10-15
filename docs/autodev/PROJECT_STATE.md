# Trạng thái dự án (đọc trước plan mốc)

Cập nhật: 2026-10-15 · Nguồn: duyệt mốc R1 (supervisor)

## Mốc
| Mốc | Trạng thái | Ghi chú |
|---|---|---|
| R1 | merged | PR #5; 3 task, mỗi task 1 vòng; 30 test pass |
| R2 | chưa chạy | chưa có `plan/R2.md` |

## Mục tiêu và tiêu chí
Mục tiêu `due-overdue` (`docs/goals/due-overdue/criteria.md`): 3/5 = **60%**.
| Mã | Lệnh đo | Ngưỡng | Hiện tại |
|---|---|---|---|
| A1 | `uv run pytest -q tests/test_due.py` | 0 failed, ≥ 7 test | 24 passed, đạt |
| A2 | `uv run pytest -q tests/test_overdue.py` | 0 failed, ≥ 6 test | chưa có (R2) |
| A3 | `uv run pytest -q` | 0 failed | 30 passed, đạt |
| A4 | `uv run ruff check .` | 0 lỗi | sạch, đạt |
| A5 | smoke `todo overdue` | đúng 1 dòng | chưa có (R2) |

## Kiến trúc hiện nay
- `src/todo/store.py`: JSON list trong một file; `add(path, title, due=None)`, `set_due`, `complete`, `valid_due`. Việc không hạn thì không có khoá `due`.
- `src/todo/cli.py`: `add <tên...> [--due]`, `list` (`id\tx\tdue\ttitle`), `done <id>`, `due <id> <ngày>`; `_ok_date` kiểm thêm dấu `-` ở vị trí 4, 7.

## Quy tắc → test bảo vệ
| Quy tắc (CLAUDE.md / plan) | Test bảo vệ |
|---|---|
| Lỗi không ghi file (so từng byte) | `test_set_due_missing_id_keeps_bytes`, `test_cli_due_errors_keep_file` |
| File cũ không có `due` vẫn chạy | `test_set_due_on_legacy_file`, `test_list_legacy_file_without_due` |
| Ngày sai thoát 2, id thiếu thoát 1 | `test_cli_add_bad_due`, `test_cli_due_errors_keep_file` |

## Lỗ hổng mở
| Mã | Mức | Tóm tắt |
|---|---|---|
| H-01 | vừa | `store.valid_due` nhận `2026-W01-1` và `"20261020  "`; chỉ CLI chặn |

## Quyết định gần đây
- 2026-10-15: merge R1 (PR #5). Đề xuất (c) "siết `valid_due` trong store" → ghi H-01, đề nghị làm đầu R2 (không đổi tiêu chí R1).
