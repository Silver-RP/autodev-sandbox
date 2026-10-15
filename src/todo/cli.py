"""todo add <title> | todo list | todo done <id>   (file: $TODO_FILE or ./todo.json)"""

import os
import sys
from pathlib import Path

from todo import store


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(os.environ.get("TODO_FILE", "todo.json"))
    if argv[:1] == ["add"] and len(argv) > 1:
        print(store.add(path, " ".join(argv[1:]))["id"])
        return 0
    if argv == ["list"]:
        for i in store.load(path):
            print(f"{i['id']}\t{'x' if i['done'] else ' '}\t{i['title']}")
        return 0
    if argv[:1] == ["done"] and len(argv) == 2 and argv[1].isdigit():
        return 0 if store.complete(path, int(argv[1])) else 1
    print(__doc__, file=sys.stderr)
    return 2
