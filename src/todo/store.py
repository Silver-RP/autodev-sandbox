"""Todo items stored as a JSON list in one file."""

import contextlib
import fcntl
import json
import math
import os
import re
import tempfile
import time
from datetime import date
from pathlib import Path


class StoreError(ValueError):
    """File dữ liệu hỏng hoặc sai cấu trúc."""


def load(path: Path) -> list[dict]:
    try:
        os.stat(path)
    except FileNotFoundError:
        return []
    except OSError as e:
        raise StoreError(f"{path}: không truy cập được ({e.strerror})") from e
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise StoreError(f"{path}: không đọc được ({e.strerror})") from e
    except UnicodeDecodeError as e:
        raise StoreError(f"{path}: không phải UTF-8 ({e.reason})") from e
    except json.JSONDecodeError as e:
        raise StoreError(f"{path}: JSON hỏng ({e.msg}, dòng {e.lineno} cột {e.colno})") from e
    except RecursionError as e:
        raise StoreError(f"{path}: JSON lồng quá sâu") from e
    except ValueError as e:
        raise StoreError(f"{path}: JSON không đọc được ({e})") from e
    if not isinstance(data, list):
        raise StoreError(f"{path}: gốc phải là danh sách")
    seen: set[int] = set()
    for n, item in enumerate(data, 1):
        if not isinstance(item, dict):
            raise StoreError(f"{path}: phần tử {n} không phải đối tượng")
        if "id" not in item:
            raise StoreError(f'{path}: phần tử {n} thiếu "id"')
        if not isinstance(item["id"], int) or isinstance(item["id"], bool):
            raise StoreError(f'{path}: phần tử {n} có "id" không phải số nguyên')
        if item["id"] < 0:
            raise StoreError(f'{path}: phần tử {n} có "id" âm ({item["id"]})')
        if item["id"] in seen:
            raise StoreError(f'{path}: phần tử {n} có "id" trùng ({item["id"]})')
        seen.add(item["id"])
    return data


def _umask() -> int:
    mask = os.umask(0)
    os.umask(mask)
    return mask


def lock_path(path: Path) -> str:
    """Đối tượng khoá: thư mục chứa đích thật (không bị os.replace thay, không sinh file mới)."""
    return os.path.dirname(os.path.realpath(path))


def _lock_timeout() -> float:
    raw = os.environ.get("TODO_LOCK_TIMEOUT")
    if raw is None:
        return 5.0
    try:
        value = float(raw)
    except ValueError:
        value = float("nan")
    if not math.isfinite(value) or value <= 0:
        raise StoreError(f"TODO_LOCK_TIMEOUT không hợp lệ: {raw!r} (cần số thực hữu hạn > 0, giây)")
    return value


@contextlib.contextmanager
def lock(path: Path):
    """Khoá độc quyền flock quanh đọc-sửa-ghi; chờ tối đa TODO_LOCK_TIMEOUT giây."""
    timeout = _lock_timeout()
    fd = os.open(lock_path(path), os.O_RDONLY)
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise StoreError(
                        f"{path}: đang bị khoá bởi tiến trình khác (quá {timeout:g} giây)"
                    ) from None
                time.sleep(0.02)
        yield
    finally:
        os.close(fd)


def save(path: Path, items: list[dict]) -> None:
    """Ghi nguyên tử vào đích thật (qua symlink): file tạm cùng thư mục đích, fsync, os.replace."""
    path = Path(os.path.realpath(path))
    try:
        data = (json.dumps(items, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    except RecursionError as e:
        raise StoreError(f"{path}: dữ liệu lồng quá sâu để ghi") from e
    except UnicodeEncodeError as e:
        raise StoreError(f"{path}: dữ liệu không phải UTF-8 hợp lệ, không ghi") from e
    except ValueError as e:
        raise StoreError(f"{path}: không ghi được JSON ({e})") from e
    try:
        st = os.stat(path)
    except FileNotFoundError:
        st = None
    except OSError as e:
        raise StoreError(f"{path}: không truy cập được ({e.strerror})") from e
    if st is not None and not os.access(path, os.W_OK):
        raise StoreError(f"{path}: file không ghi được (chỉ đọc), không ghi đè")
    if st is not None and st.st_nlink > 1:
        _write_in_place(path, data)
        return
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            os.chmod(tmp, st.st_mode & 0o777 if st else 0o666 & ~_umask())
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def _write_in_place(path: Path, data: bytes) -> None:
    """File có hard link: ghi tại chỗ để giữ inode, link và quyền."""
    with open(path, "r+b") as f:
        f.truncate(0)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def valid_due(text: str) -> bool:
    if not isinstance(text, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


_BREAKS = re.compile("\r\n|[\t\n\r\x0b\x0c\x1c\x1d\x1e\x85  ]")


def clean_title(title: str) -> str:
    """Thay mọi ký tự xuống dòng và tab bằng một khoảng trắng."""
    return _BREAKS.sub(" ", title)


def add(path: Path, title: str, due: str | None = None) -> dict:
    title = clean_title(title)
    with lock(path):
        items = load(path)
        item = {"id": max((i["id"] for i in items), default=0) + 1, "title": title, "done": False}
        if due is not None:
            item["due"] = due
        save(path, [*items, item])
    return item


def set_due(path: Path, item_id: int, due: str) -> bool:
    with lock(path):
        items = load(path)
        for i in items:
            if i["id"] == item_id:
                i["due"] = due
                save(path, items)
                return True
    return False


def complete(path: Path, item_id: int) -> bool:
    with lock(path):
        items = load(path)
        found = False
        for i in items:
            if i["id"] == item_id:
                i["done"], found = True, True
        if found:
            save(path, items)
    return found


def today() -> date:
    raw = os.environ.get("TODO_TODAY")
    if raw is None:
        return date.today()
    if not valid_due(raw):
        raise ValueError(f"TODO_TODAY không hợp lệ: {raw!r}")
    return date.fromisoformat(raw)


def overdue(items: list[dict], ref: date) -> list[dict]:
    out = []
    for i in items:
        due = i.get("due")
        if i.get("done") or not valid_due(due):
            continue
        if date.fromisoformat(due) < ref:
            out.append(i)
    return sorted(out, key=lambda i: (i["due"], i["id"]))
