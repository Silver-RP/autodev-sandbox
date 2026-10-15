"""Todo items stored as a JSON list in one file."""

import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _umask() -> int:
    mask = os.umask(0)
    os.umask(mask)
    return mask


def save(path: Path, items: list[dict]) -> None:
    """Ghi nguyên tử: file tạm cùng thư mục, fsync, rồi os.replace; lỗi giữa chừng không làm hỏng file cũ."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            os.chmod(tmp, path.stat().st_mode & 0o777 if path.exists() else 0o666 & ~_umask())
            f.write(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def valid_due(text: str) -> bool:
    if not isinstance(text, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def add(path: Path, title: str, due: str | None = None) -> dict:
    items = load(path)
    item = {"id": max((i["id"] for i in items), default=0) + 1, "title": title, "done": False}
    if due is not None:
        item["due"] = due
    save(path, [*items, item])
    return item


def set_due(path: Path, item_id: int, due: str) -> bool:
    items = load(path)
    for i in items:
        if i["id"] == item_id:
            i["due"] = due
            save(path, items)
            return True
    return False


def complete(path: Path, item_id: int) -> bool:
    items = load(path)
    found = False
    for i in items:
        if i["id"] == item_id:
            i["done"], found = True, True
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
