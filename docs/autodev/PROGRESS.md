# Nhật ký auto-dev (supervisor)

## R1: Hạn chót — merged 2026-10-15 (PR #5, `63cc7b0`)

Kiểm trên nhánh `milestone/R1` (`11226c2`), supervisor tự chạy:
`verify.py` → "sạch (không có lỗi mới so với baseline)"; `verify.py --smoke` → "sạch" (**danh sách `smoke` rỗng**, không chạy lệnh nào). CI `test` pass 2 lần; main không có check bắt buộc.

### Tiêu chí cấp mốc
| # | Tiêu chí | Lệnh tự chạy | Kết quả |
|---|---|---|---|
| 1 | `verify.py` sạch | `python3 .../scripts/verify.py` | exit 0, sạch |
| 2 | `tests/test_due.py` 0 failed, ≥ 7 test (A1) | `uv run pytest -q tests/test_due.py` | 24 passed |
| 3 | `pytest` 0 failed (A3), ruff sạch (A4) | `uv run pytest -q`; `uv run ruff check .` | 30 passed; All checks passed |

### Ước tính ↔ thực tế (`metrics.py`)
| | Ước tính | Thực tế | Lệch |
|---|---|---|---|
| Số task | 3 | 3 | 0 |
| Phút worker | 15–20 | 4 | B3 0,28 |
| USD (worker + supervisor) | ~4 | 0,71 (chưa gồm supervisor; script không cộng tạm `~`) | B3 0,18 |
| Số vòng review | 3–5 | 3 (+1 gọi lại reviewer do trả "placeholder") | trong khoảng |

Lệch > 2 lần (thấp hơn): ước tính lấy từ mốc plugin có Postgres/pytest chậm; ở đây pytest 0,1 giây và task rất nhỏ. Mốc sau nên ước tính ~5 phút, ~1 USD worker. Số USD thật sau `/autodev:session-end` (`metrics.py --write`).

### Pre-mortem
| Rủi ro | Chặn bằng |
|---|---|
| File cũ thiếu `due` | `test_set_due_on_legacy_file`, `test_list_legacy_file_without_due` |
| Lỗi vẫn ghi file | `test_set_due_missing_id_keeps_bytes`, `test_cli_due_errors_keep_file`, `test_set_due_missing_file_not_created` |
| Ngày hợp lệ giả | `test_valid_due_bad` (`2026-02-30`, `2026-13-40`, `mai`, `2026-1-5`); **còn hở ở store**: H-01 |
| `--due` bị nuốt vào tên | `test_cli_add_due_not_swallowed` |

### Kiểm biên độc lập (CLI thật, `TODO_FILE` tạm)
- `add --due 2026-10-20` (không tên), `add x --due` (thiếu giá trị) → thoát 2, không tạo file. Đúng.
- `add x --due 2026-W01-1`, `due 1 2026-W01-1`, `due 2 2026-02-29` → thoát 2, file giữ nguyên hash. `due 2 2028-02-29` (năm nhuận) → thoát 0. Đúng.
- `store.valid_due("2026-W01-1")` và `valid_due("20261020  ")` → True: lỗ hổng H-01 (store), CLI chặn được.

<!-- metrics:start (tự sinh bởi .autodev/metrics.py, đừng sửa tay) -->
<!-- metrics:end -->
