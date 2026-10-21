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

## R17: Cứng hoá todo CLI
Thêm 2026-10-21 (leader uỷ quyền; theo audit 2026-10-16 H-13, H-18 và 2026-10-21 H-26). Leader đã quyết **làm** ghi nguyên tử cho `store.save`.
- **Mục tiêu:** CLI không bao giờ ném traceback hay ghi file khi lỗi; hai tiến trình ghi cùng lúc không mất việc.
- **Phạm vi:**
  1. H-26: id không phải số ASCII (`²`, `١`) → usage exit 2; `todo add ""` (tiêu đề rỗng hoặc chỉ khoảng trắng) → exit 2, không ghi; tab/xuống dòng trong tiêu đề bị thay bằng khoảng trắng.
  2. H-13: `todo done <id không có>` không ghi file, in "không có việc id N" ra stderr, exit 1 (giống `due`).
  3. H-18: `store.save` ghi file tạm cùng thư mục rồi `os.replace` (giữ đích của symlink); khoá file (`fcntl.flock`) quanh đọc-sửa-ghi; JSON hỏng hoặc phần tử thiếu `id` → thông báo rõ, exit 2, không traceback.
- **Chỉ số giữ:** A1, A2, A3, A4.
- **Ước tính:** ~3 task, **1,5 USD**, **0,3 giờ**.
- **Xong khi:** test mới cho từng ý đỏ trước khi sửa; `uv run pytest -q` và `uv run ruff check .` sạch; test hai tiến trình `add` song song 20 lần không mất việc, không trùng id.
- **Phụ thuộc:** R2.
- **Pre-mortem:**
  1. *Test song song chập chờn*: dùng `multiprocessing` với số lần cố định, kiểm số việc và id duy nhất; không dựa thời gian.
  2. *`os.replace` phá symlink*: test ghi qua symlink, đích được cập nhật, link còn nguyên.

## R18: Todo CLI không traceback, không treo, không ghi hỏng
Thêm 2026-10-21 (supervisor đề xuất từ audit 2026-10-21 lần 3).
- **Mục tiêu:** giữ đúng lời R17 "CLI không bao giờ ném traceback hay ghi file khi lỗi" cho cả đầu vào lạ, khoá bị giữ và file có quyền/link đặc biệt.
- **Phạm vi:**
  1. H-35: id quá dài (> 4300 chữ số), JSON lồng sâu hoặc số nguyên khổng lồ trong file, argv không UTF-8 → thông báo một dòng, exit 2, không `Traceback`, file nguyên byte.
  2. H-36: `store.lock` có timeout (vài giây); tiến trình khác giữ khoá → lệnh thoát exit 2 với thông báo, không treo.
  3. H-37: `load` từ chối `id` âm hoặc trùng → exit 2, không ghi.
  4. H-38: `save` không ghi đè file chỉ đọc (0444), giữ hard link và quyền file cũ, symlink tự trỏ → exit 2; lỗi gốc không bị che; tên file dài/thư mục chỉ đọc → exit 2, không `Traceback`.
- **Chỉ số giữ:** A1, A2, A3, A4.
- **Ước tính:** ~4 task, **3 USD**, **1,4 giờ** (theo R17 đo: 3 task, 60 phút worker, 2,53 USD; cả bộ pytest ~3–5 phút mỗi lần verify).
- **Xong khi:** mỗi ý có test đỏ trên `origin/main` trước khi sửa (tên test theo audit: `test_cli_errors.py::test_done_huge_id_exit_2`, `::test_deeply_nested_json_exit_2`, `::test_load_rejects_negative_id`, `::test_load_rejects_duplicate_id`, `test_store_safety.py::test_lock_timeout_exit_2`, `::test_self_symlink_exit_2`, `test_atomic_save.py::test_readonly_file_not_overwritten`, `::test_hardlink_preserved`); stderr các ca không chứa `Traceback`; `uv run pytest -q`, `uv run ruff check .` sạch; smoke A5 vẫn đạt.
- **Phụ thuộc:** R17.
- **Pre-mortem:**
  1. *Test khoá chập chờn hoặc chậm*: tiến trình con giữ khoá qua cờ đồng bộ (file/pipe), không `sleep` đoán; timeout khoá chỉnh được qua biến môi trường để test chạy dưới 2 giây.
  2. *Giữ hard link/quyền làm mất tính nguyên tử của R17*: không bỏ `os.replace` cho trường hợp thường; chỉ đổi cách xử lý khi file có `st_nlink > 1` hoặc chỉ đọc, và test hai tiến trình `add` song song của R17 vẫn xanh.
  3. *Bắt ngoại lệ quá rộng che lỗi lập trình*: chỉ bắt các lớp lỗi đã liệt kê (`ValueError`, `RecursionError`, `OSError`, `UnicodeError`) ở biên CLI, quy về `StoreError`; test không dùng `except Exception`.

## R20: Todo CLI chịu file thiếu khoá, pipe đóng, TODO_FILE không phải file thường
Thêm 2026-10-21 (supervisor đề xuất từ audit 2026-10-21 lần 4).
- **Mục tiêu:** khép phần còn hở của lời R17/R18 "CLI không traceback, không treo": file thiếu/sai kiểu khoá, stdout bị đóng giữa chừng, `TODO_FILE` là FIFO hay thiết bị đều ra thông báo một dòng và mã thoát đúng hợp đồng.
- **Phạm vi:**
  1. H-34: `store.load` từ chối phần tử thiếu `title`/`done` hoặc sai kiểu (`title` không phải chuỗi, `done` không phải bool, `due` có mà không phải chuỗi ngày hợp lệ) → `StoreError`, exit 2, không `Traceback`, cho cả `list`, `overdue`, `add`, `done`, `due`; file nguyên byte. Việc không có `due` vẫn hợp lệ (brief).
  2. H-53: `todo list`/`overdue` ghi vào pipe đã đóng (`| head -1`) → thoát 0 hoặc 2, stderr không chứa `Exception ignored`/`BrokenPipeError`, không mã 120.
  3. H-54: `TODO_FILE` không phải file thường (FIFO, thiết bị) → exit 2 "không phải file thường" trước khi mở đọc, không treo; file vượt giới hạn kích thước (hằng trong `store.py`) → exit 2.
- **Chỉ số giữ:** A1, A2, A3, A4 (smoke A5 vẫn đạt).
- **Ước tính:** ~3 task, **2,5 USD**, **1 giờ** (theo R18 đo: 4 task, 2,40 + ~1,38 USD; mốc này ít ý hơn).
- **Xong khi:** mỗi ý có test đỏ trên `origin/main` trước khi sửa (tên theo audit: `test_cli_errors.py::test_load_rejects_bad_title_done_types` tham số hoá thiếu/sai kiểu cho `list` và `overdue`; subprocess `todo list` với stdout pipe đóng → returncode ∈ {0, 2}, không `Exception ignored`; `test_store_safety.py` `os.mkfifo` + `subprocess.run(timeout=5)` → exit 2); `uv run pytest -q`, `uv run ruff check .` sạch; smoke A5 vẫn đạt.
- **Phụ thuộc:** R18.
- **Pre-mortem:**
  1. *Kiểm kiểu chặt làm file cũ hợp lệ bị từ chối*: chỉ đòi các khoá mà `add` luôn ghi (`id`, `title`, `done`); `due` vẫn tuỳ chọn; test giữ ca file R1 không có `due` và file do `add` tạo vẫn đọc được.
  2. *Xử lý BrokenPipe che lỗi ghi thật hoặc test chập chờn*: chỉ bắt `BrokenPipeError` ở biên in và chuyển stdout về `os.devnull` trước khi thoát; test dùng đủ nhiều việc (≥ 20000) và đóng đầu đọc rõ ràng, không dựa vào thời gian.
  3. *Test FIFO treo cả bộ pytest khi bản sửa hỏng*: luôn chạy qua `subprocess.run(timeout=5)`, bỏ qua trên nền tảng không có `os.mkfifo`; kiểm `S_ISREG` bằng `os.stat` trước `open`, không mở rồi mới kiểm.

## Tổng
| Mốc | Phụ thuộc | Chỉ số | USD | Giờ máy |
|---|---|---|---|---|
| R1 | – | A1 (A3, A4) | 4 | 0,5 |
| R2 | R1 | A2, A5 (A3, A4) | 4 | 0,4 |
| R17 | R2 | A1, A2, A3, A4 | 1,5 | 0,3 |
| R18 | R17 | A1, A2, A3, A4 | 3 | 1,4 |
| R20 | R18 | A1, A2, A3, A4 | 2,5 | 1 |
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
