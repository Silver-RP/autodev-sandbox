"""CLI todo.

    todo add <title...> [--due YYYY-MM-DD]
    todo list
    todo overdue
    todo done <id>
    todo due <id> <YYYY-MM-DD>

File: $TODO_FILE hoặc ./todo.json. $TODO_TODAY=YYYY-MM-DD đặt ngày hôm nay cho overdue.
"""

import os
import sys
from pathlib import Path

from todo import store


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
    print(store.add(path, " ".join(args), due=due)["id"])
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(os.environ.get("TODO_FILE", "todo.json"))
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
    if argv[:1] == ["done"] and len(argv) == 2 and argv[1].isdigit():
        return 0 if store.complete(path, int(argv[1])) else 1
    if argv[:1] == ["due"] and len(argv) == 3 and argv[1].isdigit():
        if not store.valid_due(argv[2]):
            return _bad_date(argv[2])
        if store.set_due(path, int(argv[1]), argv[2]):
            return 0
        print(f"không có việc id {argv[1]}", file=sys.stderr)
        return 1
    return _usage()
