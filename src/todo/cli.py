"""CLI todo.

    todo add <title...> [--due YYYY-MM-DD]
    todo list
    todo overdue
    todo done <id>
    todo due <id> <YYYY-MM-DD>

File: $TODO_FILE hoặc ./todo.json. $TODO_TODAY=YYYY-MM-DD đặt ngày hôm nay cho overdue.
"""

import os
import re
import sys
from pathlib import Path

from todo import store


def _fail(msg: str) -> int:
    """In một dòng ra stderr (an toàn với surrogate), trả 2."""
    line = " ".join(msg.split()) or "lỗi"
    sys.stderr.write(line.encode("utf-8", "backslashreplace").decode("utf-8") + "\n")
    return 2


def _to_id(text: str) -> int | None:
    """int(text), hoặc None khi quá dài so với giới hạn chuyển chuỗi -> số của Python."""
    try:
        return int(text)
    except ValueError:
        return None


def _usage() -> int:
    print(__doc__, file=sys.stderr)
    return 2


def _line(i: dict) -> str:
    return f"{i['id']}\t{'x' if i['done'] else ' '}\t{i.get('due') or ''}\t{i['title']}"


def _bad_date(text: str) -> int:
    print(f"ngày không hợp lệ: {text!r} (cần YYYY-MM-DD)", file=sys.stderr)
    return 2


def _add(path: Path, args: list[str]) -> int:
    due = None
    if "--due" in args:
        k = args.index("--due")
        if k != len(args) - 2:
            return _usage()
        due = args[k + 1]
        args = args[:k]
        if not store.valid_due(due):
            return _bad_date(due)
    if not args:
        return _usage()
    title = store.clean_title(" ".join(args))
    if not title.strip():
        print("tiêu đề không được rỗng", file=sys.stderr)
        return 2
    try:
        title.encode("utf-8")
    except UnicodeEncodeError:
        return _fail("tiêu đề không phải UTF-8 hợp lệ")
    print(store.add(path, title, due=due)["id"])
    return 0


def _is_id(text: str) -> bool:
    return re.fullmatch(r"[0-9]+", text) is not None


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(os.environ.get("TODO_FILE", "todo.json"))
    try:
        return _run(argv, path)
    except (store.StoreError, ValueError, RecursionError) as e:
        return _fail(str(e) or type(e).__name__)


def _run(argv: list[str], path: Path) -> int:
    if argv[:1] == ["add"] and len(argv) > 1:
        return _add(path, argv[1:])
    if argv == ["list"]:
        for i in store.load(path):
            print(_line(i))
        return 0
    if argv == ["overdue"]:
        try:
            today = store.today()
        except ValueError as e:
            print(e, file=sys.stderr)
            return 2
        for i in store.overdue(store.load(path), today):
            print(_line(i))
        return 0
    if argv[:1] == ["done"] and len(argv) == 2 and _is_id(argv[1]):
        item_id = _to_id(argv[1])
        if item_id is None:
            return _fail(f"id không hợp lệ (quá dài): {len(argv[1])} chữ số")
        if store.complete(path, item_id):
            return 0
        print(f"không có việc id {argv[1]}", file=sys.stderr)
        return 1
    if argv[:1] == ["due"] and len(argv) == 3 and _is_id(argv[1]):
        if not store.valid_due(argv[2]):
            return _bad_date(argv[2])
        item_id = _to_id(argv[1])
        if item_id is None:
            return _fail(f"id không hợp lệ (quá dài): {len(argv[1])} chữ số")
        if store.set_due(path, item_id, argv[2]):
            return 0
        print(f"không có việc id {argv[1]}", file=sys.stderr)
        return 1
    return _usage()
